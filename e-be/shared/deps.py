"""
shared/deps.py
──────────────
FastAPI security dependencies used across all routers.
Provides `get_current_user` and `get_current_user_optional` dependencies.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.exceptions import Unauthorized
from shared.auth import verify_token
from shared.model import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Dependency that returns the authenticated User for the current request.
    Raises 401 if the token is missing, invalid, or expired.
    """
    try:
        payload = verify_token(token, expected_type="access")
    except Unauthorized:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = int(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_user_optional(
    token: Annotated[str | None, Depends(oauth2_scheme)] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,  # type: ignore[assignment]
) -> User | None:
    """
    Optional authentication – returns the User if a valid token is provided,
    otherwise returns None. Useful for endpoints that behave differently
    for logged-in vs anonymous callers.
    """
    if token is None:
        return None

    try:
        payload = verify_token(token, expected_type="access")
    except Unauthorized:
        return None

    user_id = int(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
