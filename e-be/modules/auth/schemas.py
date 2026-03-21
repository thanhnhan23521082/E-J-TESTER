"""
modules/auth/schemas.py
──────────────────────
Pydantic request/response models for the auth router.
"""

from pydantic import BaseModel, EmailStr, Field


# ── Request schemas ───────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    """Payload for user registration."""

    email: EmailStr = Field(..., description="Unique email address")
    password: str = Field(..., min_length=8, max_length=128, description="Plain-text password (8–128 chars)")
    role: str = Field(default="parent", description="Account role: parent | mentor | admin")

    model_config = {"json_schema_extra": {
        "example": {
            "email": "parent@example.com",
            "password": "SecurePass123!",
            "role": "parent",
        }
    }}


class LoginRequest(BaseModel):
    """Payload for user login."""

    email: EmailStr
    password: str

    model_config = {"json_schema_extra": {
        "example": {
            "email": "parent@example.com",
            "password": "SecurePass123!",
        }
    }}


class RefreshRequest(BaseModel):
    """Payload for refreshing an access token."""

    refresh_token: str = Field(..., description="A valid refresh token")


# ── Response schemas ─────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    """Combined access + refresh token response."""

    access_token: str = Field(..., description="Short-lived JWT access token (HS256)")
    refresh_token: str = Field(..., description="Long-lived JWT refresh token")
    token_type: str = Field(default="bearer")
    expires_in: int = Field(..., description="Access token lifetime in seconds")

    model_config = {"json_schema_extra": {
        "example": {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "expires_in": 1800,
        }
    }}


class UserResponse(BaseModel):
    """Public user profile (no password)."""

    id: int
    email: str
    role: str
    created_at: str  # ISO 8601 string

    model_config = {"from_attributes": True}
