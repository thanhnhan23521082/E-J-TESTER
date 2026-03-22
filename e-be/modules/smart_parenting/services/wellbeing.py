"""
modules/smart_parenting/services/wellbeing.py
───────────────────────────────────────────
Compute wellbeing metrics from BehaviouralLog records and
trigger alerts when thresholds are breached.
"""

import json
import logging

from pydantic import BaseModel, Field

from modules.smart_parenting.prompts.loader import get_prompt
from shared.constants import WELLBEING_THRESHOLDS
from shared.clients.llm_client import call_json
from shared.model import BehavioralLog
from modules.smart_parenting.schemas import BehavioralMetrics, WellbeingAlert, WellbeingResponse

logger = logging.getLogger(__name__)
WELLBEING_SYSTEM = get_prompt("wellbeing", "system")
WELLBEING_USER_TEMPLATE = get_prompt("wellbeing", "user_template")


class _WellbeingLLMAlert(BaseModel):
    type: str = Field(default="study_time")
    severity: str = Field(default="low")
    message: str = Field(default="")


class _WellbeingLLMResult(BaseModel):
    overall_score: float = Field(ge=0, le=100)
    severity: str = Field(default="low")
    parent_message: str = Field(default="")
    action_label: str = Field(default="")
    alerts: list[_WellbeingLLMAlert] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


def _format_logs(logs: list[BehavioralLog]) -> str:
    if not logs:
        return "(no data)"
    rows: list[str] = []
    for item in logs:
        date_val = item.date.isoformat() if hasattr(item.date, "isoformat") else str(item.date)
        rows.append(
            f"[{date_val}] duration_min={item.duration_min} studied={item.studied} "
            f"streak_day={item.streak_day} score_delta={item.score_delta} late_night={item.is_late_night}"
        )
    return "\n".join(rows)


def compute_metrics(logs: list[BehavioralLog]) -> BehavioralMetrics:
    """
    Compute behavioural metrics from a list of BehavioralLog entries.

    Args:
        logs: List of BehavioralLog rows (newest-first is conventional).

    Returns:
        BehavioralMetrics with all computed values.
    """
    if not logs:
        return BehavioralMetrics(
            avg_daily_study_min=0.0,
            total_sessions=0,
            current_streak=0,
            avg_score_delta=0.0,
            consistency_score=0.0,
            alert_level="none",
        )

    # Total study minutes / session count
    durations = [log.duration_min for log in logs if log.duration_min is not None]
    total_min = sum(durations)
    total_sessions = len([log for log in logs if log.studied])

    avg_daily_study_min = total_min / len(logs) if logs else 0.0

    # Current streak (newest log has the current streak value)
    current_streak = logs[0].streak_day if logs and logs[0].streak_day is not None else 0

    # Average score delta
    deltas = [log.score_delta for log in logs if log.score_delta is not None]
    avg_score_delta = sum(deltas) / len(deltas) if deltas else 0.0

    # Consistency score: fraction of days with studied=True out of total days
    studied_days = len([log for log in logs if log.studied])
    consistency_score = studied_days / len(logs) if logs else 0.0

    # Alert level (computed deterministically)
    alert_level = _compute_alert_level(
        avg_daily_study_min=avg_daily_study_min,
        total_sessions=total_sessions,
        current_streak=current_streak,
        avg_score_delta=avg_score_delta,
        consistency_score=consistency_score,
    )

    return BehavioralMetrics(
        avg_daily_study_min=round(avg_daily_study_min, 2),
        total_sessions=total_sessions,
        current_streak=current_streak,
        avg_score_delta=round(avg_score_delta, 4),
        consistency_score=round(consistency_score, 3),
        alert_level=alert_level,
    )


def _compute_alert_level(
    avg_daily_study_min: float,
    total_sessions: int,
    current_streak: int,
    avg_score_delta: float,
    consistency_score: float,
) -> str:
    """Deterministically compute alert level from raw metrics."""
    t = WELLBEING_THRESHOLDS

    score = 0  # Higher = more concerning

    if avg_daily_study_min < t["study_time"]["alert_below"]:
        score += 2
    elif avg_daily_study_min < t["study_time"]["min_daily_min"]:
        score += 1

    if current_streak < t["streak_day"]["alert_below"]:
        score += 2
    elif current_streak < t["streak_day"]["min_streak"]:
        score += 1

    if avg_score_delta < t["score_delta"]["negative_alert_below"]:
        score += 2
    elif avg_score_delta < 0:
        score += 1

    if consistency_score < t["consistency_score"]["alert_below"]:
        score += 2
    elif consistency_score < t["consistency_score"]["healthy_min"]:
        score += 1

    if score >= 5:
        return "high"
    elif score >= 3:
        return "medium"
    elif score >= 1:
        return "low"
    return "none"


def is_alert(metrics: BehavioralMetrics) -> bool:
    """Return True if any metric crosses an alert threshold."""
    return metrics.alert_level in ("low", "medium", "high")


