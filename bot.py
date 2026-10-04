import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import aiohttp

# ---------- SETTINGS ----------
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "YOUR_API_KEY_HERE")
AI_MODEL = "openrouter/free"
WELCOME_MSG = "Welcome {name} to ZeroX Chats! 🎉\nRules padho aur enjoy karo!"
# ------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_ai_reply(user_message: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": "You are a friendly chat bot in a Telegram group. Reply in short, friendly Hinglish/Urdu style."},
            {"role": "user", "content": user_message},
        ],
        "max_tokens": 150,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=30) as resp:
                data = await resp.json()
                return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"AI error: {e}")
        return "Sorry bhai, abhi reply nahi de pa raha. Thodi der baad try karo."


async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        name = member.first_name or "Bhai"
        msg = WELCOME_MSG.format(name=name)
        await update.message.reply_text(msg)


async def reply_to_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.is_bot:
        return
    if update.message.chat.type not in ["group", "supergroup"]:
        return
    user_text = update.message.text
    if not user_text:
        return
    ai_reply = await get_ai_reply(user_text)
    await update.message.reply_text(ai_reply)


def main():
    logger.info("Bot starting...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_to_message))
    logger.info("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
