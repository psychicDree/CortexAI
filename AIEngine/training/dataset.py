import json
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

# Single source of truth for the label mapping is the serving code.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "emotion_analysis"))
from classifier import EMOTIONS, GOEMOTIONS_TO_EMOTION  # noqa: E402

GOEMOTIONS_REPO = "google-research-datasets/go_emotions"
GOEMOTIONS_REVISION = "add492243ff905527e67aeb8b80c082af02207c3"
GOEMOTIONS_LICENSE = "Apache-2.0"
SPLITS = ("train", "validation", "test")

# Label ids of the "simplified" config, from the dataset card.
GOEMOTIONS_LABELS = (
    "admiration", "amusement", "anger", "annoyance", "approval", "caring", "confusion",
    "curiosity", "desire", "disappointment", "disapproval", "disgust", "embarrassment",
    "excitement", "fear", "gratitude", "grief", "joy", "love", "nervousness", "optimism",
    "pride", "realization", "relief", "remorse", "sadness", "surprise", "neutral",
)


def to_canonical(label_ids: Sequence[int]) -> Optional[str]:
    """Map GoEmotions label ids to one canonical emotion, or None if they disagree."""
    emotions = {GOEMOTIONS_TO_EMOTION[GOEMOTIONS_LABELS[i]] for i in label_ids}
    return emotions.pop() if len(emotions) == 1 else None


def build_rows(records: Iterable[dict], source: str) -> Tuple[List[dict], Dict[str, int]]:
    rows, dropped = [], 0
    for record in records:
        text = (record.get("text") or "").strip()
        label = to_canonical(record.get("labels") or [])
        if not text or label is None:
            dropped += 1
            continue
        rows.append({"id": record.get("id"), "text": text, "label": label, "source": source})
    counts = Counter(r["label"] for r in rows)
    stats = {e: counts.get(e, 0) for e in EMOTIONS}
    stats["dropped_ambiguous_or_empty"] = dropped
    return rows, stats


def write_jsonl(rows: Iterable[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_jsonl(path: Path, limit: Optional[int] = None) -> List[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if limit is not None and len(rows) >= limit:
                break
            rows.append(json.loads(line))
    return rows