def build_alerts(metrics: BehavioralMetrics) -> list[WellbeingAlert]:
    """
    Generate individual WellbeingAlert objects based on metric breaches.

    Args:
        metrics: Pre-computed BehaviouralMetrics.

    Returns:
        List of alerts (may be empty).
    """
    t = WELLBEING_THRESHOLDS
    alerts: list[WellbeingAlert] = []

    if metrics.avg_daily_study_min < t["study_time"]["alert_below"]:
        alerts.append(WellbeingAlert(
            type="study_time",
            severity="high",
            message=f"Thời gian học trung bình chỉ {metrics.avg_daily_study_min:.0f} phút/ngày, "
                    f"dưới ngưỡng {t['study_time']['alert_below']:.0f} phút.",
        ))
    elif metrics.avg_daily_study_min < t["study_time"]["min_daily_min"]:
        alerts.append(WellbeingAlert(
            type="study_time",
            severity="low",
            message=f"Thời gian học trung bình {metrics.avg_daily_study_min:.0f} phút/ngày. "
                    "Cố gắng đạt ít nhất 30 phút mỗi ngày.",
        ))

    if metrics.current_streak < t["streak_day"]["alert_below"]:
        alerts.append(WellbeingAlert(
            type="streak",
            severity="high",
            message=f"Streak chỉ còn {metrics.current_streak} ngày – hãy khuyến khích con học đều đặn.",
        ))

    if metrics.avg_score_delta < t["score_delta"]["negative_alert_below"]:
        alerts.append(WellbeingAlert(
            type="score_delta",
            severity="medium",
            message=f"Điểm số có xu hướng giảm (delta TB: {metrics.avg_score_delta:.2f}). "
                    "Cần xem lại phương pháp học.",
        ))

    if metrics.consistency_score < t["consistency_score"]["alert_below"]:
        alerts.append(WellbeingAlert(
            type="consistency",
            severity="medium",
            message=f"Chỉ {metrics.consistency_score*100:.0f}% ngày có học. "
                    "Hãy cùng con xây dựng thói quen học tập ổn định.",
        ))

    return alerts


def wellbeing_check_service(
    student_id: str,
    db,  # AsyncSession injected below
) -> WellbeingResponse:
    """
    High-level wellbeing check: compute metrics and build alerts.

    Note: this is a sync function that works with already-fetched logs.
    The async wrapper lives in the router.
    """
    # Metrics are computed from logs passed in by the router (logs already fetched)
    # This service function signature receives logs directly to keep it pure.
    raise NotImplementedError("Use wellbeing_check_service_from_logs instead")


async def wellbeing_check_service_from_logs(
    student_id: str,
    logs: list[BehavioralLog],
) -> WellbeingResponse:
    """
    Compute wellbeing response from a list of pre-fetched logs.

    Args:
        student_id: Target student ID.
        logs:        Pre-fetched BehaviouralLog rows.

    Returns:
        WellbeingResponse with metrics, alerts, and overall score.
    """
    metrics = compute_metrics(logs)
    deterministic_alerts = build_alerts(metrics)
    deterministic_recommendations = _build_recommendations(metrics, deterministic_alerts)

    try:
        prompt = WELLBEING_USER_TEMPLATE.format(
            student_name=student_id,
            student_id=student_id,
            behavioral_data=_format_logs(logs),
            thresholds=json.dumps(WELLBEING_THRESHOLDS, ensure_ascii=False, indent=2),
        )
        ai_result = await call_json(
            prompt=prompt,
            system_prompt=WELLBEING_SYSTEM,
            schema=_WellbeingLLMResult,
            max_tokens=800,
            temperature=0.2,
        )

        severity = str(ai_result.severity).lower()
        if severity not in {"none", "low", "medium", "high"}:
            severity = metrics.alert_level

        ai_alerts = [
            WellbeingAlert(
                type=item.type,
                severity=item.severity if item.severity in {"none", "low", "medium", "high"} else "low",
                message=item.message,
            )
            for item in ai_result.alerts
        ]
        friendly_message = ai_result.parent_message.strip()
        if friendly_message:
            ai_alerts = [
                WellbeingAlert(
                    type="parent_summary",
                    severity=severity,
                    message=friendly_message,
                ),
                *ai_alerts,
            ]

        recommendations = ai_result.recommendations or deterministic_recommendations
        if ai_result.action_label.strip():
            recommendations = [ai_result.action_label.strip(), *recommendations]

        return WellbeingResponse(
            student_id=student_id,
            overall_score=round(float(ai_result.overall_score), 1),
            severity=severity,
            alerts=ai_alerts or deterministic_alerts,
            recommendations=recommendations,
            metrics=metrics,
        )
    except Exception as exc:
        logger.warning("Wellbeing AI call failed, fallback to deterministic mode: %s", exc)

    severity_penalty = {"none": 0, "low": 15, "medium": 35, "high": 60}
    fallback_score = max(0.0, 100 - severity_penalty.get(metrics.alert_level, 0))
    return WellbeingResponse(
        student_id=student_id,
        overall_score=round(fallback_score, 1),
        severity=metrics.alert_level,
        alerts=deterministic_alerts,
        recommendations=deterministic_recommendations,
        metrics=metrics,
    )


def _build_recommendations(
    metrics: BehavioralMetrics,
    alerts: list[WellbeingAlert],
) -> list[str]:
    tips: list[str] = []

    if metrics.avg_daily_study_min < WELLBEING_THRESHOLDS["study_time"]["min_daily_min"]:
        tips.append("Cố gắng học ít nhất 30 phút mỗi ngày, chia nhỏ thành 2 buổi 15 phút.")
    if metrics.current_streak < 3:
        tips.append("Xây dựng streak bằng cách học cùng con mỗi ngày, dù chỉ 10–15 phút.")
    if metrics.consistency_score < 0.5:
        tips.append("Tạo lịch học cố định mỗi ngày để cải thiện sự nhất quán.")
    if metrics.avg_score_delta < 0:
        tips.append("Nói chuyện với mentor để điều chỉnh phương pháp học.")

    if not tips:
        tips.append("Tiếp tục duy trì thói quen học tập hiện tại – con đang làm rất tốt!")

    return tips
