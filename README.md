# E-J-TESTER

Quick guide to clone and run the app locally.

## 1) Clone the repository and SWITCH TO DEV BRANCH (required)

> Preferred branch is `dev`. In this repository, the equivalent active branch is currently `develop`.

```bash
git clone <repo-url>
cd E-J-TESTER

# Option 1: if dev branch exists
git checkout dev

# Option 2: if dev does not exist, use develop (current repo setup)
git checkout develop
# or:
# git checkout -b develop origin/develop
```

## 2) Prerequisites

- Node.js 20+
- Docker Desktop (with Docker Compose)
- Git

## 3) Run Frontend

```bash
cd e-fe
npm install
npm run dev
```

Frontend runs by default at `http://localhost:5173`.

## 4) Run Backend

Open a new terminal at the project root, then run:

```bash
cd e-be
docker compose --profile dev up --build
```

Default backend services:

- Auth API: `http://localhost:8001`
- Parenting API: `http://localhost:8002`
- Parenting Agent API: `http://localhost:8003`
- ETESTER API: `http://localhost:8004`
- PostgreSQL: `localhost:5432`
- pgAdmin: `http://localhost:5050`

## 5) Environment Variables (recommended)

A template file is available at `e-be/.env.example`.

```bash
cd e-be
cp .env.example .env
```

Update required keys (for example: `OPENAI_API_KEY`, `SERPAPI_API_KEY`, `SECRET_KEY`) before testing AI/search-related features.

## 6) Quick Verification

- Frontend is accessible at `http://localhost:5173`
- Backend health endpoints:
  - `http://localhost:8001/health`
  - `http://localhost:8002/health`
  - `http://localhost:8003/health`
  - `http://localhost:8004/health`

## 7) Stop Services

Backend:

```bash
cd e-be
docker compose --profile dev down
```

Frontend: press `Ctrl + C` in the terminal running `npm run dev`.

---

If you are new to this project, remember these 3 most important steps:

1. Clone the repository and checkout `dev`/`develop`
2. Frontend: `npm install` + `npm run dev`
3. Backend: `docker compose --profile dev up --build`
