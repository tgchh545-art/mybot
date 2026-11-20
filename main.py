import os, requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")
ALLOWED_ID = 6345411422

# قاموس جاهز - يجاوب حتى بدون ذكاء
OFFLINE = {
    "السعودية": "الرياض",
    "السعوديه": "الرياض",
    "عاصمة السعودية": "الرياض",
    "عاصمه السعوديه": "الرياض",
    "عاصمه الدوله السعوديه": "الرياض",
    "ماهيه عاصمه الدوله السعوديه": "الرياض",
    "العراق": "بغداد",
    "عاصمة العراق": "بغداد",
    "فرنسا": "باريس",
    "عاصمة فرنسا": "باريس",
    "مصر": "القاهرة",
    "سوريا": "دمشق",
    "الاردن": "عمان",
    "الكويت": "الكويت",
    "قطر": "الدوحة",
    "الامارات": "أبوظبي",
    "تركيا": "أنقرة",
    "امريكا": "واشنطن",
    "بريطانيا": "لندن",
    "المانيا": "برلين",
    "ايطاليا": "روما",
    "روسيا": "موسكو",
}

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
    await update.message.reply_text(
        f"🔥 بوت مرتضى الذكي جاهز\n"
        f"عندي {len(QUESTIONS)} سؤال محفوظ\n"
        f"+ ذكاء Groq لأي سؤال جديد\n\n"
        f"دزلي أي سؤال"
    )

def ask_g
