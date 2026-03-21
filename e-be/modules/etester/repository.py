"""
modules/etester/repository.py
────────────────────────────
Async data-access functions for the ETESTER module v4.
All queries target ETESTER-specific tables (etester_core, milestone_trace_links, etc.)
and the shared milestones/students tables.
"""

from datetime import datetime

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared.etester_models import (
    ArtifactForm,
    AuthScoringResult,
    ETESTERBadge,
    ETESTERCore,
    MentorVerification,
    MilestoneArtifact,
    MilestoneTraceLink,
)
from shared.model import Milestone, Student


# ── Student ──────────────────────────────────────────────────────────────────

async def get_student(student_id: str, db: AsyncSession) -> Student | None:
    result = await db.execute(select(Student).where(Student.student_id == student_id))
    return result.scalar_one_or_none()


# ── Milestone ────────────────────────────────────────────────────────────────

async def save_milestone(
    db: AsyncSession,
    *,
    student_id: str,
    milestone_id: str,
    type: str,
    title: str,
    date: datetime,
    score: float | None = None,
    score_label: str | None = None,
    notes: str | None = None,
    contributor_type: str = "student",
    ai_summary: str | None = None,
    auth_score: float | None = None,
) -> Milestone:
    milestone = Milestone(
        student_id=student_id,
        milestone_id=milestone_id,
        type=type,
        title=title,
        date=date,
        score=score,
        score_label=score_label,
        notes=notes,
        contributor_type=contributor_type,
        ai_summary=ai_summary,
        auth_score=auth_score,
        status="pending",
    )
    db.add(milestone)
    await db.commit()
    await db.refresh(milestone)
    return milestone


