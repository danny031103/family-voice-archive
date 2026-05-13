"""Audio (base64) → raw transcript via Claude."""
# Imports planned:
# from processing.claude import transcribe
# from tenacity import retry, stop_after_attempt, wait_exponential


async def transcribe_audio(file_path: str) -> str:
    """Read audio file and return raw transcript string.

    On repeated failure, raises TranscriptionError so caller can flag for manual review.
    """
    # TODO: read audio file bytes from file_path
    # TODO: call processing.claude.transcribe(audio_bytes)
    # TODO: return transcript string
    pass


class TranscriptionError(Exception):
    """Raised when transcription fails after all retries."""
    pass
