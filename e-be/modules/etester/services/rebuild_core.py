"""
modules/etester/services/rebuild_core.py
────────────────────────────────────────
Aggregate all milestones into an ETESTERCore scorecard.
Called after every new contribution to keep the core fresh.
"""

import json
import logging
from collections import defaultdict

from modules.etester.repository import (
    get_all_milestones,
    get_etester_core,
    save_etester_core,
)
from modules.etester.schemas import ETESTERCoreResponse
from shared.constants import MilestoneType
from shared.model import Milestone

logger = logging.getLogger(__name__)


def aggregate_core(milestones: list[Milestone]) -> dict:
    """
    Compute ETESTERCore fields from a list of milestone records.

    Args:
        milestones: All milestones for a student (newest-first is conventional).

    Returns:
        Dict of core fields suitable for save_etester_core().
    """
    if not milestones:
        return {
            "academic_score": None,
            "writing_growth": None,
            "skills": {},
            "mentor_verifications": 0,
            "parent_support_level": None,
            "institutional_stamp": None,
            "consistency_score": None,
            "total_contributions": 0,
        }

    total = len(milestones)

    # ── Academic score: weighted average of IELTS/SAT mocks ────────────────
    academic_scores: list[float] = []
    for m in milestones:
        if m.type == MilestoneType.IELTS_MOCK.value and m.score is not None:
            academic_scores.append(m.score * 10)  # IELTS band → 0–90 scale
        elif m.type == MilestoneType.SAT_MOCK.value and m.score is not None:
            academic_scores.append(m.score)  # SAT 0–1600

    academic_score = sum(academic_scores) / len(academic_scores) if academic_scores else None

    # ── Writing growth: compare earliest vs latest essay score ──────────────
    essay_scores: list[tuple] = []
    for m in milestones:
        if m.type in (MilestoneType.ESSAY_DRAFT.value, MilestoneType.ESSAY_FINAL.value):
            if m.score is not None:
                essay_scores.append((m.date, m.score))

    if len(essay_scores) >= 2:
        essay_scores.sort(key=lambda x: x[0])
        writing_growth = essay_scores[-1][1] - essay_scores[0][1]
    else:
        writing_growth = None

    # ── Skills: aggregate by type ─────────────────────────────────────────
    skills: dict[str, list[float]] = defaultdict(list)
    for m in milestones:
        if m.score is not None:
            skills[m.type].append(m.score)

    skills_avg = {k: round(sum(v) / len(v), 2) for k, v in skills.items()}

    # ── Mentor verifications ────────────────────────────────────────────────
    mentor_verifications = sum(
        1 for m in milestones
        if m.mentor_approved is True
    )

    # ── Parent support level: fraction of parent-contributed milestones ─────
    parent_count = sum(1 for m in milestones if m.contributor_type == "parent")
    parent_support_level = round(parent_count / total, 3) if total > 0 else None

    # ── Institutional stamp ────────────────────────────────────────────────
    institution_stamps = [
        m.institutional_stamp  # type: ignore[operator]
        for m in milestones
        if getattr(m, "institutional_stamp", None) and m.contributor_type == "institution"
    ]
    institutional_stamp = institution_stamps[-1] if institution_stamps else None

    # ── Consistency score: fraction of weeks with at least 1 milestone ─────
    from datetime import timedelta

    if milestones:
        dates = sorted(set(m.date.date() for m in milestones))
        if dates:
            span_days = (dates[-1] - dates[0]).days + 1
            weeks = max(1, span_days / 7)
            active_weeks = sum(1 for w in range(0, int(span_days), 7) if any(
                d >= dates[0] + timedelta(days=w) and d < dates[0] + timedelta(days=w + 7)
                for d in dates
            ))
            consistency_score = round(active_weeks / weeks, 3) if weeks > 0 else 0.0
        else:
            consistency_score = 0.0
    else:
        consistency_score = None

    return {
        "academic_score": round(academic_score, 2) if academic_score is not None else None,
        "writing_growth": round(writing_growth, 2) if writing_growth is not None else None,
        "skills": skills_avg,
        "mentor_verifications": mentor_verifications,
        "parent_support_level": parent_support_level,
        "institutional_stamp": institutional_stamp,
        "consistency_score": consistency_score,
        "total_contributions": total,
    }


async def rebuild_core_service(
    student_id: str,
    db,
) -> ETESTERCoreResponse:
    """
    Rebuild the ETESTERCore record for a student from all their milestones.

    Steps:
      1. Fetch all milestones for the student.
      2. Run `aggregate_core` to compute the new core values.
      3. Upsert the ETESTERCore record.
      4. Return the updated core.

    Args:
        student_id: Target student.
        db:         Async SQLAlchemy session.

    Returns:
        ETESTERCoreResponse with the fresh aggregated data.
    """
    # ── 1. Fetch all milestones ─────────────────────────────────────────────
    milestones = await get_all_milestones(student_id, db)

    # ── 2. Aggregate ────────────────────────────────────────────────────────
    aggregated = aggregate_core(milestones)

    # ── 3. Upsert ETESTERCore ───────────────────────────────────────────────
    core = await save_etester_core(
        db=db,
        student_id=student_id,
        **aggregated,
    )

    # ── 4. Return ───────────────────────────────────────────────────────────
    skills_data: dict | None = None
    if core.skills:
        try:
            skills_data = json.loads(core.skills)
        except json.JSONDecodeError:
            skills_data = None

    return ETESTERCoreResponse(
        student_id=core.student_id,
        academic_score=core.academic_score,
        writing_growth=core.writing_growth,
        skills=skills_data,
        mentor_verifications=core.mentor_verifications,
        parent_support_level=core.parent_support_level,
        institutional_stamp=core.institutional_stamp,
        consistency_score=core.consistency_score,
        total_contributions=core.total_contributions,
        badge_issued=core.badge_issued,
        last_updated=core.last_updated.isoformat(),
    )
