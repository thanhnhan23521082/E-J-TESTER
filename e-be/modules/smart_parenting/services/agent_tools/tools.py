"""Toolset for Smart Parenting parent chatbot agent."""

from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

import httpx
from langchain_core.tools import tool
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from shared.model import BehavioralLog, Conversation, Course, Mentor, Milestone, Parent, School, Student

settings = get_settings()


@dataclass
class ToolRuntimeContext:
    db: AsyncSession
    parent_id: int


_TOOL_RUNTIME_CONTEXT: ContextVar[ToolRuntimeContext | None] = ContextVar(
    "agent_tool_runtime_context",
    default=None,
)


def set_tool_runtime_context(*, db: AsyncSession, parent_id: int) -> Token:
    """Attach request-scoped runtime context for @tool functions."""
    return _TOOL_RUNTIME_CONTEXT.set(ToolRuntimeContext(db=db, parent_id=parent_id))


def reset_tool_runtime_context(token: Token) -> None:
    """Restore previous runtime context after tool execution."""
    _TOOL_RUNTIME_CONTEXT.reset(token)


def _require_runtime_context() -> ToolRuntimeContext:
    ctx = _TOOL_RUNTIME_CONTEXT.get()
    if ctx is None:
        raise RuntimeError("Tool runtime context is not set")
    return ctx


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime, time)):
        return value.isoformat()
    if isinstance(value, list):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    return value


def _student_payload(student: Student) -> dict[str, Any]:
    return {
        "student_id": student.student_id,
        "name": student.name,
        "program": student.program,
        "months_enrolled": student.months_enrolled,
        "ielts_score": _to_jsonable(student.ielts_score),
        "sat_score": _to_jsonable(student.sat_score),
        "gpa": _to_jsonable(student.gpa),
        "skill_breakdown": _to_jsonable(student.skill_breakdown),
        "target_schools": _to_jsonable(student.target_schools),
        "weakest_skill": student.weakest_skill,
        "progress_pct": student.progress_pct,
        "milestones_done": student.milestones_done,
        "next_deadline": _to_jsonable(student.next_deadline),
        "next_deadline_label": student.next_deadline_label,
        "days_left": student.days_left,
        "priority_action": student.priority_action,
        "current_streak": student.current_streak,
        "last_activity_date": _to_jsonable(student.last_activity_date),
        "upsell_cooldown": _to_jsonable(student.upsell_cooldown),
    }


async def resolve_parent_id(*, db: AsyncSession, user_id: int, user_email: str) -> int | None:
    """Resolve parent_id from authenticated user context."""
    result = await db.execute(select(Parent.parent_id).where(Parent.email == user_email))
    parent_id = result.scalar_one_or_none()
    if parent_id is not None:
        return parent_id

    result = await db.execute(select(Parent.parent_id).where(Parent.parent_id == user_id))
    return result.scalar_one_or_none()


