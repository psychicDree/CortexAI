import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Literal, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ollama_client import OllamaClient, OllamaError
from prompts import (
    CRISIS_MESSAGE,
    NO_ANSWER_MESSAGE,
    ask_messages,
    fallback_reply,
    has_contact_details,
    reply_messages,
)
from question_bank import QuestionBank, load_entries

DEFAULT_BANK_PATH = Path(__file__).resolve().parent / "question_bank.yaml"


class ReplyRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    emotion: Literal["joy", "sadness", "anger", "fear", "neutral"]
    crisis_flag: bool = False
    module_title: str = Field(..., min_length=1, max_length=200)
    module_description: str = Field("", max_length=1000)


class ReplyResponse(BaseModel):
    reply: str
    model: str


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    crisis_flag: bool = False


class Source(BaseModel):
    id: str
    question: str
    score: float


class AskResponse(BaseModel):
    answer: str
    sources: List[Source]
    model: str


def create_app(ollama: Optional[OllamaClient] = None, bank: Optional[QuestionBank] = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        client = ollama or OllamaClient.from_env()
        app.state.ollama = client
        app.state.include_drafts = os.getenv("COMPANION_INCLUDE_DRAFTS", "false").lower() == "true"
        app.state.bank = bank or QuestionBank(
            load_entries(Path(os.getenv("QUESTION_BANK_PATH", DEFAULT_BANK_PATH)), app.state.include_drafts),
            client.embed,
        )
        app.state.top_k = int(os.getenv("COMPANION_TOP_K", "3"))
        app.state.min_score = float(os.getenv("COMPANION_MIN_SCORE", "0.58"))
        yield

    app = FastAPI(title="CortexAI Companion Service", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.post("/reply", response_model=ReplyResponse)
    def reply(body: ReplyRequest, request: Request) -> ReplyResponse:
        # Crisis replies are fixed text, never generated.
        if body.crisis_flag:
            return ReplyResponse(reply=CRISIS_MESSAGE, model="none")
        client: OllamaClient = request.app.state.ollama
        try:
            text = client.chat(reply_messages(body.text, body.emotion, body.module_title, body.module_description))
        except OllamaError:
            raise HTTPException(status_code=503, detail="Language model unavailable")
        if has_contact_details(text):
            return ReplyResponse(reply=fallback_reply(body.module_title, body.module_description), model="fallback")
        return ReplyResponse(reply=text, model=client.chat_model)

    @app.post("/ask", response_model=AskResponse)
    def ask(body: AskRequest, request: Request) -> AskResponse:
        if body.crisis_flag:
            return AskResponse(answer=CRISIS_MESSAGE, sources=[], model="none")
        state = request.app.state
        try:
            hits = state.bank.search(body.question, state.top_k, state.min_score)
            if not hits:
                return AskResponse(answer=NO_ANSWER_MESSAGE, sources=[], model="none")
            answer = state.ollama.chat(ask_messages(body.question, [e for e, _ in hits]), max_tokens=250, temperature=0.2)
        except OllamaError:
            raise HTTPException(status_code=503, detail="Language model unavailable")
        sources = [Source(id=e.id, question=e.question, score=s) for e, s in hits]
        if has_contact_details(answer):
            # Fall back to the best-matching entry, verbatim.
            return AskResponse(answer=hits[0][0].answer, sources=sources[:1], model="fallback")
        return AskResponse(answer=answer, sources=sources, model=state.ollama.chat_model)

    @app.get("/health")
    def health(request: Request) -> dict:
        state = request.app.state
        return {
            "status": "ok",
            "chat_model": state.ollama.chat_model,
            "embed_model": state.ollama.embed_model,
            "entries": len(state.bank.entries),
            "include_drafts": state.include_drafts,
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)
