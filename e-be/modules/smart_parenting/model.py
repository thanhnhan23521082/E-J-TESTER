"""
modules/smart_parenting/model.py
────────────────────────────────
Backward-compatibility shim — all models moved to shared/model.py.
New code should import directly from shared.model.
"""

from shared.model import (
    BehavioralLog,
    Conversation,
    Course,
    Mentor,
    Milestone,
    Parent,
    Student,
    User,
)

__all__ = [
    "BehavioralLog",
    "Conversation",
    "Course",
    "Mentor",
    "Milestone",
    "Parent",
    "Student",
    "User",
]
