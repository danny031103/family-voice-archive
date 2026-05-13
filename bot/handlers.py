"""Telegram message handlers — voice note reception and routing."""
# Imports planned:
# from telegram import Update
# from telegram.ext import ContextTypes
# from config import ALLOWED_CHAT_IDS
# from processing.transcription import transcribe_audio
# from processing.structurer import structure_transcript
# from storage.google_drive import upload_audio, upload_note
# from storage.obsidian import format_note
# from storage.vector_db import save_recording
# from processing.embeddings import generate_embedding


async def handle_voice(update, context):
    """Receive a voice note, run it through the full pipeline."""
    # TODO: validate sender is in ALLOWED_CHAT_IDS (silently ignore unknown)
    # TODO: download audio file from Telegram
    # TODO: transcribe via processing.transcription
    # TODO: structure transcript via processing.structurer
    # TODO: upload audio to Google Drive
    # TODO: format and upload markdown note to Google Drive
    # TODO: save embedding to Supabase
    # TODO: reply to sender with confirmation
    # TODO: on failure, notify archivist (never surface errors to parents)
    pass


async def handle_text(update, context):
    """Handle unexpected text messages from known senders."""
    # TODO: send a gentle nudge asking for a voice note
    pass
