from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from typing import Literal


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="User input text to analyze")


class AnalyzeResponse(BaseModel):
    emotion: Literal["joy", "sadness", "anger", "fear", "neutral"]
    confidence: float


app = FastAPI(title="CortexAI Emotion Analysis Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


KEYWORDS = {
    "joy": ["happy", "great", "good", "awesome", "love", "grateful"],
    "sadness": ["sad", "down", "blue", "depressed", "cry"],
    "anger": ["angry", "mad", "furious", "annoyed", "rage"],
    "fear": ["scared", "afraid", "anxious", "worried", "nervous"],
}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    text_lower = request.text.lower()
    best_emotion = "neutral"
    best_score = 0
    for emotion, words in KEYWORDS.items():
        score = sum(1 for word in words if word in text_lower)
        if score > best_score:
            best_emotion = emotion
            best_score = score
    confidence = min(1.0, 0.2 * best_score) if best_score > 0 else 0.5
    return AnalyzeResponse(emotion=best_emotion, confidence=confidence)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)

