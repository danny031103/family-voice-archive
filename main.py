"""Entry point — starts Telegram polling + APScheduler."""
import asyncio
import logging
import os

from aiohttp import web
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from bot.handlers import handle_voice, handle_text
from bot.commands import cmd_ask, cmd_status, cmd_history, cmd_prompt, cmd_add, cmd_delete, callback_delete
from bot.scheduler import build_scheduler
from config import TELEGRAM_BOT_TOKEN, WEBHOOK_URL, WEBHOOK_SECRET
from processing.embeddings import sweep_unembedded

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


async def run_webhook(app: Application, port: int) -> None:
    url_path = TELEGRAM_BOT_TOKEN

    async def telegram_handler(request: web.Request) -> web.Response:
        if WEBHOOK_SECRET:
            if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
                return web.Response(status=403)
        update = Update.de_json(await request.json(), app.bot)
        await app.update_queue.put(update)
        return web.Response(text="OK")

    async def health(_request: web.Request) -> web.Response:
        return web.Response(text="OK")

    web_app = web.Application()
    web_app.router.add_post(f"/{url_path}", telegram_handler)
    web_app.router.add_get("/", health)

    runner = web.AppRunner(web_app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", port).start()

    async with app:
        await app.bot.set_webhook(
            url=f"{WEBHOOK_URL}/{url_path}",
            secret_token=WEBHOOK_SECRET or None,
        )
        await app.start()
        logger.info("Bot running (webhook mode) on port %s", port)
        await asyncio.Event().wait()
        await app.stop()

    await runner.cleanup()


def main() -> None:
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
    app.add_handler(CommandHandler("delete", cmd_delete))
    app.add_handler(CallbackQueryHandler(callback_delete, pattern=r"^delete:"))

    port = int(os.getenv("PORT", "8080"))

    if WEBHOOK_URL:
        asyncio.run(run_webhook(app, port))
    else:
        logger.info("Bot running (polling mode)")
        app.run_polling()


if __name__ == "__main__":
    main()
