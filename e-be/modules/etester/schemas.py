"""
modules/etester/schemas.py
──────────────────────────
Pydantic request/response models for ETESTER endpoints.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ── Contribution / Milestone ─────────────────────────────────────────────────

class ContributionRequest(BaseModel):
    """Payload submitted by a contributor (student, mentor, parent) to log a milestone."""

    student_id: str = Field(..., description="Target student ID")
    milestone_id: str = Field(..., description="Unique milestone ID within the student scope")
    type: str = Field(..., description="MilestoneType value: ielts_mock | essay_draft | ...")
    title: str = Field(..., min_length=3, max_length=255, description="Human-readable milestone title")
    date: str = Field(..., description="ISO 8601 date string (YYYY-MM-DD)")
    score: float | None = Field(None, ge=0, description="Optional numeric score (e.g. IELTS band)")
    score_label: str | None = Field(None, max_length=100, description="Human-readable score label")
    notes: str | None = Field(None, max_length=2000, description="Free-text notes / reflection")
    contributor_type: str = Field(
        default="student",
        description="ContributorType: student | mentor | parent | institution",
    )

    model_config = {"json_schema_extra": {
        "example": {
            "student_id": "STU-001",
            "milestone_id": "MIL-2026-001",
            "type": "ielts_mock",
            "title": "IELTS Mock Test – March 2026",
            "date": "2026-03-15",
            "score": 7.0,
            "score_label": "Band 7.0",
            "notes": "Reading improved by 0.5 from last attempt.",
            "contributor_type": "student",
        }
    }}


class MilestoneResponse(BaseModel):
    """Created or updated milestone record."""

    id: int = Field(..., description="Database primary key")
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
    ai_summary: str | None = Field(None, description="AI-generated summary")
    auth_score: float | None = Field(None, description="AI authenticity score (0–1)")
    created_at: str

    model_config = {"from_attributes": True}


# ── ETESTER Core ─────────────────────────────────────────────────────────────

class ETESTERCoreResponse(BaseModel):
    """Aggregated ETESTER scorecard for a student."""

    student_id: str
    academic_score: float | None
    writing_growth: float | None
    skills: dict[str, float] | None = Field(
        default=None,
        description="Skill breakdown as dict (e.g. {'reading': 7.0, 'writing': 6.5})",
    )
    mentor_verifications: int
    parent_support_level: float | None
    institutional_stamp: str | None
    consistency_score: float | None
    total_contributions: int
    badge_issued: str | None
    last_updated: str

    model_config = {"from_attributes": True}


class ETESTERProfileResponse(BaseModel):
    """Full ETESTER profile: core + milestones + narrative."""

    core: ETESTERCoreResponse
    recent_milestones: list[MilestoneResponse]
    narrative: str | None = Field(None, description="AI-generated student narrative")

    model_config = {"from_attributes": True}


# ── Authenticity ─────────────────────────────────────────────────────────────

class AuthenticityRequest(BaseModel):
    """Payload for AI essay authenticity scoring."""

    student_id: str = Field(..., description="Student submitting the essay")
    essay: str = Field(..., min_length=100, max_length=10000, description="Essay text")
    rubric_context: str | None = Field(
        None,
        max_length=500,
        description="Optional rubric or assignment brief for context",
    )

    model_config = {"json_schema_extra": {
        "example": {
            "student_id": "STU-001",
            "essay": "In the rapidly evolving landscape of modern education...",
            "rubric_context": "Write a 500-word argumentative essay on the impact of technology on learning.",
        }
    }}


class AuthenticityResponse(BaseModel):
    """AI authenticity scoring result."""

    student_id: str
    score: float = Field(..., ge=0.0, le=1.0, description="Authenticity score (0–1)")
    reasons: list[str] = Field(default_factory=list, description="Scoring rationale")
    flags: list[str] = Field(default_factory=list, description="Red flags detected")
    suggestions: list[str] = Field(
        default_factory=list,
        description="Improvement suggestions",
    )
    scored_at: str  # ISO 8601

    model_config = {"json_schema_extra": {
        "example": {
            "student_id": "STU-001",
            "score": 0.85,
            "reasons": [
                "Voice is consistent and age-appropriate",
                "Structure is coherent with clear argument flow",
            ],
            "flags": [],
            "suggestions": [
                "Consider adding more specific personal examples in paragraph 2",
            ],
            "scored_at": "2026-03-21T10:30:00Z",
        }
    }}


# ── Badge ────────────────────────────────────────────────────────────────────

class BadgeResponse(BaseModel):
    """Issued or current badge for a student."""

    student_id: str
    badge: str | None = Field(None, description="Badge tier: bronze | silver | gold | platinum | null")
    tier_order: int | None = Field(None, ge=0, le=3, description="0=bronze, 3=platinum")
    total_contributions: int
    consistency_score: float | None
    unlocked_at: str | None = Field(None, description="ISO 8601 when badge was issued")
    message: str = Field(..., description="Motivational message for the student")

    model_config = {"json_schema_extra": {
        "example": {
            "student_id": "STU-001",
            "badge": "silver",
            "tier_order": 1,
            "total_contributions": 12,
            "consistency_score": 0.68,
            "unlocked_at": "2026-03-10T00:00:00Z",
            "message": "Chúc mừng con đã đạt huy hiệu Bạc! Hành trình của con thật truyền cảm hứng.",
        }
    }}


# ── Contribution summary ─────────────────────────────────────────────────────

class ContributionSummary(BaseModel):
    """Summary of contributions grouped by type."""

    type: str
    count: int
    latest_date: str | None
    avg_score: float | None


class ContributionsListResponse(BaseModel):
    """List of milestones with optional summary."""

    student_id: str
    total: int
    milestones: list[MilestoneResponse]
    summary_by_type: list[ContributionSummary] = Field(
        default_factory=list,
        description="Aggregated counts by milestone type",
    )
