"""
shared/model.py
───────────────
SQLAlchemy ORM models for all 5 database tables.
Imported by core/database.py → Base.metadata to create schema.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


# ──────────────────────────────────────────────────────────────────────────────
# User – authentication identity (one per person)
# ──────────────────────────────────────────────────────────────────────────────
class User(Base):
    """Authenticated user account (parent, mentor, or admin)."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="parent")  # parent | mentor | admin
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    students: Mapped[list["Student"]] = relationship("Student", back_populates="user")
    conversations: Mapped[list["Conversation"]] = relationship("Conversation", back_populates="parent")


# ──────────────────────────────────────────────────────────────────────────────
# Student – core learner profile
# ──────────────────────────────────────────────────────────────────────────────
class Student(Base):
    """Student profile managed by a parent and optionally linked to a mentor."""

    __tablename__ = "students"

    student_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Academic scores
    ielts_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    sat_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    gpa: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Skill breakdown – JSON stored as Text, deserialised by application
    skill_breakdown: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Target schools – JSON stored as Text
    target_schools: Mapped[str | None] = mapped_column(Text, nullable=True)

    months_enrolled: Mapped[int | None] = mapped_column(Integer, nullable=True)
    program: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Foreign keys
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    mentor_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])
    parent: Mapped["User | None"] = relationship("User", foreign_keys=[parent_id])
    mentor: Mapped["User | None"] = relationship("User", foreign_keys=[mentor_id])
    behavioral_logs: Mapped[list["BehavioralLog"]] = relationship("BehavioralLog", back_populates="student")
    milestones: Mapped[list["Milestone"]] = relationship("Milestone", back_populates="student")
    etester_core: Mapped["ETESTERCore | None"] = relationship("ETESTERCore", back_populates="student", uselist=False)
    conversations: Mapped[list["Conversation"]] = relationship("Conversation", back_populates="student")


# ──────────────────────────────────────────────────────────────────────────────
# BehavioralLog – daily engagement telemetry
# ──────────────────────────────────────────────────────────────────────────────
class BehavioralLog(Base):
    """Daily learning behaviour record for a student."""

    __tablename__ = "behavioral_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(String(50), ForeignKey("students.student_id"), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duration_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    session_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    studied: Mapped[bool | None] = mapped_column(Boolean, default=False)
    streak_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_delta: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relations
    student: Mapped["Student"] = relationship("Student", back_populates="behavioral_logs")


# ──────────────────────────────────────────────────────────────────────────────
# Conversation – parent AI chat history
# ──────────────────────────────────────────────────────────────────────────────
class Conversation(Base):
    """Logged parent–AI chat turn."""

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    student_id: Mapped[str] = mapped_column(String(50), ForeignKey("students.student_id"), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    ai_response: Mapped[str] = mapped_column(Text, nullable=False)
    context_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    escalated: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relations
    parent: Mapped["User"] = relationship("User", back_populates="conversations")
    student: Mapped["Student"] = relationship("Student", back_populates="conversations")


# ──────────────────────────────────────────────────────────────────────────────
# Milestone – student achievement record
# ──────────────────────────────────────────────────────────────────────────────
class Milestone(Base):
    """Individual student achievement / activity entry in the ETESTER ecosystem."""

    __tablename__ = "milestones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(String(50), ForeignKey("students.student_id"), nullable=False)
    milestone_id: Mapped[str] = mapped_column(String(100), nullable=False)  # unique within student scope
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # MilestoneType value
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    mentor_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    mentor_approved: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    auth_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # AI authenticity score
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending | approved | rejected
    contributor_type: Mapped[str] = mapped_column(String(50), nullable=False)  # ContributorType value
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relations
    student: Mapped["Student"] = relationship("Student", back_populates="milestones")


# ──────────────────────────────────────────────────────────────────────────────
# ETESTERCore – aggregated ETESTER scorecard
# ──────────────────────────────────────────────────────────────────────────────
class ETESTERCore(Base):
    """
    Aggregated ETESTER scorecard per student.
    Rebuilt whenever a new milestone is contributed.
    """

    __tablename__ = "etester_core"

    student_id: Mapped[str] = mapped_column(String(50), ForeignKey("students.student_id"), primary_key=True)
    academic_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    writing_growth: Mapped[float | None] = mapped_column(Float, nullable=True)
    skills: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON dict
    mentor_verifications: Mapped[int] = mapped_column(Integer, default=0)
    parent_support_level: Mapped[float | None] = mapped_column(Float, nullable=True)
    institutional_stamp: Mapped[str | None] = mapped_column(String(100), nullable=True)
    consistency_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_contributions: Mapped[int] = mapped_column(Integer, default=0)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    narrative_cache: Mapped[str | None] = mapped_column(Text, nullable=True)  # Cached LLM narrative
    badge_issued: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relations
    student: Mapped["Student"] = relationship("Student", back_populates="etester_core")
