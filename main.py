import os, requests, urllib.parse, json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_ID = 6345411422

def load_questions():
    qs = {}
    try:
        with open("questions.txt", encoding="utf-8") as f:
            for line in f:
                if "|" in line:
                    q, a = line.strip().split("|", 1)
                    if q.strip() and a.strip():
                        qs[q.strip()] = a.strip()
    except:
        pass
    return qs

QUESTIONS = load_questions()

async def check(update: Update):
    if update.effective_user.id != ALLOWED_ID:
        await update.message.reply_text("هذا البوت خاص، مو الك.")
        return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check(update): return
    await update.message.reply_text(f"🔥 بوت مرتضى الذكي جاهز\nعندي {len(QUESTIONS)} سؤال محفوظ + ذكاء لأي سؤال جديد")

def ask_ai(question: str):
    # مصدر 1: Pollinations POST - أقوى
    try:
        r = requests.post(
            "https://text.pollinations.ai/openai",
            json={
                "model": "openai",
                "messages": [{"role": "user", "content": f"جاوب بجواب واحد قصير ومباشر فقط بالعربي، بدون شرح. السؤال: {question}"}]
            },
            timeout=30
        )
        if r.status_code == 200:
            data = r.json()
            ans = data["choices"][0]["message"]["content"].strip()
            if ans:
                return ans
    except Exception as e:
        print("AI1 fail", e)

    # مصدر 2: Pollinations GET - احتياط
    try:
        url = "https://text.pollinations.ai/" + urllib.parse.quote(f"جاوب بجواب قصير: {question}")
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200 and r.text.strip():
            return r.text.strip()[:500]
    except Exception as e:
        print("AI2 fail", e)

    # مصدر 3: ويكيبيديا - للعواصم والدول
    try:
        r = requests.get(
            "https://ar.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(question),
            timeout=15, headers={"User-Agent": "Bot/1.0"}
        )
        if r.status_code == 200:
            d = r.json()
            if d.get("extract"):
                return d["extract"][:400]
    except:
        pass

    return None

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check(update): return
    msg = update.message.text.strip()
    if msg in QUESTIONS:
        await update.message.reply_text(f"✅ الجواب من ملف الاسئلة: {QUESTIONS[msg]}")
        return
    for q, a in QUESTIONS.items():
        if msg in q or q in msg:
            await update.message.reply_text(f"✅ الجواب: {a}")
            return
    await update.message.reply_text("🤔 سؤال جديد، دا أسأل الذكاء...")
    ans = ask_ai(msg)
    if ans:
        await update.message.reply_text(f"🤖 جواب الذكاء: {ans}")
    else:
        await update.message.reply_text("❌ الذكاء ما رد، جرب مرة ثانية")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))
app.run_polling()
