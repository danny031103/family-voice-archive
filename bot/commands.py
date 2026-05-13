"""Telegram bot commands — /ask, /status, /history, /prompt, /add."""
# Imports planned:
# from telegram import Update
# from telegram.ext import ContextTypes
# from config import ARCHIVIST_CHAT_ID, ALLOWED_CHAT_IDS
# from retrieval.rag import answer_query
# from storage.vector_db import get_recent_recordings
# from bot.scheduler import send_prompt


async def cmd_ask(update, context):
    """/ask <question> — semantic search across all recordings (Phase 4)."""
    # TODO: validate sender is archivist
    # TODO: extract question from message
    # TODO: call retrieval.rag.answer_query
    # TODO: reply with answer + source citations
    pass


async def cmd_status(update, context):
    """/status — show last prompt sent and response status for each parent."""
    # TODO: validate sender is archivist
    # TODO: read state for Mom and Dad (last prompt time, last response time)
    # TODO: format and reply with status summary
    pass


async def cmd_history(update, context):
    """/history [person] — list recent recordings for a person."""
    # TODO: validate sender is archivist
    # TODO: query Supabase for recent recordings
    # TODO: format and reply with list
    pass


async def cmd_prompt(update, context):
    """/prompt [person] — immediately send a story prompt to a parent."""
    # TODO: validate sender is archivist
    # TODO: determine target (Mom, Dad, or both)
    # TODO: call scheduler.send_prompt
    pass


async def cmd_add(update, context):
    """/add <prompt text> — add a custom prompt to the bank."""
    # TODO: validate sender is archivist
    # TODO: append prompt to the runtime prompt bank
    # TODO: confirm with reply
    pass
