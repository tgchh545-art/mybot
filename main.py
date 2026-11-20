import os, re, random
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

# قاموس صغير لحل اسئلة رتب
KNOWN_WORDS = ["دكتور", "بغداد", "عراق", "كتاب", "مدرسة", "سيارة", "طائرة", "بحر", "شمس", "قمر", "وردة", "اسد", "نمر", "فيسبوك", "تلكرام", "يوتيوب"]

def solve_ratib(text):
    # يطلع الحروف من سؤال رتب
    letters = re.findall(r'[\u0621-\u064A]', text)
    if not letters:
        return None
    # يدور كلمة بنفس الحروف
    for w in KNOWN_WORDS:
        wl = list(w)
        if sorted(wl) == sorted(letters):
            return w
    return None

async def check(update: Update):
    if update.effective_user.id != ALLOWED_ID:
        await update.message.reply_text("هذا البوت خاص، مو الك.")
        return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check(update): return
    await update.message.reply_text(f"🔥 بوت مرتضى الذكي جاهز\nعندي {len(QUESTIONS)} سؤال محفوظ + ذكاء اصطناعي لأي سؤال جديد\n\nدزلي أي سؤال وأنا أجاوبك")

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check(update): return
    msg = update.message.text.strip()
    
    # 1. اذا موجود بملف الاسئلة
    if msg in QUESTIONS:
        await update.message.reply_text(f"✅ الجواب من ملف الاسئلة: {QUESTIONS[msg]}")
        return
    for q, a in QUESTIONS.items():
        if msg in q or q in msg:
            await update.message.reply_text(f"✅ لقيته بملف الاسئلة:\n{ q }\nالجواب: {a}")
            return

    # 2. اذا سؤال رتب، حاول حله
    if "رتب" in msg:
        solved = solve_ratib(msg)
        if solved:
            await update.message.reply_text(f"✅ حل سؤال رتب: {solved}")
            return

    # 3. اذا سؤال جديد، اسأل الذكاء الاصطناعي
    await update.message.reply_text("🤔 سؤال جديد، دا أسأل الذكاء الاصطناعي...")
    try:
        prompt = f"جاوب على هذا السؤال بجواب واحد قصير ومباشر، بدون شرح طويل. السؤال: {msg}"
        resp = model.generate_content(prompt)
        await update.message.reply_text(f"🤖 جواب الذكاء: {resp.text.strip()}")
    except Exception as e:
        await update.message.reply_text("❌ صار خطأ بالذكاء، تأكد من مفتاح GEMINI_KEY بالـ Secrets")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))
app.run_polling()
