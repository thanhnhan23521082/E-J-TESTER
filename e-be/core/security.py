"""
core/security.py
────────────────
Synchronous password hashing via bcrypt.
"""

import bcrypt


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
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.

    Args:
        plain: The raw password to check.
        hashed: The stored bcrypt hash.

    Returns:
        True if the password matches, False otherwise.
    """
    if not plain or not hashed:
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False
