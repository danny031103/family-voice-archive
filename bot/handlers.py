"""Telegram message handlers — voice note reception and routing."""
import datetime
import logging
import os
import shutil

from telegram import Update
from telegram.ext import ContextTypes
from tenacity import RetryError

from config import ALLOWED_CHAT_IDS, ARCHIVIST_CHAT_ID, DRY_RUN
from processing.transcription import TranscriptionError, transcribe_audio
from processing.structurer import structure
from processing import embeddings
from storage.google_drive import upload_audio, upload_note
from storage.obsidian import format_note, make_audio_filename, make_note_filename
from storage import vector_db
from bot.state import append_recording, default_person_state, load_state, save_state

logger = logging.getLogger(__name__)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Receive a voice note, run it through the full pipeline."""
    chat_id = update.effective_chat.id

    # 1. Validate sender
    person = next((name for name, cid in ALLOWED_CHAT_IDS.items() if cid == chat_id), None)
    if person is None:
        return

    today = datetime.date.today().isoformat()
    state = load_state()
    prompt = state.get(person, default_person_state()).get("last_prompt_text") or "Tell me a story from your life."

    # 3. Download voice file from Telegram
    voice_file = await context.bot.get_file(update.message.voice.file_id)
    tmp_path = f"/tmp/{voice_file.file_unique_id}.ogg"
    await voice_file.download_to_drive(tmp_path)

    try:
        # 5. Transcribe
        try:
            transcript = await transcribe_audio(tmp_path)
        except TranscriptionError as exc:
            logger.error("Transcription failed: %s", exc)
            # Save raw audio to Drive flagged for manual review
            if not DRY_RUN:
                flagged_filename = f"FAILED-{today}-{person.lower()}-{voice_file.file_unique_id}.ogg"
                try:
                    await upload_audio(tmp_path, person, flagged_filename)
                except Exception as drive_exc:
                    logger.error("Also failed to upload flagged audio: %s", drive_exc)
            await context.bot.send_message(
                ARCHIVIST_CHAT_ID,
                f"Transcription failed for {person}'s voice note. Raw audio saved for manual review.\nError: {exc}",
            )
            return

        # 6. Structure transcript
        structured = await structure(transcript, prompt)

        title = structured["title"]
        themes = structured["themes"]
        summary = structured["summary"]
        folder = structured["folder"]

        # 7. Build real filenames
        audio_filename = make_audio_filename(today, person, title)
        note_filename = make_note_filename(today, title)

        # 8. Format markdown note
        note_content = format_note(
            title=title,
            date=today,
            person=person,
            themes=themes,
            prompt=prompt,
            summary=summary,
            transcript=transcript,
            audio_filename=audio_filename,
        )

        # 9. Upload or dry-run
        if DRY_RUN:
            output_dir = os.path.join("dryrun_output", person)
            os.makedirs(output_dir, exist_ok=True)
            audio_out = os.path.join(output_dir, audio_filename)
            note_out = os.path.join(output_dir, note_filename)
            shutil.copy(tmp_path, audio_out)
            with open(note_out, "w", encoding="utf-8") as f:
                f.write(note_content)
            logger.info("[DRY_RUN] would upload to Drive: _audio/%s/%s", person.lower(), audio_filename)
            logger.info("[DRY_RUN] would upload to Drive: %s/%s/%s", person, folder, note_filename)
        else:
            await upload_audio(tmp_path, person, audio_filename)
            await upload_note(note_content, person, folder, note_filename)

            audio_drive_path = f"_audio/{person.lower()}/{audio_filename}"
            note_drive_path = f"{person}/{folder}/{note_filename}"
            row = {
                "person": person,
                "title": title,
                "date": today,
                "prompt": prompt,
                "themes": themes,
                "summary": summary,
                "transcript": transcript,
                "audio_drive_path": audio_drive_path,
                "obsidian_note_path": note_drive_path,
            }
            recording_id = await vector_db.insert_recording(row)
            await embeddings.generate_and_store(recording_id, row)

        # 10. Update state
        state = load_state()
        person_state = state.get(person, default_person_state())
        person_state["last_response_time"] = datetime.datetime.utcnow().isoformat()
        person_state["recording_count"] = person_state.get("recording_count", 0) + 1
        state[person] = person_state
        save_state(state)
        append_recording({"person": person, "title": title, "date": today, "folder": folder})

        # 11. Reply to sender
        await update.message.reply_text("Got it, thank you ♥")

        # 12. Notify archivist
        await context.bot.send_message(
            ARCHIVIST_CHAT_ID,
            f"New story from {person} saved! \U0001f3b5 {folder} > {title}",
        )

    except Exception as exc:
        # Unwrap tenacity RetryError to surface the real underlying exception
        actual_exc = exc.last_attempt.exception() if isinstance(exc, RetryError) else exc
        logger.exception("Unexpected error in handle_voice: %s", actual_exc)
        # 12. Notify archivist — never reply to parent with error
        try:
            await context.bot.send_message(
                ARCHIVIST_CHAT_ID,
                f"Unexpected error processing {person}'s voice note: {actual_exc}",
            )
        except Exception:
            logger.exception("Failed to notify archivist")
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unexpected text messages from known senders."""
    chat_id = update.effective_chat.id
    person = next((name for name, cid in ALLOWED_CHAT_IDS.items() if cid == chat_id), None)
    if person is None:
        return

    await update.message.reply_text(
        "Voice notes work best! Just hold the microphone button and tell me a story \U0001f399️"
    )
