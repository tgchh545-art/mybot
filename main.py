import os
import re
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")
ALLOWED_ID = 6345411422

COMPETITION_MODE = {}

def normalize_for_search(text):
    if not text:
        return ""
    text = re.sub(r'[\u064B-\u0652]', '', text)
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    text = text.replace("ة", "ه").replace("ى", "ي")
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# الأجوبة هنا مكتوبة بالـ ة الصحيحة، لا تغيرها
OFFLINE = {
    "السعودية": "السعودية",
    "السعوديه": "السعودية",
    "عاصمة السعودية": "الرياض",
    "عاصمه الدوله السعوديه": "الرياض",
    "ماهيه عاصمه الدوله السعوديه": "الرياض",
    "العراق": "بغداد",
    "عاصمة العراق": "بغداد",
    "فرنسا": "باريس",
    "عاصمة فرنسا": "باريس",
    "مصر": "القاهرة",
    "عاصمة مصر": "القاهرة",
    "سوريا": "دمشق",
    "الاردن": "الأردن",
    "الكويت": "الكويت",
    "قطر": "الدوحة",
    "الامارات": "الإمارات",
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
                line = line.strip()
                if not line:
                    continue
                if "|" in line:
                    parts = line.split("|", 1)
                    q = parts[0].strip()
                    a = parts[1].strip()
                    if q and a:
                        key = normalize_for_search(q)
                        qs[key] = a
    except FileNotFoundError:
        pass
    except Exception as e:
        print("load_questions error: " + str(e))
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
    await update.message.reply_text("بوت مرتضى - وضع المسابقات الدقيق\n\n/مسابقة - تشغيل وضع المسابقات\n/عادي - إيقاف وضع المسابقات")

async def comp_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check(update):
        return
    COMPETITION_MODE[update.effective_user.id] = True
    await update.message.reply_text("تم تشغيل وضع المسابقات الدقيق - الجواب راح يطلع بالضبط بالـ ة والـ ه الصحيحة")

async def comp_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check(update):
        return
    COMPETITION_MODE[update.effective_user.id] = False
    await update.message.reply_text("تم إيقاف وضع المسابقات")

def ask_groq(question):
    if not GROQ_KEY:
        return None
    for model in ["openai/gpt-oss-120b", "llama-3.1-8b-instant"]:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            head = {"Authorization": "Bearer " + GROQ_KEY.strip(), "Content-Type": "application/json"}
            prompt = "انت بوت مسابقات دقيق جدا. جاوب بكلمة واحدة فقط. مهم جدا: حافظ على التاء المربوطة ة والهاء ه كما هي، لا تبدل بينهما. مثلا اكتب السعودية بالتاء المربوطة ة وليس السعوديه بالهاء. اكتب القاهرة بالتاء المربوطة. لا تضع حركات. السؤال: " + question
            body = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.0}
            r = requests.post(url, headers=head, json=body, timeout=30)
            if r.status_code == 200:
                data = r.json()
                ans = data["choices"][0]["message"]["content"].strip()
                ans = ans.split("\n")[0].strip()
                ans = re.sub(r'[\u064B-\u0652]', '', ans)
                return ans
        except Exception as e:
            print("Groq fail: " + str(e))
            continue
    return None

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check(update):
        return
    msg_raw = update.message.text.strip()
    if not msg_raw:
        return
    msg_search = normalize_for_search(msg_raw)
    is_comp = COMPETITION_MODE.get(update.effective_user.id, False)

    for key in OFFLINE:
        if normalize_for_search(key) in msg_search:
            await update.message.reply_text(OFFLINE[key])
            return

    if msg_search in QUESTIONS:
        await update.message.reply_text(QUESTIONS[msg_search])
        return

    for q in QUESTIONS:
        if msg_search in q or q in msg_search:
            await update.message.reply_text(QUESTIONS[q])
            return

    if not is_comp:
        await update.message.reply_text("سؤال جديد، دا أسأل الذكاء...")
    ans = ask_groq(msg_raw)
    if ans:
        if is_comp:
            await update.message.reply_text(ans)
        else:
            await update.message.reply_text("جواب الذكاء: " + ans)
    else:
        await update.message.reply_text("ما لقيت جواب")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("مسابقة", comp_on))
app.add_handler(CommandHandler("عادي", comp_off))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))
app.run_polling()
