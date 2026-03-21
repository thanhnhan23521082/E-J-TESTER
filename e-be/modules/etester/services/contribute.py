"""
modules/etester/services/contribute.py
──────────────────────────────────────
Handles the "contribute an artifact" flow:
1. Save Milestone + ArtifactForm + MilestoneArtifact
2. AI-suggest trace links
3. Summarize milestone
4. Trigger core rebuild
"""

import hashlib
import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from modules.etester import repository as repo
from modules.etester.services.llm_service import suggest_trace_links, summarize_milestone
from modules.etester.services.rebuild_core import rebuild_core

logger = logging.getLogger(__name__)


async def contribute_artifact(
    db: AsyncSession,
    *,
    student_id: str,
    milestone_id: str,
    type: str,
    title: str,
    date: str,
    score: float | None = None,
    score_label: str | None = None,
    notes: str | None = None,
    contributor_type: str = "student",
    activity_type: str | None = None,
    form_data: dict | None = None,
    artifact_text: str | None = None,
    skills_practiced: list[str] | None = None,
    had_leadership_role: bool = False,
    leadership_role_title: str | None = None,
    leadership_team_size: int | None = None,
    leadership_outcome: str | None = None,
) -> dict:
    """Full contribute flow returning milestone + suggested links."""

    parsed_date = datetime.fromisoformat(date)

    ai_summary = await summarize_milestone(
        milestone_type=type,
        title=title,
        score=score,
        notes=notes,
        date=date,
    )

    milestone = await repo.save_milestone(
        db,
        student_id=student_id,
        milestone_id=milestone_id,
        type=type,
        title=title,
        date=parsed_date,
        score=score,
        score_label=score_label,
        notes=notes,
        contributor_type=contributor_type,
        ai_summary=ai_summary,
    )

    artifact_hash = None
    prev_artifact_hash = None
    if artifact_text:
        artifact_hash = hashlib.sha256(artifact_text.encode()).hexdigest()

    await repo.save_artifact(
        db,
        milestone_id=milestone.id,
        student_id=student_id,
        full_text_content=artifact_text,
        artifact_hash=artifact_hash,
        prev_artifact_hash=prev_artifact_hash,
    )

    if activity_type:
        await repo.save_artifact_form(
            db,
            milestone_id=milestone.id,
            student_id=student_id,
            activity_type=activity_type,
            form_data=form_data,
            skills_practiced=skills_practiced,
            had_leadership_role=had_leadership_role,
            leadership_role_title=leadership_role_title,
            leadership_team_size=leadership_team_size,
            leadership_outcome=leadership_outcome,
        )

    existing = await repo.get_all_milestones(student_id, db, limit=50)
    existing_dicts = [
        {
            "id": m.id,
            "type": m.type,
            "title": m.title,
            "date": m.date.isoformat() if m.date else "",
        }
        for m in existing
        if m.id != milestone.id
    ]

    suggested_links = []
    if existing_dicts:
        raw_suggestions = await suggest_trace_links(
            new_milestone_title=title,
            new_milestone_type=type,
            new_milestone_notes=notes,
            existing_milestones=existing_dicts,
        )

        for s in raw_suggestions:
            target_id = s.get("target_milestone_id")
            if target_id is None:
                continue
            try:
                link = await repo.save_trace_link(
                    db,
                    from_milestone_id=milestone.id,
                    to_milestone_id=int(target_id),
                    student_id=student_id,
                    relationship_type=s.get("relationship_type", "experience_source"),
                    evidence=s.get("evidence"),
                    confidence=float(s.get("confidence", 0.7)),
                    suggested_by_ai=True,
                )
                suggested_links.append({
                    "id": link.id,
                    "from_milestone_id": link.from_milestone_id,
                    "to_milestone_id": link.to_milestone_id,
                    "student_id": link.student_id,
                    "relationship_type": link.relationship_type,
                    "evidence": link.evidence,
                    "confidence": link.confidence,
                    "suggested_by_ai": link.suggested_by_ai,
                    "confirmed_by_mentor": link.confirmed_by_mentor,
                    "is_active": link.is_active,
                    "student_context_note": link.student_context_note,
                    "confirmed_at": None,
                    "created_at": link.created_at.isoformat() if link.created_at else "",
                })
            except Exception as exc:
                logger.warning("Failed to save trace link suggestion: %s", exc)

    await rebuild_core(student_id, db)

    return {
        "milestone": {
            "id": milestone.id,
            "student_id": milestone.student_id,
            "milestone_id": milestone.milestone_id,
            "type": milestone.type,
            "title": milestone.title,
            "date": milestone.date.isoformat() if milestone.date else "",
            "score": milestone.score,
            "score_label": milestone.score_label,
            "notes": milestone.notes,
            "status": milestone.status,
            "contributor_type": milestone.contributor_type,
            "ai_summary": milestone.ai_summary,
            "auth_score": milestone.auth_score,
            "mentor_approved": milestone.mentor_approved,
            "created_at": milestone.created_at.isoformat() if milestone.created_at else "",
        },
        "suggested_links": suggested_links,
    }
