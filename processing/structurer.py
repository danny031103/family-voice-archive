"""Raw transcript → structured JSON (title, themes, summary, folder)."""
from processing.claude import structure_transcript

REQUIRED_KEYS = {"title", "themes", "summary", "folder"}


async def structure(transcript: str, prompt: str) -> dict:
    """Return structured dict from transcript.

    Keys: title (str), themes (list[str]), summary (str), folder (str).
    themes are used to auto-create the Obsidian/Drive folder path.
    """
    result = structure_transcript(transcript, prompt)

    missing = REQUIRED_KEYS - set(result.keys())
    if missing:
        raise ValueError(f"Structured response missing required keys: {missing}")

    return result
