"""
main.py
───────
ETEST ONE Backend – FastAPI application entrypoint.

Initialises:
  • SQLAlchemy tables (create_all_tables)
  • Request-ID middleware
  • CORS middleware
  • All routers (auth, smart_parenting, etester)
  • Health-check endpoint
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import get_settings
from core.database import create_all_tables
from core.logging import RequestIDMiddleware
from modules.auth.router import router as auth_router
from modules.etester.router import router as etester_router
import shared.model  # noqa: F401 — register all tables (incl. ETESTER) with Base.metadata
from modules.smart_parenting.chatbot_router import router as smart_parenting_chatbot_router
from modules.smart_parenting.router import router as smart_parenting_router

settings = get_settings()

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


def _service_mode() -> str:
    return os.getenv("SERVICE_MODE", "all").strip().lower()


def _should_run_db_init() -> bool:
    # Keep schema changes migration-driven by default.
    value = os.getenv("RUN_DB_INIT", "false").strip().lower()
    return value in {"1", "true", "yes", "on"}


# ── Lifespan ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup → running → shutdown."""
    mode = _service_mode()
    logger.info("Starting ETEST ONE Backend (mode=%s) …", mode)
    if _should_run_db_init():
        try:
            create_all_tables()
            logger.info("Database tables ready")
        except Exception as exc:
            logger.error("Failed to create database tables: %s", exc)
    else:
        logger.info("Skipping DB init at startup (RUN_DB_INIT=false)")

    yield

    logger.info("Shutting down ETEST ONE Backend …")


# ── App factory ───────────────────────────────────────────────────────────────
def create_app() -> FastAPI:
    app = FastAPI(
        title="ETEST ONE API",
        description=(
            "Backend API for ETEST ONE – Smart Parenting + ETESTER platform. "
            "Provides AI-augmented parent coaching, student wellbeing monitoring, "
            "milestone tracking, and ETESTER scoring."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── Middleware ──────────────────────────────────────────────────────────
    app.add_middleware(RequestIDMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify allowed origins for security
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception handlers ─────────────────────────────────────────────────
    from core.exceptions import AppHTTPException

    @app.exception_handler(AppHTTPException)
    async def app_exception_handler(
        request: Request, exc: AppHTTPException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(),
            headers={"X-Request-ID": getattr(request.state, "request_id", None)},  # type: ignore[arg-type]
        )

    # ── Include routers by service mode ──────────────────────────────────
    mode = _service_mode()
    if mode in {"all", "auth"}:
        app.include_router(auth_router)
    if mode in {"all", "parenting"}:
        app.include_router(smart_parenting_router)
    if mode in {"all", "parenting-agent"}:
        app.include_router(smart_parenting_chatbot_router)
    if mode in {"all", "etester"}:
        app.include_router(etester_router)

    # ── Health check ────────────────────────────────────────────────────────
    @app.get("/", tags=["health"])
    async def root():
        return {
            "service": "ETEST ONE Backend",
            "version": "1.0.0",
            "status": "healthy",
        }

    @app.get("/health", tags=["health"])
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
