"""
modules/smart_parenting/schemas.py
──────────────────────────────────
Pydantic request/response models for Smart Parenting endpoints.
"""

from datetime import datetime

from pydantic import BaseModel, Field


# ── Shared / reused ───────────────────────────────────────────────────────────

class StudentProfile(BaseModel):
    """Public student profile returned to parents."""

    student_id: str
    name: str
    ielts_score: float | None = None
    sat_score: float | None = None
    gpa: float | None = None
    months_enrolled: int | None = None
    program: str | None = None
    skill_breakdown: dict | None = None
    target_schools: list[dict] = Field(default_factory=list)
    parent_id: int | None = None
    mentor_id: int | None = None
    progress_pct: int | None = None
    milestones_done: int | None = None
    next_deadline: str | None = None
    next_deadline_label: str | None = None
    days_left: int | None = None
    priority_action: str | None = None
    weakest_skill: str | None = None
    created_at: str  # ISO 8601

    model_config = {"from_attributes": True}


class BehavioralMetrics(BaseModel):
    """Computed behavioural metrics from a set of logs."""

    avg_daily_study_min: float = Field(description="Average study minutes per day")
    total_sessions: int = Field(description="Number of study sessions in period")
    current_streak: int = Field(description="Current consecutive study days")
    avg_score_delta: float = Field(description="Average score change per session")
    consistency_score: float = Field(description="0–1 score of study consistency")
    alert_level: str = Field(description="none | low | medium | high")


class BehavioralLogResponse(BaseModel):
    """A single behavioural log entry."""

    id: int
    student_id: str
    date: str  # ISO 8601 date
    duration_min: float | None
    session_start: str | None = None
    studied: bool
    is_late_night: bool = False
    streak_day: int | None
    score_delta: float | None
    mood_note: str | None = None

    model_config = {"from_attributes": True}


class BehavioralLogListResponse(BaseModel):
    """Paginated list of behavioural logs with computed metrics."""

    student_id: str
    days: int
    logs: list[BehavioralLogResponse]
    metrics: BehavioralMetrics


class ParentMeResponse(BaseModel):
    """Authenticated parent profile for parent dashboard context."""

    parent_id: int
    full_name: str
    email: str
    phone: str | None = None
    telegram_id: str | None = None
    student_id: str | None = None


# ── Parent AI Chat ────────────────────────────────────────────────────────────

class ParentChatRequest(BaseModel):
    """Payload for parent AI chat."""

    student_id: str = Field(..., description="Target student ID")
    question: str = Field(..., min_length=5, max_length=1000, description="Parent's question")
    escalate: bool = Field(default=False, description="Flag to escalate to human consultant")

    model_config = {"json_schema_extra": {
        "example": {
            "student_id": "STU-001",
            "question": "Con tôi tuần này học như thế nào?",
            "escalate": False,
        }
    }}


class ParentChatResponse(BaseModel):
    """AI response to a parent chat message."""

    answer: str = Field(..., description="AI-generated answer in Vietnamese")
    escalated: bool = Field(..., description="Whether this was flagged for human review")
    sources: list[str] = Field(
        default_factory=list,
        description="Context sources used for the answer",
    )
    model_config = {"json_schema_extra": {
        "example": {
            "answer": "Tuần này con bạn đã học 45 phút mỗi ngày...",
            "escalated": False,
            "sources": ["behavioral_logs", "milestones"],
        }
    }}


# ── Wellbeing ────────────────────────────────────────────────────────────────

class WellbeingRequest(BaseModel):
    """Optional payload to trigger a wellbeing check (uses query param student_id)."""

    pass


class WellbeingAlert(BaseModel):
    """Individual wellbeing concern."""

    type: str = Field(description="Alert type: study_time | streak | score_delta | consistency")
    severity: str = Field(description="none | low | medium | high")
    message: str = Field(description="Human-readable alert message")


class WellbeingResponse(BaseModel):
    """Wellbeing assessment result."""

    student_id: str
    overall_score: float = Field(..., ge=0, le=100, description="Overall wellbeing 0–100")
    severity: str = Field(..., description="none | low | medium | high")
    alerts: list[WellbeingAlert] = Field(default_factory=list)
    recommendations: list[str] = Field(
        default_factory=list,
        description="Suggested actions for the parent",
    )
    metrics: BehavioralMetrics

    model_config = {"json_schema_extra": {
        "example": {
            "student_id": "STU-001",
            "overall_score": 78.5,
            "severity": "low",
            "alerts": [
                {"type": "streak", "severity": "low", "message": "Streak giảm 1 ngày"}
            ],
            "recommendations": ["Khuyến khích con học 30 phút mỗi ngày"],
            "metrics": {
                "avg_daily_study_min": 32.0,
                "total_sessions": 5,
                "current_streak": 3,
                "avg_score_delta": 0.2,
                "consistency_score": 0.7,
                "alert_level": "low",
            },
        }
    }}


# ── Parent digest ─────────────────────────────────────────────────────────────

class DigestResponse(BaseModel):
    """Weekly parent newsletter content."""

    student_id: str
    student_name: str
    week_summary: str = Field(..., description="2–3 sentence summary of the week")
    highlights: list[str] = Field(default_factory=list, description="Key highlights")
    parent_tips: list[str] = Field(default_factory=list, description="Tips for parents")
    next_week_goals: list[str] = Field(default_factory=list, description="Goals for next week")
    generated_at: str  # ISO 8601

    model_config = {"json_schema_extra": {
        "example": {
            "student_id": "STU-001",
            "student_name": "Nguyễn Văn Minh",
            "week_summary": "Minh đã có một tuần học tập ổn định...",
            "highlights": ["IELTS mock đạt 7.0", "Hoàn thành essay draft"],
            "parent_tips": ["Hãy cùng con ôn từ vựng 15 phút mỗi tối"],
            "next_week_goals": ["Cải thiện kỹ năng Writing lên 6.5"],
            "generated_at": "2026-03-21T10:00:00Z",
        }
    }}


# ── Upsell ────────────────────────────────────────────────────────────────────

class UpsellItem(BaseModel):
    """A recommended program / upsell opportunity."""

    program_name: str = Field(..., description="Name of the recommended program")
    program_code: str = Field(..., description="Internal program code")
    priority: str = Field(..., description="high | medium | low")
    pitch: str = Field(..., description="Short personalised pitch (1–2 sentences)")
    price_estimate: str | None = Field(None, description="Estimated price range")
    expected_outcome: str = Field(..., description="Expected benefit for the student")


class UpsellResponse(BaseModel):
    """List of personalised program recommendations for a student."""

    student_id: str
    student_name: str
    current_program: str | None
    recommendations: list[UpsellItem]

    model_config = {"json_schema_extra": {
        "example": {
            "student_id": "STU-001",
            "student_name": "Nguyễn Văn Minh",
            "current_program": "IELTS Foundation",
            "recommendations": [
                {
                    "program_name": "IELTS Advanced",
                    "program_code": "IELTS-ADV-01",
                    "priority": "high",
                    "pitch": "Minh đã sẵn sàng chuyển sang lộ trình nâng cao...",
                    "price_estimate": "VND 8,000,000",
                    "expected_outcome": "IELTS 7.5+ trong 3 tháng",
                }
            ],
        }
    }}

class ParentHomeResponse(BaseModel):
    """Aggregated payload for parent home page."""

    student_id: str
    profile: StudentProfile
    wellbeing: WellbeingResponse
    digest: DigestResponse
    upsell: UpsellResponse
