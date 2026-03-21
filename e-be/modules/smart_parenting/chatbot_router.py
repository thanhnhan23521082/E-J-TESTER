"""Dedicated router for Smart Parenting chatbot endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from modules.smart_parenting.services.agent_tools.agent_graph import run_parent_agent
from modules.smart_parenting.services.agent_tools.tools import resolve_parent_id
from shared.deps import get_current_user
from shared.model import User

router = APIRouter(prefix="/api/chatbot", tags=["smart_parenting_chatbot"])


class ParentAgentChatRequest(BaseModel):
    """Request payload for parent-agent chat."""

    student_id: str = Field(..., description="Target student ID")
    message: str = Field(..., min_length=3, max_length=2000, description="Parent message")


class ParentAgentChatResponse(BaseModel):
    """Response payload returned by parent-agent chat endpoint."""

    answer: str
    tools_used: list[str]
    escalated: bool
    tool_outputs: dict


@router.post("/parent", response_model=ParentAgentChatResponse, summary="Parent chatbot")
async def parent_agent_chat(
    body: ParentAgentChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ParentAgentChatResponse:
    """Chat endpoint for parents backed by DB context tools and llm_client provider."""
    parent_id = await resolve_parent_id(
        db=db,
        user_id=current_user.id,
        user_email=current_user.email,
    )
    if parent_id is None:
        raise HTTPException(status_code=403, detail="Parent account is not linked")

    result = await run_parent_agent(
        db=db,
        parent_id=parent_id,
        student_id=body.student_id,
        question=body.message,
    )

    return ParentAgentChatResponse(
        answer=result["answer"],
        tools_used=result["tools_used"],
        escalated=result["escalated"],
        tool_outputs=result["tool_outputs"],
    )
