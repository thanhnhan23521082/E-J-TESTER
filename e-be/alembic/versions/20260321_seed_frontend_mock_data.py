"""seed frontend mock data from alembic data files

Revision ID: 20260321_seed_frontend_mock_data
Revises: 5d52fa0c6c5d
Create Date: 2026-03-21 23:05:00

This migration seeds backend tables from JSON files stored in:
    e-be/alembic/data/
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import date, time
from pathlib import Path
from typing import Any, Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, insert as pg_insert

# revision identifiers, used by Alembic.
revision: str = "20260321_seed_frontend_mock_data"
down_revision: Union[str, Sequence[str], None] = "5d52fa0c6c5d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


users_table = sa.table(
    "users",
    sa.column("email", sa.String(length=255)),
    sa.column("hashed_password", sa.String(length=255)),
    sa.column("role", sa.String(length=50)),
)

mentors_table = sa.table(
    "mentors",
    sa.column("mentor_id", sa.Integer()),
    sa.column("email", sa.String(length=255)),
    sa.column("hashed_password", sa.String(length=255)),
    sa.column("full_name", sa.String(length=255)),
    sa.column("specialty", sa.String(length=255)),
    sa.column("bio", sa.Text()),
    sa.column("avatar_url", sa.String(length=500)),
    sa.column("programs", JSONB),
    sa.column("max_students", sa.Integer()),
    sa.column("active_students", sa.Integer()),
)

parents_table = sa.table(
    "parents",
    sa.column("parent_id", sa.Integer()),
    sa.column("email", sa.String(length=255)),
    sa.column("hashed_password", sa.String(length=255)),
    sa.column("full_name", sa.String(length=255)),
    sa.column("phone", sa.String(length=50)),
    sa.column("telegram_id", sa.String(length=100)),
    sa.column("student_id", sa.String(length=50)),
)

students_table = sa.table(
    "students",
    sa.column("student_id", sa.String(length=50)),
    sa.column("name", sa.String(length=255)),
    sa.column("ielts_score", sa.Numeric(4, 1)),
    sa.column("sat_score", sa.Numeric(6, 2)),
    sa.column("gpa", sa.Numeric(4, 2)),
    sa.column("skill_breakdown", JSONB),
    sa.column("target_schools", JSONB),
    sa.column("program", sa.String(length=100)),
    sa.column("months_enrolled", sa.Integer()),
    sa.column("parent_id", sa.Integer()),
    sa.column("mentor_id", sa.Integer()),
    sa.column("progress_pct", sa.Integer()),
    sa.column("milestones_done", sa.Integer()),
    sa.column("next_deadline", sa.Date()),
    sa.column("next_deadline_label", sa.String(length=255)),
    sa.column("days_left", sa.Integer()),
    sa.column("priority_action", sa.String(length=255)),
    sa.column("current_streak", sa.Integer()),
    sa.column("last_activity_date", sa.Date()),
    sa.column("weakest_skill", sa.String(length=50)),
    sa.column("upsell_cooldown", sa.Date()),
)

behavioral_logs_table = sa.table(
    "behavioral_logs",
    sa.column("student_id", sa.String(length=50)),
    sa.column("date", sa.Date()),
    sa.column("duration_min", sa.Integer()),
    sa.column("session_start", sa.Time()),
    sa.column("session_end", sa.Time()),
    sa.column("studied", sa.Boolean()),
    sa.column("streak_day", sa.Integer()),
    sa.column("score_delta", sa.Numeric(4, 1)),
    sa.column("activities", JSONB),
    sa.column("mood_note", sa.Text()),
)

milestones_table = sa.table(
    "milestones",
    sa.column("id", sa.Integer()),
    sa.column("student_id", sa.String(length=50)),
    sa.column("milestone_id", sa.String(length=100)),
    sa.column("type", sa.String(length=50)),
    sa.column("title", sa.String(length=255)),
    sa.column("date", sa.Date()),
    sa.column("score", sa.Numeric(6, 2)),
    sa.column("score_label", sa.String(length=100)),
    sa.column("mentor_id", sa.Integer()),
    sa.column("mentor_approved", sa.Boolean()),
    sa.column("auth_score", sa.Integer()),
    sa.column("notes", sa.Text()),
    sa.column("status", sa.String(length=20)),
    sa.column("contributor_type", sa.String(length=50)),
    sa.column("ai_summary", JSONB),
)

schools_table = sa.table(
    "schools",
    sa.column("school_id", sa.Integer()),
    sa.column("data", JSONB),
)

courses_table = sa.table(
    "courses",
    sa.column("name", sa.String(length=255)),
    sa.column("slug", sa.String(length=255)),
    sa.column("type", sa.String(length=50)),
    sa.column("program", sa.String(length=100)),
    sa.column("season", sa.String(length=50)),
    sa.column("description", sa.Text()),
    sa.column("target_skills", JSONB),
    sa.column("suitable_for", JSONB),
    sa.column("cta_url", sa.String(length=500)),
    sa.column("cta_label", sa.String(length=100)),
    sa.column("duration_days", sa.Integer()),
    sa.column("start_date", sa.Date()),
    sa.column("end_date", sa.Date()),
    sa.column("location", sa.String(length=255)),
    sa.column("price_vnd", sa.BigInteger()),
    sa.column("is_featured", sa.Boolean()),
    sa.column("is_active", sa.Boolean()),
    sa.column("display_order", sa.Integer()),
)


def _load_json(filename: str) -> Any:
    return json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))


def _load_seed_bundle() -> dict[str, Any]:
    return {
        "students": _load_json("students.json"),
        "mentors": _load_json("mentors.json"),
        "parents": _load_json("parents.json"),
        "digests": _load_json("digests.json"),
        "wellbeing_alerts": _load_json("wellbeing_alerts.json"),
        "etester_profiles": _load_json("etester_profiles.json"),
        "milestones": _load_json("milestones.json"),
        "courses": _load_json("courses.json"),
        "behavioral_logs": _load_json("behavioral_logs.json"),
    }


def _upsert_rows(
    connection: sa.Connection,
    table: sa.Table,
    rows: list[dict[str, Any]],
    index_elements: list[str],
    update_columns: list[str],
) -> None:
    if not rows:
        return

    conflict_columns = [table.c[column_name] for column_name in index_elements]
    stmt = pg_insert(table).values(rows)
    connection.execute(
        stmt.on_conflict_do_update(
            index_elements=conflict_columns,
            set_={
                column_name: getattr(stmt.excluded, column_name)
                for column_name in update_columns
            },
        )
    )


def _upsert_milestone(connection: sa.Connection, payload: dict[str, Any]) -> None:
    existing_id = connection.execute(
        sa.select(milestones_table.c.id).where(
            sa.and_(
                milestones_table.c.student_id == payload["student_id"],
                milestones_table.c.milestone_id == payload["milestone_id"],
            )
        )
    ).scalar_one_or_none()

    if existing_id is None:
        connection.execute(sa.insert(milestones_table).values(**payload))
        return

    connection.execute(
        sa.update(milestones_table).where(milestones_table.c.id == existing_id).values(**payload)
    )


def _upsert_school(connection: sa.Connection, payload: dict[str, Any]) -> None:
    existing_id = connection.execute(
        sa.select(schools_table.c.school_id).where(
            schools_table.c.data.op("->>")("name") == payload["data"]["name"]
        )
    ).scalar_one_or_none()

    if existing_id is None:
        connection.execute(sa.insert(schools_table).values(**payload))
        return

    connection.execute(
        sa.update(schools_table).where(schools_table.c.school_id == existing_id).values(**payload)
    )


def _set_sequence_to_max(connection: sa.Connection, table_name: str, column_name: str) -> None:
    connection.execute(
        sa.text(
            f"""
            DO $$
            BEGIN
                IF pg_get_serial_sequence('{table_name}', '{column_name}') IS NOT NULL THEN
                    PERFORM setval(
                        pg_get_serial_sequence('{table_name}', '{column_name}'),
                        COALESCE((SELECT MAX({column_name}) FROM {table_name}), 1),
                        TRUE
                    );
                END IF;
            END $$;
            """
        )
    )


def _group_by(items: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        grouped[item[key]].append(item)
    return dict(grouped)


def upgrade() -> None:
    """Seed backend tables from JSON files under alembic/data."""
    connection = op.get_bind()
    seed = _load_seed_bundle()

    students = seed["students"]
    mentors = seed["mentors"]
    parents = seed["parents"]
    digests = {item["studentId"]: item for item in seed["digests"]}
    wellbeing_alerts = {item["studentId"]: item for item in seed["wellbeing_alerts"]}
    etester_profiles = {item["studentId"]: item for item in seed["etester_profiles"]}
    milestones = seed["milestones"]
    courses = seed["courses"]
    behavioral_logs = seed["behavioral_logs"]

    mentors_by_id = {item["id"]: item for item in mentors}
    parents_by_id = {item["id"]: item for item in parents}
    logs_by_student = _group_by(behavioral_logs, "studentId")

    _upsert_rows(
        connection,
        users_table,
        [
            {
                "email": mentor["email"],
                "hashed_password": mentor["passwordHash"],
                "role": "mentor",
            }
            for mentor in mentors
        ]
        + [
            {
                "email": parent["email"],
                "hashed_password": parent["passwordHash"],
                "role": "parent",
            }
            for parent in parents
        ],
        index_elements=["email"],
        update_columns=["hashed_password", "role"],
    )

    _upsert_rows(
        connection,
        mentors_table,
        [
            {
                "mentor_id": mentor["dbId"],
                "email": mentor["email"],
                "hashed_password": mentor["passwordHash"],
                "full_name": mentor["name"],
                "specialty": mentor.get("specialty"),
                "bio": mentor.get("bio"),
                "avatar_url": mentor.get("avatarUrl"),
                "programs": mentor.get("programs", []),
                "max_students": mentor.get("maxStudents", max(1, len(mentor.get("studentIds", [])))),
                "active_students": mentor.get("activeStudents", len(mentor.get("studentIds", []))),
            }
            for mentor in mentors
        ],
        index_elements=["mentor_id"],
        update_columns=[
            "email",
            "hashed_password",
            "full_name",
            "specialty",
            "bio",
            "avatar_url",
            "programs",
            "max_students",
            "active_students",
        ],
    )

    _upsert_rows(
        connection,
        parents_table,
        [
            {
                "parent_id": parent["dbId"],
                "email": parent["email"],
                "hashed_password": parent["passwordHash"],
                "full_name": parent["name"],
                "phone": parent.get("phone"),
                "telegram_id": parent.get("telegramId"),
                "student_id": parent["studentId"],
            }
            for parent in parents
        ],
        index_elements=["parent_id"],
        update_columns=[
            "email",
            "hashed_password",
            "full_name",
            "phone",
            "telegram_id",
            "student_id",
        ],
    )

    _upsert_rows(
        connection,
        students_table,
        [
            {
                "student_id": student["id"],
                "name": student["name"],
                "ielts_score": student.get("ieltsScore"),
                "sat_score": student.get("satScore"),
                "gpa": student.get("gpa"),
                "skill_breakdown": student.get("skillBreakdown"),
                "target_schools": student.get("targetSchools"),
                "program": student.get("program"),
                "months_enrolled": student.get("monthsEnrolled", 0),
                "parent_id": parents_by_id[student["parentId"]]["dbId"],
                "mentor_id": mentors_by_id[student["mentorId"]]["dbId"],
                "progress_pct": digests[student["id"]]["progressPct"],
                "milestones_done": digests[student["id"]]["milestonesCompleted"],
                "next_deadline": date.fromisoformat(digests[student["id"]]["nextDeadlineDate"]),
                "next_deadline_label": digests[student["id"]]["nextDeadlineLabel"],
                "days_left": digests[student["id"]]["daysLeft"],
                "priority_action": digests[student["id"]]["priorityAction"],
                "current_streak": sorted(
                    logs_by_student.get(student["id"], []),
                    key=lambda item: item["date"],
                )[-1]["streakDay"],
                "last_activity_date": date.fromisoformat(
                    etester_profiles[student["id"]]["lastUpdated"][:10]
                ),
                "weakest_skill": digests[student["id"]]["weakestSkill"],
                "upsell_cooldown": (
                    date.fromisoformat(student["upsellCooldown"])
                    if student.get("upsellCooldown")
                    else None
                ),
            }
            for student in students
        ],
        index_elements=["student_id"],
        update_columns=[
            "name",
            "ielts_score",
            "sat_score",
            "gpa",
            "skill_breakdown",
            "target_schools",
            "program",
            "months_enrolled",
            "parent_id",
            "mentor_id",
            "progress_pct",
            "milestones_done",
            "next_deadline",
            "next_deadline_label",
            "days_left",
            "priority_action",
            "current_streak",
            "last_activity_date",
            "weakest_skill",
            "upsell_cooldown",
        ],
    )

    _upsert_rows(
        connection,
        behavioral_logs_table,
        [
            {
                "student_id": row["studentId"],
                "date": date.fromisoformat(row["date"]),
                "duration_min": row["durationMin"],
                "session_start": time.fromisoformat(row["sessionStart"]) if row.get("sessionStart") else None,
                "session_end": time.fromisoformat(row["sessionEnd"]) if row.get("sessionEnd") else None,
                "studied": row["studied"],
                "streak_day": row["streakDay"],
                "score_delta": row["scoreDelta"],
                "activities": row["activities"],
                "mood_note": row.get(
                    "moodNote",
                    (
                        f"{wellbeing_alerts[row['studentId']]['severity']}: "
                        f"{wellbeing_alerts[row['studentId']]['message']} | "
                        f"{wellbeing_alerts[row['studentId']]['action']}"
                    ),
                ),
            }
            for row in behavioral_logs
        ],
        index_elements=["student_id", "date"],
        update_columns=[
            "duration_min",
            "session_start",
            "session_end",
            "studied",
            "streak_day",
            "score_delta",
            "activities",
            "mood_note",
        ],
    )

    seeded_school_names: set[str] = set()
    for student in students:
        for school in student.get("targetSchools", []):
            if school["name"] in seeded_school_names:
                continue
            seeded_school_names.add(school["name"])
            _upsert_school(
                connection,
                {
                    "data": {
                        **school,
                        "source": "alembic_mock",
                    }
                },
            )

    for milestone in milestones:
        _upsert_milestone(
            connection,
            {
                "student_id": milestone["studentId"],
                "milestone_id": milestone["id"],
                "type": milestone["type"],
                "title": milestone["title"],
                "date": date.fromisoformat(milestone["date"]),
                "score": milestone.get("score"),
                "score_label": milestone.get("scoreLabel") or None,
                "mentor_id": (
                    mentors_by_id[milestone["mentorId"]]["dbId"]
                    if milestone.get("mentorId")
                    else None
                ),
                "mentor_approved": milestone.get("mentorApproved"),
                "auth_score": milestone.get("authScore"),
                "notes": milestone.get("notes"),
                "status": milestone["status"],
                "contributor_type": milestone["contributorType"],
                "ai_summary": milestone.get("aiSummary"),
            },
        )

    _upsert_rows(
        connection,
        courses_table,
        [
            {
                "name": course["courseName"],
                "slug": course["slug"],
                "type": course["type"],
                "program": course["program"],
                "season": course.get("season", "2026"),
                "description": course["reason"],
                "target_skills": course.get("targetSkills", []),
                "suitable_for": course.get("suitableFor", []),
                "cta_url": course["ctaUrl"],
                "cta_label": course.get("ctaLabel", "Xem chi tiết"),
                "duration_days": course.get("durationDays"),
                "start_date": date.fromisoformat(course["startDate"]) if course.get("startDate") else None,
                "end_date": date.fromisoformat(course["endDate"]) if course.get("endDate") else None,
                "location": course.get("location"),
                "price_vnd": course.get("priceVnd"),
                "is_featured": course.get("isFeatured", False),
                "is_active": course.get("isActive", True),
                "display_order": course.get("displayOrder", 0),
            }
            for course in courses
        ],
        index_elements=["slug"],
        update_columns=[
            "name",
            "type",
            "program",
            "season",
            "description",
            "target_skills",
            "suitable_for",
            "cta_url",
            "cta_label",
            "duration_days",
            "start_date",
            "end_date",
            "location",
            "price_vnd",
            "is_featured",
            "is_active",
            "display_order",
        ],
    )

    for student in students:
        digest = digests[student["id"]]
        etester = etester_profiles[student["id"]]
        latest_log = sorted(logs_by_student.get(student["id"], []), key=lambda item: item["date"])[-1]
        connection.execute(
            sa.update(students_table)
            .where(students_table.c.student_id == student["id"])
            .values(
                progress_pct=digest["progressPct"],
                milestones_done=digest["milestonesCompleted"],
                next_deadline=date.fromisoformat(digest["nextDeadlineDate"]),
                next_deadline_label=digest["nextDeadlineLabel"],
                days_left=digest["daysLeft"],
                priority_action=digest["priorityAction"],
                weakest_skill=digest["weakestSkill"],
                current_streak=latest_log["streakDay"],
                last_activity_date=date.fromisoformat(etester["lastUpdated"][:10]),
            )
        )

    for table_name, column_name in [
        ("users", "id"),
        ("mentors", "mentor_id"),
        ("parents", "parent_id"),
        ("behavioral_logs", "id"),
        ("milestones", "id"),
        ("schools", "school_id"),
        ("courses", "course_id"),
    ]:
        _set_sequence_to_max(connection, table_name, column_name)


def downgrade() -> None:
    """Remove the rows seeded from alembic/data."""
    connection = op.get_bind()
    seed = _load_seed_bundle()

    students = seed["students"]
    mentors = seed["mentors"]
    parents = seed["parents"]
    milestones = seed["milestones"]
    courses = seed["courses"]
    behavioral_logs = seed["behavioral_logs"]
    school_names = {
        school["name"]
        for student in students
        for school in student.get("targetSchools", [])
    }

    connection.execute(
        sa.delete(courses_table).where(
            courses_table.c.slug.in_([course["slug"] for course in courses])
        )
    )
    connection.execute(
        sa.delete(schools_table).where(
            sa.and_(
                schools_table.c.data.op("->>")("source") == "alembic_mock",
                schools_table.c.data.op("->>")("name").in_(list(school_names)),
            )
        )
    )
    connection.execute(
        sa.delete(milestones_table).where(
            milestones_table.c.milestone_id.in_([milestone["id"] for milestone in milestones])
        )
    )
    connection.execute(
        sa.delete(behavioral_logs_table).where(
            sa.tuple_(
                behavioral_logs_table.c.student_id,
                behavioral_logs_table.c.date,
            ).in_(
                [
                    (row["studentId"], date.fromisoformat(row["date"]))
                    for row in behavioral_logs
                ]
            )
        )
    )
    connection.execute(
        sa.delete(students_table).where(
            students_table.c.student_id.in_([student["id"] for student in students])
        )
    )
    connection.execute(
        sa.delete(parents_table).where(
            parents_table.c.parent_id.in_([parent["dbId"] for parent in parents])
        )
    )
    connection.execute(
        sa.delete(mentors_table).where(
            mentors_table.c.mentor_id.in_([mentor["dbId"] for mentor in mentors])
        )
    )
    connection.execute(
        sa.delete(users_table).where(
            users_table.c.email.in_(
                [mentor["email"] for mentor in mentors]
                + [parent["email"] for parent in parents]
            )
        )
    )
