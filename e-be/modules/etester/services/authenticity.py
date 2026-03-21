"""
modules/etester/services/authenticity.py
────────────────────────────────────────
Score an essay's authenticity using Claude + RAG context.
"""

import json
import logging
from datetime import datetime

from modules.etester.prompts import AUTHENTICITY_SYSTEM, AUTHENTICITY_USER_TEMPLATE
from modules.etester.repository import get_essay_history, get_student
from modules.etester.schemas import AuthenticityRequest, AuthenticityResponse
from shared.clients.rag_client import get_rag_client

logger = logging.getLogger(__name__)


async def score_authenticity_service(
    essay: str,
    student_id: str,
    rubric_context: str | None,
    db,
) -> AuthenticityResponse:
    """
    Score an essay's authenticity using AI.

    The score reflects:
      - Voice consistency with the student's history
      - Age-appropriate language and reasoning
      - Structural coherence
      - Personal voice vs template/AI-generic language

    Args:
        essay:           The essay text to evaluate.
        student_id:      Target student (for context retrieval).
        rubric_context:  Optional rubric or assignment brief.
        db:              Async SQLAlchemy session.

    Returns:
        AuthenticityResponse with score (0–1), reasons, flags, and suggestions.
    """
    # ── 1. Fetch student & writing history ─────────────────────────────────
    student = await get_student(student_id, db)
    writing_level = f"IELTS {student.ielts_score}" if student and student.ielts_score else "unknown"

    essay_history = await get_essay_history(student_id, db, limit=5)

    # Build writing context string from history
    history_context = ""
    if essay_history:
        history_lines = []
        for m in essay_history[:3]:
            history_lines.append(
                f"[{m.type}] {m.title} | score={m.score} | notes={m.notes or ''}"
            )
        history_context = "\n".join(history_lines)

    # ── 2. Call RAG-augmented authenticity scorer ────────────────────────────
    rag = get_rag_client()

    try:
        raw_result = rag.score_essay_authenticity(
            essay=essay,
            student_id=student_id,
            rubric_context=rubric_context,
        )
    except Exception as exc:
        logger.warning("RAG authenticity call failed: %s – using fallback", exc)
        raw_result = {"score": 0.5, "reasons": ["Unable to evaluate – please try again."], "flags": []}

    # Validate and normalise the score
    score = raw_result.get("score", 0.5)
    if not isinstance(score, (int, float)) or not (0.0 <= score <= 1.0):
        score = 0.5

    reasons = raw_result.get("reasons", [])
    flags = raw_result.get("flags", [])
    suggestions = raw_result.get("suggestions", [])

    # Supplement with history-based voice check if available
    if history_context and len(essay) > 200:
        # Simple heuristic: check if essay shares vocabulary with history
        history_words = set(history_context.lower().split())
        essay_words = set(essay.lower().split())
        overlap_ratio = len(history_words & essay_words) / max(len(history_words), 1)

        if overlap_ratio < 0.05 and score > 0.6:
            flags.append(
                "Voice differs significantly from previous submissions – "
                "ensure this is genuinely your own work."
            )

    return AuthenticityResponse(
        student_id=student_id,
        score=round(score, 3),
        reasons=reasons,
        flags=flags,
        suggestions=suggestions,
        scored_at=datetime.utcnow().isoformat() + "Z",
    )