async def get_all_milestones(
    student_id: str, db: AsyncSession, limit: int = 100
) -> list[Milestone]:
    result = await db.execute(
        select(Milestone)
        .where(Milestone.student_id == student_id)
        .order_by(Milestone.date.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_essay_history(
    student_id: str, db: AsyncSession, limit: int = 10
) -> list[Milestone]:
    result = await db.execute(
        select(Milestone)
        .where(
            and_(
                Milestone.student_id == student_id,
                Milestone.type.in_(["essay_draft", "essay_final"]),
            )
        )
        .order_by(Milestone.date.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_milestone_by_id(milestone_id: int, db: AsyncSession) -> Milestone | None:
    result = await db.execute(select(Milestone).where(Milestone.id == milestone_id))
    return result.scalar_one_or_none()


# ── ETESTERCore ──────────────────────────────────────────────────────────────

async def get_etester_core(student_id: str, db: AsyncSession) -> ETESTERCore | None:
    result = await db.execute(
        select(ETESTERCore).where(ETESTERCore.student_id == student_id)
    )
    return result.scalar_one_or_none()


async def upsert_etester_core(
    db: AsyncSession, student_id: str, **fields
) -> ETESTERCore:
    core = await get_etester_core(student_id, db)
    if core is None:
        core = ETESTERCore(student_id=student_id, **fields)
        db.add(core)
    else:
        for k, v in fields.items():
            if v is not None:
                setattr(core, k, v)
    await db.commit()
    await db.refresh(core)
    return core


# ── MilestoneTraceLink ───────────────────────────────────────────────────────

async def save_trace_link(
    db: AsyncSession,
    *,
    from_milestone_id: int,
    to_milestone_id: int,
    student_id: str,
    relationship_type: str,
    evidence: str | None = None,
    confidence: float = 0.0,
    suggested_by_ai: bool = True,
) -> MilestoneTraceLink:
    link = MilestoneTraceLink(
        from_milestone_id=from_milestone_id,
        to_milestone_id=to_milestone_id,
        student_id=student_id,
        relationship_type=relationship_type,
        evidence=evidence,
        confidence=confidence,
        suggested_by_ai=suggested_by_ai,
    )
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link


async def get_trace_links_for_student(
    student_id: str, db: AsyncSession, only_active: bool = True
) -> list[MilestoneTraceLink]:
    q = select(MilestoneTraceLink).where(MilestoneTraceLink.student_id == student_id)
    if only_active:
        q = q.where(MilestoneTraceLink.is_active == True)  # noqa: E712
    q = q.order_by(MilestoneTraceLink.created_at.desc())
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_pending_trace_links_for_mentor(
    mentor_id: int, db: AsyncSession
) -> list[MilestoneTraceLink]:
    """Get unconfirmed trace links for students of this mentor."""
    result = await db.execute(
        select(MilestoneTraceLink)
        .join(Student, MilestoneTraceLink.student_id == Student.student_id)
        .where(
            and_(
                Student.mentor_id == mentor_id,
                MilestoneTraceLink.confirmed_by_mentor == False,  # noqa: E712
                MilestoneTraceLink.is_active == True,  # noqa: E712
            )
        )
        .order_by(MilestoneTraceLink.created_at.desc())
    )
    return list(result.scalars().all())


async def get_trace_link_by_id(
    link_id: int, db: AsyncSession
) -> MilestoneTraceLink | None:
    result = await db.execute(
        select(MilestoneTraceLink).where(MilestoneTraceLink.id == link_id)
    )
    return result.scalar_one_or_none()


async def update_trace_link_student_note(
    link_id: int, note: str, db: AsyncSession
) -> MilestoneTraceLink | None:
    link = await get_trace_link_by_id(link_id, db)
    if link is None:
        return None
    link.student_context_note = note
    link.student_noted_at = datetime.utcnow()
    await db.commit()
    await db.refresh(link)
    return link


async def confirm_trace_link(
    link_id: int,
    mentor_id: int,
    db: AsyncSession,
    new_relationship_type: str | None = None,
) -> MilestoneTraceLink | None:
    link = await get_trace_link_by_id(link_id, db)
    if link is None:
        return None
    link.confirmed_by_mentor = True
    link.confirmed_by_mentor_id = mentor_id
    link.confirmed_at = datetime.utcnow()
    if new_relationship_type:
        link.relationship_type = new_relationship_type
    await db.commit()
    await db.refresh(link)
    return link


async def reject_trace_link(
    link_id: int, db: AsyncSession
) -> MilestoneTraceLink | None:
    link = await get_trace_link_by_id(link_id, db)
    if link is None:
        return None
    link.is_active = False
    await db.commit()
    await db.refresh(link)
    return link


# ── MilestoneArtifact ────────────────────────────────────────────────────────

async def save_artifact(
    db: AsyncSession,
    *,
    milestone_id: int,
    student_id: str,
    full_text_content: str | None = None,
    artifact_hash: str | None = None,
    prev_artifact_hash: str | None = None,
) -> MilestoneArtifact:
    artifact = MilestoneArtifact(
        milestone_id=milestone_id,
        student_id=student_id,
        full_text_content=full_text_content,
        artifact_hash=artifact_hash,
        prev_artifact_hash=prev_artifact_hash,
    )
    db.add(artifact)
    await db.commit()
    await db.refresh(artifact)
    return artifact


# ── ArtifactForm ─────────────────────────────────────────────────────────────

async def save_artifact_form(
    db: AsyncSession,
    *,
    milestone_id: int,
    student_id: str,
    activity_type: str,
    form_data: dict | None = None,
    skills_practiced: list | None = None,
    had_leadership_role: bool = False,
    leadership_role_title: str | None = None,
    leadership_team_size: int | None = None,
    leadership_outcome: str | None = None,
) -> ArtifactForm:
    form = ArtifactForm(
        milestone_id=milestone_id,
        student_id=student_id,
        activity_type=activity_type,
        form_data=form_data or {},
        skills_practiced=skills_practiced or [],
        had_leadership_role=had_leadership_role,
        leadership_role_title=leadership_role_title,
        leadership_team_size=leadership_team_size,
        leadership_outcome=leadership_outcome,
    )
    db.add(form)
    await db.commit()
    await db.refresh(form)
    return form


# ── MentorVerification ───────────────────────────────────────────────────────

async def save_mentor_verification(
    db: AsyncSession,
    *,
    milestone_id: int,
    student_id: str,
    verifier_id: int,
    verifier_type: str,
    action_type: str,
    note: str | None = None,
    trace_link_id: int | None = None,
) -> MentorVerification:
    verification = MentorVerification(
        milestone_id=milestone_id,
        student_id=student_id,
        verifier_id=verifier_id,
        verifier_type=verifier_type,
        action_type=action_type,
        note=note,
        trace_link_id=trace_link_id,
    )
    db.add(verification)
    await db.commit()
    await db.refresh(verification)
    return verification


# ── AuthScoringResult ────────────────────────────────────────────────────────

async def save_auth_result(
    db: AsyncSession,
    *,
    milestone_id: int,
    student_id: str,
    auth_score: int,
    verdict: str,
    dimension_scores: dict | None = None,
    explaining_artifacts: list | None = None,
    explanation_en: str | None = None,
    explanation_vn: str | None = None,
    graph_snapshot: dict | None = None,
) -> AuthScoringResult:
    result_obj = AuthScoringResult(
        milestone_id=milestone_id,
        student_id=student_id,
        auth_score=auth_score,
        verdict=verdict,
        dimension_scores=dimension_scores or {},
        explaining_artifacts=explaining_artifacts or [],
        explanation_en=explanation_en,
        explanation_vn=explanation_vn,
        graph_snapshot=graph_snapshot or {},
    )
    db.add(result_obj)
    await db.commit()
    await db.refresh(result_obj)
    return result_obj


async def get_auth_results_for_milestone(
    milestone_id: int, db: AsyncSession
) -> list[AuthScoringResult]:
    result = await db.execute(
        select(AuthScoringResult)
        .where(AuthScoringResult.milestone_id == milestone_id)
        .order_by(AuthScoringResult.scored_at.desc())
    )
    return list(result.scalars().all())


async def get_latest_auth_result(
    milestone_id: int, db: AsyncSession
) -> AuthScoringResult | None:
    result = await db.execute(
        select(AuthScoringResult)
        .where(AuthScoringResult.milestone_id == milestone_id)
        .order_by(AuthScoringResult.scored_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


# ── ETESTERBadge ─────────────────────────────────────────────────────────────

async def save_badge(
    db: AsyncSession,
    *,
    core_id: int,
    student_id: str,
    badge_uid: str,
    signed_token: str,
    badge_payload: dict,
    credential_type: str = "jwt_rs256",
    expires_at: datetime | None = None,
) -> ETESTERBadge:
    badge = ETESTERBadge(
        core_id=core_id,
        student_id=student_id,
        badge_uid=badge_uid,
        signed_token=signed_token,
        badge_payload=badge_payload,
        credential_type=credential_type,
        expires_at=expires_at,
    )
    db.add(badge)
    await db.commit()
    await db.refresh(badge)
    return badge


async def get_badge_by_uid(badge_uid: str, db: AsyncSession) -> ETESTERBadge | None:
    result = await db.execute(
        select(ETESTERBadge).where(ETESTERBadge.badge_uid == badge_uid)
    )
    return result.scalar_one_or_none()


async def get_badge_for_student(
    student_id: str, db: AsyncSession
) -> ETESTERBadge | None:
    result = await db.execute(
        select(ETESTERBadge)
        .where(
            and_(
                ETESTERBadge.student_id == student_id,
                ETESTERBadge.is_revoked == False,  # noqa: E712
            )
        )
        .order_by(ETESTERBadge.issued_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


# ── Aggregation helpers ──────────────────────────────────────────────────────

async def count_pending_trace_links(student_id: str, db: AsyncSession) -> int:
    result = await db.execute(
        select(func.count(MilestoneTraceLink.id)).where(
            and_(
                MilestoneTraceLink.student_id == student_id,
                MilestoneTraceLink.confirmed_by_mentor == False,  # noqa: E712
                MilestoneTraceLink.is_active == True,  # noqa: E712
            )
        )
    )
    return result.scalar_one() or 0


async def count_pending_approvals(student_id: str, db: AsyncSession) -> int:
    result = await db.execute(
        select(func.count(Milestone.id)).where(
            and_(
                Milestone.student_id == student_id,
                Milestone.mentor_approved.is_(None),
            )
        )
    )
    return result.scalar_one() or 0


async def get_pending_artifacts_for_mentor(
    mentor_id: int, db: AsyncSession
) -> list[Milestone]:
    result = await db.execute(
        select(Milestone)
        .join(Student, Milestone.student_id == Student.student_id)
        .where(
            and_(
                Student.mentor_id == mentor_id,
                Milestone.mentor_approved.is_(None),
            )
        )
        .order_by(Milestone.date.desc())
    )
    return list(result.scalars().all())


async def get_contribution_summary(
    student_id: str, db: AsyncSession
) -> list[dict]:
    result = await db.execute(
        select(
            Milestone.type,
            func.count(Milestone.id).label("count"),
            func.max(Milestone.date).label("latest_date"),
            func.avg(Milestone.score).label("avg_score"),
        )
        .where(Milestone.student_id == student_id)
        .group_by(Milestone.type)
    )
    rows = result.all()
    return [
        {
            "type": r.type,
            "count": r.count,
            "latest_date": r.latest_date.isoformat() if r.latest_date else None,
            "avg_score": round(r.avg_score, 2) if r.avg_score else None,
        }
        for r in rows
    ]
