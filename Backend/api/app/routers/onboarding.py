from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db


router = APIRouter()


@router.post("/", response_model=schemas.OnboardingProfileOut)
def upsert_onboarding_profile(
    profile_in: schemas.OnboardingProfileCreate, db: Session = Depends(get_db)
):
    existing = (
        db.query(models.OnboardingProfile)
        .filter(models.OnboardingProfile.client_user_id == profile_in.client_user_id)
        .first()
    )
    if existing:
        existing.display_name = profile_in.display_name
        existing.age = profile_in.age
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    record = models.OnboardingProfile(
        client_user_id=profile_in.client_user_id,
        display_name=profile_in.display_name,
        age=profile_in.age,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{client_user_id}", response_model=schemas.OnboardingProfileOut)
def get_onboarding_profile(client_user_id: str, db: Session = Depends(get_db)):
    record = (
        db.query(models.OnboardingProfile)
        .filter(models.OnboardingProfile.client_user_id == client_user_id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Onboarding profile not found")
    return record

