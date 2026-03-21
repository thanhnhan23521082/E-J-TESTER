# ETEST ONE — Smart Parenting Database

> **Scope:** Module 1 — Smart Parenting
> **Engine:** PostgreSQL
> **Migration:** Alembic (`alembic/versions/`)

---

## Entity Relationship

```
parents  ───1:1───  students  ───N:1───  mentors
   │                                    │
   │── conversations (parent → student context)
   │
   └── behavioral_logs (N:1)
   └── milestones  (N:1)
   └── courses     (lookup — upsell engine)
```

---

## Table: `parents`

Phụ huynh — actor chính của Smart Parenting.

| Field | Type | Constraints | Mô tả |
|---|---|---|---|
| `parent_id` | `SERIAL` | PK | ID tự tăng |
| `email` | `VARCHAR(255)` | `NOT NULL, UNIQUE` | Email đăng nhập |
| `hashed_password` | `VARCHAR(255)` | `NOT NULL` | Mật khẩu đã hash (bcrypt) |
| `full_name` | `VARCHAR(255)` | `NOT NULL` | Tên phụ huynh (VD: "Cô Thu") |
| `phone` | `VARCHAR(50)` | | SĐT liên hệ |
| `telegram_id` | `VARCHAR(100)` | | Telegram ID (tương lai: notify qua Telegram) |
| `student_id` | `VARCHAR(50)` | `NOT NULL, UNIQUE` | Con duy nhất của phụ huynh này |
| `created_at` | `TIMESTAMPT` | `NOT NULL, DEFAULT NOW()` | Ngày tạo |
| `updated_at` | `TIMESTAMPT` | `NOT NULL, DEFAULT NOW()` | Ngày cập nhật cuối |

**Indexes:**
- `idx_parents_student_id` on `student_id`
- `idx_parents_email` on `email`

---

## Table: `students`

Học viên — đối tượng được theo dõi.

| Field | Type | Constraints | Mô tả |
|---|---|---|---|
| `student_id` | `VARCHAR(50)` | PK | ID tự nhiên (VD: "STU_001") |
| `name` | `VARCHAR(255)` | `NOT NULL` | Tên học viên |
| `ielts_score` | `DECIMAL(4,1)` | | Điểm IELTS hiện tại (VD: 6.5) |
| `sat_score` | `DECIMAL(5,1)` | | Điểm SAT hiện tại (VD: 1320) |
| `gpa` | `DECIMAL(4,2)` | | GPA trường |
| `skill_breakdown` | `JSONB` | | Chi tiết điểm 4 kỹ năng (VD: `{"listening":7.0,"reading":7.0,"writing":5.5,"speaking":6.5}`) |
| `target_schools` | `JSONB` | | Danh sách trường đích (VD: `["University of Melbourne","UNSW"]`) |
| `program` | `VARCHAR(100)` | | Chương trình: "AMP", "IELTS", "SAT" |
| `months_enrolled` | `INTEGER` | `DEFAULT 0` | Số tháng đã đăng ký |
| `parent_id` | `INTEGER` | `NOT NULL, UNIQUE, FK → parents(parent_id)` | Phụ huynh duy nhất |
| `mentor_id` | `INTEGER` | `FK → mentors(mentor_id)` | Mentor hướng dẫn (nullable) |
| `progress_pct` | `SMALLINT` | `DEFAULT 0, CHECK 0–100` | % lộ trình hoàn thành — **trigger tự cập nhật** |
| `milestones_done` | `SMALLINT` | `DEFAULT 0` | Số milestone đã hoàn thành — **trigger tự cập nhật** |
| `next_deadline` | `DATE` | | Deadline gần nhất — **trigger tự cập nhật** |
| `next_deadline_label` | `VARCHAR(255)` | | Tên milestone deadline (VD: "Nộp hồ sơ EA") — **trigger** |
| `days_left` | `SMALLINT` | | Số ngày đến deadline — **trigger tự cập nhật** |
| `priority_action` | `VARCHAR(255)` | | Hành động ưu tiên — **trigger tự cập nhật** |
| `current_streak` | `SMALLINT` | `DEFAULT 0` | Số ngày học liên tiếp hiện tại |
| `last_activity_date` | `DATE` | | Ngày hoạt động cuối cùng |
| `upsell_cooldown` | `DATE` | `DEFAULT CURRENT_DATE - 1` | Ngày hết cooldown hiển thị upsell (tránh spam) |
| `weakest_skill` | `VARCHAR(50)` | | Kỹ năng yếu nhất (VD: "writing") — dùng cho upsell matching |
| `created_at` | `TIMESTAMPT` | `NOT NULL, DEFAULT NOW()` | Ngày tạo |

