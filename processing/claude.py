"""All Claude API calls — transcription, structuring, and prompt selection."""
# Imports planned:
# import anthropic
# import base64
# from tenacity import retry, stop_after_attempt, wait_exponential
# from config import ANTHROPIC_API_KEY

# Model: claude-sonnet-4-20250514


def get_client():
    """Return an initialized Anthropic client."""
    # TODO: initialize anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    pass


def transcribe(audio_bytes: bytes, mime_type: str = "audio/ogg") -> str:
    """Send audio as base64 to Claude and return raw transcript text."""
    # TODO: base64-encode audio_bytes
    # TODO: call Claude with audio content block
    # TODO: return transcript string
    # TODO: retry 3x with exponential backoff via tenacity
    pass


def structure_transcript(transcript: str, prompt: str) -> dict:
    """Extract structured fields from raw transcript via Claude.

    Returns dict with keys: title, themes (list), summary, stage_directions.
    """
    # TODO: build system prompt asking Claude to extract fields as JSON
    # TODO: call Claude with transcript + original prompt
    # TODO: parse and return JSON response
    # TODO: retry 3x with exponential backoff
    pass


def pick_prompt(used_prompts: list) -> str:
    """Select the next unused prompt from the bank."""
    # TODO: filter PROMPT_BANK to exclude used_prompts
    # TODO: return a random unused prompt (or cycle if all used)
    pass
