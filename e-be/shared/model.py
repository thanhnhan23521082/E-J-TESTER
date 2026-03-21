"""
shared/model.py
──────────────
Central location for all SQLAlchemy ORM models.
All tables match alembic/versions/001_initial_schema.py (autogenerate source).

Usage:
    from shared.model import Student, Mentor, Parent, ...
    from core.base import Base              # declarative base

All models inherit from core.base.Base (not database.py.Base).
alembic/env.py imports this file to populate Base.metadata.
"""

from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base import Base


# ──────────────────────────────────────────────────────────────────────────────
# Mixin
# ──────────────────────────────────────────────────────────────────────────────

class TimestampMixin:
    """Adds created_at / updated_at to any model."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


# ──────────────────────────────────────────────────────────────────────────────
# User  (auth accounts — parents, mentors, students, managers)
# ──────────────────────────────────────────────────────────────────────────────

class User(Base, TimestampMixin):
    """
    User — tài khoản auth (email + password).
    Phân biệt role: parent | mentor | student | manager | admin.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="parent")  # parent | mentor | student | manager | admin
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relations
    student: Mapped["Student | None"] = relationship(
        "Student", back_populates="user", uselist=False
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


# ──────────────────────────────────────────────────────────────────────────────
# Mentor
# ──────────────────────────────────────────────────────────────────────────────

class Mentor(Base, TimestampMixin):
    """
    Mentor — người hướng dẫn học viên. 1 mentor : N students.
    """

    __tablename__ = "mentors"
    __table_args__ = (
        Index("idx_mentors_email", "email"),
        Index("mentors_programs_gin", "programs", postgresql_using="gin"),
    )

    mentor_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    specialty: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    programs: Mapped[list] = mapped_column(JSONB, default=list)  # ["AMP","IELTS","SAT"]
    max_students: Mapped[int] = mapped_column(Integer, default=10)
    active_students: Mapped[int] = mapped_column(Integer, default=0)

    # Relations
    students: Mapped[list["Student"]] = relationship("Student", back_populates="mentor")
    milestones: Mapped[list["Milestone"]] = relationship("Milestone", back_populates="mentor")

    def __repr__(self) -> str:
        return f"<Mentor(id={self.mentor_id}, name={self.full_name})>"


# ──────────────────────────────────────────────────────────────────────────────
# Parent
# ──────────────────────────────────────────────────────────────────────────────

class Parent(Base, TimestampMixin):
    """
    Parent — phụ huynh. 1:1 với student.
    """

    __tablename__ = "parents"
    __table_args__ = (
        Index("idx_parents_email", "email"),
        Index("idx_parents_student_id", "student_id"),
    )

    parent_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    telegram_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    student_id: Mapped[str | None] = mapped_column(
        String(50), unique=True, nullable=True
    )  # bidirectional 1:1

    # Relations
    student: Mapped["Student | None"] = relationship(
        "Student",
        back_populates="parent",
        primaryjoin="Parent.parent_id == Student.parent_id",
        foreign_keys="Student.parent_id",
        uselist=False,
    )
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation", back_populates="parent"
    )

    def __repr__(self) -> str:
        return f"<Parent(id={self.parent_id}, name={self.full_name})>"


# ──────────────────────────────────────────────────────────────────────────────
# Manager
# ──────────────────────────────────────────────────────────────────────────────

class Manager(Base, TimestampMixin):
    """
    Manager — quản lý trung tâm. Giám sát mentor + học viên.
    """

    __tablename__ = "managers"
    __table_args__ = (
        Index("idx_managers_email", "email"),
    )

    manager_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<Manager(id={self.manager_id}, name={self.full_name})>"


# ──────────────────────────────────────────────────────────────────────────────
# Student
# ──────────────────────────────────────────────────────────────────────────────

