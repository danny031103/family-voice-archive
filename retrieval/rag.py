"""Phase 4 — semantic search + Claude answer generation for /ask command."""
import logging

from config import CLAUDE_MODEL
from processing.embeddings import generate_embedding
from processing.claude import get_client
from storage.vector_db import search_similar

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are a warm, thoughtful family archivist. You have access to voice note transcripts "
    "from family members. Answer the question using only the provided recordings as your source. "
    "If the answer isn't in the recordings, say so honestly and warmly."
)


async def retrieve_context(question: str, k: int = 5) -> list:
    """Return top-k relevant recordings for a question."""
    embedding = generate_embedding(question)
    return await search_similar(embedding, limit=k)


async def answer_query(question: str) -> dict:
    """Answer a natural language question using RAG over all recordings.

    Returns dict with keys:
      answer (str)
      sources (list of dicts with title, date, person, obsidian_note_path)
    """
    recordings = await retrieve_context(question)

    if not recordings:
        return {
            "answer": (
                "I wasn't able to find any recordings in the archive yet. "
                "Once family members send voice notes, I'll be able to search through their stories."
            ),
            "sources": [],
        }

    # Build context block for Claude
    context_parts = []
    for r in recordings:
        themes = r.get("themes") or []
        themes_str = ", ".join(themes) if themes else "—"
        context_parts.append(
            f"--- Recording from {r['person']} on {r['date']}: \"{r['title']}\" ---\n"
            f"Themes: {themes_str}\n"
            f"Summary: {r.get('summary', '')}\n"
            f"Transcript: {r.get('transcript', '')}"
        )

    context_block = "\n\n".join(context_parts)
    user_message = f"{context_block}\n\nQuestion: {question}\n\nAnswer:"

    client = get_client()
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    answer = response.content[0].text.strip()

    sources = [
        {
            "title": r.get("title", ""),
            "date": str(r.get("date", "")),
            "person": r.get("person", ""),
            "obsidian_note_path": r.get("obsidian_note_path", ""),
        }
        for r in recordings
    ]

    return {"answer": answer, "sources": sources}
