"""
modules/etester/services/rebuild_core.py
────────────────────────────────────────
Recalculates and upserts the ETESTERCore row for a student.
Called after every contribution, trace link change, or mentor action.
"""

import logging
from collections import Counter

from sqlalchemy.ext.asyncio import AsyncSession

from modules.etester import repository as repo
from modules.etester.services.llm_service import build_narrative

logger = logging.getLogger(__name__)

WRITING_TYPES = {"essay_draft", "essay_final"}
SCORE_TYPES = {"ielts_mock", "sat_mock", "toefl_mock", "mock_test"}


async def rebuild_core(student_id: str, db: AsyncSession) -> dict:
    """
    Rebuild ETESTERCore from milestones + trace links.
    Steps:
      1. Count milestones, breakdown by contributor_type
      2. Compute academic_score from latest scored milestone
      3. Compute writing_growth from essay progression
      4. Collect skills from ArtifactForms (via JSONB)
      5. Count pending items
      6. Compute consistency_score
      7. Generate narrative (LLM)
      8. Upsert ETESTERCore
    """
    student = await repo.get_student(student_id, db)
    if student is None:
        logger.error("rebuild_core: Student %s not found", student_id)
        return {}

    milestones = await repo.get_all_milestones(student_id, db, limit=200)
    total_contributions = len(milestones)

    contributor_counts: Counter = Counter()
    for m in milestones:
        contributor_counts[m.contributor_type or "student"] += 1
    contributor_breakdown = dict(contributor_counts)

    academic_score = None
    for m in milestones:
        if m.type in SCORE_TYPES and m.score is not None:
            academic_score = float(m.score)
            break

    essays = [m for m in milestones if m.type in WRITING_TYPES and m.score is not None]
    writing_growth = None
    if len(essays) >= 2:
        oldest = essays[-1].score
        newest = essays[0].score
        if oldest and newest:
            writing_growth = round(newest - oldest, 2)

    trace_links = await repo.get_trace_links_for_student(student_id, db)
    confirmed_count = sum(1 for tl in trace_links if tl.confirmed_by_mentor)

    skills_set: set[str] = set()
    for m in milestones:
        if hasattr(m, "form") and m.form and m.form.skills_practiced:
            for s in m.form.skills_practiced:
                skills_set.add(s)

    pending_trace_links = await repo.count_pending_trace_links(student_id, db)
    pending_approvals = await repo.count_pending_approvals(student_id, db)

    consistency_score = _compute_consistency(milestones, trace_links)

    milestones_text = "\n".join(
        f"  - {m.title} ({m.type}) — {m.date.isoformat() if m.date else 'N/A'} — score: {m.score}"
        for m in milestones[:20]
    )

    core_text = (
        f"Total contributions: {total_contributions}\n"
        f"Academic score: {academic_score}\n"
        f"Writing growth: {writing_growth}\n"
        f"Mentor verifications: {confirmed_count}\n"
        f"Skills: {', '.join(sorted(skills_set))}\n"
        f"Consistency score: {consistency_score}"
    )

    narratives = await build_narrative(
        student_name=student.name or student_id,
        milestones_text=milestones_text,
        core_text=core_text,
    )

    core = await repo.upsert_etester_core(
        db,
        student_id=student_id,
        academic_score=academic_score,
        writing_growth=writing_growth,
        skills=sorted(skills_set),
        mentor_verifications=confirmed_count,
        total_contributions=total_contributions,
        contributor_breakdown=contributor_breakdown,
        pending_trace_links=pending_trace_links,
        pending_approvals=pending_approvals,
        consistency_score=consistency_score,
        narrative_en=narratives.get("narrative_en"),
        narrative_vn=narratives.get("narrative_vn"),
    )

    return {
        "student_id": core.student_id,
        "total_contributions": core.total_contributions,
        "academic_score": float(core.academic_score) if core.academic_score else None,
        "writing_growth": float(core.writing_growth) if core.writing_growth else None,
        "consistency_score": core.consistency_score,
        "badge_issued": core.badge_issued,
    }


def _compute_consistency(milestones: list, trace_links: list) -> int:
    """
    Simple consistency heuristic:
    - +10 per milestone (max 40)
    - +10 per confirmed trace link (max 30)
    - +15 if at least 3 different milestone types
    - +15 if contributions span at least 3 months
    """
    score = min(40, len(milestones) * 10)

    confirmed = sum(1 for tl in trace_links if tl.confirmed_by_mentor)
    score += min(30, confirmed * 10)

    types_used = {m.type for m in milestones}
    if len(types_used) >= 3:
        score += 15

    dates = [m.date for m in milestones if m.date]
    if dates:
        span_days = (max(dates) - min(dates)).days
        if span_days >= 90:
            score += 15

    return min(100, score)
