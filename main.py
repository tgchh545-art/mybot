import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_ID = 6345411422  # هذا انت بس

async def check_user(update: Update):
    if update.effective_user.id != ALLOWED_ID:
        await update.message.reply_text("هذا البوت خاص، مو الك.")
        return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update):
        return
    await update.message.reply_text("هلا بيك ببوت مرتضى 🔥\nهذا البوت خاص بيك وحدك\nدز أي رسالة وأنا أرد عليك")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update):
        return
    await update.message.reply_text("الأوامر:\n/start - بدء\n/help - مساعدة")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_user(update):
        return
    text = update.message.text
    await update.message.reply_text(f"وصلتني رسالتك: {text}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    print("Bot is running - Private Mode")
    app.run_polling()
