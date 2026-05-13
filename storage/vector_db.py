"""Supabase pgvector read/write for the recordings table."""
import asyncio

from supabase import create_client, Client

from config import SUPABASE_URL, SUPABASE_KEY


def get_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


async def insert_recording(row: dict) -> str:
    """Insert a new recording row (without embedding). Returns generated UUID."""
    def _insert():
        client = get_client()
        result = client.table("recordings").insert(row).execute()
        return result.data[0]["id"]

    return await asyncio.to_thread(_insert)


async def find_unembedded() -> list:
    """Return recordings where embedding IS NULL."""
    def _query():
        client = get_client()
        result = (
            client.table("recordings")
            .select("id, title, themes, summary, transcript")
            .is_("embedding", "null")
            .execute()
        )
        return result.data

    return await asyncio.to_thread(_query)


async def get_recording(recording_id: str) -> dict:
    """Fetch a single recording row by ID."""
    def _query():
        client = get_client()
        result = (
            client.table("recordings")
            .select("*")
            .eq("id", recording_id)
            .single()
            .execute()
        )
        return result.data

    return await asyncio.to_thread(_query)


async def mark_embedded(recording_id: str, embedding: list) -> None:
    """Update the embedding vector for an existing recording row."""
    def _update():
        client = get_client()
        client.table("recordings").update({"embedding": embedding}).eq("id", recording_id).execute()

    await asyncio.to_thread(_update)


async def search_similar(embedding: list, limit: int = 5) -> list:
    """Return recordings most similar to the given embedding vector (Phase 4)."""
    def _rpc():
        client = get_client()
        result = client.rpc(
            "match_recordings",
            {"query_embedding": embedding, "match_count": limit},
        ).execute()
        return result.data

    return await asyncio.to_thread(_rpc)
