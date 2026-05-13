"""Generate embeddings and write to Supabase pgvector."""
import json
import logging
import os

import openai

from config import OPENAI_API_KEY
from storage import vector_db

logger = logging.getLogger(__name__)

_UNEMBEDDED_PATH = os.path.join(os.path.dirname(__file__), "..", "state", "unembedded.json")


def build_embedding_input(recording: dict) -> str:
    themes = recording.get("themes") or []
    return (
        recording.get("title", "")
        + " "
        + ", ".join(themes)
        + " "
        + recording.get("summary", "")
        + " "
        + recording.get("transcript", "")
    )


def generate_embedding(text: str) -> list:
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    return response.data[0].embedding


async def generate_and_store(recording_id: str, recording: dict) -> None:
    try:
        text = build_embedding_input(recording)
        embedding = generate_embedding(text)
        await vector_db.mark_embedded(recording_id, embedding)
    except Exception as exc:
        logger.error("Failed to generate/store embedding for %s: %s", recording_id, exc)
        _append_unembedded(recording_id)


def _append_unembedded(recording_id: str) -> None:
    path = os.path.abspath(_UNEMBEDDED_PATH)
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                entries = json.load(f)
        else:
            entries = []
        entries.append({"id": recording_id})
        with open(path, "w", encoding="utf-8") as f:
            json.dump(entries, f)
    except Exception as exc:
        logger.error("Failed to persist unembedded entry %s: %s", recording_id, exc)


async def sweep_unembedded() -> None:
    """On startup: retry embedding for any recordings that previously failed."""
    path = os.path.abspath(_UNEMBEDDED_PATH)

    local_ids: list[str] = []
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                entries = json.load(f)
            local_ids = [e["id"] for e in entries if "id" in e]
        except Exception as exc:
            logger.error("Could not read unembedded.json: %s", exc)

    try:
        db_rows = await vector_db.find_unembedded()
    except Exception as exc:
        logger.error("Could not query unembedded recordings from Supabase: %s", exc)
        db_rows = []

    # Merge: db rows take priority (full data), local_ids are fallback IDs only
    seen: set[str] = set()
    to_process: list[tuple[str, dict | None]] = []
    for row in db_rows:
        seen.add(row["id"])
        to_process.append((row["id"], row))
    for rid in local_ids:
        if rid not in seen:
            to_process.append((rid, None))

    if not to_process:
        return

    logger.info("sweep_unembedded: %d recordings to process", len(to_process))

    succeeded: set[str] = set()
    for recording_id, row in to_process:
        if row is None:
            try:
                row = await vector_db.get_recording(recording_id)
            except Exception as exc:
                logger.error("Could not fetch recording %s: %s", recording_id, exc)
                continue
        if not row:
            logger.warning("Recording %s not found in Supabase, skipping", recording_id)
            succeeded.add(recording_id)  # Remove stale entry
            continue
        try:
            text = build_embedding_input(row)
            embedding = generate_embedding(text)
            await vector_db.mark_embedded(recording_id, embedding)
            succeeded.add(recording_id)
            logger.info("sweep_unembedded: embedded %s", recording_id)
        except Exception as exc:
            logger.error("sweep_unembedded: failed for %s: %s", recording_id, exc)

    # Remove succeeded entries from unembedded.json
    if succeeded and os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                entries = json.load(f)
            remaining = [e for e in entries if e.get("id") not in succeeded]
            with open(path, "w", encoding="utf-8") as f:
                json.dump(remaining, f)
        except Exception as exc:
            logger.error("Could not update unembedded.json after sweep: %s", exc)
