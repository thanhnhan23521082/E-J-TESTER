"""
modules/smart_parenting/services/digest.py
───────────────────────────────────────────
Generate a weekly parent newsletter (digest) for a student.
Combines student profile, behavioural logs, and milestones into an AI-generated summary.
"""

import json
import logging
from datetime import datetime

from modules.smart_parenting.prompts import DIGEST_SYSTEM, DIGEST_USER_TEMPLATE
from modules.smart_parenting.repository import (
    get_behavioral_logs,
    get_student,
    get_student_milestones,
)
from modules.smart_parenting.schemas import DigestResponse
from shared.clients.llm_client import call_text
from shared.constants import WELLBEING_THRESHOLDS

logger = logging.getLogger(__name__)


def _format_logs(logs: list) -> str:
    """Format a list of BehavioralLog rows into a readable string."""
    lines = []
    for log in logs:
        date_str = log.date.strftime("%Y-%m-%d") if hasattr(log.date, "strftime") else str(log.date)
        lines.append(
            f"  [{date_str}] "
            f"duration={log.duration_min}min studied={log.studied} "
            f"streak={log.streak_day} score_delta={log.score_delta}"
        )
    return "\n".join(lines) if lines else "(no data)"


def _format_milestones(milestones: list) -> str:
    """Format a list of Milestone rows into a readable string."""
    lines = []
    for m in milestones:
        date_str = m.date.strftime("%Y-%m-%d") if hasattr(m.date, "strftime") else str(m.date)
        lines.append(
            f"  [{date_str}] {m.type}: {m.title} "
            f"(score={m.score}, status={m.status})"
        )
    return "\n".join(lines) if lines else "(no milestones)"


async def digest_service(
    student_id: str,
    days: int = 7,
    db=None,  # AsyncSession injected by caller
) -> DigestResponse:
    """
    Generate a weekly parent digest for a student.

    Args:
        student_id: Target student.
        days:       Number of days to summarise (default 7).
        db:         Async SQLAlchemy session (injected by router).

    Returns:
        DigestResponse with all digest sections.
    """
    # Fetch student
    student = await get_student(student_id, db)
    if not student:
        from core.exceptions import StudentNotFound
        raise StudentNotFound(message=f"Student '{student_id}' not found")

    student_name = student.name

    # Fetch logs and milestones
    logs = await get_behavioral_logs(student_id, days=days, db=db)
    milestones = await get_student_milestones(student_id, db=db, limit=10)

    student_info = (
        f"student_id: {student.student_id}\n"
        f"name: {student.name}\n"
        f"IELTS: {student.ielts_score} | SAT: {student.sat_score} | GPA: {student.gpa}\n"
        f"program: {student.program} | months_enrolled: {student.months_enrolled}"
    )

    logs_text = _format_logs(logs)
    milestones_text = _format_milestones(milestones)
    thresholds_str = json.dumps(WELLBEING_THRESHOLDS, indent=2)

    prompt = DIGEST_USER_TEMPLATE.format(
        student_info=student_info,
        behavioral_data=logs_text,
        milestones=milestones_text,
        days=days,
        thresholds=thresholds_str,
    )

    try:
        digest_text = await call_text(
            prompt=prompt,
            system_prompt=DIGEST_SYSTEM,
            max_tokens=1024,
            temperature=0.7,
        )
    except Exception as exc:
        logger.warning("Digest LLM call failed: %s – returning fallback", exc)
        digest_text = (
            f"{student_name} đã có một tuần học tập {'ổn định' if len(logs) >= 5 else 'cần cải thiện'}. "
            "Vui lòng liên hệ tư vấn viên để biết thêm chi tiết."
        )

    # Parse the free-text digest into structured sections
    sections = _parse_digest_sections(digest_text, student_name)

    return DigestResponse(
        student_id=student_id,
        student_name=student_name,
        week_summary=sections["summary"],
        highlights=sections["highlights"],
        parent_tips=sections["tips"],
        next_week_goals=sections["goals"],
        generated_at=datetime.utcnow().isoformat() + "Z",
    )


def _parse_digest_sections(
    digest_text: str,
    student_name: str,
) -> dict[str, list[str]]:
    """
    Heuristically split the free-text digest into structured sections.
    In production, use `call_json` with a structured schema instead.
    """
    lines = [l.strip() for l in digest_text.split("\n") if l.strip()]
    highlights: list[str] = []
    tips: list[str] = []
    goals: list[str] = []
    summary_parts: list[str] = []

    for line in lines:
        lower = line.lower()
        if any(k in lower for k in ["nổi bật", "highlight", "thành tích"]):
            highlights.append(line)
        elif any(k in lower for k in ["lưu ý", "mẹo", "tip", "phụ huynh"]):
            tips.append(line)
        elif any(k in lower for k in ["mục tiêu", "tuần tới", "goal"]):
            goals.append(line)
        elif line and not line.startswith("-"):
            summary_parts.append(line)

    # Fallback: if nothing was categorised, use the whole text as summary
    if not summary_parts:
        summary_parts = [digest_text[:300]]

    return {
        "summary": " ".join(summary_parts),
        "highlights": highlights or ["Tiếp tục cố gắng và duy trì thói quen tốt!"],
        "tips": tips or ["Hãy cùng con ôn tập mỗi ngày 15–30 phút."],
        "goals": goals or ["Duy trì streak học tập hàng ngày."],
    }
