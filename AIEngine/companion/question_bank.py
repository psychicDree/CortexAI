import math
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Sequence, Tuple

import yaml

STATUSES = ("draft", "reviewed")

# nomic-embed-text expects these task prefixes.
DOCUMENT_PREFIX = "search_document: "
QUERY_PREFIX = "search_query: "


@dataclass(frozen=True)
class Entry:
    id: str
    question: str
    answer: str
    tags: Tuple[str, ...]
    status: str


def load_entries(path: Path, include_drafts: bool) -> List[Entry]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    entries, seen = [], set()
    for item in raw:
        entry = Entry(
            id=str(item["id"]),
            question=str(item["question"]).strip(),
            answer=str(item["answer"]).strip(),
            tags=tuple(item.get("tags", [])),
            status=str(item.get("status", "draft")),
        )
        if entry.status not in STATUSES:
            raise ValueError(f"{entry.id}: status must be one of {STATUSES}")
        if entry.id in seen:
            raise ValueError(f"duplicate id {entry.id}")
        seen.add(entry.id)
        if entry.status == "reviewed" or include_drafts:
            entries.append(entry)
    return entries


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / norm if norm else 0.0


class QuestionBank:
    """In-memory vector index over the bank. Embeds entries on first search."""

    def __init__(self, entries: List[Entry], embed: Callable[[List[str]], List[List[float]]]):
        self.entries = entries
        self._embed = embed
        self._vectors: Optional[List[List[float]]] = None
        self._lock = threading.Lock()

    def _index(self) -> List[List[float]]:
        with self._lock:
            if self._vectors is None:
                docs = [f"{DOCUMENT_PREFIX}{e.question}\n{e.answer}" for e in self.entries]
                self._vectors = self._embed(docs) if docs else []
            return self._vectors

    def search(self, query: str, top_k: int, min_score: float) -> List[Tuple[Entry, float]]:
        if not self.entries:
            return []
        vectors = self._index()
        query_vector = self._embed([f"{QUERY_PREFIX}{query}"])[0]
        scored = sorted(
            ((entry, cosine(query_vector, vec)) for entry, vec in zip(self.entries, vectors)),
            key=lambda pair: pair[1],
            reverse=True,
        )
        return [(entry, round(score, 4)) for entry, score in scored[:top_k] if score >= min_score]
