import os
from typing import List, Optional

import httpx


EMOTION_SERVICE_URL = os.getenv("EMOTION_SERVICE_URL", "http://localhost:8001")
RECOMMENDATION_SERVICE_URL = os.getenv("RECOMMENDATION_SERVICE_URL", "http://localhost:8002")
COMPANION_SERVICE_URL = os.getenv("COMPANION_SERVICE_URL", "http://localhost:8003")
AIENGINE_TIMEOUT_SECONDS = float(os.getenv("AIENGINE_TIMEOUT_SECONDS", "10"))
# Local LLM generation is slower than classification.
COMPANION_TIMEOUT_SECONDS = float(os.getenv("COMPANION_TIMEOUT_SECONDS", "60"))


class AIEngineError(Exception):
    pass


class AIEngineClient:
    def __init__(
        self,
        emotion_url: str,
        recommendation_url: str,
        companion_url: str,
        timeout: float,
        companion_timeout: float,
    ):
        self._emotion_url = emotion_url.rstrip("/")
        self._recommendation_url = recommendation_url.rstrip("/")
        self._companion_url = companion_url.rstrip("/")
        self._timeout = timeout
        self._companion_timeout = companion_timeout

    def _post(self, url: str, payload: dict, timeout: Optional[float] = None) -> dict:
        try:
            res = httpx.post(url, json=payload, timeout=timeout or self._timeout)
            res.raise_for_status()
            return res.json()
        except (httpx.HTTPError, ValueError) as exc:
            # Do not include the payload: it may contain the user's text.
            raise AIEngineError(f"{url} failed: {type(exc).__name__}") from exc

    def analyze(self, text: str) -> dict:
        return self._post(f"{self._emotion_url}/analyze", {"text": text})

    def recommend(self, user_id: str, mood: str, confidence: float, crisis_flag: bool, history: List[str]) -> dict:
        return self._post(
            f"{self._recommendation_url}/recommend",
            {
                "user_id": user_id,
                "mood": mood,
                "confidence": confidence,
                "crisis_flag": crisis_flag,
                "history": history,
            },
        )

    def reply(self, text: str, emotion: str, crisis_flag: bool, module_title: str, module_description: str) -> dict:
        return self._post(
            f"{self._companion_url}/reply",
            {
                "text": text,
                "emotion": emotion,
                "crisis_flag": crisis_flag,
                "module_title": module_title,
                "module_description": module_description,
            },
            timeout=self._companion_timeout,
        )

    def ask(self, question: str, crisis_flag: bool) -> dict:
        return self._post(
            f"{self._companion_url}/ask",
            {"question": question, "crisis_flag": crisis_flag},
            timeout=self._companion_timeout,
        )


_client = AIEngineClient(
    EMOTION_SERVICE_URL,
    RECOMMENDATION_SERVICE_URL,
    COMPANION_SERVICE_URL,
    AIENGINE_TIMEOUT_SECONDS,
    COMPANION_TIMEOUT_SECONDS,
)


def get_aiengine() -> AIEngineClient:
    return _client
