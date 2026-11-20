import os
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")
ALLOWED_ID = 6345411422

client = None
if GEMINI_KEY:
    try:
        client = genai.Client(api_key=GEMINI_KEY.strip())
    except:
        client = None

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

async def ask_ai(question: str):
    for model_name in ["gemini-3.8-flash", "gemini-3-flash", "gemini-2.5-flash"]:
        try:
            resp = client.models.generate_content(
                model=model_name,
                contents=f"انت بوت مسابقات دردشة عربية. جاوب بجواب واحد قصير ومباشر فقط، بدون شرح طويل. السؤال: {question}"
            )
            if resp.text:
                return resp.text.strip()
        except:
            continue
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
    if not client:
        await update.message.reply_text("❌ مفتاح GEMINI_KEY مو موجود")
        return
    await update.message.reply_text("🤔 سؤال جديد، دا أسأل الذكاء...")
    ans = await ask_ai(msg)
    if ans:
        await update.message.reply_text(f"🤖 جواب الذكاء: {ans}")
    else:
        await update.message.reply_text("❌ الذكاء ما رد")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))
app.run_polling()
