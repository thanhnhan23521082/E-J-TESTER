# ETEST ONE — Smart Parenting Module
## Statistics & Chatbot Specification

> **Version:** 1.1.0 — Hackathon Build
> **Stack:** React + Vite · Node.js + Express · PostgreSQL (EC2) + Alembic · Claude API (claude-sonnet-4-6)
> **DB:** PostgreSQL hosted trên EC2 · Schema migration quản lý bằng Alembic

---

## Mục lục

1. [Database Architecture — EC2 + Alembic](#1-database-architecture--ec2--alembic)
2. [AI Translation Layer — Cổng chuyển đổi ngôn ngữ](#2-ai-translation-layer--cổng-chuyển-đổi-ngôn-ngữ)
3. [Statistics — Tổng quan](#3-statistics--tổng-quan)
4. [Wellbeing](#4-wellbeing)
5. [Học thuật](#5-học-thuật)
6. [Trường / Hồ sơ](#6-trường--hồ-sơ)
7. [Học bổng](#7-học-bổng)
8. [ROI & Chi phí](#8-roi--chi-phí)
9. [Trust ETEST](#9-trust-etest)
10. [Display Model — 4 Layers](#10-display-model--4-layers-progressive-disclosure)
11. [Chatbot — 9 Điểm nổi trội](#11-chatbot--9-điểm-nổi-trội)
12. [Appendix — Claude System Prompts](#12-appendix--claude-system-prompts)

---

## 1. Database Architecture — EC2 + Alembic

### Tổng quan

Thay vì DynamoDB (managed NoSQL), toàn bộ data được lưu trên **PostgreSQL chạy trực tiếp trên EC2**. Schema migration quản lý bằng **Alembic** (Python migration tool cho SQLAlchemy).

```
EC2 Instance (t3.medium)
├── PostgreSQL 15
│   ├── DB: etest_one
│   └── Tables: students · behavioral_logs · conversations
│               milestones · etester_core · card_translations
└── Alembic
    ├── alembic.ini
    ├── env.py
    └── versions/
        ├── 001_create_students.py
        ├── 002_create_behavioral_logs.py
        ├── 003_create_milestones.py
        ├── 004_create_conversations.py
        ├── 005_create_etester_core.py
        └── 006_create_card_translations.py
```

### Setup Alembic

```bash
# Cài đặt
pip install alembic sqlalchemy psycopg2-binary

# Khởi tạo
alembic init alembic

# Chạy tất cả migrations
alembic upgrade head

# Tạo migration mới khi thay đổi schema
alembic revision --autogenerate -m "add_auth_score_to_milestones"

# Rollback 1 bước
alembic downgrade -1
```

### Connection string

```python
# .env
DATABASE_URL=postgresql://etest_user:password@<EC2_PUBLIC_IP>:5432/etest_one

# SQLAlchemy engine (Node.js dùng pg hoặc sequelize)
from sqlalchemy import create_engine
engine = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)
```

> **Security:** Mở port 5432 trên EC2 Security Group chỉ cho IP backend server. Không expose public internet.

---

### Schema Tables

#### `students`
```sql
CREATE TABLE students (
    student_id      VARCHAR PRIMARY KEY,
    name            VARCHAR NOT NULL,
    ielts_score     NUMERIC(3,1),
    sat_score       INTEGER,
    gpa             NUMERIC(3,2),
    skill_breakdown JSONB,          -- {listening, reading, writing, speaking}
    target_schools  TEXT[],
    months_enrolled INTEGER,
    program         VARCHAR,        -- 'AMP' | 'IELTS' | 'SAT'
    parent_id       VARCHAR,
    mentor_id       VARCHAR,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

#### `behavioral_logs`
```sql
CREATE TABLE behavioral_logs (
    id              SERIAL PRIMARY KEY,
    student_id      VARCHAR REFERENCES students(student_id),
    date            DATE NOT NULL,
    duration_min    INTEGER,
    session_start   TIME,
    studied         BOOLEAN,
    streak_day      INTEGER,
    score_delta     NUMERIC(3,1),
    UNIQUE(student_id, date)
);
```

#### `milestones`
```sql
CREATE TABLE milestones (
    milestone_id     VARCHAR PRIMARY KEY,
    student_id       VARCHAR REFERENCES students(student_id),
    type             VARCHAR,       -- 'ielts_mock' | 'essay_draft' | 'essay_final' | 'sat_mock' | 'csr' | 'camp'
    title            VARCHAR,
    date             TIMESTAMPTZ,
    score            NUMERIC(4,1),
    score_label      VARCHAR,
    mentor_id        VARCHAR,
    mentor_approved  BOOLEAN DEFAULT FALSE,
    auth_score       INTEGER,       -- 0–100, null nếu không phải essay
    notes            TEXT,
    status           VARCHAR,       -- 'completed' | 'in_progress' | 'upcoming'
    contributor_type VARCHAR,       -- 'student' | 'mentor' | 'parent' | 'institution'
    ai_summary       JSONB          -- {summary, skills_demonstrated, evidence_strength}
);
```

#### `conversations`
```sql
CREATE TABLE conversations (
    id               SERIAL PRIMARY KEY,
    parent_id        VARCHAR NOT NULL,
    student_id       VARCHAR REFERENCES students(student_id),
    timestamp        TIMESTAMPTZ DEFAULT NOW(),
    question         TEXT,
    ai_response      TEXT,
    context_snapshot JSONB,
    escalated        BOOLEAN DEFAULT FALSE
);
```

#### `etester_core`
```sql
CREATE TABLE etester_core (
    student_id            VARCHAR PRIMARY KEY REFERENCES students(student_id),
    academic_score        NUMERIC(5,2),
    writing_growth        NUMERIC(5,2),
    skills                TEXT[],
    mentor_verifications  INTEGER DEFAULT 0,
    parent_support_level  VARCHAR,   -- 'low' | 'medium' | 'active' | 'high'
    institutional_stamp   BOOLEAN DEFAULT FALSE,
    consistency_score     INTEGER,   -- 0–100
    total_contributions   INTEGER DEFAULT 0,
    last_updated          TIMESTAMPTZ DEFAULT NOW(),
    narrative_cache       TEXT,
    badge_issued          BOOLEAN DEFAULT FALSE
);
```

#### `card_translations` *(bảng mới — cache bản dịch AI)*
```sql
CREATE TABLE card_translations (
    id              SERIAL PRIMARY KEY,
    student_id      VARCHAR REFERENCES students(student_id),
    stat_key        VARCHAR NOT NULL,   -- 'streak_day' | 'ielts_score' | ...
    raw_value       JSONB,              -- giá trị thô từ DB
    simple_text     TEXT,              -- bản dịch đơn giản (phụ huynh low-tech)
    detail_text     TEXT,              -- bản dịch chi tiết (phụ huynh am hiểu)
    tone            VARCHAR,           -- 'simple' | 'technical'
    generated_at    TIMESTAMPTZ DEFAULT NOW(),
    expires_at      TIMESTAMPTZ        -- cache TTL
);
```

---

## 2. AI Translation Layer — Cổng chuyển đổi ngôn ngữ

### Triết lý thiết kế

**Tất cả 48 statistics đều phải đi qua cổng AI trước khi hiển thị cho phụ huynh.** Không có stat nào được show raw value trực tiếp. Claude đóng vai trò phiên dịch viên — chuyển ngôn ngữ của mentor/chuyên gia thành ngôn ngữ của phụ huynh đồng hành.

```
PostgreSQL on EC2 (raw data)
        ↓
Backend: compute layer (tính toán thuần — không dùng AI)
        ↓
AI Translation Layer  ◄── điểm mấu chốt
  ├── Nhận:   raw stats + student context + parent mode
  ├── Xử lý:  Claude dịch ngôn ngữ kỹ thuật → ngôn ngữ phụ huynh
  ├── Output: { simple_text, detail_text, badge, cta, priority }
  └── Cache:  lưu vào card_translations (TTL 1–24h tuỳ loại stat)
        ↓
Frontend: render SmartCard theo output Claude
```

### Tại sao cần AI Translation Layer?

| | Không có AI Layer | Có AI Translation Layer |
|---|---|---|
| Thuật ngữ | `streak_day: 14, duration_drop: -8%` | "Con học đều 14 ngày · giảm nhẹ so tuần trước — vẫn bình thường" |
| Ngữ cảnh | Số liệu rời rạc, không có ý nghĩa | Số liệu gắn với Minh Anh cụ thể |
| Tone | Một kiểu cố định | Tự điều chỉnh: calm / alert / celebratory |
| Hành động | Không có | Luôn kết thúc bằng 1 việc cần làm |
| Linh hoạt | Cần code lại khi đổi format | Chỉ cần chỉnh prompt |
| Ngôn ngữ 2 chiều | Không thể | Đơn giản cho cô Thu · Kỹ thuật cho anh kỹ sư |

---

### Pipeline chi tiết

```
Step 1 — Fetch raw data từ PostgreSQL (EC2)
  SELECT * FROM students, behavioral_logs, milestones
  WHERE student_id = :id

Step 2 — Backend compute (không dùng AI, tính nhanh)
  - streak_day, avg_duration, late_nights_count
  - progress_pct, milestone_completion_rate
  - deadline_gap, score_trajectory
  - cohort_rank, admission_probability

Step 3 — Check cache
  SELECT * FROM card_translations
  WHERE student_id = :id AND stat_key = :key AND expires_at > NOW()
  → Cache hit  : return cached text ngay
  → Cache miss : gọi Claude (Step 4)

Step 4 — AI Translation (Claude API)
  Input : { student_name, stats{}, parent_mode, context }
  Output: { cards[], priority_order[], upsell_trigger, escalate }

Step 5 — Save cache
  INSERT INTO card_translations (student_id, stat_key, simple_text, detail_text, expires_at)
  TTL: 1h wellbeing · 6h academic/deadline · 24h ROI/scholarship

Step 6 — Frontend render
  React nhận JSON → render SmartCard theo layer
```

---

### Cache TTL Strategy

| Nhóm stats | TTL | Lý do |
|---|---|---|
| Wellbeing (streak, late nights) | 1 giờ | Thay đổi hàng ngày |
| Academic (scores, milestones) | 6 giờ | Cập nhật sau mỗi buổi học |
| Deadline, countdown | 6 giờ | Thay đổi theo ngày |
| ROI, cohort rank | 24 giờ | Ổn định, không cần realtime |
| Trust stats (mentor activity) | 6 giờ | Cập nhật khi có action mới |
| Scholarship info | 24 giờ | Tĩnh, chỉ đổi khi admin update |

---

### Backend API routes

```
GET  /api/students/:id
     → SELECT * FROM students WHERE student_id = :id

GET  /api/behavioral-log/:studentId
     → SELECT * FROM behavioral_logs WHERE student_id = :id
       ORDER BY date DESC LIMIT 14
     → Compute: avg_duration, late_nights_count, streak_drop_%

POST /api/ai/translate-stats
     body: { studentId, mode: "simple"|"technical", context: "digest"|"alert"|"chat" }
     → Fetch all stats từ PostgreSQL
     → Check card_translations cache
     → Call Claude nếu cache miss
     → Return: { cards[], priority_order[], upsell_trigger, escalate }

POST /api/ai/parent-chat
     body: { question, studentId }
     → Fetch student context + 5 conversations gần nhất
     → ALL responses đi qua AI translation layer
     → INSERT INTO conversations ...
     → Return: { response, escalated, upsell }

POST /api/ai/wellbeing
     body: { studentId }
     → Compute behavioral stats → Claude analyze
     → Return: { alert, severity, simple_message, action }

GET  /api/digest/:studentId
     → Compute weekly digest → gọi translateStats()
     → Return translated cards (không phải raw numbers)
```

---

## 3. Statistics — Tổng quan

48 statistics phân nhóm theo 6 chiều quan tâm của phụ huynh. **Tất cả đều đi qua AI Translation Layer** — không có raw value nào được hiển thị trực tiếp.

| Nhóm | Số stats | Ưu tiên Cao | Bảng PostgreSQL | Cache TTL |
|---|---|---|---|---|
| Wellbeing | 8 | 4 | `behavioral_logs` | 1h |
| Học thuật | 10 | 4 | `students` · `milestones` | 6h |
| Trường / Hồ sơ | 7 | 3 | `students` · `milestones` | 6h |
| Học bổng | 7 | 3 | `milestones` · Claude computed | 24h |
| ROI & Chi phí | 7 | 3 | `etester_core` · ETEST internal | 24h |
| Trust ETEST | 8 | 4 | `etester_core` · `milestones` | 6h |

> Cột **"Claude dịch"** phía dưới là output mẫu của AI — không phải text hardcode. Claude tự điều chỉnh tên học viên, số liệu và tone dựa trên data thực tế từng học viên.

---

## 4. Wellbeing

> Nhóm được phụ huynh quan tâm hàng đầu — tín hiệu thói quen, sức khoẻ học tập và trạng thái tinh thần của con.
> **Bảng:** `behavioral_logs` · **Cache:** 1 giờ

| Stat | Cột PostgreSQL | Ưu tiên | Claude dịch → Đơn giản | Claude dịch → Chi tiết |
|---|---|---|---|---|
| Chuỗi học liên tiếp | `streak_day` | 🔴 Cao | "Con học liên tiếp 14 ngày không nghỉ" | "Streak: 14 days · 7-day avg: 11 days" |
| Số buổi học khuya (>22h) | `session_start` | 🔴 Cao | "Con học muộn 3 đêm tuần này" | "Late sessions (>22:00): 3/week · threshold: 2" |
| Thời gian học TB/ngày | `duration_min` | 🔴 Cao | "Mỗi ngày con học khoảng 65 phút" | "7-day avg: 65 min · vs prev week: −8%" |
| Tỷ lệ giảm thời gian học | computed | 🔴 Cao | "Con học ít hơn tuần trước một chút" | "Duration drop: 8% · alert threshold: 35%" |
| Số ngày học trong tuần | `studied` (count) | 🟡 TB | "Tuần này con học 5 trong 7 ngày" | "Days studied: 5/7 · drop >40% = alert" |
| Giờ bắt đầu học TB | `session_start` (avg) | 🟡 TB | "Con thường bắt đầu học lúc 8 giờ tối" | "Avg session start: 20:30 · trend stable" |
| Score delta buổi gần nhất | `score_delta` | 🟡 TB | "Điểm buổi học gần nhất không thay đổi nhiều" | "Last delta: −0.2 · regression threshold: −0.5" |
| Tổng giờ học tích luỹ | computed (sum) | 🟢 Thấp | "Con đã học tổng cộng hơn 150 giờ từ đầu" | "Total: 152 hrs · cohort avg: 130 hrs" |

**Alert thresholds — Claude dịch khi vượt ngưỡng:**

| Signal | Threshold | Claude nói với phụ huynh |
|---|---|---|
| Duration drop | >35% vs 7-day avg | "Con học ít hơn hẳn tuần trước — có thể đang mệt hoặc bận" |
| Late-night sessions | ≥2 sau 22:00 / 5 ngày | "Con học khuya mấy đêm liên tiếp — nên nhắc con ngủ sớm hơn" |
| Streak break | Giảm ≥4 ngày liên tiếp | "Con nghỉ học mấy ngày liên tiếp — hỏi thăm xem con có ổn không" |
| Score regression | Mock giảm ≥0.5 band / 2 lần | "Điểm thi thử giảm nhẹ hai lần gần đây — cần xem lại phần đang khó" |
| Session frequency | Sessions/tuần giảm >40% | "Tuần này con học ít buổi hơn bình thường" |

---

## 5. Học thuật

> Tiến độ điểm số, milestone và chất lượng bài làm.
> **Bảng:** `students` · `milestones` · **Cache:** 6 giờ

| Stat | Cột PostgreSQL | Ưu tiên | Claude dịch → Đơn giản | Claude dịch → Chi tiết |
|---|---|---|---|---|
| IELTS mock score gần nhất | `students.ielts_score` | 🔴 Cao | "Con thi thử gần nhất được 6.5 — đang tốt" | "Latest mock: 6.5 · prev: 6.0 · trend ↑" |
| Trajectory IELTS (3 lần gần) | `milestones` (ielts_mock) | 🔴 Cao | "Điểm con tăng đều từ 5.5 lên 6.5 trong 3 lần thi" | "5.5 → 6.0 → 6.5 · avg +0.5/attempt" |
| Skill breakdown IELTS | `students.skill_breakdown` (JSONB) | 🔴 Cao | "Đọc và Nghe tốt · Viết cần cải thiện · Nói đang tiến bộ" | "L:7.0 R:7.0 W:5.5 S:6.0 · Writing is bottleneck" |
| SAT score gần nhất | `students.sat_score` | 🔴 Cao | "Con thi thử SAT được 1320 — đủ cho hầu hết trường mục tiêu" | "SAT: 1320 · target: 1400 · gap: −80" |
| Tiến độ lộ trình % | computed từ milestones | 🟡 TB | "Con đã đi được khoảng 2/3 hành trình, còn 6 tháng nữa" | "Completion: 68% · on track · projected end: Nov 2026" |
| Số milestone hoàn thành | `milestones.status` | 🟡 TB | "Con đã hoàn thành 18 trong 23 bài tập trong lộ trình" | "18/23 complete · 3 in_progress · 2 upcoming" |
| Số bài luận đã nộp | `milestones.type` (essay) | 🟡 TB | "Con đã nộp 6 bài luận, trong đó 4 bài đã hoàn chỉnh" | "Essays: 6 total · final: 4 · draft: 2" |
| Authenticity score TB | `milestones.auth_score` (avg) | 🟡 TB | "91% bài viết của con là do con tự viết — rất tốt cho hồ sơ" | "Avg auth: 91% · min: 85% · flagged: 0" |
| GPA hiện tại | `students.gpa` | 🟢 Thấp | "Điểm học bạ của con đang ở mức khá tốt" | "GPA: 3.4 / 4.0 · cohort: top 35%" |
| Số mock test đã làm | `milestones.type` (mock) | 🟢 Thấp | "Con đã làm 5 bài thi thử từ đầu chương trình" | "Total: 5 · IELTS: 3 · SAT: 2" |

---

## 6. Trường / Hồ sơ

> Câu trả lời trực tiếp cho "Con có vào được không?".
> **Bảng:** `students` · `milestones` · **Cache:** 6 giờ

| Stat | Cột PostgreSQL | Ưu tiên | Claude dịch → Đơn giản | Claude dịch → Chi tiết |
|---|---|---|---|---|
| Số trường đủ điều kiện | `students.target_schools` + scores | 🔴 Cao | "Con đủ điều kiện vào 8 trong 10 trường đang nhắm" | "Eligible: 8/10 · IELTS 6.5 + SAT 1320 + GPA 3.4" |
| Countdown deadline gần nhất | `milestones` (upcoming) | 🔴 Cao | "Còn đúng 47 ngày để nộp hồ sơ Melbourne — cần chuẩn bị ngay" | "Melbourne EA: 47 days · need: essay + Writing 7.0" |
| Gap điểm với trường ưu tiên | computed | 🔴 Cao | "Con chỉ còn thiếu một chút phần Viết để đủ điều kiện Melbourne" | "Gap: Writing +0.5 band · Overall: met · SAT: met" |
| Xác suất đậu trường ưu tiên | Claude computed | 🟡 TB | "Dựa trên đà hiện tại, con có khoảng 73% cơ hội vào Melbourne" | "Admission probability: 73% · model: trajectory + timeline" |
| Số bài luận mentor approved | `milestones.mentor_approved` | 🟡 TB | "6 bài luận đã được thầy/cô xem xét và xác nhận" | "Approved: 6 · pending: 1" |
| Danh sách trường mục tiêu | `students.target_schools` | 🟡 TB | "Con đang nhắm 10 trường tại Úc và Canada" | "Reach: 2 · Match: 5 · Safety: 3" |
| Thời gian còn lại | `students.months_enrolled` | 🟢 Thấp | "Con còn khoảng 6 tháng để hoàn thành chương trình AMP" | "Months remaining: 6 · end: Nov 2026" |

---

## 7. Học bổng

> Nhóm tác động cảm xúc lớn nhất — quy ra tiền và điều kiện cụ thể.
> **Bảng:** `milestones` · Claude computed · **Cache:** 24 giờ

| Stat | Cột PostgreSQL | Ưu tiên | Claude dịch → Đơn giản | Claude dịch → Chi tiết |
|---|---|---|---|---|
| Học bổng tiềm năng (%) | computed + hardcoded ranges | 🔴 Cao | "Con có thể nhận học bổng 30–50% học phí nếu đủ điều kiện" | "Range: 30–50% · based on IELTS+GPA+extracurricular" |
| Học bổng quy ra VND | computed: % × avg tuition | 🔴 Cao | "Tương đương 500–900 triệu đồng — đáng để cố thêm" | "Est. value: 500–900M VND · avg tuition 2025–2026" |
| Điều kiện học bổng còn thiếu | Claude gap analysis | 🔴 Cao | "Con cần cải thiện phần Viết và thêm 1 hoạt động xã hội để đủ điều kiện học bổng merit" | "Missing: Writing 6.0 · 1 approved essay · 1 CSR" |
| Số HV ETEST đã nhận học bổng | ETEST internal | 🟡 TB | "47 học viên cùng chương trình đã nhận được học bổng" | "Recipients: 47 · avg: 35% tuition · top: Melbourne 40%" |
| Loại học bổng phù hợp nhất | Claude match | 🟡 TB | "Con phù hợp nhất với học bổng dựa trên thành tích học tập" | "Best fit: merit-based · need-based: possible · athletic: N/A" |
| Ngoại khoá / CSR | `milestones.type` (extracurricular/csr) | 🟡 TB | "Con đã tham gia 2 hoạt động xã hội — tốt cho hồ sơ học bổng" | "Extracurriculars: 2 · CSR: 1 · impact: medium" |
| Deadline nộp hồ sơ học bổng | `milestones` (upcoming) | 🟢 Thấp | "Hạn nộp học bổng Melbourne là ngày 15 tháng 11" | "Melbourne: Nov 15 · Monash: Dec 1" |

---

## 8. ROI & Chi phí

> Bằng chứng giá trị đầu tư — so sánh cohort và dự báo thực tế.
> **Bảng:** `etester_core` · ETEST internal · **Cache:** 24 giờ

| Stat | Cột PostgreSQL | Ưu tiên | Claude dịch → Đơn giản | Claude dịch → Chi tiết |
|---|---|---|---|---|
| Xếp hạng trong cohort | `etester_core` + computed | 🔴 Cao | "Con đang trong nhóm 28% học viên tiến bộ nhanh nhất chương trình AMP" | "Cohort percentile: top 28% · n=64 students" |
| Tốc độ tiến bộ vs avg cohort | computed | 🔴 Cao | "Con đạt 6.5 nhanh hơn trung bình 2 tháng so với các bạn cùng khoá" | "Time to 6.5: 14m · cohort avg: 16.2m · delta: −2.2m" |
| Track record đậu trường ETEST | ETEST internal | 🔴 Cao | "92% học viên ETEST đã vào được trường mong muốn" | "Rate: 92% · n=312 alumni · top: Australia 58%" |
| ROI ước tính | computed: scholarship/cost | 🟡 TB | "Nếu con nhận học bổng, gia đình tiết kiệm gấp 3 lần số đã đầu tư" | "Est. ROI: 3.2× · scholarship / total_program_cost" |
| Dự báo nếu không học thêm | Claude projection | 🟡 TB | "Nếu giữ tốc độ hiện tại, con có thể chưa kịp điểm Writing trước deadline" | "Projection: Writing 5.8 · gap: −0.2 · confidence: 70%" |
| Chi phí đã đầu tư | hardcoded by tier | 🟡 TB | "Gia đình đã đồng hành cùng con được 14 tháng" | "Cost to date: ~X VND · remaining: ~Y VND" |
| Số tháng học cùng ETEST | `students.months_enrolled` | 🟢 Thấp | "Con đã học cùng ETEST được 14 tháng" | "Enrolled: 14m · start: Sep 2025 · end: Nov 2026" |

---

## 9. Trust ETEST

> Tín hiệu uy tín — mentor activity, ETESTER verification và track record.
> **Bảng:** `etester_core` · `milestones` · **Cache:** 6 giờ

| Stat | Cột PostgreSQL | Ưu tiên | Claude dịch → Đơn giản | Claude dịch → Chi tiết |
|---|---|---|---|---|
| Tỷ lệ bài được mentor xem | `milestones.mentor_approved` | 🔴 Cao | "18 trong 23 bài con nộp đã được thầy/cô xem và phản hồi" | "Review rate: 18/23 (78%) · avg response: 2.3 days" |
| Lần cuối mentor tương tác | `milestones` (latest approved) | 🔴 Cao | "Thầy/cô vừa xem bài của con 3 ngày trước" | "Last: 3 days ago · type: essay review" |
| Tổng contributions ETESTER | `etester_core.total_contributions` | 🔴 Cao | "Con đã tích luỹ 23 đóng góp trong hồ sơ ETESTER — không thể làm giả" | "Total: 23 · mentor-verified: 18 · auth avg: 91%" |
| Số lần mentor human-verify | `etester_core.mentor_verifications` | 🔴 Cao | "Thầy/cô đã trực tiếp xác nhận 18 lần trong hành trình của con" | "Verifications: 18 · stamps: 1 · parent confirms: 4" |
| ETEST kinh nghiệm | hardcoded | 🟡 TB | "ETEST đã tư vấn du học hơn 20 năm tại TP.HCM" | "Founded: 20+ yrs · alumni: 500+ · partner schools: 30+" |
| IELTS TB đầu ra AMP | ETEST internal | 🟡 TB | "Học viên hoàn thành AMP đạt trung bình 6.8 điểm IELTS" | "Avg IELTS: 6.8 · SAT avg: 1380 · n=89 alumni" |
| Parent engagement score | `etester_core.parent_support_level` | 🟡 TB | "Cô/Anh đang đồng hành tốt cùng con" | "Support level: active · events: 12 this month" |
| Institutional stamp | `etester_core.institutional_stamp` | 🟢 Thấp | "Hồ sơ ETESTER đã được ETEST chính thức xác nhận và đóng dấu" | "Stamp: verified · issued by: ETEST Vietnam" |

---

## 10. Display Model — 4 Layers Progressive Disclosure

> Vấn đề không phải là bao nhiêu stats tồn tại, mà là bao nhiêu stats hiển thị cùng một lúc. Claude đọc 48 → dịch qua AI Translation Layer → chọn đúng số lượng cho từng layer.

---

### Layer 1 — Surface *(mặc định khi mở app)*

**≤ 3 stats · Mọi phụ huynh kể cả low-tech**

Claude chọn tối đa 3 stats quan trọng nhất hôm nay, dịch sang ngôn ngữ đơn giản nhất.

- 1 alert nếu có dấu hiệu bất thường
- 1 con số tiến độ chính
- 1 việc cần làm ngay

> Nếu nhìn 10 giây — phụ huynh biết con có ổn không và cần làm gì.

### Layer 2 — Digest *(bấm "Xem thêm")*

**5–8 stats · Phụ huynh trung bình**

Weekly digest. Plain text, không thuật ngữ kỹ thuật.

- Học tập & milestone tuần này · Kỹ năng mạnh/cần cải thiện
- Deadline sắp tới · So sánh tuần trước · Học bổng tiềm năng VND

> ~70% phụ huynh dừng ở đây và cảm thấy đủ thông tin.

### Layer 3 — Detail *(toggle "Xem chi tiết")*

**15–20 stats · Phụ huynh am hiểu · Không bao giờ show mặc định**

Score trajectory · Band breakdown L/R/W/S · Cohort percentile · Admission probability % · Auth score · ROI multiplier

> ~20–30% phụ huynh am hiểu dùng tầng này.

### Layer 4 — Chatbot *(hỏi bất cứ điều gì)*

**48 stats khả dụng · Mọi phụ huynh**

Claude tự điều chỉnh ngôn ngữ theo câu hỏi và người hỏi. Không bao giờ dump hết cùng lúc.

> 48 stats là "kho dữ liệu" — Claude là lớp filter thông minh nhất.

---

### Logic Claude chọn stats cho Layer 1

| Ưu tiên | Điều kiện | Output của Claude |
|---|---|---|
| 1 | Wellbeing threshold bị vượt | "Minh Anh học khuya 3 đêm tuần này — nên hỏi thăm con tối nay" |
| 2 | Deadline ≤60 ngày + còn gap | "Melbourne còn 47 ngày · Con chỉ cần cải thiện thêm phần Viết" |
| 3 | Score thay đổi đáng kể | "Minh Anh vừa tăng từ 6.0 lên 6.5 — tiến bộ rõ rệt!" |
| 4 | Milestone vừa hoàn thành | "Bài luận đầu tiên vừa được thầy/cô xác nhận — bước quan trọng!" |
| 5 | Không có gì bất thường | "Minh Anh học đều tuần này · 68% lộ trình · 6 tháng nữa hoàn thành" |

---

## 11. Chatbot — 9 Điểm nổi trội

> Điểm khác biệt cốt lõi: **context cực sâu về đứa con cụ thể** + **AI Translation Layer** biến mọi câu trả lời thành ngôn ngữ đồng hành tự nhiên.

---

### 1. Trả lời về con — không phải về IELTS nói chung
| | |
|---|---|
| ❌ | "IELTS 6.5 là đủ cho nhiều trường Úc, bạn nên check từng trường..." |
| ✅ | "6.5 của Minh Anh đủ 8/10 trường con đang nhắm. Chỉ thiếu 0.5 Writing để vào Melbourne — deadline còn 47 ngày." |

`GET /api/students/:id` → inject full student context vào system prompt mỗi request

---

### 2. Dịch thuật ngữ → ngôn ngữ phụ huynh tức thì
| | |
|---|---|
| ❌ | "Band 6.5 tương đương B2 theo CEFR, đủ điều kiện entry requirements..." |
| ✅ | "6.5 nghĩa là tiếng Anh con đang khá tốt — đủ vào đại học Úc. Melbourne cần 7.0 nên con còn thiếu một chút phần viết." |

System prompt: *"Không dùng band, CEFR, GPA — thay bằng ngôn ngữ đời thường"*

---

### 3. Wellbeing radar — phát hiện pattern trước khi phụ huynh nhận ra
| | |
|---|---|
| ❌ | "Con bạn có 3 buổi sau 22:00 và duration giảm 8% so với baseline." |
| ✅ | "Minh Anh học muộn 3 đêm và thời gian học giảm nhẹ. Con vẫn học đều — nhưng có thể đang hơi áp lực. Cô nên hỏi thăm tối nay." |

`POST /api/ai/wellbeing` → nếu alert: true → "gợi ý nhẹ nhàng, không tạo panic"

---

### 4. Mỗi câu trả lời kết thúc bằng 1 hành động cụ thể
| | |
|---|---|
| ❌ | "Bạn nên cân nhắc các phương án học thêm phù hợp..." |
| ✅ | "Việc cụ thể Cô có thể làm ngay: đăng ký khóa Writing tháng 4 — học viên cùng profile tăng 0.5 band sau 6 tuần." |

System prompt: *"Kết thúc MỌI câu trả lời bằng: 'Bạn có thể làm ngay: [1 hành động ≤15 từ]'"*

---

### 5. Nhớ ngữ cảnh — không hỏi lại từ đầu
| | |
|---|---|
| ❌ | "Vui lòng cho biết con bạn đang học chương trình gì?" |
| ✅ | "Dựa trên tốc độ cải thiện 3 tháng qua, con có thể đạt Writing 6.0 trong 6–8 tuần — vừa kịp Melbourne." |

`SELECT * FROM conversations WHERE parent_id=:id ORDER BY timestamp DESC LIMIT 5` → inject vào messages array

---

### 6. Biết khi nào escalate — không cố trả lời tất cả
| | |
|---|---|
| ❌ | "Visa student Úc yêu cầu subclass 500, học phí Melbourne khoảng 35,000 AUD..." |
| ✅ | "Câu hỏi về visa và học phí chính xác cần tư vấn viên xác nhận. Kết nối ngay không ạ?" |

System prompt: *"Visa/học phí chính xác/tâm lý → `{ escalated: true, reason: '...' }`"* → frontend show banner

---

### 7. Upsell tự nhiên — không phải quảng cáo
| | |
|---|---|
| ❌ | "ETEST có nhiều khóa học chất lượng cao, hãy tham khảo website..." |
| ✅ | "Writing là điểm duy nhất Minh Anh còn thiếu. Trại hè Writing tháng 7 có 3 HV cùng profile đã tăng 0.5 band — đúng thứ cần trước deadline." |

`GET /api/upsell/:studentId` → chỉ inject khi gap được confirm bởi score data

---

### 8. Biết tên con — dùng tên trong mọi câu trả lời
| | |
|---|---|
| ❌ | "Học viên của bạn có điểm IELTS 6.5 sau 14 tháng." |
| ✅ | "Minh Anh đã đạt 6.5 sau 14 tháng — nhanh hơn trung bình 2 tháng so với các bạn cùng AMP." |

System prompt: *"Luôn gọi bằng tên `{studentName}`. Không dùng 'học viên', 'con bạn', 'em'."*

---

### 9. Nhận diện câu hỏi cảm xúc — đồng cảm trước, data sau
| | |
|---|---|
| ❌ | "Con bạn có 78% milestone hoàn thành, đang đúng tiến độ." |
| ✅ | "Lo là điều rất tự nhiên khi đầu tư lớn như vậy. Nhìn vào những gì Minh Anh đã làm được — 14 tháng kiên trì, tăng 1 band — đó là nền tảng rất tốt." |

System prompt: *"Câu hỏi chứa: lo, stress, sợ, đáng không → 1 câu đồng cảm trước, data sau."*

---

## 12. Appendix — Claude System Prompts

### A. `translateStats()` — AI Translation Layer

```
Bạn là AI dịch thuật số liệu giáo dục của ETEST Vietnam.
Nhiệm vụ: Nhận raw stats từ PostgreSQL → dịch sang ngôn ngữ phụ huynh Việt Nam.

HỌC VIÊN: {studentName} · Chương trình {program} · {monthsEnrolled} tháng

RAW STATS:
{statsJson}

CHẾ ĐỘ: {mode}     -- "simple" hoặc "technical"
CONTEXT: {context}  -- "digest" | "alert" | "chat"

QUY TẮC DỊCH:
- Không dùng: band, CEFR, percentile, delta, threshold, baseline
- Thay bằng: điểm, xếp hạng, mức thay đổi, ngưỡng cần đạt
- Luôn gắn số liệu với ý nghĩa thực tế của {studentName}
- mode=simple: câu ngắn, không số kỹ thuật, cảm xúc tích cực khi ổn
- mode=technical: giữ số chính xác, thêm context chuyên môn
- Mỗi stat có badge: Tốt / Cần chú ý / Quan trọng + màu green/amber/red
- Stat đáng cảnh báo: kết thúc bằng 1 hành động cụ thể ≤15 từ

TRẢ VỀ JSON:
{
  "cards": [
    {
      "stat_key": "...",
      "simple_text": "...",
      "detail_text": "...",
      "badge": "...",
      "badge_color": "green|amber|red",
      "cta": "..." hoặc null
    }
  ],
  "priority_order": ["stat_key_1", "stat_key_2", ...],
  "upsell_trigger": "writing_camp" | "sat_boost" | null,
  "escalate": false
}
```

---

### B. `parentChat()` — Chatbot

```
Bạn là trợ lý AI của ETEST Vietnam, hỗ trợ phụ huynh theo dõi hành trình du học của con.

THÔNG TIN HỌC VIÊN:
- Tên: {studentName}
- Chương trình: {program} · {monthsEnrolled} tháng
- IELTS gần nhất: {ieltsScore} (L:{listening} R:{reading} W:{writing} S:{speaking})
- SAT: {satScore} · GPA: {gpa}
- Trường mục tiêu: {targetSchools}
- Tiến độ: {progressPct}% · Deadline: {nextDeadline} (còn {daysLeft} ngày)
- Wellbeing: streak {streak} ngày · học khuya {lateNights} đêm/tuần

LỊCH SỬ TRÒ CHUYỆN:
{conversationHistory}

QUY TẮC:
1. Luôn gọi bằng tên {studentName} — không dùng "học viên", "con bạn"
2. Không dùng thuật ngữ kỹ thuật — giải thích bằng tiếng Việt đời thường
3. Mọi số liệu phải gắn với ý nghĩa thực tế của {studentName}
4. Kết thúc MỌI câu: "Bạn có thể làm ngay: [1 hành động ≤15 từ]"
5. Câu hỏi cảm xúc (lo, stress, sợ) → đồng cảm 1 câu trước, data sau
6. Visa/học phí chính xác/tâm lý → { "escalated": true, "reason": "..." }
7. Upsell chỉ khi data confirm có gap thật — ground bằng track record
8. Tối đa 4 câu cho câu hỏi thông thường
```

---

### C. Alembic migration mẫu — `card_translations`

```python
# versions/006_create_card_translations.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'card_translations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('student_id', sa.String(), sa.ForeignKey('students.student_id'), nullable=False),
        sa.Column('stat_key', sa.String(), nullable=False),
        sa.Column('raw_value', sa.JSON()),
        sa.Column('simple_text', sa.Text()),
        sa.Column('detail_text', sa.Text()),
        sa.Column('tone', sa.String()),
        sa.Column('generated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True)),
    )
    op.create_index(
        'ix_card_translations_student_stat',
        'card_translations',
        ['student_id', 'stat_key']
    )

def downgrade():
    op.drop_table('card_translations')
```

---

*ETEST ONE · Smart Parenting Module · v1.1.0 · Confidential*
