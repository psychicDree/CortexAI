import os
from contextlib import asynccontextmanager
from typing import Dict, Literal, Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from classifier import DEFAULT_MODEL, DEFAULT_REVISION, Classifier, build_classifier
from safety import detect_crisis_language


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="User input text to analyze")


class AnalyzeResponse(BaseModel):
    emotion: Literal["joy", "sadness", "anger", "fear", "neutral"]
    confidence: float
    scores: Dict[str, float]
    crisis_flag: bool
    model: str


def create_app(classifier: Optional[Classifier] = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.classifier = classifier or build_classifier(
            backend=os.getenv("EMOTION_BACKEND", "transformer"),
            model_name=os.getenv("EMOTION_MODEL", DEFAULT_MODEL),
            revision=os.getenv("EMOTION_MODEL_REVISION", DEFAULT_REVISION),
        )
        yield

    app = FastAPI(title="CortexAI Emotion Analysis Service", version="0.2.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.post("/analyze", response_model=AnalyzeResponse)
    def analyze(body: AnalyzeRequest, request: Request) -> AnalyzeResponse:
        prediction = request.app.state.classifier.predict(body.text)
        return AnalyzeResponse(
            emotion=prediction.emotion,
            confidence=prediction.confidence,
            scores=prediction.scores,
            crisis_flag=detect_crisis_language(body.text),
            model=prediction.model,
        )

    @app.get("/health")
    def health(request: Request) -> dict:
        return {"status": "ok", "model": request.app.state.classifier.name}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
