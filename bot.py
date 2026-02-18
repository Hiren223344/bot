import os
import logging
import requests
from dotenv import load_dotenv

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.frenix.sh")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

FIRST_NAME, LAST_NAME, USERNAME_INPUT = range(3)


def create_key(uid, username, fn, ln):
    try:
        r = requests.post(
            f"{API_BASE_URL}/v1/api-keys",
            json={
                "user_id": uid,
                "username": username,
                "first_name": fn,
                "last_name": ln,
            },
            timeout=15,
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enter first name:", reply_markup=ReplyKeyboardRemove())
    return FIRST_NAME


async def fname(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["fn"] = update.message.text
    await update.message.reply_text("Enter last name:")
    return LAST_NAME


async def lname(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["ln"] = update.message.text
    await update.message.reply_text("Enter username:")
    return USERNAME_INPUT


async def uname(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    res = create_key(u.id, update.message.text, ctx.user_data["fn"], ctx.user_data["ln"])

    if "error" in res:
        await update.message.reply_text(res["error"])
    else:
        await update.message.reply_text(f"API KEY:\n{res['api_key']}")

    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, fname)],
            LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, lname)],
            USERNAME_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, uname)],
        },
        fallbacks=[],
    )

    app.add_handler(conv)

    log.info("Bot started on Railway 🚀")
    app.run_polling()


if __name__ == "__main__":
    main()
