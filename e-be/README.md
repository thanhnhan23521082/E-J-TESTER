# ETEST ONE – Backend API

> **ETEST ONE** là nền tảng Smart Parenting + ETESTER dành cho phụ huynh và học sinh,
> sử dụng AI (Claude) để cá nhân hóa trải nghiệm học tập và theo dõi tiến bộ toàn diện.

**Stack:** Python 3.11+ · FastAPI · PostgreSQL (SQLAlchemy async) · Claude API
**Location:** `D:/Trong/docs/E-J-TESTER/e-be/`

---

## Mục lục

1. [Kiến trúc](#1-kiến-trúc)
2. [Cấu trúc file](#2-cấu-trúc-file)
3. [API Endpoints](#3-api-endpoints)
4. [Database Schema](#4-database-schema)
5. [Auth Flow](#5-auth-flow)
6. [Development Setup](#6-development-setup)
7. [Environment Variables](#7-environment-variables)
8. [Code Conventions](#8-code-conventions)
9. [Contribution Flow](#9-contribution-flow-cho-dev-mới)
10. [Tech Stack](#10-tech-stack)

---

## 1. Kiến trúc

```
┌──────────────────────────────────────────────────────────────┐
│                        Client (Web / App)                     │
└──────────────────────────┬───────────────────────────────────┘
                           │  HTTP / REST (Bearer JWT)
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                     FastAPI Application                       │
│  ┌──────────────┐  ┌───────────────┐  ┌────────────────┐  │
│  │ Auth Router  │  │ SmartParenting│  │ ETESTER Router │  │
│  │  /api/auth   │  │    Router      │  │  /api/etester  │  │
│  └──────┬───────┘  │   /api/...    │  └───────┬────────┘  │
│         │          └───────┬────────┘          │            │
│  ┌──────▼──────────────────▼────────────────────▼────────┐  │
│  │              Shared Layer (services, repos)           │  │
│  │  auth.py  deps.py  llm_client.py  rag_client.py     │  │
│  └──────────────────────────┬───────────────────────────┘  │
│                              │                               │
│  ┌──────────────────────────▼───────────────────────────┐  │
│  │                   Core Layer                           │  │
│  │  config.py  database.py  security.py  exceptions.py  │  │
│  │  logging.py                                          │  │
│  └──────────────────────────┬───────────────────────────┘  │
└──────────────────────────────┼────────────────────────────────
                               │  SQLAlchemy (async)
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                  PostgreSQL Database                         │
└──────────────────────────────────────────────────────────────┘
                               │
                               ▼  (AI calls)
┌──────────────────────────────────────────────────────────────┐
│              Anthropic Claude API  (LLM Layer)                │
└──────────────────────────────────────────────────────────────┘
```

**Lớp Layers:**
| Layer | Trách nhiệm |
|---|---|
| **Core** | Cấu hình, DB engine, bảo mật, logging, exception |
| **Shared** | Auth JWT, dependencies, ORM models, LLM/RAG clients |
| **Modules** | Business logic theo feature: auth, smart_parenting, etester |

---

## 2. Cấu trúc file

```
e-be/
├── README.md                        ← File này
├── requirements.txt                 ← Python dependencies
├── .env.example                     ← Template biến môi trường
├── main.py                          ← FastAPI app entrypoint + lifespan
│
├── core/                            # ── Framework infrastructure ──
│   ├── config.py                    # Load env vars (pydantic-settings)
│   ├── database.py                  # SQLAlchemy async engine + get_db()
│   ├── exceptions.py                # Custom HTTP exceptions (StudentNotFound, ...)
│   ├── logging.py                   # request_id middleware + structured logger
│   └── security.py                  # bcrypt hash_password / verify_password
│
├── shared/                          # ── Business utilities ──
│   ├── auth.py                      # JWT access/refresh token creation + verification
│   ├── deps.py                      # FastAPI dependencies (get_current_user)
│   ├── constants.py                 # Enums (ContributorType, MilestoneType, ...)
│   ├── model.py                     # SQLAlchemy ORM models (5 bảng)
│   ├── schemas/                     # Shared Pydantic schemas (API versioning)
│   │   ├── __init__.py
│   │   └── v1.py                   # PaginatedResponse, APIResponse, ErrorResponse...
│   └── clients/
│       ├── llm_client.py            # Claude API wrapper (call_text, call_json)
│       └── rag_client.py            # RAG orchestrator (MockVectorStore + RAGClient)
│
└── modules/
    ├── auth/
    │   ├── router.py                # Endpoints: /register, /login, /refresh, /logout
    │   └── schemas.py                # Pydantic: RegisterRequest, LoginRequest, TokenResponse
    │
    ├── smart_parenting/
    │   ├── router.py                # Endpoints: /students, /behavioral-log, /ai/*
    │   ├── schemas.py                # Pydantic models cho tất cả request/response
    │   ├── repository.py             # Async DB queries: get_student, get_behavioral_logs, ...
    │   ├── prompts.py                # System prompts cho AI (PARENT_CHAT, WELLBEING, DIGEST)
    │   └── services/
    │       ├── parent_chat.py        # Orchestrates RAG → LLM → DB persistence
    │       ├── wellbeing.py         # compute_metrics(), build_alerts(), threshold logic
    │       ├── digest.py             # Weekly parent newsletter generation
    │       └── upsell.py            # Rule-based + LLM programme recommendation
    │
    └── etester/
        ├── router.py                # Endpoints: /contribute, /rebuild-core, /ai/authenticity, /badge
        ├── schemas.py                # Pydantic: ContributionRequest, ETESTERCoreResponse, ...
        ├── repository.py             # Async DB: save_milestone, get_etester_core, ...
        ├── prompts.py               # System prompts: SUMMARIZE, BUILD_NARRATIVE, AUTHENTICITY
        └── services/
            ├── contribute.py         # Validate → AI summary → persist milestone
            ├── rebuild_core.py       # aggregate_core() → upsert ETESTERCore
            ├── authenticity.py      # Score essay with Claude + RAG
            └── badge.py             # Badge awarding logic (bronze→platinum)
```

---

## 3. API Endpoints

Base URL: `http://localhost:8000`

### 3.1 Auth – `/api/auth`

| Method | Path | Mô tả | Auth |
|--------|------|--------|------|
| `POST` | `/api/auth/register` | Đăng ký tài khoản mới | ❌ |
| `POST` | `/api/auth/login` | Đăng nhập → nhận JWT tokens | ❌ |
| `POST` | `/api/auth/refresh` | Refresh access token | ❌ |
| `POST` | `/api/auth/logout` | Đăng xuất (client discard token) | ✅ |

**Login response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 3.2 Smart Parenting – `/api`

| Method | Path | Mô tả | Auth |
|--------|------|--------|------|
| `GET` | `/api/students/{student_id}` | Lấy hồ sơ học sinh | ✅ |
| `GET` | `/api/behavioral-log/{student_id}` | Dữ liệu hành vi + metrics tính toán | ✅ |
| `POST` | `/api/chat/completion` | Chat completion endpoint cho parent-agent (LangGraph tools) | ✅ |
| `POST` | `/api/ai/wellbeing` | Đánh giá wellbeing (query: `student_id`, `days`) | ✅ |
| `GET` | `/api/digest/{student_id}` | Tạo bản tin tuần cho phụ huynh | ✅ |
| `GET` | `/api/upsell/{student_id}` | Gợi ý chương trình học phù hợp | ✅ |

**Parent Chat request:**
```json
{
  "student_id": "STU-001",
  "question": "Con tôi tuần này học như thế nào?",
  "escalate": false
}
```

**Parent Chat response:**
```json
{
  "answer": "Tuần này Minh đã học 45 phút mỗi ngày...",
  "escalated": false,
  "sources": ["behavioral_logs", "milestones", "rag_context"]
}
```

**Wellbeing response:**
```json
{
  "student_id": "STU-001",
  "overall_score": 78.5,
  "severity": "low",
  "alerts": [{"type": "streak", "severity": "low", "message": "Streak giảm 1 ngày"}],
  "recommendations": ["Khuyến khích con học 30 phút mỗi ngày"],
  "metrics": { "avg_daily_study_min": 32, "total_sessions": 5, ... }
}
```

### 3.3 ETESTER – `/api/etester`

| Method | Path | Mô tả | Auth |
|--------|------|--------|------|
| `GET` | `/api/etester/{student_id}` | Lấy full ETESTER profile (core + milestones + narrative) | ✅ |
| `POST` | `/api/etester/contribute` | Submit milestone mới | ✅ |
| `POST` | `/api/etester/rebuild-core/{student_id}` | Tổng hợp lại ETESTERCore từ tất cả milestones | ✅ |
| `POST` | `/api/etester/ai/authenticity` | Chấm điểm tính xác thực bài viết | ✅ |
| `GET` | `/api/etester/badge/{student_id}` | Lấy badge hiện tại của học sinh | ✅ |

**Contribute request:**
```json
{
  "student_id": "STU-001",
  "milestone_id": "MIL-2026-001",
  "type": "ielts_mock",
  "title": "IELTS Mock Test – March 2026",
  "date": "2026-03-15",
  "score": 7.0,
  "score_label": "Band 7.0",
  "notes": "Reading improved by 0.5 from last attempt.",
  "contributor_type": "student"
}
```

**Badge tiers:**

| Tier | Min contributions | Min consistency |
|------|------------------|-----------------|
| 🥉 Bronze | 3 | 0.4 |
| 🥈 Silver | 10 | 0.6 |
| 🥇 Gold | 25 | 0.75 |
| 💎 Platinum | 50 | 0.9 |

### 3.4 Health

| Method | Path | Mô tả | Auth |
|--------|------|--------|------|
| `GET` | `/` | Root – version + status | ❌ |
| `GET` | `/health` | Health check | ❌ |

---

## 4. Database Schema

### 4.1 `users`
```sql
id             SERIAL PRIMARY KEY
email          VARCHAR(255) UNIQUE NOT NULL
hashed_password VARCHAR(255) NOT NULL
role           VARCHAR(50)  NOT NULL  -- parent | mentor | admin
created_at     TIMESTAMP    DEFAULT NOW()
```

### 4.2 `students`
```sql
student_id       VARCHAR(50) PRIMARY KEY
name             VARCHAR(255) NOT NULL
ielts_score      FLOAT
sat_score        FLOAT
gpa              FLOAT
skill_breakdown  TEXT  -- JSON
target_schools   TEXT  -- JSON
months_enrolled  INT
program          VARCHAR(100)
parent_id        INT  REFERENCES users(id)
mentor_id        INT  REFERENCES users(id)
user_id          INT  REFERENCES users(id)
created_at       TIMESTAMP DEFAULT NOW()
```

### 4.3 `behavioral_logs`
```sql
id            SERIAL PRIMARY KEY
student_id    VARCHAR(50) REFERENCES students(student_id)
date          TIMESTAMP NOT NULL
duration_min  FLOAT
session_start TIMESTAMP
studied       BOOLEAN DEFAULT FALSE
streak_day    INT
score_delta   FLOAT
```

### 4.4 `conversations`
```sql
id               SERIAL PRIMARY KEY
parent_id        INT  REFERENCES users(id)
student_id       VARCHAR(50) REFERENCES students(student_id)
timestamp        TIMESTAMP DEFAULT NOW()
question         TEXT NOT NULL
ai_response      TEXT NOT NULL
context_snapshot TEXT  -- JSON
escalated        BOOLEAN DEFAULT FALSE
```

### 4.5 `milestones`
```sql
id               SERIAL PRIMARY KEY
student_id       VARCHAR(50) REFERENCES students(student_id)
milestone_id     VARCHAR(100) NOT NULL
type             VARCHAR(50) NOT NULL  -- MilestoneType value
title            VARCHAR(255) NOT NULL
date             TIMESTAMP NOT NULL
score            FLOAT
score_label      VARCHAR(100)
mentor_id        INT REFERENCES users(id)
mentor_approved  BOOLEAN
auth_score       FLOAT  -- AI authenticity score
notes            TEXT
status           VARCHAR(50) DEFAULT 'pending'  -- pending | approved | rejected
contributor_type VARCHAR(50) NOT NULL
ai_summary       TEXT
```

### 4.6 `etester_core`
```sql
student_id            VARCHAR(50) PRIMARY KEY REFERENCES students(student_id)
academic_score        FLOAT
writing_growth        FLOAT
skills                TEXT  -- JSON dict
mentor_verifications  INT DEFAULT 0
parent_support_level  FLOAT
institutional_stamp   VARCHAR(100)
consistency_score     FLOAT
total_contributions   INT DEFAULT 0
last_updated          TIMESTAMP DEFAULT NOW()
narrative_cache       TEXT  -- Cached LLM narrative
badge_issued          VARCHAR(50)  -- bronze|silver|gold|platinum
```

---

## 5. Auth Flow

```
┌────────┐                    ┌──────────┐                 ┌──────────┐
│ Client │                    │  FastAPI │                 │  DB      │
└───┬────┘                    └────┬─────┘                 └────┬────┘
    │  POST /api/auth/register      │                           │
    │  {email, password, role}     │                           │
    │──────────────────────────────►│  hash(password)           │
    │                               │───────────────────────────►│
    │                               │  INSERT users              │
    │                               │◄──────────────────────────│
    │  201 UserResponse             │                           │
    │◄──────────────────────────────│                           │
    │                               │                           │
    │  POST /api/auth/login         │                           │
    │  {email, password}           │                           │
    │──────────────────────────────►│  SELECT users WHERE email  │
    │                               │───────────────────────────►│
    │                               │◄──────────────────────────│
    │                               │  verify_password()         │
    │  200 TokenResponse            │                           │
    │  {access_token,              │                           │
    │   refresh_token}             │                           │
    │◄──────────────────────────────│                           │
    │                               │                           │
    │  GET /api/students/STU-001   │                           │
    │  Authorization: Bearer <token>│                           │
    │──────────────────────────────►│  verify_token()           │
    │                               │  get_current_user()        │
    │  200 StudentProfile           │                           │
    │◄──────────────────────────────│                           │
    │                               │                           │
    │  POST /api/auth/refresh       │                           │
    │  {refresh_token}             │  decode_refresh_token()    │
    │──────────────────────────────►│                           │
    │  200 TokenResponse (new AT)  │                           │
    │◄──────────────────────────────│                           │
```

**Token details:**
- **Access token**: HS256, 30 phút (configurable), chứa `{sub: user_id, role, type: access, exp}`
- **Refresh token**: HS256, 7 ngày (configurable), chứa `{sub: user_id, type: refresh, exp}`

---

## 6. Development Setup

### 6.1 Prerequisites

- Python 3.11+
- PostgreSQL 14+ (local hoặc Docker)

### 6.2 Cài đặt

```bash
# 1. Clone / navigate
cd D:/Trong/docs/E-J-TESTER/e-be

# 2. Tạo virtual environment
python -m venv venv
source venv/Scripts/activate        # Windows
# source venv/bin/activate         # macOS/Linux

# 3. Cài dependencies
pip install -r requirements.txt

# 4. Cấu hình môi trường
cp .env.example .env
# Chỉnh sửa .env: điền DATABASE_URL, SECRET_KEY, ANTHROPIC_API_KEY

# 5. Tạo database
psql -U postgres -c "CREATE DATABASE etest_one;"

# 6. Chạy migrations (sync)
# (Lần đầu: tables được tạo tự động bởi create_all_tables() trong main.py)
# Để dùng Alembic cho production:
#   pip install alembic
#   alembic init alembic
#   alembic revision --autogenerate -m "init"
#   alembic upgrade head

# 7. Chạy server
uvicorn main:app --reload --port 8000

# 8. Mở docs
# http://localhost:8000/docs        (Swagger UI)
# http://localhost:8000/redoc      (ReDoc)
```

### 6.3 Docker (Optional)

```bash
# PostgreSQL
docker run -d \
  --name etest_pg \
  -e POSTGRES_DB=etest_one \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:15

# FastAPI
docker build -t etest-one .
docker run -d --name etest-api -p 8000:8000 --env-file .env etest-one
```

### 6.4 Testing

```bash
# Chạy unit tests
pytest -v

# Với coverage
pytest --cov=. --cov-report=html
```

---

## 7. Environment Variables

Xem `.env.example` đầy đủ. Các biến chính:

| Variable | Mô tả | Ví dụ |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://postgres:postgres@localhost:5432/etest_one` |
| `SECRET_KEY` | JWT signing key (≥64 chars) | `openssl rand -hex 64` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | TTL access token | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | TTL refresh token | `7` |
| `ANTHROPIC_API_KEY` | Claude API key | `sk-ant-api03-...` |
| `AWS_REGION` | AWS region | `ap-southeast-1` |
| `APP_ENV` | `development` \| `production` | `development` |
| `DEBUG` | Enable SQLAlchemy echo | `true` |
| `LOG_LEVEL` | Log verbosity | `INFO` |
| `CORS_ORIGINS` | Comma-separated CORS origins | `http://localhost:3000` |

---

## 8. Code Conventions

### 8.1 Quy tắc đặt tên (snake_case)

| Loại | Convention | Ví dụ | Ghi chú |
|---|---|---|---|
| File Python | `snake_case.py` | `parent_chat.py`, `wellbeing.py` | ✅ |
| Class Pydantic/Model | `PascalCase` | `ParentChatRequest`, `StudentProfile` | Pydantic convention |
| Function (public) | `snake_case()` | `get_student()`, `compute_metrics()` | ✅ |
| Function (private) | `_snake_case()` | `_build_pitch()`, `_match_programmes()` | ✅ underscore prefix |
| Constant (module) | `SCREAMING_SNAKE_CASE` | `PROGRAMME_CATALOGUE`, `BADGE_ORDER` | ✅ |
| Enum value | `snake_case` (string) | `MilestoneType.IELTS_MOCK` | ✅ |
| Variable | `snake_case` | `student_id`, `ielts_score` | ✅ |
| Async function | luôn prefix `async` | `async def get_student()` | ✅ |

**❌ Không dùng camelCase/PascalCase cho:**
- Tên file Python
- Tên function, biến
- Tên route path

```
# ✅ Đúng
def compute_metrics(logs: list): ...
async def parent_chat_service(question: str): ...

# ❌ Sai
def computeMetrics(logs): ...
async def parentChatService(question): ...
```

### 8.2 Cấu trúc mỗi module

```
modules/<tên_module>/
├── router.py          ← HTTP routing (ĐỪNG viết logic ở đây)
├── schemas.py         ← Pydantic request/response (PascalCase)
├── repository.py      ← DB queries (CRUD thuần, không logic)
├── prompts.py        ← System prompts cho AI
└── services/
    ├── __init__.py    ← export all service functions
    ├── parent_chat.py ← 1 file = 1 feature
    ├── wellbeing.py
    ├── digest.py
    └── upsell.py
```

**Luồng mỗi request:**

```
HTTP request
    ↓
router.py        → parse params, validate schema, gọi service
    ↓
services/*.py    → business logic + gọi repository + gọi AI
    ↓
repository.py   → truy vấn DB (CRUD thuần, KHÔNG logic)
    ↓
Pydantic schema → trả response về
```

### 8.3 Nguyên tắc mỗi file

| File | Được phép | Không được |
|---|---|---|
| `router.py` | Parse params, gọi service | Gọi DB trực tiếp, gọi AI trực tiếp, logic nghiệp vụ |
| `services/*.py` | Logic nghiệp vụ, gọi repository, gọi AI | Import router |
| `repository.py` | CRUD DB thuần túy | Logic nghiệp vụ, gọi AI |
| `schemas.py` | Định nghĩa model | Logic |
| `prompts.py` | String constants | Logic |

### 8.4 Import convention

```python
# Thứ tự import: stdlib → third-party → local
from datetime import datetime              # stdlib
from typing import Annotated              # stdlib

from fastapi import APIRouter, Depends   # third-party
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings     # local: core first
from core.database import get_db
from shared.model import Student          # local: shared
from shared.clients.llm_client import call_text
from modules.smart_parenting.repository import get_student  # local: modules
from modules.smart_parenting.schemas import ParentChatRequest
```

---

## 9. Contribution Flow (cho dev mới)

### 9.1 Thêm endpoint mới

```
1. Định nghĩa Schema (Pydantic)
   modules/<module>/schemas.py
   └── class NewRequest(BaseModel)
   └── class NewResponse(BaseModel)

2. Thêm Repository function
   modules/<module>/repository.py
   └── async def get_related_data(...)

3. Viết Service logic
   modules/<module>/services/new_service.py
   └── async def new_service(...)

4. Đăng ký Route
   modules/<module>/router.py
   └── @router.get("/path", response_model=NewResponse)
   └── async def new_endpoint(...):
           return await new_service(...)
```

### 9.2 Thêm một Milestone Type mới

```python
# 1. Thêm enum value
# shared/constants.py
class MilestoneType(str, Enum):
    NEW_TYPE = "new_type"    # ← thêm ở đây

# 2. Thêm prompt mới (nếu cần)
# modules/etester/prompts.py
NEW_SYSTEM = "..."
NEW_USER_TEMPLATE = "..."

# 3. Cập nhật aggregate_core() nếu có logic riêng
# modules/etester/services/rebuild_core.py
```

### 9.3 Code style bắt buộc

- **Async everywhere** cho FastAPI routes và DB queries
- **Type hints** bắt buộc cho mọi function signature
- **Docstrings** cho mọi public function
- **Custom exceptions** thay vì generic `Exception`
- **Never commit `.env`** – đã có `.gitignore`

### 9.4 Commit convention

```
feat:    Thêm tính năng mới
fix:     Sửa bug
refactor: Cải thiện code (không đổi behavior)
docs:    Cập nhật tài liệu
test:    Thêm tests
chore:   Công việc hành chính (deps, config)
```

---

## 10. Tech Stack

| Category | Library | Version | Purpose |
|---|---|---|---|
| **Framework** | FastAPI | ≥0.109 | Async REST API |
| **Server** | Uvicorn | ≥0.27 | ASGI server |
| **ORM** | SQLAlchemy | ≥2.0 | Async database ORM |
| **DB Driver** | asyncpg | ≥0.29 | Async PostgreSQL driver |
| **Validation** | Pydantic v2 | ≥2.6 | Request/response schemas |
| **Settings** | pydantic-settings | ≥2.1 | Env var loading |
| **Auth** | python-jose | ≥3.3 | JWT creation/verification |
| **Password** | passlib + bcrypt | ≥1.7 | bcrypt hashing |
| **LLM** | anthropic | ≥0.18 | Claude API client |
| **HTTP** | httpx | ≥0.27 | Async HTTP client |
| **Testing** | pytest + pytest-asyncio | ≥8.0 | Unit & integration tests |
| **Migrations** | Alembic | ≥1.13 | DB schema migrations |

---

> **Chính sách bảo mật:** Không bao giờ commit file `.env`. Luôn dùng `.env.example` làm template.
> **Production note:** Thay `SECRET_KEY` bằng giá trị ngẫu nhiên thật, bật `DEBUG=false`, dùng PostgreSQL trên RDS thay vì local.
