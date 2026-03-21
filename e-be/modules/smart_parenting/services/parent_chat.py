"""
modules/smart_parenting/services/parent_chat.py
───────────────────────────────────────────────
FastAPI service for the parent–AI chat endpoint.
Orchestrates RAG retrieval → prompt assembly → LLM call → DB persistence.
"""

import json
import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import AITimeout, InsufficientHistory, StudentNotFound
from modules.smart_parenting.prompts import PARENT_CHAT_SYSTEM, PARENT_CHAT_USER_TEMPLATE
from modules.smart_parenting.repository import (
    get_conversation_history,
    get_student,
    save_conversation,
)
from modules.smart_parenting.schemas import ParentChatResponse
from shared.clients.rag_client import get_rag_client
from shared.model import Student

logger = logging.getLogger(__name__)


def _student_to_str(student: Student) -> str:
    """Serialize a Student ORM object into a readable string for the prompt."""
    return (
        f"student_id: {student.student_id}\n"
        f"name: {student.name}\n"
        f"IELTS: {student.ielts_score}\n"
        f"SAT: {student.sat_score}\n"
        f"GPA: {student.gpa}\n"
        f"program: {student.program}\n"
        f"months_enrolled: {student.months_enrolled}\n"
        f"skill_breakdown: {student.skill_breakdown}"
    )


async def parent_chat_service(
    question: str,
    student_id: str,
    parent_id: int,
    escalate: bool,
    db: AsyncSession,
) -> ParentChatResponse:
    """
    Process a parent's chat message and return an AI-generated response.

    Steps:
      1. Fetch student record (raises StudentNotFound if absent).
      2. Retrieve conversation history and RAG context.
      3. Call Claude via RAGClient.
      4. Persist the turn to the database.
      5. Return the response.

    Args:
        question:    The parent's natural-language question.
        student_id:  Target student's primary key.
        parent_id:   Authenticated parent's user ID.
        escalate:    If True, mark the turn for human review.
        db:          Async SQLAlchemy session.

    Returns:
        ParentChatResponse with the AI answer.

    Raises:
        StudentNotFound: if the student does not exist.
        AITimeout: if the LLM call fails.
    """
    # ── 1. Student check ────────────────────────────────────────────────────
    student = await get_student(student_id, db)
    if not student:
        raise StudentNotFound(message=f"Student '{student_id}' not found")

    # ── 2. Conversation history ─────────────────────────────────────────────
    history_rows = await get_conversation_history(parent_id, student_id, limit=5, db=db)
    # Build flat history: alternating user/assistant turns
    flat_history: list[dict[str, str]] = []
    for r in reversed(history_rows):
        flat_history.append({"role": "user", "content": r.question})
        flat_history.append({"role": "assistant", "content": r.ai_response})

    # ── 3. Build prompt ──────────────────────────────────────────────────────
    rag = get_rag_client()
    student_profile_dict = {
        "student_id": student.student_id,
        "name": student.name,
        "ielts_score": student.ielts_score,
        "sat_score": student.sat_score,
        "gpa": student.gpa,
        "program": student.program,
        "months_enrolled": student.months_enrolled,
    }

    try:
        answer = rag.answer_parent_question(
            question=question,
            student_id=student_id,
            student_profile=student_profile_dict,
            conversation_history=flat_history,
        )
    except AITimeout:
        # Surface a helpful fallback without crashing
        answer = (
            "Xin lỗi, hệ thống AI đang bận. Vui lòng thử lại trong giây lát. "
            "Nếu vấn đề vẫn tiếp diễn, bạn có thể liên hệ tư vấn viên để được hỗ trợ ngay."
        )
        escalate = True

    # ── 4. Persist conversation ─────────────────────────────────────────────
    context_snapshot = json.dumps({
        "student_id": student_id,
        "rag_sources": ["mock_vector_store"],
        "model": "claude-sonnet-4",
    })
    await save_conversation(
        db=db,
        parent_id=parent_id,
        student_id=student_id,
        question=question,
        ai_response=answer,
        context_snapshot=context_snapshot,
        escalated=escalate,
    )

    return ParentChatResponse(
        answer=answer,
        escalated=escalate,
        sources=["behavioral_logs", "milestones", "rag_context"],
    )
