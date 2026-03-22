"""
modules/etester/services/auth_scoring.py
────────────────────────────────────────
Orchestrates the 7-dimension authenticity scoring pipeline.
"""

import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from modules.etester import repository as repo
from modules.etester.services.llm_service import score_authenticity_7dim

logger = logging.getLogger(__name__)


async def run_authenticity_check(
    student_id: str,
    milestone_id: int,
    essay_text: str,
    db: AsyncSession,
) -> dict:
    """
    Full authenticity scoring pipeline:
    1. Gather student context (writing history, trace links, notes)
    2. Call 7-dim LLM scorer
    3. Persist result
    4. Return scoring result

    Returns dict matching AuthScoringResultResponse fields.
    """
    essay_history = await repo.get_essay_history(student_id, db, limit=5)
    essay_history_context = "\n".join(
        f"  - {m.title} ({m.date}) score={m.score}"
        for m in essay_history
    )

    trace_links = await repo.get_trace_links_for_student(student_id, db)
    trace_links_context = "\n".join(
        f"  - {tl.relationship_type}: milestone {tl.from_milestone_id} → {tl.to_milestone_id} "
        f"(conf={tl.confidence:.2f}, confirmed={tl.confirmed_by_mentor})"
        for tl in trace_links[:20]
    )

    student_notes_context = "\n".join(
        f"  - {tl.student_context_note}"
        for tl in trace_links
        if tl.student_context_note
    )

    core = await repo.get_etester_core(student_id, db)
    student_writing_level = f"academic_score={core.academic_score}, writing_growth={core.writing_growth}" if core else "unknown"

    scoring = await score_authenticity_7dim(
        essay_text=essay_text,
        student_writing_level=student_writing_level,
        essay_history_context=essay_history_context or "No history available",
        trace_links_context=trace_links_context or "No trace links available",
        student_notes_context=student_notes_context or "No student notes available",
    )

    result_obj = await repo.save_auth_result(
        db,
        milestone_id=milestone_id,
        student_id=student_id,
        auth_score=scoring["auth_score"],
        verdict=scoring["verdict"],
        dimension_scores=scoring.get("dimension_scores"),
        explaining_artifacts=scoring.get("explaining_artifacts"),
        explanation_en=scoring.get("explanation_en"),
        explanation_vn=scoring.get("explanation_vn"),
    )

    return {
        "id": result_obj.id,
        "milestone_id": milestone_id,
        "student_id": student_id,
        "auth_score": result_obj.auth_score,
        "verdict": result_obj.verdict,
        "dimension_scores": result_obj.dimension_scores,
        "explaining_artifacts": result_obj.explaining_artifacts,
        "explanation_en": result_obj.explanation_en,
        "explanation_vn": result_obj.explanation_vn,
        "scored_at": result_obj.scored_at.isoformat(),
    }
