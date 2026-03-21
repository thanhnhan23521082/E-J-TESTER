"""
modules/etester/services/badge.py
────────────────────────────────
Award and return badge information for a student based on
total contributions and consistency score.
"""

import logging
from datetime import datetime

from modules.etester.repository import get_etester_core, get_student, save_etester_core
from modules.etester.schemas import BadgeResponse
from shared.constants import BADGE_TIERS

logger = logging.getLogger(__name__)

BADGE_ORDER = ["bronze", "silver", "gold", "platinum"]
BADGE_MESSAGES = {
    "bronze": "Chúc mừng con đã bắt đầu hành trình ETESTER! Mỗi bước tiến đều quan trọng.",
    "silver": "Xuất sắc! Con đã đạt huy hiệu Bạc nhờ sự kiên trì và nỗ lực không ngừng.",
    "gold": "Tuyệt vời! Huy hiệu Vàng là minh chứng cho hành trình học tập đầy cảm hứng của con.",
    "platinum": "Xuất sắng xuất sắc! Huy hiệu Bạch Kim – con đã đạt đến đỉnh cao của sự kiên trì và xuất sắc.",
}


def _compute_badge(total_contributions: int, consistency_score: float | None) -> str | None:
    """
    Determine which badge (if any) a student qualifies for.

    Both thresholds must be met for a badge to be awarded.
    Returns the badge name or None.
    """
    if consistency_score is None:
        return None

    awarded: str | None = None
    for tier_name, thresholds in reversed(list(BADGE_TIERS.items())):
        if (
            total_contributions >= thresholds["min_contributions"]
            and consistency_score >= thresholds["min_consistency"]
        ):
            awarded = tier_name
            break

    return awarded


async def badge_service(
    student_id: str,
    db,
) -> BadgeResponse:
    """
    Determine and return the current badge for a student.

    If the computed badge is higher than the one already stored,
    it is upgraded and the new badge is returned.
    If no badge applies, returns null badge with a motivational message.

    Args:
        student_id: Target student.
        db:         Async SQLAlchemy session.

    Returns:
        BadgeResponse with current badge status and message.
    """
    # ── 1. Fetch student + core ─────────────────────────────────────────────
    student = await get_student(student_id, db)
    if not student:
        from core.exceptions import StudentNotFound
        raise StudentNotFound(message=f"Student '{student_id}' not found")

    core = await get_etester_core(student_id, db)

    if not core:
        return _no_badge_response(student_id, "Hãy bắt đầu hành trình ETESTER bằng cách đóng góp thành tích đầu tiên!")

    # ── 2. Compute badge ─────────────────────────────────────────────────────
    new_badge = _compute_badge(
        total_contributions=core.total_contributions,
        consistency_score=core.consistency_score,
    )

    # ── 3. Upgrade badge if higher ────────────────────────────────────────────
    current_badge = core.badge_issued
    upgraded = False

    if new_badge and new_badge != current_badge:
        badge_order = {b: i for i, b in enumerate(BADGE_ORDER)}
        if badge_order.get(new_badge, -1) > badge_order.get(current_badge or "", -1):
            core.badge_issued = new_badge
            core.last_updated = datetime.utcnow()
            await db.commit()
            await db.refresh(core)
            upgraded = True

    # ── 4. Build response ─────────────────────────────────────────────────────
    final_badge = core.badge_issued
    if final_badge and final_badge in BADGE_ORDER:
        tier_order = BADGE_ORDER.index(final_badge)
        message = BADGE_MESSAGES.get(final_badge, "Chúc mừng con đã đạt huy hiệu!")
        unlocked_at = core.last_updated.isoformat() if upgraded else None
    else:
        tier_order = None
        message = "Hãy cố gắng thêm nữa để nhận huy hiệu đầu tiên! Mỗi đóng góp đều quan trọng."

    return BadgeResponse(
        student_id=student_id,
        badge=final_badge,
        tier_order=tier_order,
        total_contributions=core.total_contributions,
        consistency_score=core.consistency_score,
        unlocked_at=unlocked_at,
        message=message,
    )


def _no_badge_response(student_id: str, message: str) -> BadgeResponse:
    return BadgeResponse(
        student_id=student_id,
        badge=None,
        tier_order=None,
        total_contributions=0,
        consistency_score=None,
        unlocked_at=None,
        message=message,
    )
