from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..aiengine import AIEngineClient, AIEngineError, get_aiengine
from ..auth import get_current_user
from ..database import get_db


router = APIRouter()

# How many past check-ins feed the recommender's rotation and level logic.
HISTORY_LIMIT = 50

# Recorded instead of the classifier's label when crisis language is detected:
# the model can mislabel crisis text (e.g. "joy"), which would skew mood history.
CRISIS_EMOTION = "crisis"


@router.post("/", response_model=schemas.CheckInResult)
def create_checkin(
    checkin_in: schemas.CheckInCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    aiengine: AIEngineClient = Depends(get_aiengine),
):
    session = None
    if checkin_in.session_id is not None:
        session = (
            db.query(models.Session)
            .filter(models.Session.id == checkin_in.session_id, models.Session.user_id == current_user.id)
            .first()
        )
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")

    recent = (
        db.query(models.CheckIn.module)
        .filter(models.CheckIn.user_id == current_user.id)
        .order_by(models.CheckIn.id.desc())
        .limit(HISTORY_LIMIT)
        .all()
    )
    history = [row.module for row in reversed(recent)]

    try:
        analysis = aiengine.analyze(checkin_in.text)
        rec = aiengine.recommend(
            user_id=str(current_user.id),
            mood=analysis["emotion"],
            confidence=analysis["confidence"],
            crisis_flag=analysis["crisis_flag"],
            history=history,
        )
    except (AIEngineError, KeyError):
        raise HTTPException(status_code=503, detail="AI engine unavailable")

    crisis = bool(analysis["crisis_flag"])
    emotion = CRISIS_EMOTION if crisis else analysis["emotion"]

    # The raw text is not stored.
    record = models.CheckIn(
        user_id=current_user.id,
        session_id=session.id if session else None,
        emotion=emotion,
        confidence=0.0 if crisis else analysis["confidence"],
        crisis_flag=crisis,
        module=rec["module"],
        level=rec["level"],
    )
    db.add(record)
    if session is not None:
        session.mood = emotion
    db.commit()
    db.refresh(record)

    # The companion reply is optional: the check-in still succeeds without it.
    try:
        reply = aiengine.reply(
            text=checkin_in.text,
            emotion=analysis["emotion"],
            crisis_flag=analysis["crisis_flag"],
            module_title=rec["title"],
            module_description=rec["description"],
        )["reply"]
    except (AIEngineError, KeyError):
        reply = None

    return schemas.CheckInResult(
        **schemas.CheckInOut.model_validate(record).model_dump(),
        title=rec["title"],
        description=rec["description"],
        minutes=rec["minutes"],
        alternatives=rec["alternatives"],
        reply=reply,
    )


@router.get("/", response_model=list[schemas.CheckInOut])
def list_checkins(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return (
        db.query(models.CheckIn)
        .filter(models.CheckIn.user_id == current_user.id)
        .order_by(models.CheckIn.id.desc())
        .all()
    )
