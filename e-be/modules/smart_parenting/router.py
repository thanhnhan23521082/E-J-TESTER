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
    get_children_of_parent,
    get_parent,
    get_student,
    get_student_milestones,
    save_parent_message,
)
from modules.smart_parenting.schemas import (
    AiSummary,
    BehavioralLogListResponse,
    BehavioralLogResponse,
    DigestDataFE,
    DigestResponse,
    MilestoneResponse,
    ParentMessageRequest,
    ParentMessageResponse,
    StudentProfile,
    StudentResponse,
    UpsellResponse,
    WellbeingAlertFE,
    WellbeingRequest,
    WellbeingResponse,
)
from modules.smart_parenting.services.digest import digest_service
from modules.smart_parenting.services.upsell import upsell_service
from modules.smart_parenting.services.wellbeing import (
    compute_metrics,
    wellbeing_check_service_from_logs,
)
from shared.deps import get_current_user
from shared.model import User

router = APIRouter(prefix="/api", tags=["smart_parenting"])


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
            studied=log.studied or False,
            streak_day=log.streak_day,
            score_delta=log.score_delta,
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


# ── FE-aligned endpoints (camelCase, matching e-fe/src/types/index.ts) ───

def _not_found(detail: str):
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail=detail)


def _parse_int(raw: str, name: str) -> int:
    try:
        return int(raw)
    except ValueError:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Invalid {name}: must be an integer")


# GET /api/students/{studentId}  (FE-aligned: camelCase, full fields)
@router.get(
    "/students/{student_id}",
    response_model=StudentResponse,
    summary="Get student profile (FE-aligned)",
)
async def get_student_fe(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> StudentResponse:
    s = await get_student(student_id, db)
    if not s:
        _not_found(f"Student {student_id} not found")
    return StudentResponse.from_orm(s)


# GET /api/students/{studentId}/milestones  (FE-aligned)
@router.get(
    "/students/{student_id}/milestones",
    response_model=list[MilestoneResponse],
    summary="Get student milestones (FE-aligned)",
)
async def get_milestones_fe(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[MilestoneResponse]:
    s = await get_student(student_id, db)
    if not s:
        _not_found(f"Student {student_id} not found")
    milestones = await get_student_milestones(student_id, db)
    return [MilestoneResponse.from_orm(m) for m in milestones]


# GET /api/students/{studentId}/wellbeing  (FE-aligned flat alert)
@router.get(
    "/students/{student_id}/wellbeing",
    response_model=WellbeingAlertFE,
    summary="Get wellbeing alert (FE-aligned flat)",
)
async def get_wellbeing_fe(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> WellbeingAlertFE:
    s = await get_student(student_id, db)
    if not s:
        _not_found(f"Student {student_id} not found")
    logs = await get_behavioral_logs(student_id, days=14, db=db)
    if not logs:
        return WellbeingAlertFE(
            alert=False,
            severity="low",
            message="No activity data.",
            action="Encourage daily practice.",
        )
    studied_days = sum(1 for log in logs if log.studied)
    avg_delta = sum(float(log.score_delta or 0) for log in logs) / len(logs)
    streak = max((log.streak_day for log in logs), default=0)
    if avg_delta < -1.0 or streak < 2:
        return WellbeingAlertFE(
            alert=True, severity="high",
            message=f"Decline: avg score delta {avg_delta:.1f}, streak {streak} days.",
            action="Schedule a mentor check-in.",
        )
    elif avg_delta < 0 or streak < 5:
        return WellbeingAlertFE(
            alert=True, severity="medium",
            message=f"Slight decline: streak {streak} days.",
            action="Monitor closely.",
        )
    elif studied_days / len(logs) < 0.5:
        return WellbeingAlertFE(
            alert=True, severity="medium",
            message=f"Only {studied_days}/{len(logs)} days with study activity.",
            action="Encourage 5-6 study days/week.",
        )
    return WellbeingAlertFE(
        alert=False, severity="low",
        message="Study activity is healthy.",
        action="Keep up the great work!",
    )


# GET /api/students/{studentId}/digest  (FE-aligned flat digest)
@router.get(
    "/students/{student_id}/digest",
    response_model=DigestDataFE,
    summary="Get digest (FE-aligned flat)",
)
async def get_digest_fe(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> DigestDataFE:
    s = await get_student(student_id, db)
    if not s:
        _not_found(f"Student {student_id} not found")
    return DigestDataFE(
        progressPct=s.progress_pct or 0,
        milestonesCompleted=s.milestones_done or 0,
        nextDeadline=str(s.next_deadline) if s.next_deadline else "",
        daysLeft=s.days_left or 0,
        priorityAction=s.priority_action or "Keep up the great work!",
        weakestSkill=s.weakest_skill or "Writing",
    )


# GET /api/parents/{parentId}/children  (FE-aligned)
@router.get(
    "/parents/{parent_id}/children",
    response_model=list[StudentResponse],
    summary="Get parent's children (FE-aligned)",
)
async def get_children(
    parent_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[StudentResponse]:
    pid = _parse_int(parent_id, "parentId")
    parent = await get_parent(pid, db)
    if not parent:
        _not_found(f"Parent {parent_id} not found")
    children = await get_children_of_parent(pid, db)
    return [StudentResponse.from_orm(c) for c in children]


# POST /api/parents/{parentId}/messages
@router.post(
    "/parents/{parent_id}/messages",
    response_model=ParentMessageResponse,
    status_code=201,
    summary="Send message to mentor",
)
async def send_message(
    parent_id: str,
    body: ParentMessageRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> ParentMessageResponse:
    pid = _parse_int(parent_id, "parentId")
    parent = await get_parent(pid, db)
    if not parent:
        _not_found(f"Parent {parent_id} not found")
    conv = await save_parent_message(
        db,
        parent_id=pid,
        mentor_id=int(body.mentorId),
        message=body.message,
    )
    return ParentMessageResponse(messageId=str(conv.id))
