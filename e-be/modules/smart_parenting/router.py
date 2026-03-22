"""
modules/smart_parenting/router.py
─────────────────────────────────
FastAPI router for Smart Parenting endpoints.
All routes are prefixed with /api and require Bearer authentication.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from modules.smart_parenting.repository import (
    get_behavioral_logs,
    get_student,
)
from modules.smart_parenting.schemas import (
    BehavioralLogListResponse,
    BehavioralLogResponse,
    DigestResponse,
    ParentHomeResponse,
    ParentMeResponse,
    StudentProfile,
    UpsellResponse,
    WellbeingRequest,
    WellbeingResponse,
)
from modules.smart_parenting.services.digest import digest_service
from modules.smart_parenting.services.upsell import upsell_service
from modules.smart_parenting.services.wellbeing import (
    compute_metrics,
    wellbeing_check_service_from_logs,
)
from modules.smart_parenting.services.agent_tools.tools import resolve_parent_id
from shared.deps import get_current_user
from shared.model import Parent, User

router = APIRouter(prefix="/api", tags=["smart_parenting"])


# ── Parent profile ──────────────────────────────────────────────────────────

@router.get(
    "/parents/me",
    response_model=ParentMeResponse,
    summary="Get current parent profile",
)
async def get_parent_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ParentMeResponse:
    """Resolve and return the authenticated parent profile."""
    from fastapi import HTTPException
    from sqlalchemy import select

    parent_id = await resolve_parent_id(
        db=db,
        user_id=current_user.id,
        user_email=current_user.email,
    )
    if parent_id is None:
        raise HTTPException(status_code=403, detail="Parent account is not linked")

    result = await db.execute(select(Parent).where(Parent.parent_id == parent_id))
    parent = result.scalar_one_or_none()
    if parent is None:
        raise HTTPException(status_code=404, detail="Parent not found")

    return ParentMeResponse(
        parent_id=parent.parent_id,
        full_name=parent.full_name,
        email=current_user.email,
        phone=parent.phone,
        telegram_id=parent.telegram_id,
        student_id=parent.student_id,
    )


# ── Student profile ─────────────────────────────────────────────────────────

@router.get(
    "/students/{student_id}",
    response_model=StudentProfile,
    summary="Get student profile",
)
async def get_student_profile(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> StudentProfile:
    """
    Retrieve the public profile of a student by ID.

    Requires: authenticated parent or mentor linked to the student.
    """
    student = await get_student(student_id, db)
    if not student:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Student not found")

    return StudentProfile(
        student_id=student.student_id,
        name=student.name,
        ielts_score=student.ielts_score,
        sat_score=student.sat_score,
        gpa=student.gpa,
        months_enrolled=student.months_enrolled,
        program=student.program,
        skill_breakdown=student.skill_breakdown,
        target_schools=student.target_schools or [],
        parent_id=student.parent_id,
        mentor_id=student.mentor_id,
        progress_pct=student.progress_pct,
        milestones_done=student.milestones_done,
        next_deadline=student.next_deadline.isoformat() if student.next_deadline else None,
        next_deadline_label=student.next_deadline_label,
        days_left=student.days_left,
        priority_action=student.priority_action,
        weakest_skill=student.weakest_skill,
        created_at=student.created_at.isoformat(),
    )


# ── Behavioural log ─────────────────────────────────────────────────────────

@router.get(
    "/behavioral-log/{student_id}",
    response_model=BehavioralLogListResponse,
    summary="Get behavioural logs and computed metrics",
)
async def get_behavioural_log(
    student_id: str,
    days: Annotated[int, Query(ge=1, le=365, description="Number of days to look back")] = 30,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> BehavioralLogListResponse:
    """
    Return behavioural logs for a student over the specified period,
    together with computed BehaviouralMetrics.
    """
    student = await get_student(student_id, db)
    if not student:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Student not found")

    logs = await get_behavioral_logs(student_id, days=days, db=db)
    metrics = compute_metrics(logs)

    log_responses = [
        BehavioralLogResponse(
            id=log.id,
            student_id=log.student_id,
            date=log.date.isoformat(),
            duration_min=log.duration_min,
            session_start=log.session_start.isoformat() if log.session_start else None,
            studied=log.studied or False,
            is_late_night=log.is_late_night,
            streak_day=log.streak_day,
            score_delta=log.score_delta,
            mood_note=log.mood_note,
        )
        for log in logs
    ]

    return BehavioralLogListResponse(
        student_id=student_id,
        days=days,
        logs=log_responses,
        metrics=metrics,
    )


# ── AI: Wellbeing check ─────────────────────────────────────────────────────

@router.post(
    "/ai/wellbeing",
    response_model=WellbeingResponse,
    summary="AI wellbeing assessment",
)
async def wellbeing_check(
    body: WellbeingRequest,
    student_id: Annotated[str, Query(description="Target student ID")],
    days: Annotated[int, Query(ge=3, le=90)] = 14,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> WellbeingResponse:
    """
    Assess a student's wellbeing over the past `days` days.

    Returns an overall score (0–100), a severity level, per-metric alerts,
    and actionable parent recommendations.
    """
    logs = await get_behavioral_logs(student_id, days=days, db=db)
    return await wellbeing_check_service_from_logs(student_id=student_id, logs=logs)


# ── Digest ───────────────────────────────────────────────────────────────────

@router.get(
    "/digest/{student_id}",
    response_model=DigestResponse,
    summary="Weekly parent digest",
)
async def get_digest(
    student_id: str,
    days: Annotated[int, Query(ge=1, le=30)] = 7,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> DigestResponse:
    """
    Generate a weekly parent newsletter for the student.

    Includes: week summary, highlights, parent tips, and next-week goals.
    """
    return await digest_service(student_id=student_id, days=days, db=db)


# ── Upsell ───────────────────────────────────────────────────────────────────

@router.get(
    "/upsell/{student_id}",
    response_model=UpsellResponse,
    summary="Personalised programme upsell",
)
async def get_upsell(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> UpsellResponse:
    """
    Generate personalised programme recommendations (upsell) for a student
    based on their current profile and progress.
    """
    return await upsell_service(student_id=student_id, db=db)


@router.get(
    "/parent-home/{student_id}",
    response_model=ParentHomeResponse,
    summary="Aggregated parent home payload",
)
async def get_parent_home(
    student_id: str,
    days: Annotated[int, Query(ge=3, le=30)] = 14,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> ParentHomeResponse:
    """Return digest + wellbeing + upsell in one API for parent homepage."""
    student = await get_student(student_id, db)
    if not student:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Student not found")

    logs = await get_behavioral_logs(student_id, days=days, db=db)
    wellbeing = await wellbeing_check_service_from_logs(student_id=student_id, logs=logs)
    digest = await digest_service(student_id=student_id, days=min(days, 7), db=db)
    upsell = await upsell_service(student_id=student_id, db=db)

    profile = StudentProfile(
        student_id=student.student_id,
        name=student.name,
        ielts_score=student.ielts_score,
        sat_score=student.sat_score,
        gpa=student.gpa,
        months_enrolled=student.months_enrolled,
        program=student.program,
        skill_breakdown=student.skill_breakdown,
        target_schools=student.target_schools or [],
        parent_id=student.parent_id,
        mentor_id=student.mentor_id,
        progress_pct=student.progress_pct,
        milestones_done=student.milestones_done,
        next_deadline=student.next_deadline.isoformat() if student.next_deadline else None,
        next_deadline_label=student.next_deadline_label,
        days_left=student.days_left,
        priority_action=student.priority_action,
        weakest_skill=student.weakest_skill,
        created_at=student.created_at.isoformat(),
    )

    return ParentHomeResponse(
        student_id=student_id,
        profile=profile,
        wellbeing=wellbeing,
        digest=digest,
        upsell=upsell,
    )
