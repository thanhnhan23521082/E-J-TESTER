"""
core/logging.py
───────────────
Structured logging with a per-request UUID (`request_id`).
The middleware injects `X-Request-ID` in every response header.
"""

import logging
import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# ── Logger setup ─────────────────────────────────────────────────────────────
def _build_logger() -> logging.Logger:
    logger = logging.getLogger("etest_one")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s "
                "[%(request_id)s] %(method)s %(path)s %(duration_ms)sms "
                "(%(status)s)\n"
                "  %(message)s"
            )
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


_logger = _build_logger()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Assigns a unique `request_id` (UUID4) to every incoming request
    and exposes it via the `X-Request-ID` response header.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[..., Response]
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id  # type: ignore[attr-defined]

        t0 = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - t0) * 1000, 2)

        log_record = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "duration_ms": duration_ms,
            "status": response.status_code,
        }
        _logger.info("", extra=log_record)

        response.headers["X-Request-ID"] = request_id
        return response


def get_request_logger(request: Request) -> logging.LoggerAdapter:
    """Return a logger bound to the current request context."""
    request_id = getattr(request.state, "request_id", "no-request-id")
    return logging.LoggerAdapter(_logger, {"request_id": request_id})
