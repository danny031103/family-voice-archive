"""Raw transcript → structured JSON (title, themes, summary, stage directions)."""
# Imports planned:
# from processing.claude import structure_transcript
# from tenacity import retry, stop_after_attempt, wait_exponential


async def structure(transcript: str, prompt: str) -> dict:
    """Return structured dict from transcript.

    Keys: title (str), themes (list[str]), summary (str), stage_directions (list[str]).
    themes are used to auto-create the Obsidian/Drive folder path.
    """
    # TODO: call processing.claude.structure_transcript
    # TODO: validate required keys are present
    # TODO: return structured dict
    pass
