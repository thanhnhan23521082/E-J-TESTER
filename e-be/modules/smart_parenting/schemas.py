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
    created_at: str  # ISO 8601

    model_config = {"from_attributes": True}


# ── FE-aligned schemas (camelCase, matching e-fe/src/types/index.ts) ─────────

class SkillBreakdown(BaseModel):
    """Khớp FE Student.skillBreakdown: {L, R, W, S}."""
    L: float
    R: float
    W: float
    S: float


class TargetSchool(BaseModel):
    """Khớp FE Student.targetSchools[]."""
    name: str
    country: str
    deadline: str
    ieltsRequired: float
    satRequired: float | None
    daysUntilDeadline: int
    isEligible: bool
    gapIelts: float
    gapSat: float | None


class StudentResponse(BaseModel):
    """
    Full student record — khớp Student interface ở e-fe/src/types/index.ts.
    CamelCase field names, nested objects, string IDs.
    """
    id: str
    name: str
    program: str
    monthsEnrolled: int
    ieltsScore: float | None
    satScore: float | None
    gpa: float | None
    skillBreakdown: SkillBreakdown | None
    targetSchools: list[TargetSchool] = Field(default_factory=list)
    parentId: str
    mentorId: str

    model_config = {"populate_by_name": True, "from_attributes": True}

    @classmethod
    def from_orm(cls, s) -> "StudentResponse":
        return cls(
            id=s.student_id,
            name=s.name,
            program=s.program or "IELTS",
            monthsEnrolled=s.months_enrolled or 0,
            ieltsScore=float(s.ielts_score) if s.ielts_score is not None else None,
            satScore=float(s.sat_score) if s.sat_score is not None else None,
            gpa=float(s.gpa) if s.gpa is not None else None,
            skillBreakdown=SkillBreakdown(**s.skill_breakdown)
            if s.skill_breakdown
            else None,
            targetSchools=[TargetSchool(**t) for t in (s.target_schools or [])],
            parentId=str(s.parent_id) if s.parent_id is not None else "",
            mentorId=str(s.mentor_id) if s.mentor_id is not None else "",
        )


class AiSummary(BaseModel):
    """Khớp FE Milestone.aiSummary."""
    summary: str
    skillsDemonstrated: list[str]
    evidenceStrength: str  # 'low'|'medium'|'high'|'highest'


class MilestoneResponse(BaseModel):
    """
    Milestone record — khớp Milestone interface ở e-fe/src/types/index.ts.
    """
    id: str
    studentId: str
    type: str
    title: str
    date: str
    score: float | None
    scoreLabel: str
    mentorId: str | None
    mentorApproved: bool
    authScore: float | None
    notes: str
    status: str
    contributorType: str
    aiSummary: AiSummary

    model_config = {"populate_by_name": True, "from_attributes": True}

    @classmethod
    def from_orm(cls, m) -> "MilestoneResponse":
        ai = m.ai_summary or {}
        return cls(
            id=m.milestone_id,
            studentId=m.student_id,
            type=m.type,
            title=m.title,
            date=m.date.isoformat(),
            score=float(m.score) if m.score is not None else None,
            scoreLabel=m.score_label or "",
            mentorId=str(m.mentor_id) if m.mentor_id is not None else None,
            mentorApproved=m.mentor_approved or False,
            authScore=float(m.auth_score) if m.auth_score is not None else None,
            notes=m.notes or "",
            status=m.status,
            contributorType=m.contributor_type,
            aiSummary=AiSummary(
                summary=ai.get("summary", ""),
                skillsDemonstrated=ai.get("skills_demonstrated", []),
                evidenceStrength=ai.get("evidence_strength", "medium"),
            ),
        )


class WellbeingAlertFE(BaseModel):
    """
    Flat wellbeing alert — khớp WellbeingAlert interface ở e-fe/src/types/index.ts.
    """
    alert: bool
    severity: str
    message: str
    action: str


class DigestDataFE(BaseModel):
    """
    Digest data — khớp DigestData interface ở e-fe/src/types/index.ts.
    """
    progressPct: int
    milestonesCompleted: int
    nextDeadline: str
    daysLeft: int
    priorityAction: str
    weakestSkill: str


class ParentMessageRequest(BaseModel):
    """Payload for parent → mentor message."""
    mentorId: str
    message: str


class ParentMessageResponse(BaseModel):
    """Response after parent sends message."""
    messageId: str


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
    studied: bool
    streak_day: int | None
    score_delta: float | None

    model_config = {"from_attributes": True}


class BehavioralLogListResponse(BaseModel):
    """Paginated list of behavioural logs with computed metrics."""

    student_id: str
    days: int
    logs: list[BehavioralLogResponse]
    metrics: BehavioralMetrics


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
