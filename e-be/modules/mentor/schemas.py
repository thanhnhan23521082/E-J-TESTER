"""
modules/mentor/schemas.py
────────────────────────
Pydantic schemas for mentor endpoints.
"""
from pydantic import BaseModel


class MentorResponse(BaseModel):
    """Khớp Mentor interface ở e-fe/src/types/index.ts."""
    id: str
    name: str
    studentIds: list[str]
    pendingEssayCount: int
    pendingSessionNoteCount: int

    model_config = {"populate_by_name": True, "from_attributes": True}

    @classmethod
    def from_orm(m, pending_essays: int = 0, pending_sessions: int = 0):
        return MentorResponse(
            id=str(m.mentor_id),
            name=m.full_name,
            studentIds=[str(s.student_id) for s in m.students] if m.students else [],
            pendingEssayCount=pending_essays,
            pendingSessionNoteCount=pending_sessions,
        )


class MentorReviewRequest(BaseModel):
    """Payload for mentor review — khớp FE MentorApi.submitReview."""
    milestoneId: str
    score: float
    feedback: str
    strengths: list[str]
    improvements: list[str]


class MentorReviewResponse(BaseModel):
    """Response after mentor review — khớp FE expected shape."""
    success: bool
