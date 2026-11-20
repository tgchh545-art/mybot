import os
import re
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_KEY")
ALLOWED_ID = 6345411422

COMP = {}

def norm(t):
    t = re.sub(r'[\u064B-\u0652]', '', t)
    t = t.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    t = t.replace("ة", "ه").replace("ى", "ي")
    t = re.sub(r'\s+', ' ', t).strip()
    return t

OFFLINE = {
    "السعودية": "السعودية",
    "السعوديه": "السعودية",
    "عاصمة السعودية": "الرياض",
    "العراق": "بغداد",
    "فرنسا": "باريس",
    "مصر": "القاهرة",
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

def load_q():
    qs = {}
    try:
        with open("questions.txt", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "|" in line:
                    p = line.split("|", 1)
                    if p[0].strip() and p[1].strip():
                        qs[norm(p[0])] = p[1].strip()
    except:
        pass
    return qs

QUESTIONS = load_q()

async def check(update: Update):
    if update.effective_user.id != ALLOWED_ID:
        await update.message.reply_text("هذا البوت خاص، مو الك.")
        return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check(update):
        return
    await update.message.reply_text("بوت مرتضى جاهز\n/mosabqa - تشغيل وضع المسابقات\n/adi - إيقاف وضع المسابقات")

async def comp_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check(update):
        return
    COMP[update.effective_user.id] = True
    await update.message.reply_text("تم تشغيل وضع المسابقات - الجواب راح يطلع بالضبط بالـ ة الصحيحة")

async def comp_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check(update):
        return
    COMP[update.effective_user.id] = False
    await update.message.reply_text("تم إيقاف وضع المسابقات")

def ask_groq(q):
    if not GROQ_KEY:
        return None
    for model in ["openai/gpt-oss-120b", "llama-3.1-8b-instant"]:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            head = {"Authorization": "Bearer " + GROQ_KEY.strip(), "Content-Type": "application/json"}
            prompt = "جاوب بكلمة واحدة فقط. حافظ على التاء المربوطة ة والهاء ه كما هي. مثلا اكتب السعودية بالتاء المربوطة. لا تضع حركات. السؤال: " + q
            body = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.0}
            r = requests.post(url, headers=head, json=body, timeout=30)
            if r.status_code == 200:
                ans = r.json()["choices"][0]["message"]["content"].strip()
                ans = ans.split("\n")[0].strip()
                ans = re.sub(r'[\u064B-\u0652]', '', ans)
                return ans
        except:
            continue
    return None

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check(update):
        return
    raw = update.message.text.strip()
    s = norm(raw)
    is_comp = COMP.get(update.effective_user.id, False)
    for k in OFFLINE:
        if norm(k) in s:
            await update.message.reply_text(OFFLINE[k])
            return
    if s in QUESTIONS:
        await update.message.reply_text(QUESTIONS[s])
        return
    for q in QUESTIONS:
        if s in q or q in s:
            await update.message.reply_text(QUESTIONS[q])
            return
    if not is_comp:
        await update.message.reply_text("سؤال جديد، دا أسأل الذكاء...")
    ans = ask_groq(raw)
    if ans:
        if is_comp:
            await update.message.reply_text(ans)
        else:
            await update.message.reply_text("جواب الذكاء: " + ans)
    else:
        await update.message.reply_text("ما لقيت جواب")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("mosabqa", comp_on))
app.add_handler(CommandHandler("adi", comp_off))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))
app.run_polling()
