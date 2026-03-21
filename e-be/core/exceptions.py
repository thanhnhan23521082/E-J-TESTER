"""
core/exceptions.py
──────────────────
Custom HTTPException subclasses for domain-specific error handling.
Each exception carries a machine-readable `error_code` for client handling.
"""

from typing import Any


class AppHTTPException(Exception):
    """Base class – subclasses become FastAPI HTTPExceptions via `.http()`."""

    status_code: int = 500
    detail: str = "Internal server error"
    error_code: str = "INTERNAL_ERROR"

    def __init__(self, message: str | None = None, extra: dict[str, Any] | None = None):
        self.detail = message or self.detail
        self.extra = extra or {}

    def to_dict(self) -> dict[str, Any]:
        payload = {"error_code": self.error_code, "detail": self.detail}
        payload.update(self.extra)
        return payload


class StudentNotFound(AppHTTPException):
    """Raised when the requested student record does not exist."""

    status_code = 404
    detail = "Student not found"
    error_code = "STUDENT_NOT_FOUND"


class AITimeout(AppHTTPException):
    """Raised when the Claude API call exceeds its timeout."""

    status_code = 504
    detail = "AI service timeout – please try again"
    error_code = "AI_TIMEOUT"


class InsufficientHistory(AppHTTPException):
    """Raised when there is not enough data to perform the requested analysis."""

    status_code = 422
    detail = "Insufficient student history for this operation"
    error_code = "INSUFFICIENT_HISTORY"


class Unauthorized(AppHTTPException):
    """Raised when authentication credentials are missing or invalid."""

    status_code = 401
    detail = "Authentication required"
    error_code = "UNAUTHORIZED"


class Forbidden(AppHTTPException):
    """Raised when the user does not have permission for the requested action."""

    status_code = 403
    detail = "You do not have permission to perform this action"
    error_code = "FORBIDDEN"


class ValidationError(AppHTTPException):
    """Raised when request body or parameters fail validation."""

    status_code = 422
    detail = "Validation error"
    error_code = "VALIDATION_ERROR"


class DuplicateEmail(AppHTTPException):
    """Raised on registration attempt with an already-registered email."""

    status_code = 409
    detail = "Email already registered"
    error_code = "DUPLICATE_EMAIL"


class InvalidCredentials(AppHTTPException):
    """Raised when login credentials are incorrect."""

    status_code = 401
    detail = "Invalid email or password"
    error_code = "INVALID_CREDENTIALS"


class TokenExpired(AppHTTPException):
    """Raised when a JWT token has expired."""

    status_code = 401
    detail = "Token has expired"
    error_code = "TOKEN_EXPIRED"


class MilestoneNotFound(AppHTTPException):
    """Raised when the requested milestone does not exist."""

    status_code = 404
    detail = "Milestone not found"
    error_code = "MILESTONE_NOT_FOUND"
