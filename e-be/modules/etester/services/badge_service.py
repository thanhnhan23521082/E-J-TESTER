"""
modules/etester/services/badge_service.py
─────────────────────────────────────────
Badge issuance flow:
1. Gather ETESTERCore + signing chain
2. Build JWT payload
3. Sign with RS256 (or HS256 fallback)
4. Persist ETESTERBadge
"""

import hashlib
import json
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

try:
    import jwt as pyjwt
except ImportError:
    pyjwt = None

from modules.etester import repository as repo

logger = logging.getLogger(__name__)

ISSUER_DID = "did:web:etest.edu.vn"
VERIFY_BASE_URL = os.getenv("ETESTER_VERIFY_URL", "https://etest.edu.vn/etester/verify")
BADGE_VALIDITY_DAYS = int(os.getenv("ETESTER_BADGE_DAYS", "730"))


def _sign_jwt(payload: dict) -> tuple[str, str]:
    """
    Sign badge payload. Try RS256 with private key first, fall back to HS256.
    Returns (signed_token, credential_type).
    """
    private_key = os.getenv("ETESTER_RS256_PRIVATE_KEY")
    if private_key and pyjwt:
        token = pyjwt.encode(payload, private_key, algorithm="RS256")
        return token, "jwt_rs256"

    secret = os.getenv("JWT_SECRET", "etester-dev-secret")
    if pyjwt:
        token = pyjwt.encode(payload, secret, algorithm="HS256")
        return token, "jwt_hs256"

    logger.warning("PyJWT not available — storing raw payload as signed_token")
    return json.dumps(payload, default=str), "jwt_hs256_stub"


async def issue_badge(
    student_id: str,
    manager_id: int,
    db: AsyncSession,
) -> dict:
    """
    Issue an ETESTER badge for a student.
    Pre-conditions checked by caller (core exists, institutional_stamp, etc.).
    """
    core = await repo.get_etester_core(student_id, db)
    if core is None:
        raise ValueError(f"ETESTERCore not found for student {student_id}")

    student = await repo.get_student(student_id, db)
    student_name = student.name if student else student_id

    existing = await repo.get_badge_for_student(student_id, db)
    if existing:
        raise ValueError(f"Active badge already exists: {existing.badge_uid}")

    badge_uid = f"ETEST-{student_id[-6:].upper()}-{uuid.uuid4().hex[:8].upper()}"

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=BADGE_VALIDITY_DAYS)

    milestones = await repo.get_all_milestones(student_id, db, limit=50)
    contribution_summary = await repo.get_contribution_summary(student_id, db)

    payload = {
        "badge_uid": badge_uid,
        "student_id": student_id,
        "student_name": student_name,
        "issuer": ISSUER_DID,
        "issued_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "program": student.school_name if student and hasattr(student, "school_name") else "ETEST",
        "auth_score": core.consistency_score,
        "total_contributions": core.total_contributions,
        "mentor_verifications": core.mentor_verifications,
        "skills": core.skills or [],
        "contribution_summary": contribution_summary,
        "narrative_en": core.narrative_en,
        "narrative_vn": core.narrative_vn,
        "signing_chain": [
            {"step": "mentor_review", "status": "verified", "count": core.mentor_verifications},
            {"step": "institutional_stamp", "status": "stamped" if core.institutional_stamp else "pending"},
            {"step": "badge_issuance", "manager_id": manager_id, "issued_at": now.isoformat()},
        ],
    }

    signed_token, credential_type = _sign_jwt(payload)

    badge = await repo.save_badge(
        db,
        core_id=core.id,
        student_id=student_id,
        badge_uid=badge_uid,
        signed_token=signed_token,
        badge_payload=payload,
        credential_type=credential_type,
        expires_at=expires_at,
    )

    core.badge_issued = True
    await db.commit()

    return {
        "student_id": student_id,
        "badge_uid": badge.badge_uid,
        "credential_type": badge.credential_type,
        "badge_payload": badge.badge_payload,
        "issued_at": badge.issued_at.isoformat(),
        "expires_at": badge.expires_at.isoformat() if badge.expires_at else None,
        "qr_url": f"{VERIFY_BASE_URL}/{badge.badge_uid}",
    }


async def verify_badge(badge_uid: str, db: AsyncSession) -> dict:
    """Look up and verify a badge."""
    badge = await repo.get_badge_by_uid(badge_uid, db)
    if badge is None:
        return {
            "valid": False,
            "badge_uid": badge_uid,
            "badge_payload": {},
            "issuer": ISSUER_DID,
            "is_revoked": False,
        }

    student = await repo.get_student(badge.student_id, db)

    badge.verify_count = (badge.verify_count or 0) + 1
    badge.last_verified_at = datetime.now(timezone.utc)
    await db.commit()

    is_expired = badge.expires_at and badge.expires_at < datetime.now(timezone.utc)

    return {
        "valid": not badge.is_revoked and not is_expired,
        "badge_uid": badge.badge_uid,
        "student_name": student.name if student else None,
        "program": badge.badge_payload.get("program"),
        "badge_payload": badge.badge_payload,
        "issued_at": badge.issued_at.isoformat(),
        "issuer": ISSUER_DID,
        "is_revoked": badge.is_revoked,
    }
