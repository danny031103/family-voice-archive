"""Entry point — starts Telegram polling + APScheduler."""
import logging

from dotenv import load_dotenv
from telegram.ext import Application, MessageHandler, filters

from bot.handlers import handle_voice, handle_text
from config import TELEGRAM_BOT_TOKEN


def main() -> None:
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Family Voice Archive starting…")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Bot running (polling mode)")
    app.run_polling()


if __name__ == "__main__":
    main()
