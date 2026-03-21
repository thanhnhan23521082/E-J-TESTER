"""
modules/smart_parenting/repository.py
──────────────────────────────────────
Async data-access functions for the Smart Parenting module.
All functions are pure DB queries – no AI logic here.
"""

from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.model import BehavioralLog, Conversation, Milestone, Student


async def get_student(student_id: str, db: AsyncSession) -> Student | None:
    """Fetch a student by primary key, or None if not found."""
    result = await db.execute(select(Student).where(Student.student_id == student_id))
    return result.scalar_one_or_none()


async def get_behavioral_logs(
    student_id: str,
    db: AsyncSession,
    days: int = 30,
) -> list[BehavioralLog]:
    """
    Fetch the most recent `days` days of behavioural logs for a student,
    ordered newest-first.

    Args:
        student_id: Target student.
        days: Number of days to look back (default 30).
        db: Async SQLAlchemy session.

    Returns:
        List of BehavioralLog rows, newest first.
    """
    since = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    since = since - datetime.timedelta(days=days)

    result = await db.execute(
        select(BehavioralLog)
        .where(
            and_(
                BehavioralLog.student_id == student_id,
                BehavioralLog.date >= since,
            )
        )
        .order_by(BehavioralLog.date.desc())
    )
    return list(result.scalars().all())


async def save_conversation(
    db: AsyncSession,
    *,
    parent_id: int,
    student_id: str,
    question: str,
    ai_response: str,
    context_snapshot: str | None = None,
    escalated: bool = False,
) -> Conversation:
    """
    Persist a parent–AI chat turn to the database.

    Args:
        db: Async session.
        parent_id: Authenticated parent's user ID.
        student_id: Target student.
        question: Raw question from the parent.
        ai_response: AI-generated response.
        context_snapshot: Optional JSON string of context used.
        escalated: Whether the turn was flagged for human review.

    Returns:
        The newly created Conversation row.
    """
    conv = Conversation(
        parent_id=parent_id,
        student_id=student_id,
        question=question,
        ai_response=ai_response,
        context_snapshot=context_snapshot,
        escalated=escalated,
    )
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return conv


async def get_student_milestones(
    student_id: str,
    db: AsyncSession,
    limit: int = 20,
) -> list[Milestone]:
    """
    Fetch the most recent `limit` milestones for a student.

    Args:
        student_id: Target student.
        db: Async session.
        limit: Maximum rows to return (default 20).

    Returns:
        List of Milestone rows, newest first.
    """
    result = await db.execute(
        select(Milestone)
        .where(Milestone.student_id == student_id)
        .order_by(Milestone.date.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_conversation_history(
    parent_id: int,
    student_id: str,
    db: AsyncSession,
    limit: int = 5,
) -> list[Conversation]:
    """
    Fetch the most recent `limit` conversation turns for a parent–student pair.

    Args:
        parent_id: Authenticated parent's user ID.
        student_id: Target student.
        limit: Maximum rows to return (default 5).
        db: Async session.

    Returns:
        List of Conversation rows, newest first.
    """
    result = await db.execute(
        select(Conversation)
        .where(
            and_(
                Conversation.parent_id == parent_id,
                Conversation.student_id == student_id,
            )
        )
        .order_by(Conversation.timestamp.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
