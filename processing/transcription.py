"""Audio (base64) → raw transcript via Claude."""
from processing.claude import transcribe


class TranscriptionError(Exception):
    """Raised when transcription fails after all retries."""
    pass


async def transcribe_audio(file_path: str) -> str:
    """Transcribe audio file and return raw transcript string.

    On repeated failure, raises TranscriptionError so caller can flag for manual review.
    """
    try:
        return transcribe(file_path)
    except Exception as exc:
        raise TranscriptionError(f"Transcription failed for {file_path}: {exc}") from exc