**Indexes:**
- `idx_students_parent_id` on `parent_id`
- `idx_students_mentor_id` on `mentor_id`
- `idx_students_program` on `program`

> Trigger: mỗi khi INSERT/UPDATE/DELETE `milestones` → PostgreSQL trigger tự động cập nhật 5 trường digest (`progress_pct`, `milestones_done`, `next_deadline`, `days_left`, `priority_action`).

---

## Table: `mentors`

Mentor — người hướng dẫn học viên. 1 mentor : N students.

| Field | Type | Constraints | Mô tả |
|---|---|---|---|
| `mentor_id` | `SERIAL` | PK | ID tự tăng |
| `email` | `VARCHAR(255)` | `NOT NULL, UNIQUE` | Email đăng nhập |
| `hashed_password` | `VARCHAR(255)` | `NOT NULL` | Mật khẩu đã hash |
| `full_name` | `VARCHAR(255)` | `NOT NULL` | Tên mentor (VD: "Cô Lan — Mentor AMP") |
| `specialty` | `VARCHAR(255)` | | Chuyên môn (VD: "IELTS Writing, SAT Math") |
| `bio` | `TEXT` | | Tiểu sử |
| `avatar_url` | `VARCHAR(500)` | | Link avatar |
| `programs` | `JSONB` | | Danh sách chương trình có thể mentor (VD: `["AMP","IELTS"]`) |
| `max_students` | `SMALLINT` | `DEFAULT 10` | Số học viên tối đa |
| `active_students` | `SMALLINT` | `DEFAULT 0` | Số học viên đang active |
| `created_at` | `TIMESTAMPT` | `NOT NULL, DEFAULT NOW()` | Ngày tạo |
| `updated_at` | `TIMESTAMPT` | `NOT NULL, DEFAULT NOW()` | Ngày cập nhật |

**Indexes:**
- `idx_mentors_email` on `email`
- `idx_mentors_programs` on `programs` (GIN — tìm mentor theo chương trình)

---

## Table: `courses`

Khóa học / trại hè — dùng cho engine upsell (Module 1D).

| Field | Type | Constraints | Mô tả |
|---|---|---|---|
| `course_id` | `SERIAL` | PK | ID tự tăng |
| `name` | `VARCHAR(255)` | `NOT NULL` | Tên khóa học (VD: "IELTS Writing Intensive — Summer Camp") |
| `slug` | `VARCHAR(255)` | `NOT NULL, UNIQUE` | URL-friendly (VD: "ielts-writing-intensive-summer") |
| `type` | `VARCHAR(50)` | `NOT NULL` | Loại: `'camp'`, `'workshop'`, `'course'` |
| `program` | `VARCHAR(100)` | | Chương trình: `'AMP'`, `'IELTS'`, `'SAT'`, `'ALL'` |
| `season` | `VARCHAR(50)` | | Mùa: `'Summer 2026'`, `'Spring 2026'`, `'All Year'` |
| `description` | `TEXT` | | Mô tả chi tiết |
| `target_skills` | `JSONB` | | Kỹ năng học: `["IELTS_Writing","Essay_Structure"]` |
| `suitable_for` | `JSONB` | | Tags để match với học viên: `["student_gap_writing","student_target_7plus"]` |
| `cta_url` | `VARCHAR(500)` | | Link đăng ký / xem chi tiết |
| `cta_label` | `VARCHAR(100)` | | Nút bấm (VD: "Đăng ký ngay") |
| `duration_days` | `SMALLINT` | | Số ngày |
| `start_date` | `DATE` | | Ngày bắt đầu |
| `end_date` | `DATE` | | Ngày kết thúc |
| `location` | `VARCHAR(255)` | | Địa điểm: "Online", "TP.HCM", "Hà Nội" |
| `price_vnd` | `BIGINT` | | Giá VND |
| `is_featured` | `BOOLEAN` | `DEFAULT FALSE` | Hiển thị ưu tiên trên upsell cards |
| `is_active` | `BOOLEAN` | `DEFAULT TRUE` | Còn mở đăng ký không |
| `display_order` | `SMALLINT` | `DEFAULT 0` | Thứ tự hiển thị |
| `created_at` | `TIMESTAMPT` | `NOT NULL, DEFAULT NOW()` | Ngày tạo |
| `updated_at` | `TIMESTAMPT` | `NOT NULL, DEFAULT NOW()` | Ngày cập nhật |

