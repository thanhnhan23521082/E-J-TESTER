"""
modules/etester/repository.py
────────────────────────────
Async data-access functions for the ETESTER module.
"""

from datetime import datetime

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.model import Milestone, Student


async def get_student(student_id: str, db: AsyncSession) -> Student | None:
    """Fetch a student by primary key, or None."""
    result = await db.execute(select(Student).where(Student.student_id == student_id))
    return result.scalar_one_or_none()


async def save_milestone(
    db: AsyncSession,
    *,
    student_id: str,
    milestone_id: str,
    type: str,
    title: str,
    date: datetime,
    score: float | None = None,
    score_label: str | None = None,
    notes: str | None = None,
    contributor_type: str = "student",
    ai_summary: str | None = None,
    auth_score: float | None = None,
) -> Milestone:
    """
    Create and persist a new Milestone record.

    Args:
        db: Async session.
        student_id:  Target student.
        milestone_id: Unique ID within student scope.
        type:        MilestoneType value string.
        title:       Human-readable title.
        date:        Milestone date.
        score:       Optional numeric score.
        score_label: Optional label (e.g. "Band 7.0").
        notes:       Free-text notes / reflection.
        contributor_type: Who contributed this record.
        ai_summary:  Optional AI-generated summary.
        auth_score:  Optional AI authenticity score.

    Returns:
        The newly created Milestone row.
    """
    milestone = Milestone(
        student_id=student_id,
        milestone_id=milestone_id,
        type=type,
        title=title,
        date=date,
        score=score,
        score_label=score_label,
        notes=notes,
        contributor_type=contributor_type,
        ai_summary=ai_summary,
        auth_score=auth_score,
        status="pending",
    )
    db.add(milestone)
    await db.commit()
    await db.refresh(milestone)
    return milestone


async def get_all_milestones(
    student_id: str,
    db: AsyncSession,
    limit: int = 100,
) -> list[Milestone]:
    """
    Fetch all milestones for a student, newest first.

    Args:
        student_id: Target student.
        db: Async session.
        limit: Maximum rows to return.

    Returns:
        List of Milestone rows.
    """
    result = await db.execute(
        select(Milestone)
        .where(Milestone.student_id == student_id)
        .order_by(Milestone.date.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_etester_core(
    student_id: str,
    db: AsyncSession,
) -> Student | None:
    """Fetch a student with ETESTER aggregate fields, or None."""
    result = await db.execute(select(Student).where(Student.student_id == student_id))
    return result.scalar_one_or_none()


async def save_etester_core(
    db: AsyncSession,
    *,
    student_id: str,
    academic_score: float | None = None,
    writing_growth: float | None = None,
    skills: dict | None = None,
    mentor_verifications: int = 0,
    parent_support_level: float | None = None,
    institutional_stamp: str | None = None,
    consistency_score: float | None = None,
    total_contributions: int = 0,
    narrative_cache: str | None = None,
    badge_issued: str | None = None,
) -> Student:
    """Update the student's ETESTER aggregate fields and return the row."""
    student = await get_student(student_id, db)
    if student is None:
        raise ValueError(f"Student not found: {student_id}")

    student.ielts_score = academic_score
    student.skill_breakdown = skills
    student.progress_pct = total_contributions
    student.priority_action = badge_issued
    student.weakest_skill = institutional_stamp

    await db.commit()
    await db.refresh(student)
    return student


async def get_essay_history(
    student_id: str,
    db: AsyncSession,
    limit: int = 10,
) -> list[Milestone]:
    """
    Fetch the most recent essay-related milestones for a student.

    Args:
        student_id: Target student.
        db: Async session.
        limit: Maximum rows.

    Returns:
        List of Milestone rows where type in (essay_draft, essay_final).
    """
    result = await db.execute(
        select(Milestone)
        .where(
            and_(
                Milestone.student_id == student_id,
                Milestone.type.in_(["essay_draft", "essay_final"]),
            )
        )
        .order_by(Milestone.date.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_contribution_summary(
    student_id: str,
    db: AsyncSession,
) -> list[dict]:
    """
    Aggregate milestones by type: count, latest date, average score.

    Returns:
        List of dicts: [{type, count, latest_date, avg_score}, ...]
    """
    result = await db.execute(
        select(
            Milestone.type,
            func.count(Milestone.id).label("count"),
            func.max(Milestone.date).label("latest_date"),
            func.avg(Milestone.score).label("avg_score"),
        )
        .where(Milestone.student_id == student_id)
        .group_by(Milestone.type)
    )
    rows = result.all()
    return [
        {
            "type": r.type,
            "count": r.count,
            "latest_date": r.latest_date.isoformat() if r.latest_date else None,
            "avg_score": round(r.avg_score, 2) if r.avg_score else None,
        }
        for r in rows
    ]
