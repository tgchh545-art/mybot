import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")
ALLOWED_ID = 6345411422

print("GROQ_KEY موجود؟", bool(GROQ_KEY))
if GROQ_KEY:
    print("بداية المفتاح:", GROQ_KEY[:7])

OFFLINE = {
    "السعودية": "الرياض",
    "السعوديه": "الرياض",
    "عاصمة السعودية": "الرياض",
    "عاصمه الدوله السعوديه": "الرياض",
    "ماهيه عاصمه الدوله السعوديه": "الرياض",
    "العراق": "بغداد",
    "فرنسا": "باريس",
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
        f = open("questions.txt", encoding="utf-8")
        for line in f:
            if "|" in line:
                parts = line.strip().split("|", 1)
                qs[parts[0].strip()] = parts[1].strip()
        f.close()
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
    if not await check(update):
        return
    txt = "بوت مرتضى جاهز - GROQ موجود؟ " + str(bool(GROQ_KEY))
    await update.message.reply_text(txt)

def ask_groq(question):
    if not GROQ_KEY:
        return "GROQ_KEY فارغ"
    last_err = ""
    for model in ["openai/gpt-oss-120b", "llama-3.1-8b-instant", "llama-3.3-70b-versatile"]:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            head = {"Authorization": "Bearer " + GROQ_KEY.strip(), "Content-Type": "application/json"}
            msg_text = "جاوب بجواب واحد قصير ومباشر فقط بالعربي. السؤال: " + question
            body = {"model": model, "messages": [{"role": "user", "content": msg_text}], "temperature": 0.1}
            r = requests.post(url, headers=head, json=body, timeout=30)
            print("Groq model " + model + " status " + str(r.status_code))
            print(r.text[:400])
            if r.status_code == 200:
                data = r.json()
                return data["choices"][0]["message"]["content"].strip()
            last_err = "Groq " + str(r.status_code) + " - " + r.text[:200]
        except Exception as e:
            last_err = "Groq fail " + str(e)
    return "ERROR: " + last_err

def ask_pollinations(question):
    try:
        r = requests.post(
            "https://text.pollinations.ai/openai",
            json={"model": "openai", "messages": [{"role": "user", "content": "جاوب بجواب واحد قصير بالعربي: " + question}]},
            timeout=30
        )
        if r.status_code == 200:
            data = r.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("Polli fail " + str(e))
    return None

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check(update):
        return
    msg = update.message.text.strip()
    for key in OFFLINE:
        if key in msg:
            await update.message.reply_text("الجواب: " + OFFLINE[key])
            return
    if msg in QUESTIONS:
        await update.message.reply_text("الجواب: " + QUESTIONS[msg])
        return
    for q in QUESTIONS:
        if msg in q or q in msg:
            await update.message.reply_text("الجواب: " + QUESTIONS[q])
            return
    await update.message.reply_text("سؤال جديد، دا أسأل الذكاء...")
    ans = ask_groq(msg)
    if ans and not ans.startswith("ERROR"):
        await update.message.reply_text("جواب الذكاء: " + ans)
        return
    print("Groq failed, trying Pollinations")
    ans2 = ask_pollinations(msg)
    if ans2:
        await update.message.reply_text("جواب الذكاء: " + ans2)
        return
    await update.message.reply_text("الخطأ الحقيقي: " + str(ans))

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))
app.run_polling()
