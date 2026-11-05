from typing import List, Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from engine import recommend as pick_module


class RecommendRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    mood: Literal["joy", "sadness", "anger", "fear", "neutral"]
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    crisis_flag: bool = False
    history: List[str] = Field(
        default_factory=list, max_length=200, description="Previously recommended module ids, oldest first"
    )


class RecommendResponse(BaseModel):
    module: str
    level: Literal["intro", "intermediate", "advanced"]
    title: str
    description: str
    minutes: int
    reason: Literal["mood_match", "low_confidence", "crisis_flag"]
    alternatives: List[str]


app = FastAPI(title="CortexAI Recommendation Service", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/recommend", response_model=RecommendResponse)
def recommend(request: RecommendRequest) -> RecommendResponse:
    rec = pick_module(request.mood, request.confidence, request.crisis_flag, request.history)
    return RecommendResponse(
        module=rec.module.id,
        level=rec.level,
        title=rec.module.title,
        description=rec.module.description,
        minutes=rec.module.minutes,
        reason=rec.reason,
        alternatives=rec.alternatives,
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