**Indexes:**
- `idx_courses_target_skills` on `target_skills` (GIN)
- `idx_courses_suitable_for` on `suitable_for` (GIN)
- `idx_courses_program_season` on `(program, season)` partial WHERE `is_active = TRUE`

**Upsell matching logic:**
```sql
-- Tìm courses phù hợp với học viên yếu Writing
SELECT * FROM courses
WHERE is_active = TRUE
  AND suitable_for && '["student_gap_writing"]'::jsonb
ORDER BY is_featured DESC, display_order ASC
LIMIT 3;
```

---

## Table: `behavioral_logs`

Nhật ký học tập hàng ngày — 1 row / học viên / ngày. Dùng cho Wellbeing Engine.

| Field | Type | Constraints | Mô tả |
|---|---|---|---|
| `id` | `SERIAL` | PK | ID tự tăng |
| `student_id` | `VARCHAR(50)` | `NOT NULL, FK → students` | Học viên |
| `date` | `DATE` | `NOT NULL` | Ngày (YYYY-MM-DD) |
| `duration_min` | `SMALLINT` | | Tổng phút học trong ngày |
| `session_start` | `TIME` | | Giờ bắt đầu (VD: "23:15") |
| `session_end` | `TIME` | | Giờ kết thúc |
| `studied` | `BOOLEAN` | `DEFAULT FALSE` | Có học không |
| `streak_day` | `SMALLINT` | `DEFAULT 0` | Ngày học liên tiếp |
| `score_delta` | `DECIMAL(4,1)` | `DEFAULT 0` | Thay đổi điểm IELTS so với lần trước |
| `is_late_night` | `BOOLEAN` | **Generated** | `TRUE` nếu `session_start >= '22:00'` (tự tính, không cần app) |
| `activities` | `JSONB` | | Tags hoạt động: `["ielts_mock","essay_draft"]` |
| `mood_note` | `TEXT` | | Ghi chú tâm trạng tự học viên |
| `created_at` | `TIMESTAMPT` | `NOT NULL, DEFAULT NOW()` | Ngày tạo |

**Unique constraint:** `(student_id, date)` — mỗi ngày chỉ 1 row. Dùng `ON CONFLICT DO UPDATE` để upsert.

**Indexes:**
- `idx_behavioral_logs_student_date` on `(student_id, date DESC)`
- `idx_behavioral_logs_studied` on `(student_id, date DESC)` partial WHERE `studied = TRUE`

---

## Table: `conversations`

Lịch sử chat giữa phụ huynh và AI chatbot. `expires_at` → TTL 30 ngày.

| Field | Type | Constraints | Mô tả |
|---|---|---|---|
| `id` | `SERIAL` | PK | ID tự tăng |
| `parent_id` | `INTEGER` | `NOT NULL, FK → parents` | Ai hỏi |
| `student_id` | `VARCHAR(50)` | `NOT NULL, FK → students` | Con được hỏi |
| `timestamp` | `TIMESTAMPT` | `NOT NULL, DEFAULT NOW()` | Thời điểm hỏi |
| `question` | `TEXT` | `NOT NULL` | Câu hỏi phụ huynh (tiếng Việt) |
| `ai_response` | `TEXT` | `NOT NULL` | Phản hồi AI |
| `context_snapshot` | `JSONB` | | Snapshot dữ liệu học viên tại thời điểm hỏi (quan trọng cho AI context) |
| `escalated` | `BOOLEAN` | `DEFAULT FALSE` | Có escalate lên tư vấn viên không |
| `escalator_note` | `TEXT` | | Ghi chú khi escalate |
| `expires_at` | `TIMESTAMPT` | | Hết hạn = `timestamp + 30 days`. Cron job xóa hàng đêm. |
| `created_at` | `TIMESTAMPT` | `NOT NULL, DEFAULT NOW()` | Ngày tạo |

