"""Supabase pgvector read/write for the recordings table."""
# Imports planned:
# from supabase import create_client, Client
# from config import SUPABASE_URL, SUPABASE_KEY

# Table schema (recordings):
#   id, person, title, date, prompt, themes, summary, transcript,
#   audio_drive_path, obsidian_note_path, embedding (vector 1536), created_at


def get_client():
    """Return an initialized Supabase client."""
    # TODO: create_client(SUPABASE_URL, SUPABASE_KEY)
    pass


async def save_recording(data: dict) -> str:
    """Insert a new recording row (without embedding). Returns row ID."""
    # TODO: insert into recordings table
    # TODO: return generated UUID
    pass


async def upsert_embedding(recording_id: str, embedding: list) -> None:
    """Update the embedding vector for an existing recording row."""
    # TODO: update recordings set embedding = embedding where id = recording_id
    pass


async def get_recent_recordings(person: str = None, limit: int = 10) -> list:
    """Return recent recordings, optionally filtered by person."""
    # TODO: query recordings table ordered by date desc
    # TODO: filter by person if provided
    # TODO: return list of dicts
    pass


async def search_similar(embedding: list, limit: int = 5) -> list:
    """Return recordings most similar to the given embedding vector (Phase 4)."""
    # TODO: call Supabase RPC for pgvector cosine similarity search
    # TODO: return ranked list of recordings
    pass
