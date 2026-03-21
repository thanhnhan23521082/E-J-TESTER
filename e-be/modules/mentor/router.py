"""
modules/mentor/router.py
────────────────────────
FastAPI router for /api/mentors/ endpoints.
All routes require Bearer authentication.
Prefix: /api/mentors
"""
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from modules.mentor.repository import (
    count_pending,
    get_mentor,
    get_mentor_students,
    get_pending_essays,
    update_review,
)
from modules.smart_parenting.schemas import (
    MilestoneResponse,
    StudentResponse,
)
from modules.mentor.schemas import (
    MentorResponse,
    MentorReviewRequest,
    MentorReviewResponse,
)
from shared.deps import get_current_user
from shared.model import User

router = APIRouter(prefix="/api/mentors", tags=["mentors"])


def _not_found(detail: str) -> HTTPException:
    raise HTTPException(status_code=404, detail=detail)


def _parse_int(raw: str, name: str) -> int:
    try:
        return int(raw)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid {name}: must be an integer")


# GET /api/mentors/{mentorId}
@router.get(
    "/{mentor_id}",
    response_model=MentorResponse,
    summary="Get mentor profile",
)
async def get_mentor_profile(
    mentor_id: str = Path(..., description="Mentor integer ID"),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> MentorResponse:
    mid = _parse_int(mentor_id, "mentorId")
    m = await get_mentor(mid, db)
    if not m:
        _not_found(f"Mentor {mentor_id} not found")
    pending_essays = await count_pending(mid, db, ["essay_draft", "essay_review"])
    pending_sessions = await count_pending(mid, db, ["session_notes"])
    return MentorResponse.from_orm(m, pending_essays, pending_sessions)


# GET /api/mentors/{mentorId}/students
@router.get(
    "/{mentor_id}/students",
    response_model=list[StudentResponse],
    summary="Get students assigned to mentor",
)
async def list_mentor_students(
    mentor_id: str = Path(...),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[StudentResponse]:
    mid = _parse_int(mentor_id, "mentorId")
    if not await get_mentor(mid, db):
        _not_found(f"Mentor {mentor_id} not found")
    students = await get_mentor_students(mid, db)
    return [StudentResponse.from_orm(s) for s in students]


# GET /api/mentors/{mentorId}/pending-essays
@router.get(
    "/{mentor_id}/pending-essays",
    response_model=list[MilestoneResponse],
    summary="Get essays pending mentor review",
)
async def list_pending_essays(
    mentor_id: str = Path(...),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[MilestoneResponse]:
    mid = _parse_int(mentor_id, "mentorId")
    if not await get_mentor(mid, db):
        _not_found(f"Mentor {mentor_id} not found")
    milestones = await get_pending_essays(mid, db)
    return [MilestoneResponse.from_orm(m) for m in milestones]


# POST /api/mentors/{mentorId}/reviews
@router.post(
    "/{mentor_id}/reviews",
    response_model=MentorReviewResponse,
    status_code=201,
    summary="Submit a mentor review",
)
async def submit_review(
    mentor_id: str = Path(...),
    body: MentorReviewRequest = ...,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> MentorReviewResponse:
    mid = _parse_int(mentor_id, "mentorId")
    if not await get_mentor(mid, db):
        _not_found(f"Mentor {mentor_id} not found")
    m = await update_review(db, body.milestoneId, mid, score=body.score, feedback=body.feedback)
    if not m:
        _not_found(
            f"Milestone {body.milestoneId} not found or not assigned to this mentor"
        )
    return MentorReviewResponse(success=True)
