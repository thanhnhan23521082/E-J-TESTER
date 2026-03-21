"""seed demo data

Revision ID: 003
Revises: 002
Create Date: 2026-03-21

Seed data cho demo Nguyen Ha Minh Anh.
All INSERT uses ON CONFLICT (PK) DO UPDATE for idempotency.
"""

import json as _json

from alembic import op

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # pylint: disable=line-too-long

    # 1. Mentor
    op.execute("""
        INSERT INTO mentors
            (mentor_id, email, hashed_password, full_name, specialty,
             programs, max_students, active_students)
        VALUES (
            1,
            'co-lan@etest.edu.vn',
            '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfZ3ZZZZ',
            'Co Lan',
            'IELTS Writing, SAT Math, AMP Academic',
            '["AMP","IELTS","SAT"]'::jsonb,
            10, 1
        )
        ON CONFLICT (mentor_id) DO UPDATE SET
            full_name = EXCLUDED.full_name,
            specialty = EXCLUDED.specialty,
            programs = EXCLUDED.programs;
    """)

    # 2. Parent
    op.execute("""
        INSERT INTO parents
            (parent_id, email, hashed_password, full_name, phone, student_id)
        VALUES (
            1,
            'co-thu@example.com',
            '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfZ3ZZZZ',
            'Co Thu',
            '+84 90x xxx 1234',
            'STU_001'
        )
        ON CONFLICT (parent_id) DO UPDATE SET
            full_name = EXCLUDED.full_name,
            student_id = EXCLUDED.student_id;
    """)

    # 3. Student
    op.execute("""
        INSERT INTO students
            (student_id, name, ielts_score, sat_score, gpa,
             skill_breakdown, target_schools,
             program, months_enrolled,
             parent_id, mentor_id,
             progress_pct, milestones_done,
             next_deadline, next_deadline_label, days_left, priority_action,
             current_streak, last_activity_date, weakest_skill)
        VALUES (
            'STU_001',
            'Nguyen Ha Minh Anh',
            6.5, 1320.0, 8.4,
            '{\"listening\": 7.0, \"reading\": 7.0, \"writing\": 5.5, \"speaking\": 6.5}'::jsonb,
            '[\"University of Melbourne\", \"UNSW Sydney\", \"Monash University\"]'::jsonb,
            'AMP', 14,
            1, 1,
            80, 12,
            '2026-04-20'::date,
            'Personal Statement Final v2 (Melbourne)',
            30,
            'Hoan thanh: Personal Statement Final v2 (Melbourne)',
            3, '2026-03-20'::date,
            'writing'
        )
        ON CONFLICT (student_id) DO UPDATE SET
            ielts_score = EXCLUDED.ielts_score,
            sat_score = EXCLUDED.sat_score,
            progress_pct = EXCLUDED.progress_pct,
            milestones_done = EXCLUDED.milestones_done,
            next_deadline = EXCLUDED.next_deadline,
            next_deadline_label = EXCLUDED.next_deadline_label,
            days_left = EXCLUDED.days_left,
            priority_action = EXCLUDED.priority_action,
            current_streak = EXCLUDED.current_streak,
            last_activity_date = EXCLUDED.last_activity_date,
            weakest_skill = EXCLUDED.weakest_skill;
    """)

    # 4. Behavioral Logs (14 rows)
    # pylint: disable=line-too-long
    _logs = [
        ("2026-03-08", 60,  "20:00", "21:00", True,  6, 0.0, ["reading"]),
        ("2026-03-09", 75,  "19:30", "20:45", True,  7, 0.0, ["writing_task2"]),
        ("2026-03-10", 110, "20:00", "21:50", True,  8, 0.0, ["ielts_mock", "essay_review"]),
        ("2026-03-11", 80,  "19:45", "21:05", True,  1, 0.0, ["speaking_mock"]),
        ("2026-03-12", 95,  "21:00", "22:35", True,  2, 0.0, ["sat_math"]),
        ("2026-03-13", 70,  "20:30", "21:40", True,  3, 0.0, ["vocabulary"]),
        ("2026-03-14", 85,  "19:00", "20:25", True,  4, 0.0, ["reading_comprehension"]),
        ("2026-03-15", 90,  "20:15", "21:45", True,  5, 0.0, ["writing_task1"]),
        ("2026-03-16", 60,  "19:30", "20:30", True,  6, 0.0, ["listening"]),
        ("2026-03-17", 80,  "20:00", "21:20", True,  7, 0.0, ["speaking_practice"]),
        # late nights (Mar 18-20)
        ("2026-03-18", 100, "22:30", "00:10", True,  8, 0.5, ["sat_math", "reading"]),
        ("2026-03-19",  95, "23:40", "01:15", True,  1, 0.0, ["ielts_practice"]),
        ("2026-03-20", 110, "23:15", "01:05", True,  2, 0.0, ["ielts_mock", "essay_draft"]),
        # today
        ("2026-03-21",  75, "21:00", "22:15", True,  3, 0.0, ["essay_draft"]),
    ]
    for log_date, dur, start, end, studied, streak, delta, activities in _logs:
        studied_sql = "TRUE" if studied else "FALSE"
        op.execute("""
            INSERT INTO behavioral_logs
                (student_id, date, duration_min, session_start, session_end,
                 studied, streak_day, score_delta, activities)
            VALUES (
                'STU_001',
                '%s'::date,
                %d,
                '%s'::time,
                '%s'::time,
                %s,
                %d,
                %f,
                '%s'::jsonb
            )
            ON CONFLICT (student_id, date) DO UPDATE SET
                duration_min  = EXCLUDED.duration_min,
                session_start = EXCLUDED.session_start,
                session_end   = EXCLUDED.session_end,
                studied       = EXCLUDED.studied,
                streak_day    = EXCLUDED.streak_day,
                score_delta   = EXCLUDED.score_delta,
                activities    = EXCLUDED.activities;
        """ % (log_date, dur, start, end, studied_sql, streak, delta,
               _json.dumps(activities)))

    # 5. Milestones (12 completed + 3 upcoming)
    _ms = [
        # completed
        ("ms_001","ielts_mock",       "IELTS Mock #1 - Overall 5.5",
         "2024-10-15", "5.5",  "IELTS Band 5.5", 1, True,  None,  None,  "completed", "student"),
        ("ms_002","essay_draft",       "Personal Statement Draft #1",
         "2024-11-20", None,    "Draft",           1, False, "82",   None,  "completed", "student"),
        ("ms_003","ielts_mock",       "IELTS Mock #2 - Overall 6.0",
         "2024-12-10", "6.0",   "IELTS Band 6.0", 1, True,  None,  None,  "completed", "student"),
        ("ms_004","essay_final",       "Personal Statement Final v1",
         "2025-01-15", None,    "Final",           1, True,  "88",  "Minh Anh the hien ro giong van ca nhan.", "completed", "student"),
        ("ms_005","sat_mock",         "SAT Mock #1",
         "2025-02-20", "1250",  "SAT 1250",       1, True,  None,  None,  "completed", "student"),
        ("ms_006","extracurricular",  "ETEST CSR - Day tieng Anh tre em",
         "2025-03-10", None,    "Hoat dong",       1, True,  None,  "Tham gia tich duc duoc ph huynh ghi nhan.", "completed", "student"),
        ("ms_007","consultation",     "Tu van lo trinh AMP",
         "2025-03-25", None,    "Consultation",     1, True,  None,  "Co Thu tham du cung con.", "completed", "parent"),
        ("ms_008","sat_mock",         "SAT Mock #2 - 1320",
         "2025-05-05", "1320",  "SAT 1320",       1, True,  None,  "Dat target SAT!", "completed", "student"),
        ("ms_009","ielts_mock",       "IELTS Mock #3 - Overall 6.5",
         "2025-06-15", "6.5",   "IELTS Band 6.5", 1, True,  None,  "Dat target IELTS.", "completed", "student"),
        ("ms_010","camp",            "ETEST Summer Camp - Academic Writing",
         "2025-07-10", None,    "Trai he",          1, True,  None,  "Cai thien Writing 0.5 band sau trai he.", "completed", "student"),
        ("ms_011","essay_draft",      "Supplemental Essay Draft",
         "2025-09-01", None,    "Draft",           1, False, "85",  "Essay bo sung cho Monash.", "completed", "student"),
        ("ms_012","target_achieved",  "Dat IELTS 6.5 + SAT 1320",
         "2025-09-05", None,    "Milestone",        1, True,  None,  "Hai target chinh hoan thanh truoc deadline.", "completed", "student"),
        # upcoming
        ("ms_013","essay_final",      "Personal Statement Final v2 (Melbourne)",
         "2026-04-20", None,    "Final",           1, False, None, None,          "upcoming",  "student"),
        ("ms_014","ielts_mock",      "IELTS Mock #4 - target 7.0",
         "2026-04-30", None,    "IELTS Band 7.0",  1, False, None, None,          "upcoming",  "student"),
        ("ms_015","consultation",     "Nop ho so Early Action",
         "2026-05-07", None,    "Early Action",     1, False, None, None,          "upcoming",  "student"),
    ]
    for ms_id, mtype, title, mdate, score, score_lbl, mid, approved, auth, notes, status, contrib in _ms:
        approved_sql = "TRUE" if approved else "FALSE"
        score_sql   = "'%s'" % score if score else "NULL"
        auth_sql    = "'%s'" % auth  if auth  else "NULL"
        notes_sql   = "'%s'" % notes.replace("'", "''") if notes else "NULL"
        op.execute("""
            INSERT INTO milestones
                (student_id, milestone_id, type, title, date, score, score_label,
                 mentor_id, mentor_approved, auth_score, notes, status, contributor_type)
            VALUES (
                'STU_001', '%s', '%s', '%s',
                '%s'::date,
                %s, '%s',
                %d, %s, %s, %s,
                '%s', '%s'
            )
            ON CONFLICT (student_id, milestone_id) DO UPDATE SET
                status = EXCLUDED.status;
        """ % (ms_id, mtype, title, mdate, score_sql, score_lbl,
               mid, approved_sql, auth_sql, notes_sql, status, contrib))

    # 6. Courses
    _courses = [
        ("ielts-writing-intensive-camp",
         "IELTS Writing Intensive Camp", "camp", "AMP", "Summer 2026",
         "Khoa hoc tap trung cai thien IELTS Writing tu 5.5 len 6.0-6.5 trong 2 tuan.",
         ["writing"], ["student_gap_writing", "student_target_6plus"],
         "https://etest.edu.vn/ielts-writing-camp", "Dang ky ngay",
         14, "2026-07-01", "2026-07-14", "TP.HCM", 8500000, True, True, 1),
        ("personal-statement-workshop",
         "Personal Statement Workshop", "workshop", "AMP", "Spring 2026",
         "Workshop 1 ngay hoan thien PS cho Melbourne va Monash.",
         ["essay", "writing"], ["student_target_melbourne", "student_target_essay"],
         "https://etest.edu.vn/ps-workshop", "Xem chi tiet",
         1, "2026-04-05", "2026-04-05", "Online", 1500000, True, True, 2),
        ("sat-math-sprint",
         "SAT Math Sprint", "course", "SAT", "All Year",
         "Khoa luyen SAT Math 8 tuan, phoi hop muon dat 1400+ SAT.",
         ["sat_math"], ["student_gap_sat", "student_target_1400"],
         "https://etest.edu.vn/sat-math-sprint", "Dang ky ngay",
         56, "2026-04-01", "2026-05-26", "TP.HCM", 12000000, False, True, 3),
        ("ielts-speaking-booster",
         "IELTS Speaking Booster", "camp", "IELTS", "Summer 2026",
         "Trai he Speaking 1 tuan luyen noi IELTS voi giao vien ban ngu.",
         ["speaking"], ["student_gap_speaking", "student_target_7plus"],
         "https://etest.edu.vn/ielts-speaking-booster", "Dang ky ngay",
         7, "2026-07-20", "2026-07-26", "TP.HCM", 5000000, False, True, 4),
    ]
    for slug, name, ctype, prog, season, desc, targets, suitable, cta_url, cta_lbl, dur, sd, ed, loc, price, feat, active, order in _courses:
        feat_sql   = "TRUE" if feat   else "FALSE"
        active_sql = "TRUE" if active else "FALSE"
        op.execute("""
            INSERT INTO courses
                (name, slug, type, program, season, description,
                 target_skills, suitable_for,
                 cta_url, cta_label,
                 duration_days, start_date, end_date, location, price_vnd,
                 is_featured, is_active, display_order)
            VALUES (
                '%s', '%s', '%s', '%s', '%s', '%s',
                '%s'::jsonb, '%s'::jsonb,
                '%s', '%s',
                %d, '%s'::date, '%s'::date, '%s', %d,
                %s, %s, %d
            )
            ON CONFLICT (slug) DO UPDATE SET
                name = EXCLUDED.name;
        """ % (name, slug, ctype, prog, season, desc,
               _json.dumps(targets), _json.dumps(suitable),
               cta_url, cta_lbl,
               dur, sd, ed, loc, price,
               feat_sql, active_sql, order))


def downgrade() -> None:
    op.execute("DELETE FROM courses WHERE slug IN "
               "('ielts-writing-intensive-camp','personal-statement-workshop',"
               "'sat-math-sprint','ielts-speaking-booster');")
    op.execute("DELETE FROM conversations WHERE parent_id = 1 AND student_id = 'STU_001';")
    op.execute("DELETE FROM milestones WHERE student_id = 'STU_001';")
    op.execute("DELETE FROM behavioral_logs WHERE student_id = 'STU_001';")
    op.execute("DELETE FROM students WHERE student_id = 'STU_001';")
    op.execute("DELETE FROM parents WHERE parent_id = 1;")
    op.execute("DELETE FROM mentors WHERE mentor_id = 1;")
