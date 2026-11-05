import hashlib
import hmac
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db


router = APIRouter()

# The client generates a random secret with the profile and sends it on every call.
# Only its SHA-256 is stored; the secret is high-entropy, so a fast hash is enough.
DEVICE_SECRET_HEADER = "X-Device-Secret"
MIN_SECRET_LENGTH = 32


def device_secret(x_device_secret: Optional[str] = Header(None, alias=DEVICE_SECRET_HEADER)) -> str:
    if not x_device_secret or not (MIN_SECRET_LENGTH <= len(x_device_secret) <= 256):
        raise HTTPException(
            status_code=401,
            detail=f"{DEVICE_SECRET_HEADER} header of at least {MIN_SECRET_LENGTH} characters is required",
        )
    return x_device_secret


def _hash(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def _credential(db: Session, client_user_id: str) -> Optional[models.OnboardingCredential]:
    return (
        db.query(models.OnboardingCredential)
        .filter(models.OnboardingCredential.client_user_id == client_user_id)
        .first()
    )


def _matches(credential: Optional[models.OnboardingCredential], secret: str) -> bool:
    return credential is not None and hmac.compare_digest(credential.secret_hash, _hash(secret))


@router.post("/", response_model=schemas.OnboardingProfileOut)
def upsert_onboarding_profile(
    profile_in: schemas.OnboardingProfileCreate,
    db: Session = Depends(get_db),
    secret: str = Depends(device_secret),
):
    existing = (
        db.query(models.OnboardingProfile)
        .filter(models.OnboardingProfile.client_user_id == profile_in.client_user_id)
        .first()
    )
    credential = _credential(db, profile_in.client_user_id)
    if credential is not None and not _matches(credential, secret):
        raise HTTPException(status_code=403, detail="Device secret does not match this profile")

    if existing:
        existing.display_name = profile_in.display_name
        existing.age = profile_in.age
        record = existing
    else:
        record = models.OnboardingProfile(
            client_user_id=profile_in.client_user_id,
            display_name=profile_in.display_name,
            age=profile_in.age,
        )
        db.add(record)

    # Profiles created before credentials existed are claimed by the first secret that updates them.
    if credential is None:
        db.flush()
        db.add(models.OnboardingCredential(client_user_id=profile_in.client_user_id, secret_hash=_hash(secret)))

    db.commit()
    db.refresh(record)
    return record


@router.get("/{client_user_id}", response_model=schemas.OnboardingProfileOut)
def get_onboarding_profile(
    client_user_id: str, db: Session = Depends(get_db), secret: str = Depends(device_secret)
):
    record = (
        db.query(models.OnboardingProfile)
        .filter(models.OnboardingProfile.client_user_id == client_user_id)
        .first()
    )
    # Same 404 for a missing profile and a wrong secret, so IDs can't be probed.
    if not record or not _matches(_credential(db, client_user_id), secret):
        raise HTTPException(status_code=404, detail="Onboarding profile not found")
    return record
