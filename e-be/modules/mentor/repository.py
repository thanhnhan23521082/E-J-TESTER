"""
modules/mentor/repository.py
─────────────────────────────
Async SQLAlchemy repository for /api/mentors/ endpoints.
"""
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.model import Mentor, Milestone, Student


async def get_mentor(mentor_id: int, db: AsyncSession) -> Mentor | None:
    """Fetch a mentor by their integer primary key."""
    result = await db.execute(
        select(Mentor).where(Mentor.mentor_id == mentor_id)
    )
    return result.scalar_one_or_none()


async def get_mentor_students(mentor_id: int, db: AsyncSession) -> list[Student]:
    """Return all students assigned to this mentor."""
    result = await db.execute(
        select(Student).where(Student.mentor_id == mentor_id)
    )
    return list(result.scalars().all())


async def count_pending(
    mentor_id: int,
    db: AsyncSession,
    types: list[str],
) -> int:
    """Count milestones of given types that are in_progress for this mentor."""
    result = await db.execute(
        select(func.count(Milestone.id)).where(
            and_(
                Milestone.mentor_id == mentor_id,
                Milestone.status == "in_progress",
                Milestone.type.in_(types),
            )
        )
    )
    return result.scalar() or 0


async def get_pending_essays(mentor_id: int, db: AsyncSession) -> list[Milestone]:
    """Return essay milestones pending mentor review, newest first."""
    result = await db.execute(
        select(Milestone)
        .where(
            and_(
                Milestone.mentor_id == mentor_id,
                Milestone.status == "in_progress",
                Milestone.type.in_(["essay_draft", "essay_review"]),
            )
        )
        .order_by(Milestone.date.desc())
    )
    return list(result.scalars().all())


async def update_review(
    db: AsyncSession,
    milestone_id: str,
    mentor_id: int,
    *,
    score: float | None = None,
    feedback: str | None = None,
) -> Milestone | None:
    """
    Record a mentor's review on a milestone.
    Approves the milestone and marks it completed.
    """
    result = await db.execute(
        select(Milestone).where(
            and_(
                Milestone.milestone_id == milestone_id,
                Milestone.mentor_id == mentor_id,
            )
        )
    )
    m = result.scalar_one_or_none()
    if not m:
        return None
    if score is not None:
        m.score = score
    if feedback is not None:
        m.notes = feedback
    m.mentor_approved = True
    if m.status == "in_progress":
        m.status = "completed"
    await db.commit()
    await db.refresh(m)
    return m
