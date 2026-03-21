# ETESTER — Module Specification v4
## Proof of Learning Journey · Hackathon Build

> **Version:** 4.0 — Added Mentor UI + Approach C linking flow  
> **Stack:** Inherits Smart Parenting stack — agent reads codebase before coding  
> **DB Priority:** Reuse Smart Parenting models — only define new entities where needed  
> **Audience:** Human teammates + AI coding models (Claude Opus / Sonnet)  
>
> **[AI READING NOTE]**  
> - Sections marked `[AI]` contain explicit coding instructions. Follow precisely.  
> - Do NOT invent schema, routes, or logic not described here.  
> - Import from `shared.model` first. Only create new models when nothing existing works.  
> - Priority order for every decision: reuse → extend → create new.  
> - Linking flow is Approach C: AI suggest → Student context note (optional) → Mentor confirm.
> - **Read `requirements.txt` and `package.json` before writing any code.** Use existing libraries.
> - If Smart Parenting stack is incompatible with any ETESTER feature → use best-fit modern alternative. Do not force compatibility.
> - **If a Smart Parenting library cannot be reused for a new ETESTER feature, use the best available alternative — do not force an incompatible tool.**

---

## Table of Contents

1. [Concept](#1-concept)
2. [Key Values — Demo highlights](#2-key-values--demo-highlights)
3. [Layer 1 — User View](#3-layer-1--user-view)
4. [Linking Flow — Approach C](#4-linking-flow--approach-c)
5. [Layer 2 — Dev + Tech](#5-layer-2--dev--tech)
6. [Layer 3 — AI Vibe Code](#6-layer-3--ai-vibe-code)
7. [Database Models](#7-database-models)
8. [Artifact Types + Form Schemas](#8-artifact-types--form-schemas)
9. [Artifact Graph](#9-artifact-graph)
10. [Auth Scoring Framework](#10-auth-scoring-framework)
11. [Claude Prompts](#11-claude-prompts)
12. [Component Specs](#12-component-specs)
13. [Signing Chain](#13-signing-chain)
14. [Build Order](#14-build-order)
15. [Demo Script](#15-demo-script)

---

## 1. Concept

**ETESTER** là "con dấu số" của ETEST — một living credential được xây dựng dần dần từ nhiều nguồn đóng góp. Không phải snapshot tĩnh — mà là **proof of process** tích lũy theo thời gian.

### Tại sao không fake được

Mỗi artifact đều có:
- Timestamp thật được hash vào chain
- Contributor xác nhận thật (mentor approve, admin verify)
- AI trace kết nối artifact — mối quan hệ nhân quả có evidence cụ thể
- Auth scoring 7 chiều dựa trên toàn bộ graph — không thể game từng chiều riêng lẻ

Không thể tạo ra 14 tháng hành trình trong 1 đêm — dù AI có giỏi đến đâu.

### Pitch line

> *"In a world where AI can write any essay — ETESTER is the only proof universities can trust."*

### 4 Contributors

| Contributor | Đóng góp | Trust weight |
|---|---|---|
| **Student** | Submit artifacts + context notes cho trace links | Medium |
| **Mentor** | Confirm trace links + approve artifacts + session notes | High |
| **Parent** | Engagement signal từ Smart Parenting Module 1 | Low–Medium |
| **ETEST Manager** | Đóng dấu chính thức · issue badge · spot-check | Highest |

---


---

## 1b. Overall Pipeline

> Đây là toàn bộ luồng dữ liệu của ETESTER từ input đến consumer.  
> Click vào mỗi node trong diagram (chat) để xem chi tiết từng phần.

```
╔══════════════════════════════════════════════════════════════════════╗
║  LANE 1 — INPUT                                                      ║
║                                                                      ║
║  [Student]        [Mentor]        [Parent]       [ETEST Manager]    ║
║  essay·camp·CSR   session·approve  engagement     verify·issue       ║
╚══════════╤═══════════════╤═════════════╤═══════════════╤════════════╝
           │               │             │               │
           ▼               ▼             ▼               ▼
╔══════════════════════════════════════════════════════════════════════╗
║  LANE 2 — AI LAYER (OpenAI / compatible LLM)                         ║
║                                                                      ║
║  [Trace Engine]      [Auth Scorer]        [Narrative Builder]        ║
║  link artifacts      7-dim reasoning      EN + VN story              ║
║  causally            on full graph        from artifact graph        ║
║                                                                      ║
║              ▼─────────────────────────▼                            ║
║                    [Artifact Graph]                                  ║
║         milestones · trace links · auth scores · narrative cache     ║
╚══════════════════════════════════╤═══════════════════════════════════╝
                                   │
                                   ▼
╔══════════════════════════════════════════════════════════════════════╗
║  LANE 3 — VERIFY  (Approach C)                                       ║
║                                                                      ║
║  [Student]            [Mentor]              [Manager]                ║
║  add context note     confirm·reject·modify  sign · issue badge      ║
║                                                                      ║
║  Note: Mentor confirm → re-triggers Auth Scorer + Narrative Builder  ║
║  (feedback loop — dashed arrow back to AI layer)                     ║
║                                                                      ║
║              ▼─────────────────────────▼                            ║
║                     [ETESTERCore]                                    ║
║   skills · auth avg · contributions · narrative · requirements cov.  ║
╚══════════════════════════════════╤═══════════════════════════════════╝
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼               ▼
╔═════════════════════════════════════════════════════════════════════╗
║  LANE 4 — OUTPUT                                                     ║
║                                                                      ║
║  [Dashboard]        [QR Badge]          [Mentor Dashboard]           ║
║  graph·timeline     JWT signed          pending queue·review         ║
║  narrative·stats    scannable                                        ║
║                          │                                           ║
║                          ▼                                           ║
║                   [ETESTERPublic]                                    ║
║         stats · requirements grid · trace summary · narrative EN     ║
╚══════════════════════════╤══════════════════════════════════════════╝
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
╔══════════════════════════════════════════════════════════════════════╗
║  LANE 5 — CONSUMERS                                                  ║
║                                                                      ║
║  [University]       [Scholarship]        [Parent]                    ║
║  scan·verify·admit  verify requirements  share · follow journey      ║
╚══════════════════════════════════════════════════════════════════════╝

Key:
  Trace Engine    → POST /api/etester/trace/:milestoneId (async, internal)
  Auth Scorer     → POST /api/etester/score-auth/:milestoneId (after mentor confirm)
  Narrative       → POST /api/etester/rebuild-narrative/:studentId (after score-auth)
  Feedback loop   → Every mentor confirm re-triggers: Auth → Core → Narrative
  ETESTERCore     → Single source of truth, rebuilt on every confirmed event
  QR Badge        → JWT RS256 signed payload, verify without account
```

## 2. Key Values — Demo highlights

> **[AI]** Đây là những feature PHẢI hoạt động trong demo. Không được cut.

| # | Feature | Demo moment |
|---|---|---|
| KV1 | Artifact graph kết nối milestones | Click "Personal Statement FINAL" → thấy trace chain với evidence |
| KV2 | Auth scoring 7 chiều theo graph context | Click essay → 94% "justified_growth" + 7-dim breakdown |
| KV3 | Approach C linking: AI → Student → Mentor | Student add note → Mentor confirm → link becomes verified |
| KV4 | Mentor dashboard với pending queue | Mentor thấy 3 items chờ verify, click confirm từng cái |
| KV5 | QR badge scannable | Scan bằng điện thoại → ETESTERPublic load đúng |
| KV6 | University requirements coverage | Grid 9 requirements, 8/9 covered ✓ |

---

## 3. Layer 1 — User View

### Flow tổng thể

```
Student nộp artifact + optional context note
         ↓
AI suggest trace links (với evidence)
         ↓
Mentor nhận notification → review queue
         ↓
Mentor: Confirm ✓ | Reject ✗ | Modify ~ (đổi relationship type)
         ↓
Link confirmed → auth scoring chạy → core update → narrative rebuild
         ↓
Manager: spot-check → issue badge → QR
         ↓
University scan QR → verify page
```

### Outputs

**Artifact Graph** — network diagram. Confirmed links = solid. Pending links = dashed. Click node → side panel.

**Timeline** — chronological. Click milestone → trace links + auth score + form + leadership.

**AI Story** — narrative EN + VN, rebuild after each confirmed link.

**QR Badge** — scan → public verify. No account needed.

### Relationship types

| Type | Meaning | Color |
|---|---|---|
| `experience_source` | Camp/CSR/award cung cấp experience cho essay | Teal |
| `revision_of` | Draft là bản sửa của draft trước | Amber |
| `mentor_guided` | Mentor session dẫn đến thay đổi | Purple |
| `skill_applied` | Kỹ năng học ở đây, dùng ở kia | Blue |
| `score_progression` | Test scores cải thiện theo thời gian | Gray |
| `recommends` | Mentor/teacher recommend học viên | Green |

---

## 4. Linking Flow — Approach C

> **[AI]** Đây là core flow của ETESTER. Implement đúng thứ tự. Không skip bước.

### Tại sao Approach C

3 options đã được xét:
- **Approach A** (Student tự link): Trust thấp — university không tin student tự certify.
- **Approach B** (Mentor link thẳng): Mentor bottleneck, student mất agency.
- **Approach C** (AI suggest → Student note → Mentor confirm): Trust cao nhất — AI + student memory + mentor expert verify cùng lúc.

```
AI không biết: intention của student khi link 2 artifacts
Student biết:  context thật — "Tôi dùng PEEL từ camp này"
Mentor biết:   cả 2 artifacts + session history → authority verify
```

### Step-by-step flow

#### Step 1 — Student submit artifact

Student nộp bài/form xong → backend trigger Trace Engine ngay (async).

#### Step 2 — AI generates suggestions

Claude Trace Engine trả về top 3–5 suggested links với evidence.
Saved vào `MilestoneTraceLink` với `confirmed_by_mentor = False`.

#### Step 3 — Student sees suggestions (ArtifactForm post-submit screen)

```
Màn hình hiện sau khi submit:

"AI phát hiện 3 kết nối có thể:"

[ ] Writing Camp — Jul 2025                    [confidence 94%]
    "Essay references thesis workshop from camp"
    Note (optional): ____________________________
    placeholder: "VD: Tôi dùng cách viết thesis từ camp này..."

[ ] Mentor Session #5 — Oct 2025               [confidence 91%]
    "Session focused on structure matches essay changes"
    Note (optional): ____________________________

[ ] CSR Share & Care — Aug 2025                [confidence 88%]
    "Leadership narrative matches CSR coordinator role"
    Note (optional): ____________________________

[Bỏ qua tất cả]     [Gửi cho mentor review →]
```

**Rules:**
- Student KHÔNG confirm/reject — chỉ add note hoặc bỏ qua
- Tất cả suggestions đều được gửi cho mentor kèm student note (nếu có)
- Student note được lưu vào `MilestoneTraceLink.student_context_note`
- Action này không block — student có thể bỏ qua toàn bộ

#### Step 4 — Mentor receives notification

Mentor dashboard hiện badge: "3 items pending review"

#### Step 5 — Mentor reviews (MentorDashboard)

```
Mỗi pending link hiện:

  Writing Camp → Personal Statement Draft #1
  ─────────────────────────────────────────
  AI evidence:     "Essay references thesis workshop from camp"
  Confidence:      94%
  Student note:    "Tôi học cách viết thesis ở camp này và áp dụng vào bài"

  [✓ Confirm]  [✗ Reject]  [~ Modify type ▾]
```

**Mentor actions:**
- `Confirm` → `confirmed_by_mentor = True`, link becomes solid in graph
- `Reject` → `is_active = False`, lưu MentorVerification với action `trace_reject`
- `Modify` → đổi `relationship_type` rồi confirm

#### Step 6 — Post-confirm triggers

Sau mỗi mentor confirm:
1. `auth_scoring.py` chạy lại cho essay liên quan
2. `ETESTERCore` rebuild skills + stats
3. `narrative_cache` invalidated → rebuild async
4. Graph UI update: dashed edge → solid edge

---

## 5. Layer 2 — Dev + Tech

### Stack

> **[AI] — ĐỌC CODEBASE TRƯỚC KHI LÀM BẤT KỲ THỨ GÌ**
>
> ETESTER được build on top của Smart Parenting — cùng repo, cùng codebase.
> Trước khi viết bất kỳ dòng code nào, agent PHẢI:
>
> 1. Đọc `requirements.txt` hoặc `pyproject.toml` → detect backend stack + AI SDK đang dùng
> 2. Đọc `package.json` → detect frontend stack + libraries đang dùng
> 3. Đọc `shared/model.py` (đã có trong context) → biết models nào đã có
> 4. Đọc cấu trúc thư mục hiện tại → hiểu pattern tổ chức code
> 5. **Dùng đúng những gì đã có.** Không install thư viện mới nếu đã có thứ tương đương.
>
> Ví dụ: nếu Smart Parenting dùng `openai` SDK → ETESTER dùng `openai` luôn, không dùng `anthropic`.
> Nếu dùng `pyjwt` → dùng `pyjwt`. Nếu dùng `axios` → dùng `axios`.
> Không assume. Đọc rồi mới code.

**Chỉ những thứ sau là ETESTER thêm mới — chưa có trong Smart Parenting:**

```
Graph UI:  SVG thuần — artifact network diagram, không cần thư viện
```

> `react-qr-code` và `python-jose` JWT đã có sẵn trong `package.json` và `requirements.txt` — không cần install thêm.

**Production only — không build trong hackathon:**
```
W3C VC:    didkit — Ed25519 credential signing
```

### DB priority

```
PRIORITY 1 — Reuse từ model.py (KHÔNG SỬA):
  Student, Mentor, Parent, Milestone, BehavioralLog,
  Conversation, School, Course, User, TimestampMixin

PRIORITY 2 — Extend qua bảng liên kết:
  MilestoneTraceLink  (thêm student_context_note field)
  MilestoneArtifact

PRIORITY 3 — Thực thể mới:
  ArtifactForm · MentorVerification · AuthScoringResult
  ETESTERCore · ETESTERBadge
```

### API Routes

> **[AI]** Implement đúng list này. Không thêm route ngoài list.

```
# Student endpoints
GET  /api/etester/:studentId
     → ETESTERCore + milestones + trace_links + auth_results + narrative

POST /api/etester/contribute
     body: { studentId, milestoneId, formData, artifactText }
     → save ArtifactForm + MilestoneArtifact
     → async: trigger Trace Engine → save suggested links
     → return: { milestone, suggested_links[] }

POST /api/etester/student-note/:traceLinkId
     body: { studentNote: string }
     → update MilestoneTraceLink.student_context_note
     → notify mentor (optional notification)

# Mentor endpoints
GET  /api/etester/mentor/:mentorId/pending
     → list pending trace links + artifacts for this mentor's students
     → return: { pending_links[], pending_approvals[] }

POST /api/etester/verify-trace/:traceLinkId
     body: { mentorId, action: "confirm"|"reject"|"modify",
             new_relationship_type?: string, note?: string }
     → update MilestoneTraceLink
     → save MentorVerification
     → if confirm: trigger auth-score + rebuild-core

POST /api/etester/approve-artifact/:milestoneId
     body: { mentorId, approved: bool, note?: string }
     → update Milestone.mentor_approved
     → save MentorVerification

# AI endpoints (backend triggers, not direct frontend calls)
POST /api/etester/trace/:milestoneId          (internal async)
POST /api/etester/score-auth/:milestoneId     (internal, after verify-trace)
POST /api/etester/rebuild-narrative/:studentId (internal, after score-auth)

# Manager endpoints
POST /api/etester/issue-badge/:studentId
     body: { managerId }
     → sign JWT → save ETESTERBadge → return badge_uid + QR URL

# Public
GET  /api/etester/verify/:badgeUid            (no auth)
```

### File structure

> **Legend:** ✅ đã có — không cần tạo | 🔄 đã có — cần update v4 | 🆕 chưa có — cần tạo mới

```
e-be/
├── shared/
│   ├── model.py                              # ✅ EXISTS — KHÔNG SỬA
│   └── etester_models.py                     # 🆕 CREATE — 7 new models
├── modules/etester/                          # ✅ EXISTS (base structure)
│   ├── router.py                             # 🔄 UPDATE — add new routes
│   ├── schemas.py                            # 🔄 UPDATE — add new schemas
│   ├── models.py                             # ✅ EXISTS
│   ├── repository.py                         # 🔄 UPDATE
│   ├── prompts.py                            # ✅ EXISTS
│   └── services/
│       ├── authenticity.py                   # 🔄 UPDATE → wire to auth_scoring.py
│       ├── badge.py                          # ✅ EXISTS
│       ├── contribute.py                     # 🔄 UPDATE — trigger trace engine
│       ├── rebuild_core.py                   # 🔄 UPDATE — pending counts
│       ├── llm_service.py                    # 🆕 CREATE — 4 prompts via llm_client.py
│       └── auth_scoring.py                   # 🆕 CREATE — 7-dim engine
└── alembic/versions/006_etester_v4.py        # 🆕 CREATE — new tables + fields

e-fe/src/
├── pages/
│   ├── student/StudentEtester.tsx            # 🔄 UPDATE — add pending banner (v4)
│   ├── mentor/MentorEtester.tsx              # 🔄 UPDATE — full MentorDashboard spec
│   └── shared/EtesterPublic.tsx             # 🔄 UPDATE — add trace chain summary (v4)
├── components/
│   ├── shared/
│   │   ├── MilestoneTimeline.tsx             # 🔄 UPDATE — trace panel + student notes
│   │   ├── QrBadge.tsx                       # ✅ EXISTS — no changes
│   │   ├── ContributorDonut.tsx              # ✅ EXISTS — no changes
│   │   └── AuthGauge.tsx                     # ✅ EXISTS — no changes
│   └── etester/                              # 🆕 CREATE subfolder
│       ├── ArtifactGraph.tsx                 # 🆕 CREATE
│       ├── ArtifactForm.tsx                  # 🆕 CREATE (includes post-submit screen)
│       ├── TraceLinkSuggestions.tsx          # 🆕 CREATE — NEW v4
│       ├── MentorTraceReview.tsx             # 🆕 CREATE — NEW v4
│       ├── AuthScoreCard.tsx                 # 🆕 CREATE
│       └── NarrativeCard.tsx                 # 🆕 CREATE
└── api/
    ├── student/index.ts                      # 🔄 UPDATE — add etester endpoints
    └── mentor/index.ts                       # 🔄 UPDATE — add pending endpoint
```

---

## 6. Layer 3 — AI Vibe Code

> **[AI]** Build theo thứ tự. Mỗi step phụ thuộc step trước.

```
Step 1   etester_models.py          7 models + student_context_note field
Step 2   alembic migration          python -m alembic revision --autogenerate
Step 3   Seed data                  18–20 milestones + links (confirmed=True) + forms
Step 4   Claude prompts             Test 4 prompts, verify JSON format
Step 5   API: GET /etester/:id      Full data response
Step 6   API: POST /contribute      + async trace trigger
Step 7   API: Mentor pending + verify-trace
Step 8   ArtifactGraph.jsx          Solid vs dashed edges
Step 9   TraceLinkSuggestions.jsx   Post-submit screen với student notes
Step 10  MentorDashboard.jsx        Pending queue + review cards
Step 11  MilestoneTimeline.jsx      + trace panel + auth breakdown
Step 12  AuthScoreCard.jsx          7-dim breakdown
Step 13  NarrativeCard.jsx          + regenerate
Step 14  QRBadge + ETESTERPublic    Scan test on real phone
```

---

## 7. Database Models

> **[AI]** File: `shared/etester_models.py`

### Quan hệ tổng thể

```
[Từ model.py]
Student ──1:N──► Milestone ──1:1──► MilestoneArtifact (hash + sign)
                     │    └──1:1──► ArtifactForm (form + leadership fields)
                     │
              MilestoneTraceLink
              from_milestone → to_milestone
              student_context_note (NEW)
              confirmed_by_mentor
                     │
Student ──1:1──► ETESTERCore ──1:1──► ETESTERBadge
                     │
              AuthScoringResult (N per essay milestone)

[Feed Smart Parenting → ETESTER]
BehavioralLog  → auth scoring chiều 6 + parent_support_level
Conversation   → parent_engagement_count
```

---

### `MilestoneTraceLink`

```python
class MilestoneTraceLink(Base, TimestampMixin):
    __tablename__ = "milestone_trace_links"

    id:                      int (PK)
    from_milestone_id:       int FK → milestones.id (RESTRICT)
    to_milestone_id:         int FK → milestones.id (RESTRICT)
    student_id:              str FK → students.student_id (CASCADE)

    relationship_type:       str
    # experience_source | revision_of | mentor_guided
    # skill_applied | score_progression | recommends

    evidence:                Text | None    # AI-generated evidence text
    confidence:              float          # 0.0–1.0 (AI confidence)

    # Approach C fields
    student_context_note:    Text | None    # Student's optional explanation
    student_noted_at:        datetime | None

    # Mentor verification
    suggested_by_ai:         bool = True
    confirmed_by_mentor:     bool = False
    confirmed_by_mentor_id:  int FK → mentors.mentor_id | None
    confirmed_at:            datetime | None

    is_active:               bool = True
    # Rule: confirmed=True → is_active cannot be set False
    # Enforce at application layer

    # Constraints:
    # UniqueConstraint(from_milestone_id, to_milestone_id)
    # CheckConstraint confidence 0.0–1.0
    # CheckConstraint relationship_type IN (6 types)
```

---

### `MilestoneArtifact`

```python
class MilestoneArtifact(Base):
    __tablename__ = "milestone_artifacts"

    id:                  int (PK)
    milestone_id:        int FK → milestones.id UNIQUE
    student_id:          str FK → students.student_id

    full_text_content:   Text | None   # AI reads for trace + auth
    artifact_hash:       str(64) | None  # SHA256
    prev_artifact_hash:  str(64) | None

    # 3-stage signing
    vc_signature:        Text | None
    mentor_signed:       bool = False
    admin_signed:        bool = False
    manager_signed:      bool = False
    signed_at:           datetime | None

    created_at:          datetime
```

---

### `ArtifactForm`

```python
class ArtifactForm(Base, TimestampMixin):
    __tablename__ = "artifact_forms"

    id:                      int (PK)
    milestone_id:            int FK → milestones.id UNIQUE
    student_id:              str FK → students.student_id

    activity_type:           str       # See Section 8
    form_version:            str = "1.0"
    form_data:               JSONB = {}  # Schema per type, see Section 8

    # Derived — denormalized for fast query
    blooms_level:            str | None
    skills_practiced:        JSONB = []

    # Leadership — dedicated columns for direct query + aggregate
    had_leadership_role:     bool = False
    leadership_role_title:   str | None
    leadership_team_size:    int | None
    leadership_outcome:      str | None   # max 100 words, measurable

    # Mentor comment — mentor fills, student cannot edit
    mentor_comment:          Text | None
    mentor_comment_by:       int FK → mentors.mentor_id | None
```

---

### `MentorVerification` (append-only)

```python
class MentorVerification(Base):
    __tablename__ = "mentor_verifications"
    # NO updated_at. NO DELETE.

    id:             int (PK)
    milestone_id:   int FK → milestones.id (RESTRICT)
    student_id:     str FK → students.student_id (CASCADE)

    verifier_id:    int
    verifier_type:  str  # "mentor" | "admin" | "manager"

    action_type:    str
    # mentor_approve | mentor_reject | admin_verify | admin_flag
    # trace_confirm  | trace_reject  | trace_modify

    note:           Text | None
    trace_link_id:  int FK → milestone_trace_links.id | None

    created_at:     datetime (immutable)
```

---

### `AuthScoringResult`

```python
class AuthScoringResult(Base):
    __tablename__ = "auth_scoring_results"

    id:                    int (PK)
    milestone_id:          int FK → milestones.id (CASCADE)
    student_id:            str FK → students.student_id (CASCADE)

    auth_score:            int          # 0–100
    verdict:               str
    # justified_growth | consistent | needs_review
    # suspicious_jump  | insufficient_data

    dimension_scores:      JSONB = {}
    # { "d1": { score, weight, note }, ... "d7": { score, weight, note } }
    # JSONB → add new dimensions without migration

    explaining_artifacts:  JSONB = []
    # [{ id, relationship, explains }]

    explanation_en:        Text | None
    explanation_vn:        Text | None
    graph_snapshot:        JSONB = {}

    scored_at:             datetime
```

---

### `ETESTERCore`

```python
class ETESTERCore(Base, TimestampMixin):
    __tablename__ = "etester_core"

    id:                       int (PK)
    student_id:               str FK UNIQUE

    academic_score:           Numeric(5,2) | None
    writing_growth:           Numeric(5,2) | None

    skills:                   JSONB = []
    # [{
    #   skill, evidence_count, artifacts[],
    #   had_formal_role (leadership),
    #   max_team_size, ai_summary
    # }]

    mentor_verifications:     int = 0
    total_contributions:      int = 0
    contributor_breakdown:    JSONB = {}

    # Pending counts — for mentor badge notification
    pending_trace_links:      int = 0
    pending_approvals:        int = 0

    requirements_coverage:    JSONB = {}
    # { english_proficiency, standardized_test, personal_essay,
    #   extracurricular, community_service, leadership_evidence,
    #   academic_record, recommendation_context, awards_honors }

    parent_support_level:     str = "low"
    parent_engagement_count:  int = 0
    institutional_stamp:      bool = False
    stamped_at:               datetime | None
    stamped_by:               int FK → mentors.mentor_id | None
    consistency_score:        int = 0

    narrative_en:             Text | None
    narrative_vn:             Text | None
    narrative_updated_at:     datetime | None
    badge_issued:             bool = False
```

---

### `ETESTERBadge`

```python
class ETESTERBadge(Base):
    __tablename__ = "etester_badges"

    id:               int (PK)
    core_id:          int FK → etester_core.id UNIQUE
    student_id:       str FK → students.student_id

    badge_uid:        str UNIQUE   # "ETR-2026-001234"
    credential_type:  str = "jwt_rs256"
    signed_token:     Text
    issuer_did:       str = "did:web:etest.edu.vn"

    badge_payload:    JSONB = {}
    # name, program, months, milestones, mentor_verified,
    # ielts, sat, auth_avg, essays_approved,
    # leadership_evidence, requirements_coverage

    issued_at:        datetime
    expires_at:       datetime | None
    is_revoked:       bool = False
    revoked_at:       datetime | None
    revoke_reason:    Text | None
    verify_count:     int = 0
    last_verified_at: datetime | None
```

---

## 8. Artifact Types + Form Schemas

> **[AI]** `activity_type` values và `form_data` JSONB schema tương ứng.  
> Leadership fields (`had_leadership_role`, `leadership_role_title`, `leadership_team_size`, `leadership_outcome`) là **dedicated columns** trong `ArtifactForm` — KHÔNG nằm trong `form_data`.

### `ielts_mock` / `sat_mock` / `toefl_mock`
```json
{
  "score_this": 6.5,
  "score_prev": 6.0,
  "score_breakdown": { "listening": 7.0, "reading": 7.0,
                       "writing": 6.0, "speaking": 6.5 },
  "test_center": "ETEST Q3",
  "official": false,
  "weak_areas": ["writing task 1"],
  "strategy_note": "Focus on data description vocabulary"
}
```
Leadership: N/A

---

### `essay_draft` / `essay_final`
```json
{
  "draft_number": 2,
  "topic": "Personal Statement",
  "word_count": 650,
  "target_school": "University of Melbourne",
  "improvement_from_prev": "Stronger thesis, added counter-argument",
  "forward_intent": "Will use in Common App"
}
```
Leadership: N/A

---

### `camp`
```json
{
  "camp_name": "ETEST Writing Camp",
  "organizer": "ETEST Vietnam",
  "duration_days": 21,
  "location": "HCMC",
  "key_skills": ["thesis writing", "PEEL structure"],
  "key_experience": "Led morning discussion sessions",
  "forward_intent": "Apply PEEL in Personal Statement"
}
```
Leadership columns: `had_leadership_role=true`, `leadership_role_title="Morning session facilitator"`, `leadership_team_size=8`, `leadership_outcome="Group improved draft quality by end of week 2"`

---

### `csr`
```json
{
  "org_name": "Share and Care",
  "activity_type": "tutoring",
  "duration_weeks": 12,
  "hours_per_week": 3,
  "beneficiaries": "underprivileged students",
  "beneficiary_count": 15,
  "impact_description": "Helped 15 students pass grade 5 math exam"
}
```
Leadership columns: `had_leadership_role=true`, `leadership_role_title="Volunteer coordinator"`, `leadership_team_size=5`, `leadership_outcome="Organized 3 community events, 50+ attendees"`

---

### `extracurricular`
```json
{
  "org_name": "English Club THPT Gia Dinh",
  "role": "Vice President",
  "duration_months": 8,
  "commitment_hrs_per_week": 4,
  "description": "Organized weekly debates and English movies night",
  "achievements": "Grew membership from 20 to 45 in one semester"
}
```
Leadership columns: `had_leadership_role=true`, `leadership_role_title="Vice President"`, `leadership_team_size=45`, `leadership_outcome="Grew club 2x, organized 12 events"`

---

### `mentor_session`
```json
{
  "focus_area": "Personal Statement structure",
  "action_items": ["Rewrite opening hook", "Add specific example"],
  "readiness_level": 4,
  "student_note": "Finally understood how to open with a scene"
}
```
Leadership: N/A

---

### `consultation`
```json
{
  "topic": "School list finalization",
  "schools_discussed": ["Melbourne", "RMIT", "Monash"],
  "decisions_made": "Set Melbourne as EA target",
  "next_steps": ["Complete supplements by Nov 1"]
}
```
Leadership: N/A

---

### `recommendation_letter`
```json
{
  "recommender_name": "Nguyen Van Cuong",
  "recommender_role": "AMP Mentor",
  "recommender_org": "ETEST Vietnam",
  "relationship": "14-month AMP mentor",
  "relationship_duration_months": 14,
  "submitted_to": ["University of Melbourne", "RMIT"],
  "date_sent": "2026-01-15",
  "key_themes": ["intellectual curiosity", "leadership", "resilience"],
  "letter_excerpt": "Optional — mentor cho phép share 1-2 sentences"
}
```
Leadership: N/A

---

### `academic_record`
```json
{
  "school_name": "THPT Gia Dinh",
  "semester": "2024-2025 HK1",
  "grade_system": "10-point",
  "subjects": [
    { "name": "Toán", "grade": 9.2, "credit_hours": 4 },
    { "name": "Văn",  "grade": 8.8, "credit_hours": 3 },
    { "name": "Anh",  "grade": 9.5, "credit_hours": 3 }
  ],
  "gpa_this_term": 9.1,
  "cumulative_gpa": 9.0,
  "rank_in_class": "3/45"
}
```
> **Note:** Data imbalance across grade systems is intentional and acceptable. Store raw. Do not normalize. University reads as-is.

Leadership: N/A

---

### `award_honor`
```json
{
  "award_name": "First Prize — National English Essay Competition",
  "issuing_org": "Ministry of Education Vietnam",
  "level": "national",
  "year": 2025,
  "category": "academic",
  "description": "Essay on climate change and youth responsibility",
  "certificate_issued": true
}
```
Leadership: N/A

---

## 9. Artifact Graph

> **[AI]** Component: `ArtifactGraph.jsx`

### Node visual rules

| Node type | Shape | Color |
|---|---|---|
| `essay_draft`, `essay_final` | Rounded rect | Amber |
| `camp`, `csr`, `extracurricular`, `award_honor` | Circle | Teal |
| `ielts_mock`, `sat_mock` | Circle | Gray |
| `mentor_session`, `recommendation_letter` | Rounded rect | Purple |
| `academic_record` | Rounded rect | Blue |
| `ETESTERCore` | Large rounded rect filled | Purple dark |

**Node badges:**
- `mentor_approved = true` → thick border 2px
- Unconfirmed links TO this node → small amber dot top-right "⏳"
- `had_leadership_role = true` → small "L" badge bottom-right

### Edge visual rules

| State | Style |
|---|---|
| `confirmed_by_mentor = true` | Solid stroke, full opacity |
| `confirmed_by_mentor = false` | Dashed stroke, opacity 0.4, amber dot at midpoint |
| `revision_of` | Thicker 2.5px |
| `contributes_to` (→ Core) | Blue dashed |

### Interaction

```
Default:     all nodes + edges visible
Click node:  connected nodes → opacity 1.0
             unconnected → opacity 0.15
             connected edges → solid + show label
             unconnected edges → opacity 0.08
Click again: reset

Side panel on click:
  Title + date + type badge
  Auth score chip (color by verdict) — essays only
  Leadership badge if had_leadership_role
  Trace links list:
    Each: relationship chip + confidence% + status
    confirmed: "✓ Mentor verified" green
    pending:   "⏳ Awaiting mentor" amber
    student_note (if exists): italic below link
  "View in timeline →" button
```

### Seed trace links (pre-confirmed for demo)

```python
SEED_TRACE_LINKS = [
  { "from": "camp_001",     "to": "essay_draft_001",
    "type": "experience_source", "confidence": 0.94,
    "evidence": "Essay draft references Writing Camp thesis workshop",
    "student_context_note": "Tôi học cách viết thesis ở camp và áp dụng ngay vào Draft #1",
    "confirmed_by_mentor": True },

  { "from": "csr_003",      "to": "essay_draft_001",
    "type": "experience_source", "confidence": 0.88,
    "evidence": "Leadership narrative matches CSR coordinator role",
    "student_context_note": "Câu chuyện leadership trong essay lấy từ trải nghiệm CSR",
    "confirmed_by_mentor": True },

  { "from": "session_005",  "to": "essay_draft_001",
    "type": "mentor_guided", "confidence": 0.91,
    "evidence": "Session focused on structure — draft shows new PEEL format",
    "confirmed_by_mentor": True },

  { "from": "essay_draft_001", "to": "essay_draft_002",
    "type": "revision_of", "confidence": 0.97,
    "evidence": "Opening preserved, body restructured per session notes",
    "confirmed_by_mentor": True },

  { "from": "session_007",  "to": "essay_draft_002",
    "type": "mentor_guided", "confidence": 0.93,
    "evidence": "Counter-argument added per session feedback",
    "confirmed_by_mentor": True },

  { "from": "essay_draft_002", "to": "essay_final_001",
    "type": "revision_of", "confidence": 0.98,
    "evidence": "Final preserves Draft 2 structure, refined intro",
    "confirmed_by_mentor": True },

  { "from": "session_007",  "to": "essay_final_001",
    "type": "mentor_guided", "confidence": 0.89,
    "evidence": "Mentor approved after final session review",
    "confirmed_by_mentor": True },

  { "from": "rec_letter_001", "to": "essay_final_001",
    "type": "recommends", "confidence": 1.0,
    "evidence": "Mentor formally recommends to target universities",
    "confirmed_by_mentor": True },

  { "from": "award_001",    "to": "essay_final_001",
    "type": "experience_source", "confidence": 0.82,
    "evidence": "Essay references national competition experience",
    "student_context_note": "Tôi viết về bài thi quốc gia trong essay",
    "confirmed_by_mentor": True },
]
```

---

## 10. Auth Scoring Framework

> **[AI]** File: `backend/api/etester/auth_scoring.py`  
> Prerequisite: Pull confirmed trace_links TRƯỚC khi chạy. Auth needs graph data.  
> Trigger: After each `verify-trace` confirm action.

### Core principle

> **"Bài này có fit vào toàn bộ hành trình của học viên này không?"**

Không hỏi "AI viết bài này không?" — hỏi "Growth này có được giải thích bởi graph không?"

### 7 Dimensions

| # | Dimension | Weight | Key question |
|---|---|---|---|
| D1 | Growth explained by artifacts | 0.25 | Có artifact linked giải thích growth không? |
| D2 | Topic familiarity matches history | 0.15 | Vocabulary/topic match artifact history? |
| D3 | Narrative timeline consistent | 0.15 | Events referenced có artifacts prior không? |
| D4 | Error pattern consistent | 0.15 | Errors giảm dần hay biến mất đột ngột? |
| D5 | Mentor notes corroborate | 0.20 | Mentor notes align với essay quality? |
| D6 | Behavioral context matches | 0.05 | Study hours/streak match submission quality? |
| D7 | Structural fingerprint consistent | 0.05 | Writing structure consistent với history? |

### D1 — Growth explained (most important)

| Situation | Verdict |
|---|---|
| Score tăng + artifact linked (confidence ≥ 0.7, mentor confirmed) | `justified_growth` |
| Score tăng + mentor session note aligned | `justified_growth` |
| Score ổn định qua nhiều bài | `consistent` |
| Score nhảy + không artifact nào explain | `suspicious_jump` |
| Chưa đủ writing samples (< 2) | `insufficient_data` |

> **Rule tuyệt đối:** Nếu `explaining_artifacts` có ít nhất 1 artifact với confidence ≥ 0.7 VÀ confirmed_by_mentor = True VÀ D5 ≥ 80 → verdict PHẢI là `justified_growth`. Không được flag `suspicious_jump`.

### Verdict logic

```python
def compute_verdict(
    dimension_scores: dict,
    explaining_artifacts: list,
    writing_sample_count: int
) -> str:
    if writing_sample_count < 2:
        return "insufficient_data"

    weighted = sum(d["score"] * d["weight"]
                   for d in dimension_scores.values())

    d1 = dimension_scores["d1_growth_explained"]
    d5 = dimension_scores["d5_mentor_corroborate"]["score"]

    # Justified growth: large increase but explained
    if d1.get("growth_delta", 0) > 10 and explaining_artifacts:
        if d5 >= 80:
            return "justified_growth"

    if weighted >= 85: return "consistent"
    if weighted >= 65: return "needs_review"
    if d1.get("suspicious") and not explaining_artifacts:
        return "suspicious_jump"
    return "needs_review"
```

### Output format

```json
{
  "auth_score": 94,
  "verdict": "justified_growth",
  "dimension_scores": {
    "d1_growth_explained":       { "score": 95, "weight": 0.25,
      "growth_delta": 16,
      "note": "Growth +16pts explained by Writing Camp (confidence 0.94, mentor confirmed)" },
    "d2_topic_familiarity":      { "score": 92, "weight": 0.15,
      "note": "Leadership claims match camp role + CSR coordinator artifact" },
    "d3_narrative_timeline":     { "score": 90, "weight": 0.15,
      "note": "All referenced events have prior artifacts with correct dates" },
    "d4_error_pattern":          { "score": 88, "weight": 0.15,
      "note": "Comma splice reduced gradually — consistent with mentor feedback" },
    "d5_mentor_corroborate":     { "score": 96, "weight": 0.20,
      "note": "Mentor session #7 improvement aligns with final essay quality" },
    "d6_behavioral_context":     { "score": 85, "weight": 0.05,
      "note": "3.2h/day average 2 weeks before submission" },
    "d7_structural_fingerprint": { "score": 91, "weight": 0.05,
      "note": "Paragraph opening style consistent with all previous drafts" }
  },
  "explaining_artifacts": [
    { "id": "camp_001", "relationship": "experience_source",
      "explains": "vocabulary_expansion + leadership narrative",
      "student_note": "Tôi học cách viết thesis ở camp và áp dụng vào bài" }
  ],
  "explanation_en": "Score increase from 78% to 94% is fully explained by verified artifacts: Writing Camp (Jul 2025) provided vocabulary foundation; Mentor Session #7 guided counter-argument development. Growth trajectory is consistent with expected learning progression.",
  "explanation_vn": "Điểm tăng từ 78% lên 94% được giải thích đầy đủ bởi các artifact đã xác nhận: Trại hè Writing cung cấp nền tảng từ vựng; Buổi học mentor #7 hướng dẫn lập luận phản biện."
}
```

### Extensibility note

> `dimension_scores` là JSONB — thêm dimension mới chỉ cần update Claude prompt + weight distribution. Không cần DB migration.

---

## 11. LLM Prompts

> **[AI]** File: `e-be/modules/etester/services/llm_service.py`  
> Project dùng **OpenAI SDK** (không phải Anthropic). Reuse `shared/clients/llm_client.py` đã có sẵn — đừng tạo mới.

### Helper

```python
# e-be/modules/etester/services/llm_service.py
# Dùng llm_client.py đã có trong shared/clients/ — KHÔNG import anthropic
from shared.clients.llm_client import call_json, call_text
import json
from typing import Any

def parse_json(text: str, fallback: Any = None) -> Any:
    try:
        clean = text.replace("```json","").replace("```","").strip()
        return json.loads(clean)
    except Exception:
        return fallback if fallback is not None else {}

# call_json(prompt, system, max_tokens) → dict  (đã có timeout + retry + JSON fallback)
# call_text(prompt, system, max_tokens) → str
```

---

### Prompt 1 — Trace Engine

```python
async def trace_artifact(
    new_milestone: dict,
    artifact_history: list[dict],
    form_data: dict | None = None
) -> list[dict]:

    top5 = sorted(
        [a for a in artifact_history if a["date"] < new_milestone["date"]],
        key=lambda x: x["date"]
    )[-5:]

    form_ctx = f"\nForm data: {json.dumps(form_data)}" if form_data else ""

    prompt = f"""
You are analyzing learning artifact connections for a Vietnamese student
building a verified study portfolio (ETESTER).

NEW ARTIFACT:
- type: {new_milestone['type']}
- title: {new_milestone['title']}
- date: {new_milestone['date']}
- summary: {new_milestone.get('ai_summary', 'N/A')}
{form_ctx}

RECENT HISTORY (up to 5 prior artifacts):
{chr(10).join([
    f"- id:{a['id']} [{a['date']}] ({a['type']}) {a['title']}: {a.get('ai_summary','')}"
    for a in top5
])}

Find CAUSAL relationships only — not just "happened before" but "actually contributed to".
Only return links with genuine evidence from content or form data.

Relationship types: experience_source | revision_of | mentor_guided |
                    skill_applied | score_progression | recommends

Return JSON only — empty array if no genuine links:
[{{
  "from_milestone_id": "id",
  "relationship_type": "type",
  "evidence": "specific observation",
  "confidence": 0.0-1.0
}}]
"""
    result = await call_json(prompt, max_tokens=600)
    return result if isinstance(result, list) else []
```

---

### Prompt 2 — Auth Scorer (7 dimensions)

```python
async def score_auth_7dim(
    new_essay_text: str,
    writing_samples: list[dict],
    confirmed_trace_links: list[dict],
    mentor_notes: list[str],
    behavioral_stats: dict,
    student_name: str,
    leadership_artifacts: list[dict]
) -> dict:

    explaining = [
        t for t in confirmed_trace_links
        if t["relationship_type"] in ["experience_source", "mentor_guided"]
        and t["confidence"] >= 0.7
        and t["confirmed_by_mentor"]
    ]

    # Include student_context_notes in explaining artifacts
    explaining_with_notes = [
        { **t, "student_note": t.get("student_context_note", "") }
        for t in explaining
    ]

    prompt = f"""
You are scoring writing authenticity for {student_name}.

CORE PRINCIPLE: Ask "Does this essay fit this student's complete journey?"
NOT "Did AI write this?"

IMPORTANT RULES:
1. If explaining_artifacts exist (confidence ≥ 0.7, mentor confirmed) AND
   D5 (mentor corroborate) ≥ 80 → verdict MUST be "justified_growth"
2. Student context notes (their own explanation) are strong evidence
3. Vietnamese L1 interference patterns are authentic markers — do not penalize
4. Gradual error reduction with mentor sessions = expected growth

HISTORICAL WRITING:
{chr(10).join([f"[{s['date']}] ({s['type']}): {s['content'][:400]}" for s in writing_samples])}

NEW ESSAY:
{new_essay_text[:1200]}

CONFIRMED TRACE LINKS (mentor-verified artifacts that explain this essay):
{chr(10).join([
    f"- {t.get('from_title','')} ({t['relationship_type']}, conf {t['confidence']}): {t['evidence']}"
    + (f"\n  Student note: {t['student_note']}" if t.get('student_note') else "")
    for t in explaining_with_notes
]) or "None confirmed yet"}

MENTOR NOTES (from linked sessions):
{chr(10).join(mentor_notes) or "No linked mentor notes"}

BEHAVIORAL CONTEXT:
avg_hours/day: {behavioral_stats.get('avg_hours','?')}
streak: {behavioral_stats.get('streak','?')} days
late_nights: {behavioral_stats.get('late_nights', 0)}

LEADERSHIP CONTEXT:
{chr(10).join([f"- {a['title']}: {a.get('leadership_role_title')}, {a.get('leadership_team_size')} ppl" for a in leadership_artifacts]) or "None documented"}

Score each dimension 0-100:
d1_growth_explained (0.25) — growth explained by graph artifacts?
d2_topic_familiarity (0.15) — topic knowledge matches artifact history?
d3_narrative_timeline (0.15) — essay references have prior artifacts?
d4_error_pattern (0.15) — error patterns consistent with history?
d5_mentor_corroborate (0.20) — mentor notes align with essay quality?
d6_behavioral_context (0.05) — study behavior supports submission?
d7_structural_fingerprint (0.05) — writing structure consistent?

Return JSON only:
{{
  "auth_score": 0-100,
  "verdict": "justified_growth|consistent|needs_review|suspicious_jump|insufficient_data",
  "dimension_scores": {{
    "d1_growth_explained":       {{"score":0-100,"growth_delta":0,"note":"..."}},
    "d2_topic_familiarity":      {{"score":0-100,"note":"..."}},
    "d3_narrative_timeline":     {{"score":0-100,"note":"..."}},
    "d4_error_pattern":          {{"score":0-100,"note":"..."}},
    "d5_mentor_corroborate":     {{"score":0-100,"note":"..."}},
    "d6_behavioral_context":     {{"score":0-100,"note":"..."}},
    "d7_structural_fingerprint": {{"score":0-100,"note":"..."}}
  }},
  "explanation_en": "1-2 sentences",
  "explanation_vn": "1-2 câu tiếng Việt"
}}
"""
    result = await call_json(prompt, max_tokens=1000)
    return result or {
        "auth_score": 85, "verdict": "insufficient_data",
        "dimension_scores": {},
        "explanation_en": "Insufficient data for full analysis.",
        "explanation_vn": "Chưa đủ dữ liệu."
    }
```

---

### Prompt 3 — Narrative Builder

```python
async def build_narrative(
    student: dict,
    milestones: list[dict],
    etester_core: dict
) -> dict:

    completed = [m for m in milestones if m["status"] == "completed"]
    leadership = [m for m in completed if m.get("form", {}).get("had_leadership_role")]

    prompt = f"""
Build a verified learning credential narrative for {student['name']},
{student['months_enrolled']} months in {student['program']} at ETEST Vietnam.

Verified milestones (chronological):
{chr(10).join([
    f"- {m['date']}: [{m['type']}] {m['title']}"
    + (f" score:{m['score']}" if m.get('score') else "")
    + (f" auth:{m['auth_score']}%" if m.get('auth_score') else "")
    + (" ✓mentor" if m.get('mentor_approved') else "")
    for m in completed
])}

Leadership evidence:
{chr(10).join([f"- {m['title']}: {m['form']['leadership_role_title']} ({m['form']['leadership_team_size']} people) → {m['form']['leadership_outcome']}" for m in leadership]) or "None documented"}

Requirements covered: {json.dumps(etester_core.get('requirements_coverage', {}))}

Write TWO paragraphs:
1. English (university): Professional, evidence-based. Reference actual dates.
   Show progression. Highlight leadership if present. No generic phrases.
2. Vietnamese (parents): Warm, plain language. 30-second read. No jargon.

Return JSON: {{"narrative_en": "...", "narrative_vn": "..."}}
"""
    result = await call_json(prompt, max_tokens=900)
    return result or {
        "narrative_en": "Narrative being generated...",
        "narrative_vn": "Đang tạo..."
    }
```

---

### Prompt 4 — Leadership Aggregator

```python
async def aggregate_leadership(
    student_name: str,
    leadership_artifacts: list[dict]
) -> dict:

    if not leadership_artifacts:
        return {"has_leadership": False}

    prompt = f"""
Synthesize leadership evidence for {student_name} from verified activities.

Activities (all mentor/admin confirmed):
{chr(10).join([
    f"- [{a['date']}] {a['title']}: role={a.get('leadership_role_title')}, "
    f"team={a.get('leadership_team_size')}, outcome={a.get('leadership_outcome')}"
    for a in leadership_artifacts
])}

Be specific and evidence-based. Do not overstate.

Return JSON:
{{
  "has_leadership": true,
  "evidence_count": {len(leadership_artifacts)},
  "max_team_size": <max>,
  "duration_months": <span first to last>,
  "ai_summary": "2 sentences, specific",
  "key_roles": ["role 1", "role 2"],
  "credibility": "high|medium|low"
}}
"""
    result = await call_json(prompt, max_tokens=400)
    return result or {"has_leadership": False}
```

---

## 12. Component Specs

> **[AI]** Actual paths: `e-fe/src/components/etester/` (🆕 new subfolder) và `e-fe/src/pages/` (existing). Extensions là `.tsx` không phải `.jsx`. Xem legend: ✅ = no change, 🔄 = update existing, 🆕 = create new.

---

### `ArtifactGraph.tsx` — 🆕 CREATE `e-fe/src/components/etester/ArtifactGraph.tsx`

```
Props:
  milestones: Milestone[]
  traceLinks: TraceLink[]    # includes student_context_note, confirmed_by_mentor
  onNodeSelect: (id) => void

Node badges:
  mentor_approved=true       → thick border 2px
  has pending unconfirmed links → amber dot "⏳" top-right
  had_leadership_role=true   → "L" badge bottom-right

Edge states:
  confirmed_by_mentor=true  → solid, full opacity
  confirmed_by_mentor=false → dashed 0.4 opacity + amber midpoint dot

Side panel on click:
  Title + date + type
  Auth score chip (essays only)
  Leadership summary (if had_leadership_role)
  Trace links list:
    relationship chip + confidence%
    "✓ Mentor verified" green OR "⏳ Awaiting mentor" amber
    student_context_note in italic below (if exists)
  "View in timeline →"
```

---

### `TraceLinkSuggestions.tsx` — 🆕 CREATE `e-fe/src/components/etester/TraceLinkSuggestions.tsx`

Shown immediately after student submits artifact (post-submit screen).

```
Props:
  suggestions: TraceLink[]    # AI-suggested, unconfirmed
  onNotesSubmit: (notes: {[traceLinkId]: string}) => void
  onSkip: () => void

Layout:
  Header: "AI phát hiện {N} kết nối có thể"
  Subtext: "Xem lại và thêm ghi chú nếu muốn — mentor sẽ xác nhận"

  For each suggestion:
    ┌─────────────────────────────────────────────┐
    │ [teal dot] Writing Camp — Jul 2025          │
    │            relationship: experience_source  │
    │            confidence: 94%                  │
    │                                             │
    │ AI: "Essay references thesis workshop"      │
    │                                             │
    │ Ghi chú của bạn (tùy chọn):                │
    │ [________________________________]          │
    │  VD: Tôi học cách viết thesis ở camp này... │
    └─────────────────────────────────────────────┘

  Bottom actions:
    [Bỏ qua tất cả]    [Gửi cho mentor review →]

Rules:
  - Student does NOT confirm/reject links — only adds optional note
  - "Bỏ qua" sends all suggestions to mentor WITHOUT notes
  - "Gửi" sends suggestions WITH notes to mentor
  - Either action saves notes to MilestoneTraceLink.student_context_note
  - Non-blocking: student can leave page anytime
```

---

### `MentorEtester.tsx` — 🔄 UPDATE `e-fe/src/pages/mentor/MentorEtester.tsx` (full MentorDashboard spec)

> File đã tồn tại nhưng chưa có pending queue. Cần refactor thành full dashboard theo spec dưới đây.

Main page for mentor. Route: `/mentor/dashboard`

```
Props: none (uses auth context for mentorId)

Layout:
  Header: "Mentor Dashboard" + mentor name + "Powered by ETEST"

  Pending queue section:
    Title: "Cần xác nhận ({total_pending})"
    Two tabs:
      [Trace Links ({N})]  [Artifact Approvals ({N})]

    Tab 1 — Trace Links:
      List of MentorTraceReview cards (see below)
      Sorted by: student name → date submitted

    Tab 2 — Artifact Approvals:
      List of pending milestone approvals
      Each: student name + milestone title + date + type badge
             [✓ Approve]  [✗ Reject]  + optional note input

  My students section:
    Summary cards per student:
      Student name + program + total contributions
      Progress bar (ETESTERCore.total_contributions)
      "View ETESTER →" link
```

---

### `MentorTraceReview.tsx` — 🆕 CREATE `e-fe/src/components/etester/MentorTraceReview.tsx`

Single trace link review card. Used inside `MentorDashboard`.

```
Props:
  traceLink: MilestoneTraceLink (with from/to milestone details)
  onConfirm: (id, newType?) => void
  onReject:  (id, note) => void

Layout:
  ┌──────────────────────────────────────────────────┐
  │ [Student name] · submitted {relative date}       │
  │                                                  │
  │ Writing Camp (Jul 2025)                          │
  │        ──[experience_source]──►                  │
  │ Essay Draft #1 (Oct 2025)                        │
  │                                                  │
  │ AI evidence:                                     │
  │ "Essay references thesis workshop from camp"     │
  │ Confidence: 94%                                  │
  │                                                  │
  │ Student note:                                    │
  │ "Tôi học cách viết thesis ở camp và áp dụng..." │
  │                                                  │
  │ Relationship: [experience_source ▾] (editable)  │
  │                                                  │
  │  [✓ Confirm]    [✗ Reject]                       │
  │  Note (optional): [_____________________]        │
  └──────────────────────────────────────────────────┘

Rules:
  - Relationship type dropdown is editable before confirm (Modify flow)
  - Confirm saves: confirmed_by_mentor=True, relationship_type (possibly changed)
  - Reject saves: is_active=False + MentorVerification record
  - Both save MentorVerification with action trace_confirm or trace_reject
  - After confirm: trigger POST /api/etester/score-auth/:milestoneId (async)
```

---

### `MilestoneTimeline.tsx` — 🔄 UPDATE `e-fe/src/components/shared/MilestoneTimeline.tsx`

> File đã tồn tại. Chỉ cần bổ sung: trace links panel, student notes hiển thị, auth score breakdown, `⏳ pending` badge.

```
Props:
  milestones: Milestone[]
  traceLinks: TraceLink[]
  authResults: AuthScoringResult[]

Filter tabs: All | Essay | Academic | Activities | Verified

Each milestone row:
  Colored dot (contributor_type)
  Title + relative date
  Score badge (if exists)
  Auth score chip (essays: color by verdict)
  "✓ Mentor" tag (if mentor_approved)
  "L" leadership badge (if had_leadership_role)
  "⏳ {N} pending" badge (if unconfirmed trace links)

Click → side panel:
  Full details + form_data summary
  Leadership fields (if applicable)
  Trace links with status + student notes
  Auth score breakdown (if essay)
```

---

### `AuthScoreCard.tsx` — 🆕 CREATE `e-fe/src/components/etester/AuthScoreCard.tsx`

```
Props: authResult: AuthScoringResult

  Large score circle (94%) — green/amber/red by verdict
  Verdict badge: justified_growth | consistent | needs_review | etc.
  Explanation EN (1-2 sentences)

  Expandable "Score breakdown":
    7 rows: dimension name + score bar + note
    Bar colors: >85 green · 65-85 amber · <65 red
    Weights shown as small text

  If verdict = justified_growth:
    "Explaining artifacts" chips with student notes
```

---

### `NarrativeCard.tsx` — 🆕 CREATE `e-fe/src/components/etester/NarrativeCard.tsx`

```
Props: narrativeEn, narrativeVn, onRegenerate, loading

  Tab: English | Tiếng Việt
  Paragraph text
  Badge: "Generated by AI from verified data"
  Button: "Refresh ↻" → POST /rebuild-narrative
  Loading: 3-line skeleton
  Fallback: cached if timeout
```

---

### `EtesterPublic.tsx` — 🔄 UPDATE `e-fe/src/pages/shared/EtesterPublic.tsx`

> File đã tồn tại. Bổ sung v4: mục **6 — Trace chain summary** và **5 — Leadership summary** chưa có.

```
Route: /etester/verify/:badgeUid  (no auth)

  1. Trust header: ETEST logo + green ✓ + "Verified by ETEST Vietnam"
  2. Student identity: name + program + months
  3. Requirements coverage grid: 9 items, green ✓ or gray —
  4. Verified stats table (from badge_payload)
  5. Leadership summary (if has_leadership)
  6. Trace chain summary:
     "Personal Statement verified through 9 connected artifacts,
      all mentor-confirmed."
  7. Narrative EN (1 paragraph)
  8. Issuer: ETEST Vietnam · etest.edu.vn
  9. Footer: issued_at · "For verification purposes only"
```

---

### `StudentEtester.tsx` — 🔄 UPDATE `e-fe/src/pages/student/StudentEtester.tsx`

> File đã tồn tại. Bổ sung v4: **Pending banner** (amber strip khi `pending_trace_links > 0`) và kết nối `ArtifactGraph` + `NarrativeCard` mới.

```
Route: /etester/:studentId

Layout (top to bottom):
  Header: ETESTER seal + student name + "ETEST Verified Learner"
          Share + Download QR buttons

  Pending banner (if pending_trace_links > 0):
    amber strip: "Your mentor has {N} connections to review"

  Stats row: 4 metric cards
    Total contributions · Mentor verified · Avg auth% · Months

  Two columns:
    Left:  Contributor donut (Recharts)
    Right: NarrativeCard

  ArtifactGraph (full width)

  MilestoneTimeline (full width)

  QRBadge section
```

---

## 13. Signing Chain

```
Mentor sign (per artifact)
    → confirms content is authentic
    → MilestoneArtifact.mentor_signed = True

Admin sign (process verification)
    → auto-trigger after mentor sign (can be manual)
    → MilestoneArtifact.admin_signed = True

Manager issue badge (final seal)
    → reviews ETESTERCore.pending_trace_links == 0
    → reviews requirements_coverage
    → signs JWT with ETEST private key
    → ETESTERBadge created
```

### JWT payload

```python
payload = {
    "v": "1",
    "badge_uid": f"ETR-{year}-{core.id:06d}",
    "name": student.name,
    "program": student.program,
    "months": student.months_enrolled,
    "milestones": len(completed),
    "mentor_verified": core.mentor_verifications,
    "ielts": ielts_score,
    "sat": sat_score,
    "auth_avg": core.consistency_score,
    "essays_approved": essays_approved_count,
    "leadership_evidence": leadership_data.get("has_leadership"),
    "leadership_summary": leadership_data.get("ai_summary"),
    "requirements_coverage": core.requirements_coverage,
    "issued": today,
    "issuer": "ETEST Vietnam",
    "iss": "did:web:etest.edu.vn",
    "exp": expires_timestamp
}
```

### Production path

```
JWT RS256 (demo) → W3C VC Ed25519 (production)
  · Generate Ed25519 keypair → AWS Secrets Manager
  · Publish did.json → etest.edu.vn/.well-known/did.json
  · pip install didkit → replace jwt.encode()
```

---

## 14. Build Order

```
H0–H2   Data + Migration
        ├── shared/etester_models.py       (🆕 7 new models + student_context_note)
        ├── modules/etester/services/      (🔄 update contribute, rebuild_core)
        ├── alembic revision --autogenerate -m "etester_v4"
        ├── alembic upgrade head
        └── Seed: 18–20 milestones + 9 trace links (confirmed) + forms

H2–H4   Backend
        ├── llm_service.py — 4 prompts via llm_client.py (OpenAI, không phải Anthropic)
        ├── auth_scoring.py — 7-dim engine
        ├── JWT sign/verify (dùng python-jose đã có sẵn)
        ├── GET /etester/:id → full response
        ├── POST /contribute → trace trigger async
        └── GET /mentor/:id/pending + POST /verify-trace

H4–H7   Frontend — Student view
        ├── ETESTERDashboard layout (H4)
        ├── ArtifactGraph: solid vs dashed edges (H4–H6)
        ├── TraceLinkSuggestions post-submit screen (H5–H6)
        └── MilestoneTimeline + side panel (H6–H7)

H7–H9   Frontend — Mentor view + AI
        ├── MentorDashboard: pending queue (H7–H8)
        ├── MentorTraceReview card: confirm/reject/modify (H7–H8)
        ├── AuthScoreCard: 7-dim breakdown (H8)
        └── NarrativeCard + regenerate (H8–H9)

H9–H10  QR + Deploy
        ├── QRBadge + ETESTERPublic (requirements coverage grid)
        ├── Railway + Vercel deploy
        └── Scan QR on real phone test
```

### Seed data — 18 milestones Minh Anh

```
Sep 2025  ielts_mock #1       5.5
Oct 2025  mentor_session #1   focus: basics
Nov 2025  ielts_mock #2       6.0
Dec 2025  camp                Writing Camp · leadership: 8 ppl
Jan 2026  csr                 Share & Care · leadership: coordinator 5 ppl
Feb 2026  mentor_session #5   focus: essay structure
Mar 2026  essay_draft #1      auth: 78% (seed AuthScoringResult)
Apr 2026  mentor_session #7   focus: counter-argument
May 2026  essay_draft #2      auth: 87% verdict: justified_growth
Jun 2026  ielts_mock #3       6.5 · target_achieved
Jul 2026  extracurricular     English Club VP · leadership: 45 members
Aug 2026  sat_mock #1         1280
Sep 2026  award_honor         National competition · national level
Oct 2026  academic_record     HK1 GPA 9.1
Nov 2026  sat_mock #2         1320
Dec 2026  recommendation_letter  Mentor Cuong → Melbourne + RMIT
Jan 2027  mentor_session #12  approve PS
Feb 2027  essay_final         auth: 94% justified_growth ✓ approved
```

---

## 15. Demo Script

**Minh Anh — 17t · IELTS 6.5 · SAT 1320 · 14 tháng AMP**

```
[Student view — 2 phút]
1. Dashboard: 4 stats + requirements coverage 8/9
2. Artifact Graph: click Personal Statement Final
   → Trace chain highlights: Camp → CSR → Draft#2 → Final
   → Solid edges = mentor confirmed · student notes visible
3. Auth score: 94% justified_growth
   → "Growth explained by Writing Camp + 2 mentor sessions"
   → Show 7-dim breakdown

[Mentor view — 1 phút]
4. Switch to MentorDashboard
   → Pending queue: "3 trace links awaiting review"
   → Click 1 link: thấy AI evidence + student context note
   → Click "✓ Confirm" → edge turns solid in graph live

[QR — 30 giây]
5. Back to student view → QR Badge
   → Scan bằng điện thoại
   → ETESTERPublic: verified stats + trace chain summary + narrative

Close: "Khi AI viết được mọi thứ — ETESTER là bằng chứng duy nhất university tin."
```

### Q&A

| Câu hỏi | Trả lời |
|---|---|
| Ai link artifacts? | AI suggest · Student add context · Mentor confirm. Không ai làm một mình. |
| Auth score accurate không? | 7 chiều, cần graph data. Growth lớn không bị flag nếu có artifact explain + mentor confirm. |
| Mentor có bị overload không? | Mentor chỉ review gợi ý của AI — không tự tạo. Review 1 link mất 10 giây với UI đơn giản. |
| University tin không? | ETEST 20 năm, badge signed bởi ETEST key, verify không cần account. |
| Scale thế nào? | Mỗi campus/center có Manager riêng. Mentor manage max_students trong model. |

---

## Appendix — What changed from v3 to v4

| Change | Reason |
|---|---|
| Added Approach C linking flow (Section 4) | Core flow chưa được spec rõ |
| Added `student_context_note` to MilestoneTraceLink | Approach C requires student input field |
| Added `pending_trace_links`, `pending_approvals` to ETESTERCore | Mentor badge notification |
| Added `TraceLinkSuggestions.jsx` | Student sees suggestions post-submit |
| Added `MentorDashboard.jsx` | Mentor view hoàn toàn thiếu trong v3 |
| Added `MentorTraceReview.jsx` | Single review card for mentor |
| Added `MentorArtifactApprove` tab in MentorDashboard | Mentor approves artifacts, not just links |
| Added `GET /mentor/:id/pending` route | Mentor fetches their queue |
| Added `POST /student-note/:traceLinkId` route | Student submits optional note |
| Updated Auth Scorer prompt to include student_context_note | Notes are strong evidence for D1 |
| Updated ETESTERPublic with trace chain summary | University sees verification depth |
| Updated build order | Mentor UI now H7–H9, not skipped |

