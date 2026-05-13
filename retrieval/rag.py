"""Phase 4 — semantic search + Claude answer generation for /ask command."""
# Imports planned:
# from processing.embeddings import generate_embedding_vector
# from storage.vector_db import search_similar
# from processing.claude import get_client
# from config import ANTHROPIC_API_KEY


async def answer_query(question: str) -> dict:
    """Answer a natural language question using RAG over all recordings.

    Returns dict with keys: answer (str), sources (list of recording titles/dates).
    """
    # TODO: generate embedding for the question
    # TODO: retrieve top-k similar recordings from Supabase
    # TODO: build context from retrieved recordings (transcripts + metadata)
    # TODO: call Claude with context + question
    # TODO: return answer + source citations
    pass


async def retrieve_context(question: str, k: int = 5) -> list:
    """Return top-k relevant recordings for a question."""
    # TODO: embed question
    # TODO: call storage.vector_db.search_similar
    pass
