"""Compatibility wrappers for database tools used by parent chatbot."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from modules.smart_parenting.services.agent_tools.tools import (
    get_behavioral_logs,
    get_conversation_history,
    get_milestones,
    get_student_profile,
)


async def build_student_context(
    *,
    db: AsyncSession,
    student_id: str,
    parent_id: int,
    days: int = 14,
    history_limit: int = 5,
    milestones_limit: int = 5,
) -> dict:
    """Build a compact context object from the canonical tool implementations."""
    return {
        "student": await get_student_profile(db=db, student_id=student_id),
        "behavioral": await get_behavioral_logs(db=db, student_id=student_id, days=days),
        "milestones": await get_milestones(
            db=db,
            student_id=student_id,
            limit=milestones_limit,
        ),
        "conversation": await get_conversation_history(
            db=db,
            parent_id=parent_id,
            student_id=student_id,
            limit=history_limit,
        ),
    }
