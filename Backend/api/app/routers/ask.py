from fastapi import APIRouter, Depends, HTTPException

from .. import models, schemas
from ..aiengine import AIEngineClient, AIEngineError, get_aiengine
from ..auth import get_current_user


router = APIRouter()


@router.post("/", response_model=schemas.AskOut)
def ask(
    ask_in: schemas.AskCreate,
    current_user: models.User = Depends(get_current_user),
    aiengine: AIEngineClient = Depends(get_aiengine),
):
    # Screen the question with the same crisis check as check-ins. Nothing is stored.
    try:
        crisis_flag = aiengine.analyze(ask_in.question)["crisis_flag"]
        result = aiengine.ask(ask_in.question, crisis_flag)
    except (AIEngineError, KeyError):
        raise HTTPException(status_code=503, detail="AI engine unavailable")
    return schemas.AskOut(answer=result["answer"], sources=result["sources"], crisis_flag=crisis_flag)
