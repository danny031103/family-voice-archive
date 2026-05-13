"""Generate embeddings and write to Supabase pgvector."""
# Imports planned:
# import openai
# from config import OPENAI_API_KEY  # or use Anthropic embeddings — decide on cost
# from storage.vector_db import upsert_embedding

# Embedding model: text-embedding-3-small (1536 dims)
# Input: title + " " + " ".join(themes) + " " + summary + " " + transcript


async def generate_and_store(recording_id: str, recording: dict) -> None:
    """Generate embedding for a recording and store in Supabase.

    recording dict expected keys: title, themes, summary, transcript.
    Failures are logged and continue — note marked unembedded for later sweep.
    """
    # TODO: build embedding input string from recording fields
    # TODO: call OpenAI text-embedding-3-small
    # TODO: call storage.vector_db.upsert_embedding(recording_id, vector)
    pass


def build_embedding_input(recording: dict) -> str:
    """Concatenate fields into the embedding input string."""
    # TODO: title + themes + summary + transcript
    pass