class Student(Base, TimestampMixin):
    """
    Student — học viên.
    FK user_id:   1:1 với User (auth account).
    FK parent_id: 1:1 với Parent.
    FK mentor_id: N:1 với Mentor.
    Digest fields: tự cập nhật qua trigger trên milestones.
    """

    __tablename__ = "students"
    __table_args__ = (
        Index("idx_students_user_id", "user_id"),
        Index("idx_students_parent_id", "parent_id"),
        Index("idx_students_mentor_id", "mentor_id"),
        Index("idx_students_program", "program"),
        CheckConstraint(
            "progress_pct >= 0 AND progress_pct <= 100",
            name="chk_progress_pct",
        ),
    )

    # PK
    student_id: Mapped[str] = mapped_column(String(50), primary_key=True)

    # FK — 1:1 with User (auth account)
    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=True,
    )

    # Identity
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Academic scores
    ielts_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 1), nullable=True)
    sat_score: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    gpa: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), nullable=True)

    # JSON fields
    skill_breakdown: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    target_schools: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Program
    program: Mapped[str | None] = mapped_column(String(100), nullable=True)
    months_enrolled: Mapped[int] = mapped_column(Integer, default=0)

    # FK — 1:1 Parent, N:1 Mentor
    parent_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("parents.parent_id", ondelete="RESTRICT"),
        unique=True,
        nullable=True,
    )
    mentor_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("mentors.mentor_id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Trigger-maintained digest fields ────────────────────────────────────
    progress_pct: Mapped[int] = mapped_column(Integer, default=0)
    milestones_done: Mapped[int] = mapped_column(Integer, default=0)
    next_deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    next_deadline_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    days_left: Mapped[int | None] = mapped_column(Integer, nullable=True)
    priority_action: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ── Wellbeing context ────────────────────────────────────────────────────
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_activity_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    weakest_skill: Mapped[str | None] = mapped_column(String(50), nullable=True)
    upsell_cooldown: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Relations
    user: Mapped["User | None"] = relationship(
        "User", back_populates="student", uselist=False
    )
    parent: Mapped["Parent | None"] = relationship(
        "Parent", back_populates="student", foreign_keys=[parent_id]
    )
    mentor: Mapped["Mentor | None"] = relationship("Mentor", back_populates="students")
    behavioral_logs: Mapped[list["BehavioralLog"]] = relationship(
        "BehavioralLog", back_populates="student", cascade="all, delete-orphan"
    )
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation", back_populates="student", cascade="all, delete-orphan"
    )
    milestones: Mapped[list["Milestone"]] = relationship(
        "Milestone", back_populates="student", cascade="all, delete-orphan"
    )

    # ETESTER relationships
    etester_core: Mapped["ETESTERCore | None"] = relationship(
        "ETESTERCore", back_populates="student", uselist=False
    )

    def __repr__(self) -> str:
        return f"<Student(id={self.student_id}, name={self.name})>"

    def get_weakest_skill(self) -> str | None:
        """Return the lowest-scored skill from skill_breakdown."""
        if not self.skill_breakdown:
            return None
        return min(self.skill_breakdown, key=self.skill_breakdown.get)


# ──────────────────────────────────────────────────────────────────────────────
# School
# ──────────────────────────────────────────────────────────────────────────────

class School(Base):
    """
    School — metadata trường học lưu semi-structured data bằng JSONB.
    Chỉ giữ 2 cột để linh hoạt cho requirement / scholarship / notes theo từng trường.
    """

    __tablename__ = "schools"
    __table_args__ = (
        Index("idx_schools_data_gin", "data", postgresql_using="gin"),
    )

    school_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    data: Mapped[dict] = mapped_column(JSONB, nullable=False)

    def __repr__(self) -> str:
        return f"<School(id={self.school_id})>"


# ──────────────────────────────────────────────────────────────────────────────
# Course
# ──────────────────────────────────────────────────────────────────────────────

class Course(Base, TimestampMixin):
    """
    Course — khóa học / trại hè cho upsell engine (Module 1D).
    """

    __tablename__ = "courses"
    __table_args__ = (
        Index("courses_target_skills_gin", "target_skills", postgresql_using="gin"),
        Index("courses_suitable_for_gin", "suitable_for", postgresql_using="gin"),
        Index("idx_courses_program_season", "program", "season"),
    )

    course_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # camp | workshop | course
    program: Mapped[str | None] = mapped_column(String(100), nullable=True)
    season: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_skills: Mapped[list] = mapped_column(JSONB, default=list)
    suitable_for: Mapped[list] = mapped_column(JSONB, default=list)
    cta_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cta_label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    duration_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    price_vnd: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<Course(id={self.course_id}, name={self.name})>"


# ──────────────────────────────────────────────────────────────────────────────
# BehavioralLog
# ──────────────────────────────────────────────────────────────────────────────