async def get_student_profile(*, db: AsyncSession, student_id: str) -> dict[str, Any]:
    result = await db.execute(select(Student).where(Student.student_id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        return {"student": None}
    return _student_payload(student)


async def get_mentor_info(*, db: AsyncSession, student_id: str) -> dict[str, Any]:
    mentor_result = await db.execute(
        select(Mentor)
        .join(Student, Student.mentor_id == Mentor.mentor_id)
        .where(Student.student_id == student_id)
    )
    mentor = mentor_result.scalar_one_or_none()

    milestone_result = await db.execute(
        select(Milestone)
        .where(
            and_(
                Milestone.student_id == student_id,
                Milestone.mentor_approved.is_(True),
            )
        )
        .order_by(Milestone.date.desc())
        .limit(1)
    )
    latest = milestone_result.scalar_one_or_none()

    return {
        "mentor": None if mentor is None else {
            "mentor_id": mentor.mentor_id,
            "full_name": mentor.full_name,
            "specialty": mentor.specialty,
            "bio": mentor.bio,
            "programs": _to_jsonable(mentor.programs),
        },
        "last_approved_milestone": None if latest is None else {
            "title": latest.title,
            "date": _to_jsonable(latest.date),
            "score": _to_jsonable(latest.score),
            "score_label": latest.score_label,
            "notes": latest.notes,
            "ai_summary": _to_jsonable(latest.ai_summary),
        },
    }


async def get_behavioral_logs(*, db: AsyncSession, student_id: str, days: int = 14) -> dict[str, Any]:
    result = await db.execute(
        select(BehavioralLog)
        .where(BehavioralLog.student_id == student_id)
        .order_by(BehavioralLog.date.desc())
        .limit(days)
    )
    logs = list(result.scalars().all())

    entries = [
        {
            "date": _to_jsonable(log.date),
            "duration_min": log.duration_min,
            "session_start": _to_jsonable(log.session_start),
            "session_end": _to_jsonable(log.session_end),
            "studied": bool(log.studied),
            "streak_day": log.streak_day,
            "score_delta": _to_jsonable(log.score_delta),
            "activities": _to_jsonable(log.activities),
            "mood_note": log.mood_note,
            "is_late_night": bool(log.is_late_night),
        }
        for log in logs
    ]

    late_night_count = sum(1 for log in logs if log.is_late_night)
    studied_days = sum(1 for log in logs if log.studied)
    durations = [int(log.duration_min) for log in logs if log.duration_min]
    avg_duration = round(sum(durations) / len(durations), 2) if durations else 0
    duration_this_week = sum(int(log.duration_min or 0) for log in logs[:7])
    duration_prev_week = sum(int(log.duration_min or 0) for log in logs[7:14])
    duration_drop_pct = 0
    if duration_prev_week > 0:
        duration_drop_pct = round((duration_prev_week - duration_this_week) / duration_prev_week * 100)

    return {
        "logs": entries,
        "summary": {
            "late_night_count": late_night_count,
            "studied_days": studied_days,
            "avg_duration_min": avg_duration,
            "duration_drop_pct": duration_drop_pct,
            "has_mood_notes": any(bool(log.mood_note) for log in logs),
        },
    }


async def get_milestones(
    *,
    db: AsyncSession,
    student_id: str,
    status: str | None = None,
    type_filter: list[str] | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    query = select(Milestone).where(Milestone.student_id == student_id)
    if status:
        query = query.where(Milestone.status == status)
    if type_filter:
        query = query.where(Milestone.type.in_(type_filter))

    result = await db.execute(query.order_by(Milestone.date.desc()).limit(limit))
    rows = list(result.scalars().all())

    return {
        "milestones": [
            {
                "milestone_id": item.milestone_id,
                "type": item.type,
                "title": item.title,
                "date": _to_jsonable(item.date),
                "score": _to_jsonable(item.score),
                "score_label": item.score_label,
                "mentor_approved": item.mentor_approved,
                "auth_score": item.auth_score,
                "notes": item.notes,
                "status": item.status,
                "contributor_type": item.contributor_type,
                "ai_summary": _to_jsonable(item.ai_summary),
            }
            for item in rows
        ]
    }


async def get_conversation_history(
    *,
    db: AsyncSession,
    parent_id: int,
    student_id: str,
    limit: int = 20,
) -> dict[str, Any]:
    result = await db.execute(
        select(Conversation)
        .where(
            and_(
                Conversation.parent_id == parent_id,
                Conversation.student_id == student_id,
                or_(Conversation.expires_at.is_(None), Conversation.expires_at > func.now()),
            )
        )
        .order_by(Conversation.timestamp.desc())
        .limit(limit)
    )
    rows = list(result.scalars().all())

    messages: list[dict[str, str]] = []
    for conv in reversed(rows):
        messages.append({"role": "user", "content": conv.question})
        messages.append({"role": "assistant", "content": conv.ai_response})

    return {
        "messages": messages,
        "total": len(messages),
        "has_escalated": any(bool(item.escalated) for item in rows),
    }


async def search_courses(
    *,
    db: AsyncSession,
    student_id: str,
    skill: str | None = None,
    program: str | None = None,
    course_type: str | None = None,
) -> dict[str, Any]:
    profile_result = await db.execute(select(Student).where(Student.student_id == student_id))
    student = profile_result.scalar_one_or_none()
    if student and student.upsell_cooldown and student.upsell_cooldown > date.today():
        return {"blocked": True, "courses": []}

    query = select(Course).where(Course.is_active.is_(True))
    if skill:
        query = query.where(Course.target_skills.contains([skill]))
    if program:
        query = query.where(Course.suitable_for.contains([program]))
    if course_type:
        query = query.where(Course.type == course_type)

    result = await db.execute(
        query.order_by(Course.is_featured.desc(), Course.display_order.asc()).limit(3)
    )
    rows = list(result.scalars().all())

    return {
        "blocked": False,
        "courses": [
            {
                "course_id": row.course_id,
                "name": row.name,
                "type": row.type,
                "program": row.program,
                "description": row.description,
                "target_skills": _to_jsonable(row.target_skills),
                "suitable_for": _to_jsonable(row.suitable_for),
                "price_vnd": row.price_vnd,
                "start_date": _to_jsonable(row.start_date),
                "end_date": _to_jsonable(row.end_date),
                "duration_days": row.duration_days,
                "location": row.location,
                "season": row.season,
                "cta_url": row.cta_url,
                "cta_label": row.cta_label,
                "is_featured": row.is_featured,
            }
            for row in rows
        ],
    }


async def get_school_info(*, db: AsyncSession, school_names: list[str]) -> dict[str, Any]:
    if not school_names:
        return {"schools": []}

    exact_query = select(School).where(School.data["name"].astext.in_(school_names))
    result = await db.execute(exact_query)
    rows = list(result.scalars().all())

    if not rows:
        like_clauses = [School.data["name"].astext.ilike(f"%{name}%") for name in school_names]
        fuzzy_result = await db.execute(select(School).where(or_(*like_clauses)))
        rows = list(fuzzy_result.scalars().all())

    return {
        "schools": [
            {
                "school_id": row.school_id,
                "data": _to_jsonable(row.data),
            }
            for row in rows
        ]
    }


async def get_weekly_digest(*, db: AsyncSession, student_id: str) -> dict[str, Any]:
    profile = await get_student_profile(db=db, student_id=student_id)
    behavior = await get_behavioral_logs(db=db, student_id=student_id, days=7)
    milestones = await get_milestones(db=db, student_id=student_id, limit=20)

    weekly_milestones = milestones["milestones"]
    digest = {
        "progress_pct": profile.get("progress_pct"),
        "next_deadline": profile.get("next_deadline"),
        "next_deadline_label": profile.get("next_deadline_label"),
        "days_left": profile.get("days_left"),
        "priority_action": profile.get("priority_action"),
        "weakest_skill": profile.get("weakest_skill"),
    }

    return {
        "period": "last_7_days",
        "behavioral": {
            "studied_days": behavior["summary"]["studied_days"],
            "total_duration_min": sum(int(item.get("duration_min") or 0) for item in behavior["logs"]),
            "avg_duration_min": behavior["summary"]["avg_duration_min"],
            "late_night_count": behavior["summary"]["late_night_count"],
            "current_streak": profile.get("current_streak"),
        },
        "milestones_this_week": weekly_milestones,
        "digest": digest,
    }


async def get_progress_summary(*, db: AsyncSession, student_id: str) -> dict[str, Any]:
    profile = await get_student_profile(db=db, student_id=student_id)

    ielts_result = await db.execute(
        select(Milestone)
        .where(and_(Milestone.student_id == student_id, Milestone.type == "ielts_mock"))
        .order_by(Milestone.date.asc())
    )
    sat_result = await db.execute(
        select(Milestone)
        .where(and_(Milestone.student_id == student_id, Milestone.type == "sat_mock"))
        .order_by(Milestone.date.asc())
    )

    ielts_rows = list(ielts_result.scalars().all())
    sat_rows = list(sat_result.scalars().all())

    def _avg_improvement(rows: list[Milestone]) -> float:
        scores = [float(item.score) for item in rows if item.score is not None]
        if len(scores) < 2:
            return 0.0
        return round((scores[-1] - scores[0]) / len(scores), 2)

    return {
        "progress_pct": profile.get("progress_pct"),
        "milestones_done": profile.get("milestones_done"),
        "months_enrolled": profile.get("months_enrolled"),
        "days_left_to_deadline": profile.get("days_left"),
        "priority_action": profile.get("priority_action"),
        "ielts_trajectory": [
            {"date": _to_jsonable(item.date), "score": _to_jsonable(item.score)}
            for item in ielts_rows
        ],
        "sat_trajectory": [
            {"date": _to_jsonable(item.date), "score": _to_jsonable(item.score)}
            for item in sat_rows
        ],
        "ielts_avg_improvement_per_attempt": _avg_improvement(ielts_rows),
        "sat_avg_improvement_per_attempt": _avg_improvement(sat_rows),
    }


def chitchat(query: str) -> dict[str, Any]:
    return {
        "type": "chitchat",
        "query": query,
        "instruction": "Tra loi tu kien thuc tong quat, khong can truy van DB.",
    }


async def web_search(query: str, count: int = 3) -> dict[str, Any]:
    api_key = settings.BRAVE_SEARCH_API_KEY
    if not api_key:
        return {
            "query": query,
            "results": [],
            "error": "BRAVE_SEARCH_API_KEY is not configured",
        }

    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key,
    }
    params = {
        "q": query,
        "count": max(1, min(count, 10)),
        "search_lang": "vi",
        "country": "VN",
        "text_decorations": False,
        "spellcheck": True,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            if response.status_code == 422:
                # Some Brave plans/regions reject certain locale combinations.
                fallback_params = {
                    **params,
                    "search_lang": "en",
                    "country": "US",
                }
                response = await client.get(url, headers=headers, params=fallback_params)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as exc:
            return {
                "query": query,
                "results": [],
                "error": f"Brave API HTTP {exc.response.status_code}",
            }
        except httpx.HTTPError as exc:
            return {
                "query": query,
                "results": [],
                "error": f"Brave API request failed: {exc}",
            }

    results: list[dict[str, Any]] = []
    for item in data.get("web", {}).get("results", []):
        results.append(
            {
                "title": item.get("title"),
                "url": item.get("url"),
                "description": item.get("description"),
            }
        )

    return {
        "query": query,
        "results": results,
    }


async def escalate(*, db: AsyncSession, parent_id: int, student_id: str, reason: str) -> dict[str, Any]:
    result = await db.execute(
        select(Conversation)
        .where(
            and_(
                Conversation.parent_id == parent_id,
                Conversation.student_id == student_id,
            )
        )
        .order_by(Conversation.timestamp.desc())
        .limit(1)
    )
    latest = result.scalar_one_or_none()

    if latest is not None:
        latest.escalated = True
        latest.escalator_note = reason
        await db.commit()

    return {
        "escalated": True,
        "reason": reason,
        "message_to_parent": "Cau hoi nay can tu van vien ETEST ho tro truc tiep de dam bao thong tin chinh xac.",
    }


TOOL_REGISTRY = {
    "get_student_profile": get_student_profile,
    "get_mentor_info": get_mentor_info,
    "get_behavioral_logs": get_behavioral_logs,
    "get_milestones": get_milestones,
    "get_conversation_history": get_conversation_history,
    "search_courses": search_courses,
    "get_school_info": get_school_info,
    "get_weekly_digest": get_weekly_digest,
    "get_progress_summary": get_progress_summary,
    "chitchat": chitchat,
    "web_search": web_search,
    "escalate": escalate,
}


@tool("get_student_profile")
async def get_student_profile_tool(student_id: str) -> dict[str, Any]:
    """Get the student profile by student_id."""
    ctx = _require_runtime_context()
    return await get_student_profile(db=ctx.db, student_id=student_id)


@tool("get_mentor_info")
async def get_mentor_info_tool(student_id: str) -> dict[str, Any]:
    """Get mentor information and latest approved milestone."""
    ctx = _require_runtime_context()
    return await get_mentor_info(db=ctx.db, student_id=student_id)


@tool("get_behavioral_logs")
async def get_behavioral_logs_tool(student_id: str, days: int = 14) -> dict[str, Any]:
    """Get behavioral logs and summary statistics for a student."""
    ctx = _require_runtime_context()
    return await get_behavioral_logs(db=ctx.db, student_id=student_id, days=days)


@tool("get_milestones")
async def get_milestones_tool(
    student_id: str,
    status: str | None = None,
    type_filter: list[str] | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """Get milestone rows with optional status/type filters."""
    ctx = _require_runtime_context()
    return await get_milestones(
        db=ctx.db,
        student_id=student_id,
        status=status,
        type_filter=type_filter,
        limit=limit,
    )


@tool("get_conversation_history")
async def get_conversation_history_tool(student_id: str, limit: int = 20) -> dict[str, Any]:
    """Get recent parent-assistant conversation history for a student."""
    ctx = _require_runtime_context()
    return await get_conversation_history(
        db=ctx.db,
        parent_id=ctx.parent_id,
        student_id=student_id,
        limit=limit,
    )


@tool("search_courses")
async def search_courses_tool(
    student_id: str,
    skill: str | None = None,
    program: str | None = None,
    course_type: str | None = None,
) -> dict[str, Any]:
    """Search active courses by skill/program/type filters."""
    ctx = _require_runtime_context()
    return await search_courses(
        db=ctx.db,
        student_id=student_id,
        skill=skill,
        program=program,
        course_type=course_type,
    )


@tool("get_school_info")
async def get_school_info_tool(school_names: list[str]) -> dict[str, Any]:
    """Get school metadata matched by school names."""
    ctx = _require_runtime_context()
    return await get_school_info(db=ctx.db, school_names=school_names)


@tool("get_weekly_digest")
async def get_weekly_digest_tool(student_id: str) -> dict[str, Any]:
    """Get an aggregated weekly digest for a student."""
    ctx = _require_runtime_context()
    return await get_weekly_digest(db=ctx.db, student_id=student_id)


@tool("get_progress_summary")
async def get_progress_summary_tool(student_id: str) -> dict[str, Any]:
    """Get longitudinal progress summary and score trajectories."""
    ctx = _require_runtime_context()
    return await get_progress_summary(db=ctx.db, student_id=student_id)


@tool("chitchat")
def chitchat_tool(query: str) -> dict[str, Any]:
    """Signal that the question can be answered without DB tools."""
    return chitchat(query)


@tool("web_search")
async def web_search_tool(query: str, count: int = 3) -> dict[str, Any]:
    """Perform Brave web search for realtime information."""
    return await web_search(query=query, count=count)


@tool("escalate")
async def escalate_tool(student_id: str, reason: str) -> dict[str, Any]:
    """Escalate latest conversation for human consultant follow-up."""
    ctx = _require_runtime_context()
    return await escalate(
        db=ctx.db,
        parent_id=ctx.parent_id,
        student_id=student_id,
        reason=reason,
    )


LANGGRAPH_TOOLS = {
    "get_student_profile": get_student_profile_tool,
    "get_mentor_info": get_mentor_info_tool,
    "get_behavioral_logs": get_behavioral_logs_tool,
    "get_milestones": get_milestones_tool,
    "get_conversation_history": get_conversation_history_tool,
    "search_courses": search_courses_tool,
    "get_school_info": get_school_info_tool,
    "get_weekly_digest": get_weekly_digest_tool,
    "get_progress_summary": get_progress_summary_tool,
    "chitchat": chitchat_tool,
    "web_search": web_search_tool,
    "escalate": escalate_tool,
}
