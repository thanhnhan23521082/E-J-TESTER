"""
modules/etester/services/contribute.py
──────────────────────────────────────
Handle milestone contribution: validation → AI summary → DB persistence.
"""

import json
import logging
from datetime import datetime

from modules.etester.prompts import SUMMARIZE_SYSTEM, SUMMARIZE_USER_TEMPLATE
from modules.etester.repository import get_student, save_milestone
from modules.etester.schemas import ContributionRequest, MilestoneResponse
from shared.clients.llm_client import call_text
from shared.constants import MilestoneType

logger = logging.getLogger(__name__)

VALID_MILESTONE_TYPES = {m.value for m in MilestoneType}
VALID_CONTRIBUTOR_TYPES = {"student", "mentor", "parent", "institution"}


def validate_contribution(payload: ContributionRequest) -> None:
    """
    Validate a contribution request.

    Raises:
        ValueError with a descriptive message on failure.
    """
    if payload.type not in VALID_MILESTONE_TYPES:
        raise ValueError(
            f"Invalid milestone type '{payload.type}'. "
            f"Valid types: {sorted(VALID_MILESTONE_TYPES)}"
        )
    if payload.contributor_type not in VALID_CONTRIBUTOR_TYPES:
        raise ValueError(
            f"Invalid contributor_type '{payload.contributor_type}'. "
            f"Valid types: {sorted(VALID_CONTRIBUTOR_TYPES)}"
        )
    if payload.score is not None and (payload.score < 0 or payload.score > 100):
        raise ValueError(f"Score must be between 0 and 100, got {payload.score}")


async def _summarize_milestone(
    type: str,
    title: str,
    score: float | None,
    score_label: str | None,
    notes: str | None,
    date: str,
) -> str | None:
    """
    Call Claude to generate a short AI summary for a milestone.

    Returns None on failure (non-critical – we don't fail the whole request).
    """
    prompt = SUMMARIZE_USER_TEMPLATE.format(
        milestone_type=type,
        title=title,
        score=score,
        score_label=score_label or "N/A",
        notes=notes or "Không có ghi chú.",
        date=date,
    )
    try:
        return call_text(
            prompt=prompt,
            system_prompt=SUMMARIZE_SYSTEM,
            max_tokens=256,
            temperature=0.5,
        )
    except Exception as exc:
        logger.warning("Milestone summarization failed: %s", exc)
        return None


async def contribute_service(
    payload: ContributionRequest,
    db,
) -> MilestoneResponse:
    """
    Process a milestone contribution:
      1. Validate the payload
      2. Verify the student exists
      3. Generate an AI summary
      4. Persist the milestone to the database
      5. Return the created record

    Args:
        payload: The validated contribution request.
        db:      Async SQLAlchemy session.

    Returns:
        MilestoneResponse with the created milestone.

    Raises:
        StudentNotFound: if the student does not exist.
        ValueError: if the payload fails validation.
    """
    # ── 1. Validate ─────────────────────────────────────────────────────────
    try:
        validate_contribution(payload)
    except ValueError as exc:
        # Re-raise as a 422 so FastAPI maps it correctly
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    # ── 2. Student check ────────────────────────────────────────────────────
    student = await get_student(payload.student_id, db)
    if not student:
        from core.exceptions import StudentNotFound
        raise StudentNotFound(message=f"Student '{payload.student_id}' not found")

    # ── 3. AI summary (non-blocking – continue even if it fails) ─────────────
    date_str = payload.date if isinstance(payload.date, str) else str(payload.date)
    ai_summary = await _summarize_milestone(
        type=payload.type,
        title=payload.title,
        score=payload.score,
        score_label=payload.score_label,
        notes=payload.notes,
        date=date_str,
    )

    # ── 4. Persist ──────────────────────────────────────────────────────────
    milestone_date = datetime.fromisoformat(payload.date)
    milestone = await save_milestone(
        db=db,
        student_id=payload.student_id,
        milestone_id=payload.milestone_id,
        type=payload.type,
        title=payload.title,
        date=milestone_date,
        score=payload.score,
        score_label=payload.score_label,
        notes=payload.notes,
        contributor_type=payload.contributor_type,
        ai_summary=ai_summary,
    )

    # ── 5. Return ──────────────────────────────────────────────────────────
    return MilestoneResponse(
        id=milestone.id,
        student_id=milestone.student_id,
        milestone_id=milestone.milestone_id,
        type=milestone.type,
        title=milestone.title,
        date=milestone.date.isoformat(),
        score=milestone.score,
        score_label=milestone.score_label,
        notes=milestone.notes,
        status=milestone.status,
        contributor_type=milestone.contributor_type,
        ai_summary=milestone.ai_summary,
        auth_score=milestone.auth_score,
        created_at=milestone.date.isoformat(),
    )