class BehavioralLog(Base):
    """
    BehavioralLog — nhật ký học tập hàng ngày. 1 row / student / date.
    is_late_night: Python-computed property (session_start >= 22:00).
    """

    __tablename__ = "behavioral_logs"
    __table_args__ = (
        UniqueConstraint("student_id", "date", name="uq_behavioral_logs_student_date"),
        Index("idx_behavioral_logs_student_date", "student_id", "date"),
        Index("idx_behavioral_logs_studied", "student_id", "date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    duration_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    session_start: Mapped[time | None] = mapped_column(Time, nullable=True)
    session_end: Mapped[time | None] = mapped_column(Time, nullable=True)
    studied: Mapped[bool] = mapped_column(Boolean, server_default="false", default=False)
    streak_day: Mapped[int] = mapped_column(Integer, server_default="0", default=0)
    score_delta: Mapped[Decimal] = mapped_column(
        Numeric(4, 1), server_default="0", default=Decimal("0.0")
    )
    activities: Mapped[list] = mapped_column(
        JSONB, server_default=text("'[]'::jsonb"), default=list
    )
    mood_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relations
    student: Mapped["Student"] = relationship("Student", back_populates="behavioral_logs")

    @property
    def is_late_night(self) -> bool:
        """True if session started at or after 22:00."""
        if self.session_start is None:
            return False
        return self.session_start >= time(22, 0)

    def __repr__(self) -> str:
        return f"<BehavioralLog(student={self.student_id}, date={self.date})>"


# ──────────────────────────────────────────────────────────────────────────────
# Conversation
# ──────────────────────────────────────────────────────────────────────────────

class Conversation(Base):
    """
    Conversation — lịch sử chat giữa phụ huynh và AI.
    expires_at: timestamp + 30 days → TTL cleanup hàng đêm.
    """

    __tablename__ = "conversations"
    __table_args__ = (
        Index("idx_conversations_parent_timestamp", "parent_id", "timestamp"),
        Index("idx_conversations_student_id", "student_id", "timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("parents.parent_id", ondelete="CASCADE"), nullable=False
    )
    student_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    ai_response: Mapped[str] = mapped_column(Text, nullable=False)
    context_snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    escalated: Mapped[bool] = mapped_column(Boolean, default=False)
    escalator_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relations
    parent: Mapped["Parent"] = relationship("Parent", back_populates="conversations")
    student: Mapped["Student"] = relationship("Student", back_populates="conversations")

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, parent={self.parent_id})>"


# ──────────────────────────────────────────────────────────────────────────────
# Milestone
# ──────────────────────────────────────────────────────────────────────────────

class Milestone(Base):
    """
    Milestone — cột mốc thành tích của học viên.
    Trigger trên bảng này tự cập nhật digest fields trên students.
    """

    __tablename__ = "milestones"
    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "milestone_id",
            name="uq_milestones_student_milestone_id",
        ),
        Index("idx_milestones_student_date", "student_id", "date"),
        Index(
            "idx_milestones_upcoming",
            "student_id",
            "date",
            postgresql_where="status = 'upcoming'",
        ),
        Index(
            "idx_milestones_completed",
            "student_id",
            "date",
            postgresql_where="status = 'completed'",
        ),
        Index("idx_milestones_essays", "student_id", "date"),
        CheckConstraint(
            "auth_score IS NULL OR (auth_score >= 0 AND auth_score <= 100)",
            name="chk_auth_score",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False
    )
    milestone_id: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    score: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    score_label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    mentor_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("mentors.mentor_id", ondelete="SET NULL"), nullable=True
    )
    mentor_approved: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    auth_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="upcoming")
    contributor_type: Mapped[str] = mapped_column(String(50), default="student")
    ai_summary: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relations
    student: Mapped["Student"] = relationship("Student", back_populates="milestones")
    mentor: Mapped["Mentor | None"] = relationship("Mentor", back_populates="milestones")

    # ETESTER relationships
    artifact: Mapped["MilestoneArtifact | None"] = relationship(
        "MilestoneArtifact", back_populates="milestone", uselist=False
    )
    form: Mapped["ArtifactForm | None"] = relationship(
        "ArtifactForm", back_populates="milestone", uselist=False
    )
    trace_links_from: Mapped[list["MilestoneTraceLink"]] = relationship(
        "MilestoneTraceLink",
        foreign_keys="MilestoneTraceLink.from_milestone_id",
        back_populates="from_milestone",
    )
    trace_links_to: Mapped[list["MilestoneTraceLink"]] = relationship(
        "MilestoneTraceLink",
        foreign_keys="MilestoneTraceLink.to_milestone_id",
        back_populates="to_milestone",
    )
    auth_results: Mapped[list["AuthScoringResult"]] = relationship(
        "AuthScoringResult", back_populates="milestone"
    )

    def __repr__(self) -> str:
        return f"<Milestone(id={self.milestone_id}, type={self.type}, status={self.status})>"


# ──────────────────────────────────────────────────────────────────────────────
# ETESTER Module v4 — 7 models
# ──────────────────────────────────────────────────────────────────────────────

# Valid relationship types for MilestoneTraceLink
VALID_RELATIONSHIP_TYPES = (
    "experience_source", "revision_of", "mentor_guided",
    "skill_applied", "score_progression", "recommends",
)


# ── ETESTERCore — single source of truth per student (1:1) ───────────────────

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
    badge: Mapped["ETESTERBadge | None"] = relationship(
        "ETESTERBadge", back_populates="core", uselist=False
    )

    def __repr__(self) -> str:
        return f"<ETESTERCore(student={self.student_id}, contributions={self.total_contributions})>"


# ── MilestoneTraceLink — Approach C linking ────────────────────────────────────

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


# ── MilestoneArtifact — hash + 3-stage signing ───────────────────────────────

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


# ── ArtifactForm — structured form data + leadership ──────────────────────────

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


# ── MentorVerification — append-only audit log ─────────────────────────────────

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


# ── AuthScoringResult — 7-dimension scoring ───────────────────────────────────

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


# ── ETESTERBadge — issued credential ───────────────────────────────────────────

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
# __all__  (public API)
# ──────────────────────────────────────────────────────────────────────────────

__all__ = [
    "Base",
    "TimestampMixin",
    # Auth
    "User",
    # Domain
    "Mentor",
    "Parent",
    "Manager",
    "Student",
    "School",
    "Course",
    "BehavioralLog",
    "Conversation",
    "Milestone",
    # ETESTER
    "ETESTERCore",
    "MilestoneTraceLink",
    "MilestoneArtifact",
    "ArtifactForm",
    "MentorVerification",
    "AuthScoringResult",
    "ETESTERBadge",
    "VALID_RELATIONSHIP_TYPES",
]
