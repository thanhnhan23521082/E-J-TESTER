"""
core/security.py
────────────────
Synchronous password hashing via bcrypt (passlib wrapper).
"""

from passlib.context import CryptContext

# ── bcrypt context ────────────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(plain: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Args:
        plain: The raw password string.

    Returns:
        The bcrypt hash (~60 characters).
    """
    if not plain:
        raise ValueError("Password cannot be empty")
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.

    Args:
        plain: The raw password to check.
        hashed: The stored bcrypt hash.

    Returns:
        True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain, hashed)
