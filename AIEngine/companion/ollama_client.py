import os
from typing import Dict, List

import httpx


class OllamaError(Exception):
    pass


class OllamaClient:
    def __init__(self, base_url: str, chat_model: str, embed_model: str, timeout: float):
        self._base_url = base_url.rstrip("/")
        self.chat_model = chat_model
        self.embed_model = embed_model
        self._timeout = timeout

    @classmethod
    def from_env(cls) -> "OllamaClient":
        return cls(
            base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
            chat_model=os.getenv("COMPANION_CHAT_MODEL", "llama3.2:3b"),
            embed_model=os.getenv("COMPANION_EMBED_MODEL", "nomic-embed-text"),
            timeout=float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "60")),
        )

    def _post(self, path: str, payload: dict) -> dict:
        try:
            res = httpx.post(f"{self._base_url}{path}", json=payload, timeout=self._timeout)
            res.raise_for_status()
            return res.json()
        except (httpx.HTTPError, ValueError) as exc:
            # Do not include the payload: it may contain the user's text.
            raise OllamaError(f"Ollama {path} failed: {type(exc).__name__}") from exc

    def chat(self, messages: List[Dict[str, str]], max_tokens: int = 200, temperature: float = 0.4) -> str:
        data = self._post(
            "/api/chat",
            {
                "model": self.chat_model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": temperature, "num_predict": max_tokens},
            },
        )
        try:
            return data["message"]["content"].strip()
        except (KeyError, TypeError, AttributeError) as exc:
            raise OllamaError("Ollama /api/chat returned no message") from exc

    def embed(self, texts: List[str]) -> List[List[float]]:
        data = self._post("/api/embed", {"model": self.embed_model, "input": texts})
        embeddings = data.get("embeddings")
        if not isinstance(embeddings, list) or len(embeddings) != len(texts):
            raise OllamaError("Ollama /api/embed returned the wrong number of embeddings")
        return embeddings
