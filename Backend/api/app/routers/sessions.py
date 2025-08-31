from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db


router = APIRouter()


@router.post("/", response_model=schemas.SessionOut)
def create_session(
    session_in: schemas.SessionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    record = models.Session(
        user_id=current_user.id,
        mood=session_in.mood,
        duration_seconds=session_in.duration_seconds,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/", response_model=list[schemas.SessionOut])
def list_sessions(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Session).filter(models.Session.user_id == current_user.id).all()

