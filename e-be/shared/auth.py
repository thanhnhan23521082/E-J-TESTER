"""
shared/auth.py
──────────────
JWT access-token and refresh-token creation and verification.
Tokens are signed with HS256 using SECRET_KEY from environment.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from core.config import get_settings
from core.exceptions import TokenExpired

settings = get_settings()

ALGORITHM = "HS256"


def create_access_token(user_id: int, role: str) -> str:
    """
    Create a short-lived JWT access token.

    Args:
        user_id: The authenticated user's primary key.
        role:    User role (e.g. "parent", "mentor", "admin").

    Returns:
        Encoded JWT string.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    """
    Create a long-lived JWT refresh token.

    Args:
        user_id: The authenticated user's primary key.

    Returns:
        Encoded JWT string.
    """
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str, expected_type: str = "access") -> dict:
    """
    Verify and decode a JWT token.

    Args:
        token:        The JWT string.
        expected_type: "access" or "refresh".

    Returns:
        Decoded payload dict.

    Raises:
        TokenExpired if the token has expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise TokenExpired()

    if payload.get("type") != expected_type:
        raise TokenExpired()

    return payload


def decode_refresh_token(token: str) -> int:
    """
    Decode a refresh token and return the user_id.

    Args:
        token: Refresh JWT string.

    Returns:
        The user_id (int) from the token payload.

    Raises:
        TokenExpired if invalid or expired.
    """
    payload = verify_token(token, expected_type="refresh")
    return int(payload["sub"])
