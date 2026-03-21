"""
modules/auth/router.py
──────────────────────
Authentication endpoints: register, login, refresh, logout.
All routes live under /api/auth.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from core.database import get_db
from core.exceptions import DuplicateEmail, InvalidCredentials
from core.security import hash_password, verify_password
from modules.auth.schemas import (
    LoginRequest,
    MeResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from shared.auth import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from shared.model import Manager, Mentor, Parent, Student, User
from shared.deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])
settings = get_settings()


# ── Helpers ──────────────────────────────────────────────────────────────────

async def _get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def _check_email_in_profile_tables(db: AsyncSession, email: str) -> bool:
    """Check if email is already used in any profile table (mentor, parent, manager, student name)."""
    for model in (Mentor, Parent, Manager):
        result = await db.execute(select(model).where(model.email == email))
        if result.scalar_one_or_none():
            return True
    return False


async def _create_profile_record(
    db: AsyncSession,
    body: RegisterRequest,
    hashed_pw: str,
    user: User | None = None,
) -> None:
    """Create the role-specific profile record alongside the User row."""

    if body.role == "parent":
        profile = Parent(
            email=body.email,
            hashed_password=hashed_pw,
            full_name=body.full_name,
            phone=body.phone,
            telegram_id=body.telegram_id,
        )
        db.add(profile)

    elif body.role == "mentor":
        profile = Mentor(
            email=body.email,
            hashed_password=hashed_pw,
            full_name=body.full_name,
            specialty=body.specialty,
            bio=body.bio,
            programs=[],
        )
        db.add(profile)

    elif body.role == "student":
        # Generate a short unique student_id
        student_id = f"S-{uuid.uuid4().hex[:8].upper()}"
        profile = Student(
            student_id=student_id,
            user_id=user.id if user else None,
            name=body.full_name,
            program=body.program,
        )
        db.add(profile)

    elif body.role == "manager":
        profile = Manager(
            email=body.email,
            hashed_password=hashed_pw,
            full_name=body.full_name,
            phone=body.phone,
            department=body.department,
        )
        db.add(profile)


# ── Routes ───────────────────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Register a new user account.

    - **email**: unique email address
    - **password**: 8–128 characters
    - **role**: `parent` | `mentor` | `student` | `manager`
    - **full_name**: user's full name (required)
    - **phone**: optional phone number
    - Additional role-specific fields are accepted based on role.
    """
    # Check duplicate in users table
    existing = await _get_user_by_email(db, body.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Check duplicate in profile tables
    if await _check_email_in_profile_tables(db, body.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    hashed_pw = hash_password(body.password)

    # Create User auth record
    user = User(
        email=body.email,
        hashed_password=hashed_pw,
        role=body.role,
        full_name=body.full_name,
        phone=body.phone,
    )
    db.add(user)
    await db.flush()  # populate user.id so child records can reference it

    # Create role-specific profile record
    await _create_profile_record(db, body, hashed_pw, user)

    await db.commit()
    await db.refresh(user)

    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        full_name=user.full_name,
        phone=user.phone,
        created_at=user.created_at.isoformat(),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and obtain JWT tokens",
)
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Authenticate with email + password and receive access + refresh tokens.

    - Access token: valid for `ACCESS_TOKEN_EXPIRE_MINUTES` (default 30 min)
    - Refresh token: valid for `REFRESH_TOKEN_EXPIRE_DAYS` (default 7 days)
    """
    user = await _get_user_by_email(db, body.email)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user_id=user.id, role=user.role)
    refresh_token = create_refresh_token(user_id=user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh the access token",
)
async def refresh_token(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Issue a new access token from a valid refresh token.

    The refresh token itself is not renewed (rotation is not used to keep the
    implementation simple; in production consider refresh token rotation).
    """
    try:
        user_id = decode_refresh_token(body.refresh_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    access_token = create_access_token(user_id=user.id, role=user.role)

    return TokenResponse(
        access_token=access_token,
        refresh_token=body.refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get(
    "/me",
    response_model=MeResponse,
    summary="Get current authenticated user profile",
)
async def me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MeResponse:
    """
    Return the authenticated user's profile including role-specific IDs.
    Requires a valid Bearer access token.
    """
    student_id = None
    parent_id = None
    mentor_id = None
    manager_id = None

    if current_user.role == "student":
        result = await db.execute(
            select(Student.student_id).where(Student.user_id == current_user.id)
        )
        student_id = result.scalar_one_or_none()

    elif current_user.role == "parent":
        result = await db.execute(
            select(Parent.parent_id).where(Parent.email == current_user.email)
        )
        parent_id = result.scalar_one_or_none()

    elif current_user.role == "mentor":
        result = await db.execute(
            select(Mentor.mentor_id).where(Mentor.email == current_user.email)
        )
        mentor_id = result.scalar_one_or_none()

    elif current_user.role == "manager":
        result = await db.execute(
            select(Manager.manager_id).where(Manager.email == current_user.email)
        )
        manager_id = result.scalar_one_or_none()

    return MeResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        full_name=current_user.full_name,
        phone=current_user.phone,
        created_at=current_user.created_at.isoformat(),
        student_id=student_id,
        parent_id=parent_id,
        mentor_id=mentor_id,
        manager_id=manager_id,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout (client-side token discard)",
)
async def logout() -> None:
    """
    Logout endpoint – token invalidation is handled client-side.
    In production, implement a token denylist (Redis) if immediate revocation is needed.
    """
    return None
