"""
modules/etester/router.py
────────────────────────
FastAPI router for ETESTER v4 endpoints.
All routes require Bearer authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from modules.etester import repository as repo
from modules.etester.schemas import (
    ApproveArtifactRequest,
    AuthenticityRequest,
    AuthenticityResponse,
    AuthScoringResultResponse,
    BadgeResponse,
    BadgeVerifyResponse,
    ContributeResponse,
    ContributionRequest,
    ContributionsListResponse,
    ContributionSummary,
    ETESTERCoreResponse,
    ETESTERProfileResponse,
    IssueBadgeRequest,
    MentorPendingResponse,
    MilestoneResponse,
    StudentNoteRequest,
    TraceLinkResponse,
    VerifyTraceRequest,
)
from modules.etester.services.auth_scoring import run_authenticity_check
from modules.etester.services.badge_service import issue_badge, verify_badge
from modules.etester.services.contribute import contribute_artifact
from modules.etester.services.rebuild_core import rebuild_core
from shared.deps import get_current_user
from shared.model import User

router = APIRouter(prefix="/api/etester", tags=["etester"])


# ═══════════════════════════════════════════════════════════════════════════════
# PROFILE
# ═══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/{student_id}",
    response_model=ETESTERProfileResponse,
    summary="Get full ETESTER profile",
)
async def get_etester_profile(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> ETESTERProfileResponse:
    student = await repo.get_student(student_id, db)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    core = await repo.get_etester_core(student_id, db)
    milestones = await repo.get_all_milestones(student_id, db, limit=20)
    trace_links = await repo.get_trace_links_for_student(student_id, db)

    if core:
        core_resp = ETESTERCoreResponse(
            student_id=core.student_id,
            academic_score=float(core.academic_score) if core.academic_score else None,
            writing_growth=float(core.writing_growth) if core.writing_growth else None,
            skills=core.skills,
            mentor_verifications=core.mentor_verifications,
            total_contributions=core.total_contributions,
            contributor_breakdown=core.contributor_breakdown,
            pending_trace_links=core.pending_trace_links,
            pending_approvals=core.pending_approvals,
            requirements_coverage=core.requirements_coverage,
            parent_support_level=core.parent_support_level,
            consistency_score=core.consistency_score,
            narrative_en=core.narrative_en,
            narrative_vn=core.narrative_vn,
            badge_issued=core.badge_issued,
            last_updated=core.updated_at.isoformat() if core.updated_at else "",
        )
    else:
        core_resp = ETESTERCoreResponse(student_id=student_id)

    milestone_responses = [
        MilestoneResponse(
            id=m.id,
            student_id=m.student_id,
            milestone_id=m.milestone_id,
            type=m.type,
            title=m.title,
            date=m.date.isoformat() if m.date else "",
            score=m.score,
            score_label=m.score_label,
            notes=m.notes,
            status=m.status,
            contributor_type=m.contributor_type,
            ai_summary=m.ai_summary,
            auth_score=m.auth_score,
            mentor_approved=m.mentor_approved,
            created_at=m.created_at.isoformat() if m.created_at else "",
        )
        for m in milestones
    ]

    tl_responses = _build_trace_link_responses(trace_links, milestones)

    return ETESTERProfileResponse(
        core=core_resp,
        recent_milestones=milestone_responses,
        trace_links=tl_responses,
        narrative_en=core.narrative_en if core else None,
        narrative_vn=core.narrative_vn if core else None,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CONTRIBUTE (Student)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/contribute",
    response_model=ContributeResponse,
    status_code=201,
    summary="Submit a milestone contribution",
)
async def contribute(
    body: ContributionRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> ContributeResponse:
    result = await contribute_artifact(
        db,
        student_id=body.student_id,
        milestone_id=body.milestone_id,
        type=body.type,
        title=body.title,
        date=body.date,
        score=body.score,
        score_label=body.score_label,
        notes=body.notes,
        contributor_type=body.contributor_type,
        activity_type=body.activity_type,
        form_data=body.form_data,
        artifact_text=body.artifact_text,
        skills_practiced=body.skills_practiced,
        had_leadership_role=body.had_leadership_role,
        leadership_role_title=body.leadership_role_title,
        leadership_team_size=body.leadership_team_size,
        leadership_outcome=body.leadership_outcome,
    )
    return ContributeResponse(**result)


# ═══════════════════════════════════════════════════════════════════════════════
# CONTRIBUTIONS LIST
# ═══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/contributions/{student_id}",
    response_model=ContributionsListResponse,
    summary="List all contributions for a student",
)
async def list_contributions(
    student_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> ContributionsListResponse:
    milestones = await repo.get_all_milestones(student_id, db, limit=limit)
    summary = await repo.get_contribution_summary(student_id, db)

    return ContributionsListResponse(
        student_id=student_id,
        total=len(milestones),
        milestones=[
            MilestoneResponse(
                id=m.id,
                student_id=m.student_id,
                milestone_id=m.milestone_id,
                type=m.type,
                title=m.title,
                date=m.date.isoformat() if m.date else "",
                score=m.score,
                score_label=m.score_label,
                notes=m.notes,
                status=m.status,
                contributor_type=m.contributor_type,
                ai_summary=m.ai_summary,
                auth_score=m.auth_score,
                mentor_approved=m.mentor_approved,
                created_at=m.created_at.isoformat() if m.created_at else "",
            )
            for m in milestones
        ],
        summary_by_type=[ContributionSummary(**s) for s in summary],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# REBUILD CORE
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/rebuild-core/{student_id}",
    response_model=ETESTERCoreResponse,
    summary="Rebuild ETESTER core from all milestones",
)
async def rebuild_core_endpoint(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> ETESTERCoreResponse:
    await rebuild_core(student_id, db)
    core = await repo.get_etester_core(student_id, db)
    if not core:
        raise HTTPException(status_code=404, detail="Core rebuild failed")
    return ETESTERCoreResponse(
        student_id=core.student_id,
        academic_score=float(core.academic_score) if core.academic_score else None,
        writing_growth=float(core.writing_growth) if core.writing_growth else None,
        skills=core.skills,
        mentor_verifications=core.mentor_verifications,
        total_contributions=core.total_contributions,
        contributor_breakdown=core.contributor_breakdown,
        pending_trace_links=core.pending_trace_links,
        pending_approvals=core.pending_approvals,
        requirements_coverage=core.requirements_coverage,
        parent_support_level=core.parent_support_level,
        consistency_score=core.consistency_score,
        narrative_en=core.narrative_en,
        narrative_vn=core.narrative_vn,
        badge_issued=core.badge_issued,
        last_updated=core.updated_at.isoformat() if core.updated_at else "",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TRACE LINKS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/trace-links/{student_id}",
    response_model=list[TraceLinkResponse],
    summary="Get trace links for a student",
)
async def get_trace_links(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[TraceLinkResponse]:
    links = await repo.get_trace_links_for_student(student_id, db)
    milestones = await repo.get_all_milestones(student_id, db, limit=200)
    return _build_trace_link_responses(links, milestones)


@router.put(
    "/trace-links/{link_id}/note",
    response_model=TraceLinkResponse,
    summary="Student adds context note to a trace link",
)
async def add_student_note(
    link_id: int,
    body: StudentNoteRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> TraceLinkResponse:
    link = await repo.update_trace_link_student_note(link_id, body.student_note, db)
    if not link:
        raise HTTPException(status_code=404, detail="Trace link not found")
    return TraceLinkResponse(
        id=link.id,
        from_milestone_id=link.from_milestone_id,
        to_milestone_id=link.to_milestone_id,
        student_id=link.student_id,
        relationship_type=link.relationship_type,
        evidence=link.evidence,
        confidence=link.confidence,
        student_context_note=link.student_context_note,
        suggested_by_ai=link.suggested_by_ai,
        confirmed_by_mentor=link.confirmed_by_mentor,
        confirmed_at=link.confirmed_at.isoformat() if link.confirmed_at else None,
        is_active=link.is_active,
        created_at=link.created_at.isoformat() if link.created_at else "",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MENTOR ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/mentor/{mentor_id}/pending",
    response_model=MentorPendingResponse,
    summary="Get pending reviews for a mentor",
)
async def get_mentor_pending(
    mentor_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> MentorPendingResponse:
    pending_links = await repo.get_pending_trace_links_for_mentor(mentor_id, db)
    pending_milestones = await repo.get_pending_artifacts_for_mentor(mentor_id, db)

    return MentorPendingResponse(
        pending_links=[
            TraceLinkResponse(
                id=tl.id,
                from_milestone_id=tl.from_milestone_id,
                to_milestone_id=tl.to_milestone_id,
                student_id=tl.student_id,
                relationship_type=tl.relationship_type,
                evidence=tl.evidence,
                confidence=tl.confidence,
                student_context_note=tl.student_context_note,
                suggested_by_ai=tl.suggested_by_ai,
                confirmed_by_mentor=tl.confirmed_by_mentor,
                confirmed_at=None,
                is_active=tl.is_active,
                created_at=tl.created_at.isoformat() if tl.created_at else "",
            )
            for tl in pending_links
        ],
        pending_approvals=[
            MilestoneResponse(
                id=m.id,
                student_id=m.student_id,
                milestone_id=m.milestone_id,
                type=m.type,
                title=m.title,
                date=m.date.isoformat() if m.date else "",
                score=m.score,
                score_label=m.score_label,
                notes=m.notes,
                status=m.status,
                contributor_type=m.contributor_type,
                ai_summary=m.ai_summary,
                auth_score=m.auth_score,
                mentor_approved=m.mentor_approved,
                created_at=m.created_at.isoformat() if m.created_at else "",
            )
            for m in pending_milestones
        ],
    )


@router.post(
    "/mentor/verify-trace/{link_id}",
    response_model=TraceLinkResponse,
    summary="Mentor confirms/rejects a trace link",
)
async def verify_trace(
    link_id: int,
    body: VerifyTraceRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> TraceLinkResponse:
    if body.action == "confirm":
        link = await repo.confirm_trace_link(
            link_id, body.mentor_id, db,
            new_relationship_type=body.new_relationship_type,
        )
    elif body.action == "reject":
        link = await repo.reject_trace_link(link_id, db)
    else:
        raise HTTPException(status_code=400, detail="action must be confirm|reject")

    if not link:
        raise HTTPException(status_code=404, detail="Trace link not found")

    if body.note:
        await repo.save_mentor_verification(
            db,
            milestone_id=link.from_milestone_id,
            student_id=link.student_id,
            verifier_id=body.mentor_id,
            verifier_type="mentor",
            action_type=f"trace_link_{body.action}",
            note=body.note,
            trace_link_id=link.id,
        )

    await rebuild_core(link.student_id, db)

    return TraceLinkResponse(
        id=link.id,
        from_milestone_id=link.from_milestone_id,
        to_milestone_id=link.to_milestone_id,
        student_id=link.student_id,
        relationship_type=link.relationship_type,
        evidence=link.evidence,
        confidence=link.confidence,
        student_context_note=link.student_context_note,
        suggested_by_ai=link.suggested_by_ai,
        confirmed_by_mentor=link.confirmed_by_mentor,
        confirmed_at=link.confirmed_at.isoformat() if link.confirmed_at else None,
        is_active=link.is_active,
        created_at=link.created_at.isoformat() if link.created_at else "",
    )


@router.post(
    "/mentor/approve-artifact/{milestone_id}",
    response_model=MilestoneResponse,
    summary="Mentor approves/rejects a milestone artifact",
)
async def approve_artifact(
    milestone_id: int,
    body: ApproveArtifactRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> MilestoneResponse:
    milestone = await repo.get_milestone_by_id(milestone_id, db)
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    milestone.mentor_approved = body.approved
    await db.commit()
    await db.refresh(milestone)

    await repo.save_mentor_verification(
        db,
        milestone_id=milestone.id,
        student_id=milestone.student_id,
        verifier_id=body.mentor_id,
        verifier_type="mentor",
        action_type="approve" if body.approved else "reject",
        note=body.note,
    )

    await rebuild_core(milestone.student_id, db)

    return MilestoneResponse(
        id=milestone.id,
        student_id=milestone.student_id,
        milestone_id=milestone.milestone_id,
        type=milestone.type,
        title=milestone.title,
        date=milestone.date.isoformat() if milestone.date else "",
        score=milestone.score,
        score_label=milestone.score_label,
        notes=milestone.notes,
        status=milestone.status,
        contributor_type=milestone.contributor_type,
        ai_summary=milestone.ai_summary,
        auth_score=milestone.auth_score,
        mentor_approved=milestone.mentor_approved,
        created_at=milestone.created_at.isoformat() if milestone.created_at else "",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# AUTHENTICITY SCORING
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/ai/authenticity",
    response_model=AuthScoringResultResponse,
    summary="7-dimension authenticity scoring",
)
async def authenticity(
    body: AuthenticityRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> AuthScoringResultResponse:
    milestones = await repo.get_all_milestones(body.student_id, db, limit=5)
    if not milestones:
        raise HTTPException(status_code=404, detail="No milestones found for scoring")

    result = await run_authenticity_check(
        student_id=body.student_id,
        milestone_id=milestones[0].id,
        essay_text=body.essay,
        db=db,
    )
    return AuthScoringResultResponse(**result)


@router.get(
    "/ai/auth-results/{milestone_id}",
    response_model=list[AuthScoringResultResponse],
    summary="Get auth scoring history for a milestone",
)
async def get_auth_results(
    milestone_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[AuthScoringResultResponse]:
    results = await repo.get_auth_results_for_milestone(milestone_id, db)
    return [
        AuthScoringResultResponse(
            id=r.id,
            milestone_id=r.milestone_id,
            student_id=r.student_id,
            auth_score=r.auth_score,
            verdict=r.verdict,
            dimension_scores=r.dimension_scores,
            explaining_artifacts=r.explaining_artifacts,
            explanation_en=r.explanation_en,
            explanation_vn=r.explanation_vn,
            scored_at=r.scored_at.isoformat(),
        )
        for r in results
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# BADGE (Manager)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/badge/issue/{student_id}",
    response_model=BadgeResponse,
    status_code=201,
    summary="Issue ETESTER badge for a student",
)
async def issue_badge_endpoint(
    student_id: str,
    body: IssueBadgeRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> BadgeResponse:
    core = await repo.get_etester_core(student_id, db)
    if not core:
        raise HTTPException(status_code=404, detail="ETESTERCore not found")
    if core.badge_issued:
        raise HTTPException(status_code=409, detail="Badge already issued")

    result = await issue_badge(student_id, body.manager_id, db)
    return BadgeResponse(**result)


@router.get(
    "/badge/{student_id}",
    response_model=BadgeResponse,
    summary="Get existing badge for a student",
)
async def get_badge(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> BadgeResponse:
    badge = await repo.get_badge_for_student(student_id, db)
    if not badge:
        raise HTTPException(status_code=404, detail="No badge found")
    return BadgeResponse(
        student_id=badge.student_id,
        badge_uid=badge.badge_uid,
        credential_type=badge.credential_type,
        badge_payload=badge.badge_payload,
        issued_at=badge.issued_at.isoformat(),
        expires_at=badge.expires_at.isoformat() if badge.expires_at else None,
    )


@router.get(
    "/badge/verify/{badge_uid}",
    response_model=BadgeVerifyResponse,
    summary="Verify a badge by UID (public endpoint)",
)
async def verify_badge_endpoint(
    badge_uid: str,
    db: AsyncSession = Depends(get_db),
) -> BadgeVerifyResponse:
    result = await verify_badge(badge_uid, db)
    return BadgeVerifyResponse(**result)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _build_trace_link_responses(
    links: list, milestones: list
) -> list[TraceLinkResponse]:
    milestone_map = {m.id: m for m in milestones}

    responses = []
    for tl in links:
        from_m = milestone_map.get(tl.from_milestone_id)
        to_m = milestone_map.get(tl.to_milestone_id)
        responses.append(
            TraceLinkResponse(
                id=tl.id,
                from_milestone_id=tl.from_milestone_id,
                to_milestone_id=tl.to_milestone_id,
                student_id=tl.student_id,
                relationship_type=tl.relationship_type,
                evidence=tl.evidence,
                confidence=tl.confidence,
                student_context_note=tl.student_context_note,
                suggested_by_ai=tl.suggested_by_ai,
                confirmed_by_mentor=tl.confirmed_by_mentor,
                confirmed_at=tl.confirmed_at.isoformat() if tl.confirmed_at else None,
                is_active=tl.is_active,
                created_at=tl.created_at.isoformat() if tl.created_at else "",
                from_milestone_title=from_m.title if from_m else None,
                from_milestone_type=from_m.type if from_m else None,
                to_milestone_title=to_m.title if to_m else None,
                to_milestone_type=to_m.type if to_m else None,
            )
        )
    return responses
