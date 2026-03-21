"""
modules/smart_parenting/services/upsell.py
───────────────────────────────────────────
Generate personalised program upsell recommendations for a student.
Uses the student's profile to identify next logical programme upgrades.
"""

import json
import logging
from dataclasses import dataclass

from modules.smart_parenting.prompts import UPSELL_SYSTEM, UPSELL_USER_TEMPLATE
from modules.smart_parenting.repository import get_student
from modules.smart_parenting.schemas import UpsellItem, UpsellResponse
from shared.clients.llm_client import call_json
from shared.clients.rag_client import get_rag_client
from shared.constants import ContributorType

logger = logging.getLogger(__name__)


# ── Programme catalogue (static, in-memory) ───────────────────────────────────
@dataclass(frozen=True)
class ProgrammeEntry:
    code: str
    name: str
    price: str | None
    target_ielts: str | None
    prerequisite: str | None
    keywords: tuple[str, ...]


PROGRAMME_CATALOGUE: list[ProgrammeEntry] = [
    ProgrammeEntry("IELTS-FND-01", "IELTS Foundation", "VND 5,000,000", "5.0–6.0", None,
                   ("ielts", "foundation", "starter", "beginner")),
    ProgrammeEntry("IELTS-ADV-01", "IELTS Advanced", "VND 8,000,000", "6.5–7.5", "IELTS Foundation",
                   ("ielts", "advanced", "nang cao", "7.0", "7.5")),
    ProgrammeEntry("SAT-PREP-01", "SAT Preparation", "VND 10,000,000", "1200–1400", None,
                   ("sat", "scholastic", "american", "college")),
    ProgrammeEntry("ESSAY-WRT-01", "Essay Writing Master", "VND 4,500,000", "writing 7.0+", "IELTS 6.0+",
                   ("essay", "writing", "viet", "sang tao")),
    ProgrammeEntry("CAMP-SUM-01", "Summer Bootcamp", "VND 12,000,000", "multi-skill", None,
                   ("camp", "bootcamp", "mua he", "intensive", "summer")),
    ProgrammeEntry("MENTOR-01-1", "1-on-1 Mentor", "VND 15,000,000/tháng", "personalised", None,
                   ("mentor", "ca nhan", "1-1", "private")),
    ProgrammeEntry("CSD-SKILL-01", "Computational Thinking", "VND 6,000,000", "problem solving", None,
                   ("csr", "computational", "stem", "coding", "ky nang")),
    ProgrammeEntry("CONSULT-01", "University Consultation", "VND 3,000,000", "target school", None,
                   ("consultation", "university", "chuyen", "truong dai hoc", "application")),
]


def _match_programmes(
    student_id: str,
    ielts_score: float | None,
    sat_score: float | None,
    gpa: float | None,
    months_enrolled: int | None,
    program: str | None,
) -> list[UpsellItem]:
    """
    Rule-based matching: score each catalogue programme against student profile.
    Returns programmes sorted by priority (high → low).
    """
    suggestions: list[tuple[int, UpsellItem]] = []  # (priority_score, item)

    enrolled = months_enrolled or 0

    for prog in PROGRAMME_CATALOGUE:
        score = 0

        # Penalise if already enrolled in this exact programme
        if program and prog.name.lower() in program.lower():
            continue

        # Prerequisite check (simplified)
        if prog.prerequisite and not (ielts_score and ielts_score >= 6.0):
            if "IELTS 6.0" in prog.prerequisite:
                continue  # skip programmes requiring IELTS 6.0

        # Score based on readiness signals
        if ielts_score:
            if prog.target_ielts and "6.0" in prog.target_ielts:
                score += 3
            if prog.target_ielts and ("7.0" in prog.target_ielts or "7.5" in prog.target_ielts):
                if ielts_score >= 6.0:
                    score += 5
        if sat_score:
            if "SAT" in prog.code:
                score += 4
        if enrolled >= 3:
            score += 2
        if enrolled >= 6:
            score += 3

        if score > 0:
            priority = "high" if score >= 7 else ("medium" if score >= 4 else "low")
            item = UpsellItem(
                program_name=prog.name,
                program_code=prog.code,
                priority=priority,
                pitch=_build_pitch(prog, ielts_score, sat_score),
                price_estimate=prog.price,
                expected_outcome=f"Mục tiêu đạt {prog.target_ielts or 'cải thiện kỹ năng'}",
            )
            suggestions.append((score, item))

    # Sort descending by score, then by priority enum order
    priority_order = {"high": 0, "medium": 1, "low": 2}
    suggestions.sort(key=lambda x: (priority_order.get(x[1].priority, 2), -x[0]))
    return [item for _, item in suggestions[:5]]  # top-5


def _build_pitch(prog: ProgrammeEntry, ielts: float | None, sat: float | None) -> str:
    """Build a 1–2 sentence personalised pitch for a programme."""
    name = prog.name
    target = prog.target_ielts or "kỹ năng mới"
    if ielts and ielts >= 6.0 and "IELTS" in prog.code:
        return f"{name} là bước tiếp theo hoàn hảo để đạt {target}."
    if sat and "SAT" in prog.code:
        return f"Với nền tảng hiện tại, {name} sẽ giúp con đạt {target}."
    if "Essay" in prog.name:
        return f"Khóa {name} giúp con viết bài luận xuất sắc, phù hợp với hồ sơ apply đại học."
    return f"{name} phù hợp để con phát triển {target}."


async def upsell_service(
    student_id: str,
    db=None,
) -> UpsellResponse:
    """
    Generate personalised programme upsell recommendations.

    Args:
        student_id: Target student.
        db:         Async SQLAlchemy session (injected by router).

    Returns:
        UpsellResponse with ranked programme recommendations.
    """
    student = await get_student(student_id, db)
    if not student:
        from core.exceptions import StudentNotFound
        raise StudentNotFound(message=f"Student '{student_id}' not found")

    # Rule-based matching (fast, deterministic)
    items = _match_programmes(
        student_id=student_id,
        ielts_score=student.ielts_score,
        sat_score=student.sat_score,
        gpa=student.gpa,
        months_enrolled=student.months_enrolled,
        program=student.program,
    )

    # Optionally enhance with LLM for a personalised pitch paragraph
    if items:
        try:
            rag = get_rag_client()
            student_info = (
                f"IELTS: {student.ielts_score}, SAT: {student.sat_score}, "
                f"GPA: {student.gpa}, program: {student.program}, "
                f"months_enrolled: {student.months_enrolled}"
            )
            prompt = UPSELL_USER_TEMPLATE.format(
                student_info=student_info,
                months_enrolled=student.months_enrolled,
                program=student.program or "chưa có",
            )
            enhanced = await call_text(
                prompt=prompt,
                system_prompt=UPSELL_SYSTEM,
                max_tokens=512,
                temperature=0.5,
            )
            # Inject LLM-enhanced pitch as the first item's extended pitch
            if items and enhanced:
                first = items[0]
                items[0] = UpsellItem(
                    program_name=first.program_name,
                    program_code=first.program_code,
                    priority=first.priority,
                    pitch=enhanced[:200],
                    price_estimate=first.price_estimate,
                    expected_outcome=first.expected_outcome,
                )
        except Exception as exc:
            logger.warning("Upsell LLM enhancement failed: %s – using rule-based only", exc)

    return UpsellResponse(
        student_id=student_id,
        student_name=student.name,
        current_program=student.program,
        recommendations=items,
    )
