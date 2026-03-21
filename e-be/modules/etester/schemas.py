"""
modules/etester/schemas.py
──────────────────────────
Pydantic request/response models for ETESTER v4 endpoints.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ── Contribution / Milestone ─────────────────────────────────────────────────

class ContributionRequest(BaseModel):
    student_id: str = Field(..., description="Target student ID")
    milestone_id: str = Field(..., description="Unique milestone ID within the student scope")
    type: str = Field(..., description="MilestoneType value")
    title: str = Field(..., min_length=3, max_length=255)
    date: str = Field(..., description="ISO 8601 date string")
    score: float | None = Field(None, ge=0)
    score_label: str | None = Field(None, max_length=100)
    notes: str | None = Field(None, max_length=2000)
    contributor_type: str = Field(default="student")

    activity_type: str | None = Field(None, description="ArtifactForm activity type")
    form_data: dict | None = Field(None, description="ArtifactForm structured data")
    artifact_text: str | None = Field(None, description="Full text content for artifact hash")
    skills_practiced: list[str] | None = Field(None)

    had_leadership_role: bool = Field(default=False)
    leadership_role_title: str | None = None
    leadership_team_size: int | None = None
    leadership_outcome: str | None = None

    model_config = {"json_schema_extra": {
        "example": {
            "student_id": "student_001",
            "milestone_id": "MIL-2026-001",
            "type": "essay_draft",
            "title": "Essay Draft #1",
            "date": "2025-10-01",
            "score": 65,
            "activity_type": "essay_draft",
            "form_data": {"draft_number": 1, "topic": "Personal Statement"},
            "skills_practiced": ["Academic Writing"],
        }
    }}


class MilestoneResponse(BaseModel):
    id: int
    student_id: str
    milestone_id: str
    type: str
    title: str
    date: str
    score: float | None
    score_label: str | None
    notes: str | None
    status: str
    contributor_type: str
    ai_summary: str | None = None
    auth_score: float | None = None
    mentor_approved: bool | None = None
    created_at: str

    model_config = {"from_attributes": True}


# ── Trace Link ───────────────────────────────────────────────────────────────

class TraceLinkResponse(BaseModel):
    id: int
    from_milestone_id: int
    to_milestone_id: int
    student_id: str
    relationship_type: str
    evidence: str | None
    confidence: float
    student_context_note: str | None
    suggested_by_ai: bool
    confirmed_by_mentor: bool
    confirmed_at: str | None
    is_active: bool
    created_at: str

    from_milestone_title: str | None = None
    from_milestone_type: str | None = None
    to_milestone_title: str | None = None
    to_milestone_type: str | None = None

    model_config = {"from_attributes": True}


class StudentNoteRequest(BaseModel):
    student_note: str = Field(..., min_length=1, max_length=2000)


class VerifyTraceRequest(BaseModel):
    mentor_id: int
    action: str = Field(..., description="confirm | reject | modify")
    new_relationship_type: str | None = None
    note: str | None = None


class ApproveArtifactRequest(BaseModel):
    mentor_id: int
    approved: bool
    note: str | None = None


# ── Contribution response with suggestions ───────────────────────────────────

class ContributeResponse(BaseModel):
    milestone: MilestoneResponse
    suggested_links: list[TraceLinkResponse] = Field(default_factory=list)


# ── Auth Scoring ─────────────────────────────────────────────────────────────

class AuthScoringResultResponse(BaseModel):
    id: int
    milestone_id: int
    student_id: str
    auth_score: int
    verdict: str
    dimension_scores: dict | None
    explaining_artifacts: list | None
    explanation_en: str | None
    explanation_vn: str | None
    scored_at: str

    model_config = {"from_attributes": True}


# ── ETESTER Core ─────────────────────────────────────────────────────────────

class ETESTERCoreResponse(BaseModel):
    student_id: str
    academic_score: float | None = None
    writing_growth: float | None = None
    skills: list | None = None
    mentor_verifications: int = 0
    total_contributions: int = 0
    contributor_breakdown: dict | None = None
    pending_trace_links: int = 0
    pending_approvals: int = 0
    requirements_coverage: dict | None = None
    parent_support_level: str = "low"
    consistency_score: int = 0
    narrative_en: str | None = None
    narrative_vn: str | None = None
    badge_issued: bool = False
    last_updated: str = ""

    model_config = {"from_attributes": True}


# ── Full Profile ─────────────────────────────────────────────────────────────

class ETESTERProfileResponse(BaseModel):
    core: ETESTERCoreResponse
    recent_milestones: list[MilestoneResponse] = Field(default_factory=list)
    trace_links: list[TraceLinkResponse] = Field(default_factory=list)
    auth_results: list[AuthScoringResultResponse] = Field(default_factory=list)
    narrative_en: str | None = None
    narrative_vn: str | None = None

    model_config = {"from_attributes": True}


# ── Mentor Pending ───────────────────────────────────────────────────────────

class MentorPendingResponse(BaseModel):
    pending_links: list[TraceLinkResponse] = Field(default_factory=list)
    pending_approvals: list[MilestoneResponse] = Field(default_factory=list)


# ── Badge ────────────────────────────────────────────────────────────────────

class IssueBadgeRequest(BaseModel):
    manager_id: int


class BadgeResponse(BaseModel):
    student_id: str
    badge_uid: str
    credential_type: str
    badge_payload: dict
    issued_at: str
    expires_at: str | None = None
    qr_url: str | None = None

    model_config = {"from_attributes": True}


class BadgeVerifyResponse(BaseModel):
    valid: bool
    badge_uid: str
    student_name: str | None = None
    program: str | None = None
    badge_payload: dict = Field(default_factory=dict)
    issued_at: str | None = None
    issuer: str = "ETEST Vietnam"
    is_revoked: bool = False


# ── Legacy compatibility ─────────────────────────────────────────────────────

class AuthenticityRequest(BaseModel):
    student_id: str
    essay: str = Field(..., min_length=100, max_length=10000)
    rubric_context: str | None = None


class AuthenticityResponse(BaseModel):
    student_id: str
    score: float = Field(..., ge=0.0, le=1.0)
    reasons: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    scored_at: str


class ContributionSummary(BaseModel):
    type: str
    count: int
    latest_date: str | None
    avg_score: float | None


class ContributionsListResponse(BaseModel):
    student_id: str
    total: int
    milestones: list[MilestoneResponse]
    summary_by_type: list[ContributionSummary] = Field(default_factory=list)
