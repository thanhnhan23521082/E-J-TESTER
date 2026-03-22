"""
shared/constants.py
───────────────────
Application-wide Enums, constants, and threshold dictionaries.
Import what you need – avoid module-level side-effects.
"""

from enum import Enum


# ── Contributor types ────────────────────────────────────────────────────────
class ContributorType(str, Enum):
    """Who contributed a milestone record."""

    STUDENT = "student"
    MENTOR = "mentor"
    PARENT = "parent"
    INSTITUTION = "institution"


# ── Alert severity ────────────────────────────────────────────────────────────
class Severity(str, Enum):
    """Severity level for wellbeing alerts."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ── Milestone types ───────────────────────────────────────────────────────────
class MilestoneType(str, Enum):
    """Type of achievement / activity recorded as a milestone."""

    IELTS_MOCK = "ielts_mock"
    ESSAY_DRAFT = "essay_draft"
    ESSAY_FINAL = "essay_final"
    SAT_MOCK = "sat_mock"
    TOEFL_MOCK = "toefl_mock"
    MOCK_TEST = "mock_test"
    EXTRACURRICULAR = "extracurricular"
    CONSULTATION = "consultation"
    MENTOR_SESSION = "mentor_session"
    CAMP = "camp"
    CSR = "csr"
    AWARD = "award"
    ACADEMIC_RECORD = "academic_record"
    RECOMMENDATION = "recommendation"
    TARGET_ACHIEVED = "target_achieved"


# ── Wellbeing thresholds ─────────────────────────────────────────────────────
# Used by modules/smart_parenting/services/wellbeing.py
WELLBEING_THRESHOLDS: dict[str, dict[str, float]] = {
    "study_time": {
        "min_daily_min": 30.0,  # minimum expected daily study minutes
        "alert_below": 15.0,  # trigger low-alert below this
    },
    "session_count": {
        "expected_weekly": 5.0,  # expected sessions per week
        "alert_below": 2.0,
    },
    "streak_day": {
        "min_streak": 3.0,  # minimum healthy streak
        "alert_below": 1.0,
    },
    "score_delta": {
        "positive_min": 0.1,  # any positive delta is good
        "negative_alert_below": -0.5,
    },
    "consistency_score": {
        "healthy_min": 0.6,  # 0–1 scale
        "alert_below": 0.3,
    },
}

# ── Milestone status ─────────────────────────────────────────────────────────
MILESTONE_STATUS_PENDING = "pending"
MILESTONE_STATUS_APPROVED = "approved"
MILESTONE_STATUS_REJECTED = "rejected"

# ── Badge tiers ─────────────────────────────────────────────────────────────
BADGE_TIERS = {
    "bronze":  {"min_contributions": 3,   "min_consistency": 0.4},
    "silver":  {"min_contributions": 10,  "min_consistency": 0.6},
    "gold":    {"min_contributions": 25,  "min_consistency": 0.75},
    "platinum":{"min_contributions": 50,  "min_consistency": 0.9},
}
