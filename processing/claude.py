"""All Claude API calls — transcription, structuring, and prompt selection."""
import json
import re

import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL


def get_client() -> anthropic.Anthropic:
    """Return an initialized Anthropic client."""
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def transcribe(file_path: str) -> str:
    """Transcribe an audio file via OpenAI Whisper and return raw transcript text."""
    import openai
    from config import OPENAI_API_KEY
    oai = openai.OpenAI(api_key=OPENAI_API_KEY)
    with open(file_path, "rb") as f:
        result = oai.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="text",
        )
    return result.strip()


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
