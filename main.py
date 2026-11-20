import os, re
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")
ALLOWED_ID = 6345411422

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

def load_questions():
    qs = {}
    try:
        with open("questions.txt", encoding="utf-8") as f:
            for line in f:
                if "|" in line:
                    q, a = line.strip().split("|", 1)
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

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check(update): return
    msg = update.message.text.strip()
    if msg in QUESTIONS:
        await update.message.reply_text(f"✅ الجواب: {QUESTIONS[msg]}")
        return
    for q, a in QUESTIONS.items():
        if msg in q or q in msg:
            await update.message.reply_text(f"✅ الجواب: {a}")
            return
    await update.message.reply_text("🤔 سؤال جديد، دا أسأل الذكاء...")
    try:
        prompt = f"جاوب بجواب واحد قصير ومباشر، بدون شرح طويل. السؤال: {msg}"
        resp = model.generate_content(prompt)
        await update.message.reply_text(f"🤖 جواب الذكاء: {resp.text.strip()}")
    except:
        await update.message.reply_text("❌ خطأ بالذكاء، تأكد من GEMINI_KEY")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))
app.run_polling()