**`context_snapshot` example:**
```json
{
  "student_name": "Nguyễn Hà Minh Anh",
  "ielts_score": 6.5,
  "target_schools": ["University of Melbourne", "UNSW", "Monash"],
  "progress_pct": 68,
  "weakest_skill": "Writing",
  "next_deadline": "2026-05-07"
}
```

**Indexes:**
- `idx_conversations_parent_timestamp` on `(parent_id, timestamp DESC)`
- `idx_conversations_student_id` on `(student_id, timestamp DESC)`
- `idx_conversations_expires_at` on `expires_at` partial WHERE `expires_at IS NOT NULL`

---

## Table: `milestones`

Cột mốc thành tích / deadline của học viên. Đây là nguồn trigger chính cập nhật digest fields trên `students`.

| Field | Type | Constraints | Mô tả |
|---|---|---|---|
| `id` | `SERIAL` | PK | ID tự tăng |
| `student_id` | `VARCHAR(50)` | `NOT NULL, FK → students` | Học viên |
| `milestone_id` | `VARCHAR(100)` | `NOT NULL` | ID cột mốc (VD: "ms_001") |
| `type` | `VARCHAR(50)` | `NOT NULL` | Loại (xem bảng dưới) |
| `title` | `VARCHAR(255)` | `NOT NULL` | Tên cột mốc |
| `date` | `DATE` | `NOT NULL` | Ngày dự kiến / hoàn thành |
| `score` | `DECIMAL(5,2)` | | Điểm đạt được (VD: 6.5, 1320) |
| `score_label` | `VARCHAR(100)` | | Nhãn điểm (VD: "IELTS Band 6.5") |
| `mentor_id` | `INTEGER` | `FK → mentors` | Mentor xác nhận |
| `mentor_approved` | `BOOLEAN` | | Mentor đã approve chưa |
| `auth_score` | `SMALLINT` | `CHECK 0–100` | Điểm authenticity bài luận (0–100, NULL nếu không phải essay) |
| `notes` | `TEXT` | | Ghi chú |
| `status` | `VARCHAR(20)` | `NOT NULL, DEFAULT 'upcoming'` | Trạng thái |
| `contributor_type` | `VARCHAR(50)` | `NOT NULL, DEFAULT 'student'` | Ai đóng góp milestone này |
| `ai_summary` | `JSONB` | | AI summarize: `{summary, skills_demonstrated[], evidence_strength}` |
| `created_at` | `TIMESTAMPT` | `NOT NULL, DEFAULT NOW()` | Ngày tạo |
| `updated_at` | `TIMESTAMPT` | `NOT NULL, DEFAULT NOW()` | Ngày cập nhật cuối |

**Unique constraint:** `(student_id, milestone_id)`

### Giá trị hợp lệ

| Field | Values |
|---|---|
| `type` | `ielts_mock`, `essay_draft`, `essay_final`, `sat_mock`, `extracurricular`, `consultation`, `camp`, `csr`, `target_achieved` |
| `status` | `completed`, `in_progress`, `upcoming` |
| `contributor_type` | `student`, `mentor`, `parent`, `institution` |

**Indexes:**
- `idx_milestones_student_date` on `(student_id, date DESC)`
- `idx_milestones_student_status` on `(student_id, status, date ASC)` partial WHERE `status IN ('completed','upcoming')`
- `idx_milestones_upcoming` on `(student_id, date ASC)` partial WHERE `status = 'upcoming'`
- `idx_milestones_completed` on `(student_id, date DESC)` partial WHERE `status = 'completed'`
- `idx_milestones_essays` on `(student_id, date DESC)` partial WHERE `type IN ('essay_draft','essay_final') AND auth_score IS NOT NULL`

---

## Tổng kết

| Bảng | Rows / entity | Mối quan hệ |
|---|---|---|
| `parents` | 1 row / phụ huynh | 1:1 ↔ `students` |
| `students` | 1 row / học viên | N:1 ↔ `parents`, N:1 ↔ `mentors` |
| `mentors` | 1 row / mentor | 1:N → `students` |
| `courses` | N rows / khóa học | Lookup table — không FK trực tiếp |
| `behavioral_logs` | N rows / ngày / học viên | N:1 → `students` |
| `conversations` | N rows / lần chat | N:1 → `parents`, N:1 → `students` |
| `milestones` | N rows / cột mốc / học viên | N:1 → `students`, N:1 → `mentors` |

**Tổng số bảng: 7**
