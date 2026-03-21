"""
shared/etester_models.py
────────────────────────
ETESTER Module v4 — 7 new ORM models.
All FK references point to existing tables (students, milestones, mentors).
No existing table is altered.

Usage:
    from shared.etester_models import ETESTERCore, MilestoneTraceLink, ...
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base import Base
from shared.model import TimestampMixin


# ──────────────────────────────────────────────────────────────────────────────
# ETESTERCore — single source of truth per student (1:1)
# ──────────────────────────────────────────────────────────────────────────────

class ETESTERCore(Base, TimestampMixin):
    __tablename__ = "etester_core"
    __table_args__ = (
        Index("idx_etester_core_student", "student_id", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("students.student_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    academic_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    writing_growth: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    skills: Mapped[list | None] = mapped_column(JSONB, default=list)
    mentor_verifications: Mapped[int] = mapped_column(Integer, default=0)
    total_contributions: Mapped[int] = mapped_column(Integer, default=0)
    contributor_breakdown: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    pending_trace_links: Mapped[int] = mapped_column(Integer, default=0)
    pending_approvals: Mapped[int] = mapped_column(Integer, default=0)

    requirements_coverage: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    parent_support_level: Mapped[str] = mapped_column(String(20), default="low")
    parent_engagement_count: Mapped[int] = mapped_column(Integer, default=0)
    institutional_stamp: Mapped[bool] = mapped_column(Boolean, default=False)
    stamped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    stamped_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("mentors.mentor_id", ondelete="SET NULL"),
        nullable=True,
    )
    consistency_score: Mapped[int] = mapped_column(Integer, default=0)

    narrative_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    narrative_vn: Mapped[str | None] = mapped_column(Text, nullable=True)
    narrative_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    badge_issued: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="etester_core", uselist=False)
    badge: Mapped["ETESTERBadge | None"] = relationship("ETESTERBadge", back_populates="core", uselist=False)

    def __repr__(self) -> str:
        return f"<ETESTERCore(student={self.student_id}, contributions={self.total_contributions})>"


# ──────────────────────────────────────────────────────────────────────────────
# MilestoneTraceLink — Approach C linking
# ──────────────────────────────────────────────────────────────────────────────

VALID_RELATIONSHIP_TYPES = (
    "experience_source", "revision_of", "mentor_guided",
    "skill_applied", "score_progression", "recommends",
)

class MilestoneTraceLink(Base, TimestampMixin):
    __tablename__ = "milestone_trace_links"
    __table_args__ = (
        UniqueConstraint("from_milestone_id", "to_milestone_id", name="uq_trace_link_pair"),
        CheckConstraint("confidence >= 0.0 AND confidence <= 1.0", name="chk_trace_confidence"),
        CheckConstraint(
            f"relationship_type IN ({', '.join(repr(t) for t in VALID_RELATIONSHIP_TYPES)})",
            name="chk_relationship_type",
        ),
        Index("idx_trace_links_student", "student_id"),
        Index("idx_trace_links_pending", "student_id", "confirmed_by_mentor"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_milestone_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("milestones.id", ondelete="RESTRICT"),
        nullable=False,
    )
    to_milestone_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("milestones.id", ondelete="RESTRICT"),
        nullable=False,
    )
    student_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("students.student_id", ondelete="CASCADE"),
        nullable=False,
    )

    relationship_type: Mapped[str] = mapped_column(String(30), nullable=False)
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)

    student_context_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    student_noted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    suggested_by_ai: Mapped[bool] = mapped_column(Boolean, default=True)
    confirmed_by_mentor: Mapped[bool] = mapped_column(Boolean, default=False)
    confirmed_by_mentor_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("mentors.mentor_id", ondelete="SET NULL"),
        nullable=True,
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    from_milestone: Mapped["Milestone"] = relationship(
        "Milestone", foreign_keys=[from_milestone_id], back_populates="trace_links_from"
    )
    to_milestone: Mapped["Milestone"] = relationship(
        "Milestone", foreign_keys=[to_milestone_id], back_populates="trace_links_to"
    )

    def __repr__(self) -> str:
        return f"<TraceLink(from={self.from_milestone_id}→to={self.to_milestone_id}, type={self.relationship_type})>"


# ──────────────────────────────────────────────────────────────────────────────
# MilestoneArtifact — hash + 3-stage signing
# ──────────────────────────────────────────────────────────────────────────────

class MilestoneArtifact(Base):
    __tablename__ = "milestone_artifacts"
    __table_args__ = (
        Index("idx_milestone_artifacts_student", "student_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    milestone_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("milestones.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    student_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("students.student_id", ondelete="CASCADE"),
        nullable=False,
    )

    full_text_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    artifact_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    prev_artifact_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    vc_signature: Mapped[str | None] = mapped_column(Text, nullable=True)
    mentor_signed: Mapped[bool] = mapped_column(Boolean, default=False)
    admin_signed: Mapped[bool] = mapped_column(Boolean, default=False)
    manager_signed: Mapped[bool] = mapped_column(Boolean, default=False)
    signed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    milestone: Mapped["Milestone"] = relationship("Milestone", back_populates="artifact")

    def __repr__(self) -> str:
        return f"<MilestoneArtifact(milestone={self.milestone_id})>"


# ──────────────────────────────────────────────────────────────────────────────
# ArtifactForm — structured form data + leadership
# ──────────────────────────────────────────────────────────────────────────────

class ArtifactForm(Base, TimestampMixin):
    __tablename__ = "artifact_forms"
    __table_args__ = (
        Index("idx_artifact_forms_student", "student_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    milestone_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("milestones.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    student_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("students.student_id", ondelete="CASCADE"),
        nullable=False,
    )

    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    form_version: Mapped[str] = mapped_column(String(10), default="1.0")
    form_data: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    blooms_level: Mapped[str | None] = mapped_column(String(30), nullable=True)
    skills_practiced: Mapped[list | None] = mapped_column(JSONB, default=list)

    had_leadership_role: Mapped[bool] = mapped_column(Boolean, default=False)
    leadership_role_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    leadership_team_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    leadership_outcome: Mapped[str | None] = mapped_column(String(500), nullable=True)

    mentor_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    mentor_comment_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("mentors.mentor_id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    milestone: Mapped["Milestone"] = relationship("Milestone", back_populates="form")

    def __repr__(self) -> str:
        return f"<ArtifactForm(milestone={self.milestone_id}, type={self.activity_type})>"


# ──────────────────────────────────────────────────────────────────────────────
# MentorVerification — append-only audit log
# ──────────────────────────────────────────────────────────────────────────────

class MentorVerification(Base):
    __tablename__ = "mentor_verifications"
    __table_args__ = (
        Index("idx_mentor_verif_student", "student_id"),
        Index("idx_mentor_verif_milestone", "milestone_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    milestone_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("milestones.id", ondelete="RESTRICT"),
        nullable=False,
    )
    student_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("students.student_id", ondelete="CASCADE"),
        nullable=False,
    )

    verifier_id: Mapped[int] = mapped_column(Integer, nullable=False)
    verifier_type: Mapped[str] = mapped_column(String(20), nullable=False)

    action_type: Mapped[str] = mapped_column(String(30), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    trace_link_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("milestone_trace_links.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<MentorVerification(milestone={self.milestone_id}, action={self.action_type})>"


# ──────────────────────────────────────────────────────────────────────────────
# AuthScoringResult — 7-dimension scoring
# ──────────────────────────────────────────────────────────────────────────────

class AuthScoringResult(Base):
    __tablename__ = "auth_scoring_results"
    __table_args__ = (
        Index("idx_auth_scoring_student", "student_id"),
        Index("idx_auth_scoring_milestone", "milestone_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    milestone_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("milestones.id", ondelete="CASCADE"),
        nullable=False,
    )
    student_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("students.student_id", ondelete="CASCADE"),
        nullable=False,
    )

    auth_score: Mapped[int] = mapped_column(Integer, nullable=False)
    verdict: Mapped[str] = mapped_column(String(30), nullable=False)

    dimension_scores: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    explaining_artifacts: Mapped[list | None] = mapped_column(JSONB, default=list)

    explanation_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation_vn: Mapped[str | None] = mapped_column(Text, nullable=True)
    graph_snapshot: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    scored_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    milestone: Mapped["Milestone"] = relationship("Milestone", back_populates="auth_results")

    def __repr__(self) -> str:
        return f"<AuthScoringResult(milestone={self.milestone_id}, score={self.auth_score})>"


# ──────────────────────────────────────────────────────────────────────────────
# ETESTERBadge — issued credential
# ──────────────────────────────────────────────────────────────────────────────

class ETESTERBadge(Base):
    __tablename__ = "etester_badges"
    __table_args__ = (
        Index("idx_etester_badges_student", "student_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    core_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("etester_core.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    student_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("students.student_id", ondelete="CASCADE"),
        nullable=False,
    )

    badge_uid: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    credential_type: Mapped[str] = mapped_column(String(30), default="jwt_rs256")
    signed_token: Mapped[str] = mapped_column(Text, nullable=False)
    issuer_did: Mapped[str] = mapped_column(String(100), default="did:web:etest.edu.vn")

    badge_payload: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoke_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    verify_count: Mapped[int] = mapped_column(Integer, default=0)
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    core: Mapped["ETESTERCore"] = relationship("ETESTERCore", back_populates="badge")

    def __repr__(self) -> str:
        return f"<ETESTERBadge(uid={self.badge_uid}, student={self.student_id})>"


# ──────────────────────────────────────────────────────────────────────────────
# Forward references for relationship resolution
# ──────────────────────────────────────────────────────────────────────────────
from shared.model import Milestone, Student  # noqa: E402, F811

__all__ = [
    "ETESTERCore",
    "MilestoneTraceLink",
    "MilestoneArtifact",
    "ArtifactForm",
    "MentorVerification",
    "AuthScoringResult",
    "ETESTERBadge",
    "VALID_RELATIONSHIP_TYPES",
]
