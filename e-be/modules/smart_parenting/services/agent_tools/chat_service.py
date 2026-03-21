"""Compatibility chat service that proxies to LangGraph workflow."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from modules.smart_parenting.services.agent_tools.agent_graph import run_parent_agent

settings = get_settings()


async def chat_with_parent(
    *,
    db: AsyncSession,
    parent_id: int,
    student_id: str,
    question: str,
) -> dict:
    """Backward-compatible wrapper for older imports."""
    result = await run_parent_agent(
        db=db,
        parent_id=parent_id,
        student_id=student_id,
        question=question,
    )
    return {
        "answer": result["answer"],
        "context": result.get("tool_outputs", {}),
        "used_model": settings.OPENAI_MODEL,
        "tools_used": result.get("tools_used", []),
        "escalated": result.get("escalated", False),
    }
