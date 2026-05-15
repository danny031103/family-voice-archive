"""Telegram bot commands — /ask, /status, /history, /prompt, /add."""
import json
import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from config import ALLOWED_CHAT_IDS, ARCHIVIST_CHAT_ID
from storage import google_drive, vector_db
from bot.state import (
    default_person_state,
    load_state,
    save_state,
)
from bot.scheduler import send_prompt

logger = logging.getLogger(__name__)

_ALLOWLIST_FILE = os.path.join(os.path.dirname(__file__), "..", "state", "allowlist.json")


def _is_archivist(update: Update) -> bool:
    return update.effective_chat.id == ARCHIVIST_CHAT_ID


async def cmd_ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/ask <question> — semantic search across all recordings."""
    if not _is_archivist(update):
        return

    question = " ".join(context.args).strip() if context.args else ""
    if not question:
        await update.message.reply_text("Usage: /ask <question>\nExample: /ask What did Mom say about her childhood?")
        return

    placeholder = await update.message.reply_text("Searching the archive…")

    try:
        from retrieval.rag import answer_query
        result = await answer_query(question)
    except Exception as exc:
        logger.error("RAG query failed: %s", exc)
        await placeholder.edit_text("Sorry, something went wrong while searching the archive. Please try again.")
        return

    answer = result["answer"]
    sources = result["sources"]

    lines = [answer]
    if sources:
        lines.append("\n*Sources:*")
        for s in sources:
            folder = s.get("obsidian_note_path") or "—"
            lines.append(f"• {s['title']} — {s['date']} — {s['person']} — `{folder}`")

    await placeholder.edit_text("\n".join(lines), parse_mode="Markdown")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/status — show last prompt sent and response status for each parent."""
    if not _is_archivist(update):
        return

    state = load_state()
    lines = ["*Archive Status*\n"]

    for person in ["Mom", "Dad"]:
        ps = state.get(person, default_person_state())
        last_prompt = ps.get("last_prompt_text") or "—"
        last_prompt_sent = ps.get("last_prompt_sent") or "never"
        last_response = ps.get("last_response_time") or "never"
        count = ps.get("recording_count", 0)

        lines.append(
            f"*{person}*\n"
            f"  Recordings: {count}\n"
            f"  Last prompt: {last_prompt[:60]}{'…' if len(last_prompt) > 60 else ''}\n"
            f"  Prompt sent: {last_prompt_sent}\n"
            f"  Last response: {last_response}\n"
        )

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def cmd_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/history [person] — list last 10 recordings for a person."""
    if not _is_archivist(update):
        return

    args = context.args
    person_filter = args[0].strip() if args else None

    recent = await vector_db.get_recent_recordings(person=person_filter)

    if not recent:
        label = f" for {person_filter}" if person_filter else ""
        await update.message.reply_text(f"No recordings found{label}.")
        return

    lines = [f"*Last {len(recent)} recording(s)*\n"]
    keyboard = []
    for e in recent:
        lines.append(f"• [{e.get('date', '?')}] *{e.get('person', '?')}* — {e.get('title', '?')}")
        keyboard.append([
            InlineKeyboardButton(
                f"🗑 Delete: {e.get('title', e['id'])[:40]}",
                callback_data=f"delete:{e['id']}",
            )
        ])

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def cmd_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/prompt [name] — immediately send a story prompt to a parent."""
    if not _is_archivist(update):
        return

    args = context.args
    app = context.application
    if args:
        name = args[0].strip()
        chat_id = ALLOWED_CHAT_IDS.get(name)
        if chat_id is None:
            await update.message.reply_text(f"Unknown person: {name}. Known: {', '.join(ALLOWED_CHAT_IDS.keys())}")
            return
        await send_prompt(app, chat_id, name)
        await update.message.reply_text(f"Prompt sent to {name}.")
    else:
        for name, chat_id in ALLOWED_CHAT_IDS.items():
            if chat_id:
                await send_prompt(app, chat_id, name)
        await update.message.reply_text("Prompts sent to all parents.")


async def cmd_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/delete <recording_id> — delete a recording from Drive and Supabase."""
    if not _is_archivist(update):
        return

    if not context.args:
        await update.message.reply_text("Usage: /delete <recording_id>")
        return

    recording_id = context.args[0].strip()
    row = await vector_db.delete_recording(recording_id)
    if row is None:
        await update.message.reply_text(f"No recording found with id `{recording_id}`.", parse_mode="Markdown")
        return

    errors = []
    for field, label in [("audio_drive_id", "audio"), ("note_drive_id", "note")]:
        file_id = row.get(field)
        if file_id:
            try:
                await google_drive.delete_file(file_id)
            except Exception as exc:
                logger.error("Failed to delete Drive %s (id=%s): %s", label, file_id, exc)
                errors.append(f"{label} ({exc})")

    title = row.get("title", recording_id)
    if errors:
        await update.message.reply_text(
            f"Deleted from Supabase, but Drive deletion failed for: {', '.join(errors)}.\n"
            f"Recording: *{title}*",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(f"Deleted: *{title}*", parse_mode="Markdown")


async def callback_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inline-button handler for delete confirmations from /history."""
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ARCHIVIST_CHAT_ID:
        return

    recording_id = query.data.removeprefix("delete:")
    row = await vector_db.delete_recording(recording_id)
    if row is None:
        await query.edit_message_text(f"No recording found with id `{recording_id}`.", parse_mode="Markdown")
        return

    errors = []
    for field, label in [("audio_drive_id", "audio"), ("note_drive_id", "note")]:
        file_id = row.get(field)
        if file_id:
            try:
                await google_drive.delete_file(file_id)
            except Exception as exc:
                logger.error("Failed to delete Drive %s (id=%s): %s", label, file_id, exc)
                errors.append(f"{label} ({exc})")

    title = row.get("title", recording_id)
    if errors:
        await query.edit_message_text(
            f"Deleted from Supabase, but Drive deletion failed for: {', '.join(errors)}.\n"
            f"Recording: *{title}*",
            parse_mode="Markdown",
        )
    else:
        await query.edit_message_text(f"Deleted: *{title}*", parse_mode="Markdown")


async def cmd_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/add <name> <chat_id> — add a new person to the allowlist."""
    if not _is_archivist(update):
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /add <name> <chat_id>")
        return

    name = args[0].strip()
    try:
        chat_id = int(args[1].strip())
    except ValueError:
        await update.message.reply_text("chat_id must be an integer.")
        return

    os.makedirs(os.path.dirname(_ALLOWLIST_FILE), exist_ok=True)
    if os.path.exists(_ALLOWLIST_FILE):
        with open(_ALLOWLIST_FILE, "r", encoding="utf-8") as f:
            allowlist = json.load(f)
    else:
        allowlist = {}

    allowlist[name] = chat_id
    with open(_ALLOWLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(allowlist, f, indent=2)

    await update.message.reply_text(
        f"Added {name} (chat_id={chat_id}) to allowlist.json. Restart the bot for the change to take effect."
    )
