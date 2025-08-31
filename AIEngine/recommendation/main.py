from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from typing import Literal


class RecommendRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    mood: Literal["joy", "sadness", "anger", "fear", "neutral"]


class RecommendResponse(BaseModel):
    module: str
    level: Literal["intro", "intermediate", "advanced"]


app = FastAPI(title="CortexAI Recommendation Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/recommend", response_model=RecommendResponse)
def recommend(request: RecommendRequest) -> RecommendResponse:
    mood_to_module = {
        "joy": ("gratitude_practice", "intermediate"),
        "sadness": ("mood_journaling", "intro"),
        "anger": ("breathwork", "intro"),
        "fear": ("grounding_exercises", "intro"),
        "neutral": ("mindfulness_check_in", "intro"),
    }
    module, level = mood_to_module.get(request.mood, ("mindfulness_check_in", "intro"))
    return RecommendResponse(module=module, level=level)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)

