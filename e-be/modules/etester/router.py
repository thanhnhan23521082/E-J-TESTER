"""
modules/etester/router.py
────────────────────────
FastAPI router for ETESTER endpoints.
All routes require Bearer authentication.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from modules.etester.repository import (
    get_all_milestones,
    get_contribution_summary,
    get_etester_core,
    get_student,
)
from modules.etester.schemas import (
    AuthenticityRequest,
    AuthenticityResponse,
    BadgeResponse,
    ContributionRequest,
    ContributionsListResponse,
    ETESTERCoreResponse,
    ETESTERProfileResponse,
    MilestoneResponse,
)
from modules.etester.services.authenticity import score_authenticity_service
from modules.etester.services.badge import badge_service
from modules.etester.services.contribute import contribute_service
from modules.etester.services.rebuild_core import rebuild_core_service
from shared.deps import get_current_user
from shared.model import User

router = APIRouter(prefix="/api/etester", tags=["etester"])


# ── Profile ───────────────────────────────────────────────────────────────────

@router.get(
    "/{student_id}",
    response_model=ETESTERProfileResponse,
    summary="Get full ETESTER profile",
)
async def get_etester_profile(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> ETESTERProfileResponse:
    """
    Return the full ETESTER profile for a student:
    aggregated core scorecard + recent milestones + cached narrative.
    """
    student = await get_student(student_id, db)
    if not student:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Student not found")

    core = await get_etester_core(student_id, db)
    milestones = await get_all_milestones(student_id, db, limit=20)

    if core:
        import json as _json
        skills_data = None
        if core.skills:
            try:
                skills_data = _json.loads(core.skills)
            except Exception:
                pass
        core_resp = ETESTERCoreResponse(
            student_id=core.student_id,
            academic_score=core.academic_score,
            writing_growth=core.writing_growth,
            skills=skills_data,
            mentor_verifications=core.mentor_verifications,
            parent_support_level=core.parent_support_level,
            institutional_stamp=core.institutional_stamp,
            consistency_score=core.consistency_score,
            total_contributions=core.total_contributions,
            badge_issued=core.badge_issued,
            last_updated=core.last_updated.isoformat(),
        )
        narrative = core.narrative_cache
    else:
        core_resp = ETESTERCoreResponse(
            student_id=student_id,
            academic_score=None,
            writing_growth=None,
            skills=None,
            mentor_verifications=0,
            parent_support_level=None,
            institutional_stamp=None,
            consistency_score=None,
            total_contributions=0,
            badge_issued=None,
            last_updated="",
        )
        narrative = None

    milestone_responses = [
        MilestoneResponse(
            id=m.id,
            student_id=m.student_id,
            milestone_id=m.milestone_id,
            type=m.type,
            title=m.title,
            date=m.date.isoformat(),
            score=m.score,
            score_label=m.score_label,
            notes=m.notes,
            status=m.status,
            contributor_type=m.contributor_type,
            ai_summary=m.ai_summary,
            auth_score=m.auth_score,
            created_at=m.date.isoformat(),
        )
        for m in milestones
    ]

    return ETESTERProfileResponse(
        core=core_resp,
        recent_milestones=milestone_responses,
        narrative=narrative,
    )


# ── Contribute ────────────────────────────────────────────────────────────────

@router.post(
    "/contribute",
    response_model=MilestoneResponse,
    status_code=201,
    summary="Submit a milestone contribution",
)
async def contribute(
    body: ContributionRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> MilestoneResponse:
    """
    Submit a new milestone (achievement / activity) for a student.

    This endpoint:
      1. Validates the contribution payload.
      2. Generates an AI summary.
      3. Persists the milestone.
      4. Returns the created record.

    The ETESTERCore is NOT rebuilt here – call POST /rebuild-core/{student_id}
    after a batch of contributions.
    """
    return await contribute_service(payload=body, db=db)


# ── Rebuild Core ─────────────────────────────────────────────────────────────

@router.post(
    "/rebuild-core/{student_id}",
    response_model=ETESTERCoreResponse,
    summary="Rebuild ETESTER core from all milestones",
)
async def rebuild_core(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> ETESTERCoreResponse:
    """
    Re-aggregate all milestones into the ETESTERCore scorecard.

    Call this after submitting contributions (e.g. in a background task or
    after the last contribution in a batch).
    """
    return await rebuild_core_service(student_id=student_id, db=db)


# ── Authenticity ─────────────────────────────────────────────────────────────

@router.post(
    "/ai/authenticity",
    response_model=AuthenticityResponse,
    summary="Score essay authenticity",
)
async def authenticity(
    body: AuthenticityRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> AuthenticityResponse:
    """
    Score an essay's authenticity using OpenAI.

    Returns a score (0–1), reasons, flags, and improvement suggestions.
    """
    return await score_authenticity_service(
        essay=body.essay,
        student_id=body.student_id,
        rubric_context=body.rubric_context,
        db=db,
    )


# ── Badge ────────────────────────────────────────────────────────────────────

@router.get(
    "/badge/{student_id}",
    response_model=BadgeResponse,
    summary="Get student badge",
)
async def get_badge(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> BadgeResponse:
    """
    Return the current badge for a student, upgrading if thresholds are met.

    Badges: bronze → silver → gold → platinum.
    Awarded based on total_contributions and consistency_score.
    """
    return await badge_service(student_id=student_id, db=db)
