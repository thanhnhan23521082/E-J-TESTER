"""
shared/clients/rag_client.py
────────────────────────────
RAG (Retrieval-Augmented Generation) orchestrator for ETEST ONE.
Currently a stub/mock implementation suitable for hackathon development.

Structure allows drop-in replacement with a real vector DB (Pinecone, Weaviate, etc.)
without changing the service layer.
"""

import json
import logging
from typing import Any

from pydantic import BaseModel

from shared.clients.llm_client import call_text

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Mock vector store (in-memory, no external dependencies)
# ─────────────────────────────────────────────────────────────────────────────
class MockVectorStore:
    """
    In-memory document store for hackathon / demo purposes.
    Stores a flat list of chunks with pre-computed similarity (simulated).

    In production, replace with Pinecone / Weaviate / FAISS index.
    """

    def __init__(self) -> None:
        # List of {"id": str, "text": str, "student_id": str, "metadata": dict}
        self._chunks: list[dict[str, Any]] = []

    def add_chunk(self, chunk_id: str, text: str, student_id: str, metadata: dict | None = None) -> None:
        self._chunks.append({
            "id": chunk_id,
            "text": text,
            "student_id": student_id,
            "metadata": metadata or {},
        })

    def retrieve(
        self,
        query: str,
        student_id: str | None = None,
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Retrieve the top_k most relevant chunks for a query.
        Current implementation: simple keyword overlap (mock).

        Args:
            query:       Search query string.
            student_id:  Optional filter – only return chunks for this student.
            top_k:       Maximum number of chunks to return.

        Returns:
            List of chunk dicts sorted by relevance.
        """
        query_words = set(query.lower().split())

        scored: list[tuple[float, dict[str, Any]]] = []
        for chunk in self._chunks:
            if student_id and chunk.get("student_id") != student_id:
                continue
            chunk_words = set(chunk["text"].lower().split())
            score = len(query_words & chunk_words) / max(len(query_words), 1)
            scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored[:top_k]]


# ── Global singleton store ─────────────────────────────────────────────────────
_vector_store = MockVectorStore()


def get_vector_store() -> MockVectorStore:
    return _vector_store


# ─────────────────────────────────────────────────────────────────────────────
# RAG orchestrator
# ─────────────────────────────────────────────────────────────────────────────
class RAGClient:
    """
    High-level RAG operations used by Smart Parenting and ETESTER services.

    Each method:
      1. Retrieves relevant context from the vector store
      2. Builds a prompt with context
      3. Calls Claude via `call_text`

    Replace the `_build_prompt` internals when migrating to a real vector DB.
    """

    def __init__(self) -> None:
        self._store = get_vector_store()

    # ── Smart Parenting helpers ───────────────────────────────────────────────

    def answer_parent_question(
        self,
        question: str,
        student_id: str,
        student_profile: dict[str, Any],
        conversation_history: list[dict[str, str]],
    ) -> str:
        """
        Answer a parent's question using RAG-augmented context.

        Args:
            question:            The parent's natural-language question.
            student_id:          Target student.
            student_profile:     Serialised student data for context.
            conversation_history: Previous turns [{role, content}, ...].

        Returns:
            AI-generated answer string.
        """
        # Retrieve relevant history chunks
        chunks = self._store.retrieve(question, student_id=student_id, top_k=3)

        # Build context string
        context_parts = [f"Student profile:\n{json.dumps(student_profile, indent=2, default=str)}"]
        if chunks:
            context_parts.append("Relevant history:\n" + "\n---\n".join(c["text"] for c in chunks))
        if conversation_history:
            context_parts.append(
                "Recent conversation:\n" +
                "\n".join(f'{h["role"]}: {h["content"]}' for h in conversation_history[-3:])
            )

        context = "\n\n".join(context_parts)

        prompt = (
            f"Context:\n{context}\n\n"
            f"Parent question: {question}\n\n"
            "Provide a helpful, empathetic, and specific answer to the parent. "
            "If you don't have enough information, say so honestly."
        )

        system = (
            "You are ETEST ONE's Smart Parenting AI assistant. "
            "You help parents understand their child's academic progress, wellbeing, "
            "and suggest constructive next steps. Be warm, specific, and data-driven."
        )

        return call_text(prompt=prompt, system_prompt=system, max_tokens=1024)

    # ── ETESTER helpers ───────────────────────────────────────────────────────

    def score_essay_authenticity(
        self,
        essay: str,
        student_id: str,
        rubric_context: str | None = None,
    ) -> dict[str, Any]:
        """
        Score an essay's authenticity (writing style consistency, structure, depth).

        Returns a dict with keys: score (0–1), reasons (list[str]), flags (list[str]).
        """
        prompt = (
            f"Essay to evaluate:\n{essay}\n\n"
            f"{'Rubric context: ' + rubric_context if rubric_context else ''}\n\n"
            "Evaluate the authenticity of this essay. Consider:\n"
            "1. Writing style consistency\n"
            "2. Age-appropriate vocabulary and reasoning\n"
            "3. Structural coherence\n"
            "4. Personal voice vs generic template language\n\n"
            "Respond ONLY with valid JSON:\n"
            '{"score": 0.0, "reasons": ["..."], "flags": ["..."]}'
        )

        system = (
            "You are an academic authenticity evaluator. "
            "Output strict JSON with a score between 0.0 and 1.0, "
            "a list of reasons for the score, and any red flags."
        )

        raw = call_text(prompt=prompt, system_prompt=system, max_tokens=512, temperature=0.2)

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Authenticity JSON parse failed, returning fallback: %s", raw[:100])
            return {"score": 0.5, "reasons": ["Parse error – defaulting to 0.5"], "flags": []}

    def build_student_narrative(
        self,
        student_id: str,
        milestones: list[dict[str, Any]],
        etester_core: dict[str, Any],
    ) -> str:
        """
        Build a compelling, human-readable student narrative for portfolio / parent digest.

        Returns a narrative paragraph (2–4 sentences).
        """
        milestones_text = json.dumps(milestones, indent=2, default=str)
        core_text = json.dumps(etester_core, indent=2, default=str)

        prompt = (
            f"Student milestones:\n{milestones_text}\n\n"
            f"ETESTER core profile:\n{core_text}\n\n"
            "Write a 2–4 sentence compelling narrative about this student's "
            "learning journey. Highlight growth, effort, and achievements. "
            "Make it suitable for a parent-facing portfolio summary."
        )

        system = (
            "You are an educational storytelling assistant. "
            "Write in a warm, inspiring, and factual tone. "
            "Focus on growth mindset language without exaggeration."
        )

        return call_text(prompt=prompt, system_prompt=system, max_tokens=512, temperature=0.7)


# ── Global singleton ───────────────────────────────────────────────────────────
_rag_client: RAGClient | None = None


def get_rag_client() -> RAGClient:
    global _rag_client
    if _rag_client is None:
        _rag_client = RAGClient()
    return _rag_client
