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
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
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
# User  (auth accounts — parents, mentors, admins)
# ──────────────────────────────────────────────────────────────────────────────

class User(Base, TimestampMixin):
    """
    User — tài khoản auth (email + password).
    Phân biệt role: parent | mentor | admin.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="parent")  # parent | mentor | admin

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
        "Student", back_populates="parent", foreign_keys=[student_id]
    )
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation", back_populates="parent"
    )

    def __repr__(self) -> str:
        return f"<Parent(id={self.parent_id}, name={self.full_name})>"


# ──────────────────────────────────────────────────────────────────────────────
# Student
# ──────────────────────────────────────────────────────────────────────────────

class Student(Base, TimestampMixin):
    """
    Student — học viên.
    FK parent_id: 1:1 với Parent.
    FK mentor_id:  N:1 với Mentor.
    Digest fields: tự cập nhật qua trigger trên milestones.
    """

    __tablename__ = "students"
    __table_args__ = (
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

    def __repr__(self) -> str:
        return f"<Student(id={self.student_id}, name={self.name})>"

    def get_weakest_skill(self) -> str | None:
        """Return the lowest-scored skill from skill_breakdown."""
        if not self.skill_breakdown:
            return None
        return min(self.skill_breakdown, key=self.skill_breakdown.get)


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
        JSONB, server_default="'[]'::jsonb", default=list
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

    def __repr__(self) -> str:
        return f"<Milestone(id={self.milestone_id}, type={self.type}, status={self.status})>"


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
    "Student",
    "Course",
    "BehavioralLog",
    "Conversation",
    "Milestone",
]
