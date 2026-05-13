"""Entry point — starts Telegram polling + APScheduler."""
import logging

from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from bot.handlers import handle_voice, handle_text
from bot.commands import cmd_ask, cmd_status, cmd_history, cmd_prompt, cmd_add
from bot.scheduler import build_scheduler
from config import TELEGRAM_BOT_TOKEN
from processing.embeddings import sweep_unembedded


def main() -> None:
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Family Voice Archive starting…")

    scheduler = None

    async def post_init(application: Application) -> None:
        nonlocal scheduler
        scheduler = build_scheduler(application)
        application.bot_data["scheduler"] = scheduler
        scheduler.start()
        logger.info("APScheduler started")
        await sweep_unembedded()

    async def post_shutdown(application: Application) -> None:
        if scheduler is not None and scheduler.running:
            scheduler.shutdown(wait=False)
            logger.info("APScheduler stopped")

    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("history", cmd_history))
    app.add_handler(CommandHandler("prompt", cmd_prompt))
    app.add_handler(CommandHandler("add", cmd_add))
    app.add_handler(CommandHandler("ask", cmd_ask))

    logger.info("Bot running (polling mode)")
    app.run_polling()


if __name__ == "__main__":
    main()
