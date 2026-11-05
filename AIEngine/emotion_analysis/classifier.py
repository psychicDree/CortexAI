import logging
import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Protocol

logger = logging.getLogger(__name__)

EMOTIONS = ("joy", "sadness", "anger", "fear", "neutral")

DEFAULT_MODEL = "SamLowe/roberta-base-go_emotions"
DEFAULT_REVISION = "d75048347613a25d77de8cf6412eaae9fa7b26be"

# GoEmotions labels grouped by the paper's Ekman mapping (Demszky et al., 2020),
# with disgust folded into anger and surprise into neutral.
GOEMOTIONS_TO_EMOTION = {
    "anger": "anger",
    "annoyance": "anger",
    "disapproval": "anger",
    "disgust": "anger",
    "fear": "fear",
    "nervousness": "fear",
    "joy": "joy",
    "amusement": "joy",
    "approval": "joy",
    "excitement": "joy",
    "gratitude": "joy",
    "love": "joy",
    "optimism": "joy",
    "relief": "joy",
    "pride": "joy",
    "admiration": "joy",
    "desire": "joy",
    "caring": "joy",
    "sadness": "sadness",
    "disappointment": "sadness",
    "embarrassment": "sadness",
    "grief": "sadness",
    "remorse": "sadness",
    "surprise": "neutral",
    "realization": "neutral",
    "confusion": "neutral",
    "curiosity": "neutral",
    "neutral": "neutral",
}


@dataclass(frozen=True)
class Prediction:
    emotion: str
    confidence: float
    scores: Dict[str, float]
    model: str


class Classifier(Protocol):
    name: str

    def predict(self, text: str) -> Prediction: ...


def _prediction(scores: Dict[str, float], model: str) -> Prediction:
    rounded = {e: round(scores.get(e, 0.0), 4) for e in EMOTIONS}
    emotion = max(EMOTIONS, key=lambda e: rounded[e])
    return Prediction(emotion=emotion, confidence=rounded[emotion], scores=rounded, model=model)


class TransformerClassifier:
    """Multi-label GoEmotions model; each canonical score is the max of its member labels."""

    def __init__(self, pipe: Callable[[List[str]], List[List[dict]]], name: str):
        self._pipe = pipe
        self.name = name

    @classmethod
    def load(cls, model_name: str, revision: str) -> "TransformerClassifier":
        from transformers import pipeline

        pipe = pipeline(
            "text-classification",
            model=model_name,
            revision=revision,
            top_k=None,
            truncation=True,
        )
        return cls(pipe, model_name)

    def predict(self, text: str) -> Prediction:
        scores = {e: 0.0 for e in EMOTIONS}
        for item in self._pipe([text])[0]:
            emotion = GOEMOTIONS_TO_EMOTION.get(item["label"])
            if emotion:
                scores[emotion] = max(scores[emotion], float(item["score"]))
        return _prediction(scores, self.name)


KEYWORDS = {
    "joy": {"happy", "great", "good", "awesome", "love", "grateful", "glad", "excited", "calm", "proud"},
    "sadness": {"sad", "down", "blue", "depressed", "cry", "crying", "lonely", "hopeless", "empty"},
    "anger": {"angry", "mad", "furious", "annoyed", "rage", "frustrated", "irritated"},
    "fear": {"scared", "afraid", "anxious", "worried", "nervous", "panic", "panicking", "stressed"},
}
NEGATIONS = {"not", "no", "never", "hardly", "isn't", "aren't", "wasn't", "don't", "didn't", "doesn't"}
_TOKEN_RE = re.compile(r"[a-z']+")


class LexiconClassifier:
    """Keyword fallback for when the model is unavailable. Skips words negated in the previous 3 tokens."""

    name = "lexicon"

    def predict(self, text: str) -> Prediction:
        tokens = _TOKEN_RE.findall(text.lower())
        counts = {e: 0 for e in KEYWORDS}
        for i, token in enumerate(tokens):
            if any(t in NEGATIONS for t in tokens[max(0, i - 3):i]):
                continue
            for emotion, words in KEYWORDS.items():
                if token in words:
                    counts[emotion] += 1

        scores = {e: min(1.0, 0.2 * c) for e, c in counts.items()}
        scores["neutral"] = 0.0 if any(counts.values()) else 0.5
        return _prediction(scores, self.name)


def build_classifier(backend: str, model_name: str, revision: str) -> Classifier:
    if backend == "lexicon":
        return LexiconClassifier()
    try:
        return TransformerClassifier.load(model_name, revision)
    except Exception:
        logger.exception("Could not load %s; falling back to lexicon classifier", model_name)
        return LexiconClassifier()
