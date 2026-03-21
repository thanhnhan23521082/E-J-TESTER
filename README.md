# ETEST ONE — Developer Guide

> **Version:** 1.0.0 — Hackathon Build
> **Stack:** React + Vite (Frontend) · Python/FastAPI (Backend) · DynamoDB (planned) · Claude API
> **Status:** Active development

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Project Structure](#3-project-structure)
4. [Modules & Conventions](#4-modules--conventions)
5. [API Reference](#5-api-reference)
6. [Skills & Agents](#6-skills--agents)
7. [Development Setup](#7-development-setup)
8. [Contribution Workflow](#8-contribution-workflow)

---

## 1. Project Overview

**ETEST ONE** là ứng dụng hackathon gồm 2 module chính:

| Module | Mô tả | Người dùng |
|---|---|---|
| **Smart Parenting** | AI chatbot + wellbeing alert + weekly digest cho phụ huynh học viên du học | Phụ huynh (45 tuổi, low-tech) |
| **ETESTER** | "Con dấu số" — living profile tích lũy contributions theo thời gian, university verify được qua QR | Học viên · Mentor · Manager · University |

### Demo Scenario (Minh Anh)

```
Nhân vật:  Nguyễn Hà Minh Anh — 17t · IELTS 6.5 · SAT 1320 · 14 tháng AMP
Phụ huynh: Cô Thu — 45t · bận rộn · không biết thuật ngữ du học
Trigger:   3 đêm học sau 11pm · streak giảm · EA deadline 47 ngày

Demo flow:
  1. Cô Thu mở app → thấy Wellbeing Alert (severity: high)
  2. Cô Thu hỏi AI: "Con IELTS 6.5 có đủ không?"
     → AI: "Đủ 8/10 trường. Thiếu 0.5 để vào Melbourne trực tiếp."
  3. Cô Thu xem Progress → Writing đang yếu
  4. Upsell: "Trại hè Writing tháng 7 phù hợp với Minh Anh"
  5. Switch sang ETESTER → thấy timeline 14 tháng + QR badge
  6. Scan QR → ETESTERPublic page → "ETEST Verified Learner"
  7. Pitch close: "Đây là con dấu không thể fake trong thời đại AI"
```

---

## 2. Architecture

### 2.1 Logical Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      React Web App                           │
│                                                              │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────────────┐ │
│  │ ParentHome │  │ ParentChat  │  │  StudentProgress     │ │
│  └────────────┘  └─────────────┘  └──────────────────────┘ │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────────────┐ │
│  │ETESTERDash │  │ETESTERPublic│  │  ContributeForm      │ │
│  └────────────┘  └─────────────┘  └──────────────────────┘ │
│                            │                                 │
└────────────────────────────┼────────────────────────────────┘
                             │ REST API
┌────────────────────────────┼────────────────────────────────┐
│               Python/FastAPI Backend                         │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Smart Parenting Module                   │   │
│  │  student · behavioral · digest · wellbeing          │   │
│  │  conversation · upsell                               │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               ETESTER Module                          │   │
│  │  contribution · core-aggregator · authenticity      │   │
│  │  badge · narrative-builder                           │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Claude Orchestrator                      │   │
│  │  callTextPrompt · callJsonPrompt · 10s timeout       │   │
│  │  retry ×1 · safe JSON parse · fallback              │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│           ┌────────────────┴────────────────┐                │
│           ▼                                 ▼                │
│   ┌───────────────┐               ┌───────────────┐       │
│   │   DynamoDB    │               │  Claude API    │       │
│   │  (5 Tables)    │               │ (claude-sonnet)│       │
│   └───────────────┘               └───────────────┘       │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Deployment Architecture

```
Frontend:  Vite build → Vercel / Netlify
Backend:   Docker → AWS App Runner
Data:      AWS DynamoDB
AI:        Anthropic Claude API
```

### 2.3 AI Orchestration

```
AI chỉ làm 3 việc:
  ✦ Giải thích    → plain VN cho phụ huynh
  ✦ Summarize     → contribution metadata JSON
  ✦ Compare        → writing pattern authenticity

AI KHÔNG làm:
  ✗ Threshold logic (dùng rule-engine)
  ✗ Score aggregate cơ bản (dùng pure function)
  ✗ Upsell logic cơ bản (dùng rule-based)
```

---

## 3. Project Structure

```
E-J-TESTER/
├── e-be/                          # Backend (Python/FastAPI)
│   ├── modules/
│   │   ├── etester/
│   │   │   ├── router.py         # ETESTER API routes
│   │   │   ├── schemas.py        # Pydantic request/response models
│   │   │   └── __init__.py
│   │   └── smart_parenting/
│   │       ├── router.py         # Smart Parenting API routes
│   │       ├── schemas.py        # Pydantic request/response models
│   │       └── __init__.py
│   └── infra/
│       └── pg_repository.py      # Database access layer
│
├── e-fe/                          # Frontend (React + Vite + Tailwind)  [chưa tạo]
│
└── docs/                          # Design & Spec documents
    ├── ETEST_ONE_TechSpec.md
    ├── ETEST_ONE_High_Level_Design.md
    └── ...
```

> **Lưu ý:** Backend hiện tại dùng Python/FastAPI (khác với spec gốc là Node.js). Frontend chưa được khởi tạo.

---

## 4. Modules & Conventions

### 4.1 Backend Modules

Mỗi module gồm 3 file bắt buộc:

```
modules/<name>/
├── router.py      # FastAPI router + endpoint definitions
├── schemas.py     # Pydantic models (Request/Response)
└── __init__.py
```

#### Module: `smart_parenting`

| File | Trách nhiệm |
|---|---|
| `router.py` | 6 routes: student, behavioral-log, digest, wellbeing, parent-chat, upsell |
| `schemas.py` | `StudentProfile`, `BehavioralLog`, `DigestResponse`, `WellbeingResponse`, `ParentChatRequest`, `UpsellItem` |

#### Module: `etester`

| File | Trách nhiệm |
|---|---|
| `router.py` | 5 routes: etester profile, contribute, rebuild-core, authenticity, badge |
| `schemas.py` | `ContributionRequest`, `MilestoneResponse`, `AuthenticityRequest`, `BadgeResponse` |

#### Module: `infra`

| File | Trách nhiệm |
|---|---|
| `pg_repository.py` | DynamoDB (hoặc mock) access — **chưa implement đầy đủ** |

### 4.2 Naming Conventions

| Loại | Convention | Ví dụ |
|---|---|---|
| Route | `snake_case` | `GET /api/behavioral-log/{studentId}` |
| Schema class | `PascalCase` | `WellbeingResponse`, `ContributionRequest` |
| Schema field | `snake_case` | `student_id`, `mentor_approved` |
| Service function | `snake_case` | `parent_chat()`, `score_authenticity()` |
| Pydantic model | `PascalCase` + `Request`/`Response` suffix | `ParentChatRequest`, `DigestResponse` |

### 4.3 Response Schema Pattern

```python
# ✅ Dùng Pydantic Response model
from fastapi import APIRouter
router = APIRouter(prefix="/api", tags=["smart-parenting"])

@router.get("/students/{student_id}", response_model=StudentProfile)
async def get_student(student_id: str):
    ...

# ❌ Không trả dict thuần
@router.get("/students/{student_id}")
async def get_student(student_id: str):
    return {"name": "..."}  # ← bad
```

### 4.4 AI Call Pattern (Claude Orchestrator)

```python
# ✅ Luôn có timeout, retry, fallback, safe-parse
async def call_claude_json(prompt: str, schema: type):
    try:
        response = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            timeout=10.0,
            messages=[{"role": "user", "content": prompt}]
        )
        return schema.model_validate_json(response.content[0].text)
    except (TimeoutError, JSONDecodeError):
        return schema.model_validate_fallback()  # fallback hardcoded
```

### 4.5 Frontend Conventions (tương lai)

| Loại | Convention | Ví dụ |
|---|---|---|
| Component | `PascalCase` | `WellbeingAlertCard`, `MilestoneTimeline` |
| Hook | `camelCase` prefixed `use` | `useStudent`, `useWellbeing` |
| API file | `api/<module>.ts` | `api/parent.ts`, `api/etester.ts` |
| Route | `kebab-case` | `/parent`, `/etester/verify/:id` |

---

## 5. API Reference

### 5.1 Smart Parenting

```
GET  /api/students/{student_id}
     → StudentProfile

GET  /api/behavioral-log/{student_id}
     → BehavioralLogResponse
       { logs[], metrics: { avg_duration, late_nights_count, current_streak, ... } }

POST /api/ai/parent-chat
     body: { question: string, student_id: string }
     → ParentChatResponse
       { response: string, action: string, escalated: bool }

POST /api/ai/wellbeing
     body: { student_id: string }
     → WellbeingResponse
       { alert: bool, severity: "low"|"medium"|"high", message: string, action: string }

GET  /api/digest/{student_id}
     → DigestResponse
       { progress_pct, milestones_done, next_deadline, days_left, priority_action }

GET  /api/upsell/{student_id}
     → UpsellResponse
       List<{ course_name: string, reason: string, cta_url: string, priority: int }>
```

### 5.2 ETESTER

```
GET  /api/etester/{student_id}
     → ETESTERProfile
       { core: ETESTERCore, milestones: Milestone[], narrative: string }

POST /api/etester/contribute
     body: { student_id, type, data: {}, contributor_type }
     → MilestoneResponse (tạo milestone + trigger rebuild-core sync)

POST /api/etester/rebuild-core/{student_id}
     → ETESTERCore (aggregate + narrative rebuild)

POST /api/ai/authenticity
     body: { essay: string, student_id: string }
     → AuthenticityResponse
       { auth_score: int, confidence: str, consistent_patterns[], divergent_patterns[], recommendation }

GET  /api/etester/badge/{student_id}
     → BadgePayload (verify URL + metadata, frontend tự generate QR)
```

### 5.3 HTTP Status Codes

| Code | Dùng khi |
|---|---|
| `200` | Thành công |
| `400` | Request payload sai / validation fail |
| `404` | Student / resource không tồn tại |
| `422` | Không đủ writing history cho authenticity |
| `500` | Lỗi hệ thống |
| `504` | AI timeout — dùng fallback |

---

## 6. Skills & Agents

### 6.1 Khi nào dùng Skill / Agent nào

| Tình huống | Tool |
|---|---|
| Tạo project mới từ đầu | `bootstrap` hoặc `bootstrap:auto` |
| Lên kế hoạch chi tiết (có nghiên cứu) | `plan:two` hoặc `plan:parallel` |
| Lên kế hoạch nhanh (đã rõ) | `plan:fast` |
| Code feature mới (step-by-step) | `cook` hoặc `cook:auto` |
| Code nhiều phase song song | `code:parallel` |
| Code nhanh (trust me bro) | `cook:auto:fast` |
| Fix bug / lỗi cụ thể | `fix` hoặc `fix:fast` |
| Fix nhiều bug cùng lúc | `fix:parallel` |
| Debug issue phức tạp | `debug` agent |
| Nghiên cứu công nghệ mới | `research` |
| Tạo/sửa skill | `skill-creator` |
| Quản lý MCP server | `use-mcp` |
| Review code | `code-review` |
| Viết/bảo trì docs | `docs:update` |
| Tạo UI/UX | `frontend-design` hoặc `design:*` |
| Viết copy marketing | `content:fast` hoặc `content:good` |
| Git operations | `git:pr`, `git:cm`, `git:cp` |
| Tạo document (PDF/Word) | `document-skills:pdf` / `docx` |
| Test and fix | `test` |

### 6.2 Quick Reference — Các Skill phổ biến nhất cho dự án này

```
/bootstrap:auto:fast   ← Tạo project nhanh từ spec
/cook:auto             ← Implement feature step-by-step (Recommended)
/plan:two              ← Lên kế hoạch với 2 cách tiếp cận
/fix                   ← Debug và fix issue
/frontend-design       ← UI/UX design
/docs:update          ← Cập nhật documentation
/test                  ← Chạy test và phân tích kết quả
```

### 6.3 Các Agent đặc biệt

| Agent | Khi nào dùng |
|---|---|
| `fullstack-developer` | Implement một phase từ parallel plan |
| `code-reviewer` | Review PR / code quality trước merge |
| `tester` | Chạy test suite, coverage analysis |
| `planner` | Thiết kế kiến trúc phức tạp |
| `brainstormer` | Đánh giá trade-off trước khi implement |
| `debugger` | Investigate lỗi, phân tích logs, performance |
| `database-admin` | DynamoDB optimization, backup strategy |
| `docs-manager` | Manage technical docs, PDRs |
| `researcher` | Research library, best practices |
| `ui-ux-designer` | Thiết kế UI/UX chi tiết |

---

## 7. Development Setup

### 7.1 Prerequisites

- **Python** 3.11+
- **Node.js** 20+ (cho frontend — chưa setup)
- **Claude API Key** (`ANTHROPIC_API_KEY`)
- **AWS Credentials** (cho DynamoDB — tùy chọn, có thể mock)

### 7.2 Backend Setup

```bash
cd E-J-TESTER/e-be

# Tạo virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r modules/etester/requirements.txt
pip install -r modules/smart_parenting/requirements.txt

# Chạy server
uvicorn main:app --reload --port 8000
```

### 7.3 Environment Variables

Tạo `.env` ở `e-be/`:

```env
ANTHROPIC_API_KEY=sk-ant-...
AWS_REGION=ap-southeast-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
```

### 7.4 Backend Module Dependencies

```
etester/
  requirements.txt  → fastapi, uvicorn, anthropic, boto3, pydantic

smart_parenting/
  requirements.txt  → fastapi, uvicorn, anthropic, boto3, pydantic
```

---

## 8. Contribution Workflow

### 8.1 Git Branching

```
main                   ← production-ready
├── develop            ← integration branch
│   ├── feat/sp-001-parent-home
│   ├── feat/sp-002-parent-chat
│   ├── feat/et-001-etester-dashboard
│   └── fix/wb-001-wellbeing-threshold
```

### 8.2 Checklist trước khi commit

- [ ] Schema Pydantic định nghĩa cho mọi endpoint
- [ ] Claude call có timeout + fallback
- [ ] JSON parse có try/catch
- [ ] Response trả về qua schema (không phải dict thuần)
- [ ] Chạy `test` agent để verify
- [ ] API tested với mock data

### 8.3 Checklist trước khi merge

- [ ] Review bởi `code-reviewer` agent
- [ ] Test end-to-end với demo scenario (Minh Anh)
- [ ] Frontend đã kết nối và hoạt động
- [ ] Fallback hoạt động khi Claude timeout

### 8.4 Demo Acceptance Criteria

```
□ Phụ huynh mở app thấy Wellbeing Alert (severity: high)
□ Phụ huynh hỏi AI → nhận 1 action cụ thể
□ Progress page hiển thị activity + milestones
□ Contribute essay → authenticity preview chạy
□ ETESTER dashboard cập nhật sau contribution mới
□ QR scan → public verify page mở đúng
□ Pitch demo chạy ổn định ≥3 lần liên tiếp
```

### 8.5 Tech Spec Documents

| File | Mục đích |
|---|---|
| `ETEST_ONE_TechSpec.md` | Chi tiết kỹ thuật đầy đủ (source of truth) |
| `ETEST_ONE_High_Level_Design.md` | Architecture blueprint cho dev team |

---

## Quick Start Cheat Sheet

```bash
# 1. Tạo project mới hoặc tiếp tục
/bootstrap:auto:fast

# 2. Lên kế hoạch feature
/plan:two

# 3. Implement feature
/cook:auto

# 4. Fix bug
/fix

# 5. Test
/test

# 6. Review code
/code-review

# 7. Update docs
/docs:update

# 8. Commit
/git:cm

# 9. Create PR
/git:pr
```
