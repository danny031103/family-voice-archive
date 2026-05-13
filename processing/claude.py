"""All Claude API calls — transcription, structuring, and prompt selection."""
import base64
import json
import re

import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL


def get_client() -> anthropic.Anthropic:
    """Return an initialized Anthropic client."""
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def transcribe(audio_bytes: bytes, mime_type: str = "audio/ogg") -> str:
    """Send audio as base64 to Claude and return raw transcript text."""
    client = get_client()
    audio_b64 = base64.standard_b64encode(audio_bytes).decode("utf-8")

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=4096,
        system=(
            "You are transcribing a voice note. Preserve the speaker's exact voice and phrasing. "
            "Add stage directions like [laughing], [gets quiet], [sighs] where natural. "
            "Return only the transcript text."
        ),
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": audio_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Please transcribe this voice note.",
                    },
                ],
            }
        ],
    )
    return response.content[0].text.strip()


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def structure_transcript(transcript: str, prompt: str) -> dict:
    """Extract structured fields from raw transcript via Claude.

    Returns dict with keys: title (str), themes (list[str]), summary (str), folder (str).
    """
    client = get_client()

    system_prompt = (
        "You are a family archivist. Given a voice note transcript and the prompt that inspired it, "
        "extract structured metadata and return it as a JSON object with exactly these keys:\n"
        '  "title": a short evocative title for this story (string)\n'
        '  "themes": 2-4 short theme strings (list of strings, e.g. ["Childhood", "School"])\n'
        '  "summary": one sentence summarizing the story (string)\n'
        '  "folder": a single vault subfolder name that best fits the story, like "Childhood", '
        '"Advice", "Family", "Work", "Travel", "Relationships", "Milestones" (string)\n'
        "Return only valid JSON, no explanation, no markdown fences."
    )

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Original prompt: {prompt}\n\n"
                    f"Transcript:\n{transcript}"
                ),
            }
        ],
    )

    raw = response.content[0].text.strip()

    # Strip markdown code fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    return json.loads(raw)


def pick_prompt(used_prompts: list) -> str:
    """Select the next unused prompt from the bank. Populated in Phase 2."""
    pass
