from dataclasses import dataclass
from typing import List, Sequence

from catalog import CATALOG, CRISIS_SUPPORT, Module

# Below this emotion confidence the mood is treated as neutral.
LOW_CONFIDENCE = 0.4

# (times recommended before, level), checked in order.
LEVEL_STEPS = ((8, "advanced"), (3, "intermediate"), (0, "intro"))


@dataclass(frozen=True)
class Recommendation:
    module: Module
    level: str
    reason: str
    alternatives: List[str]


def level_for(times_seen: int) -> str:
    return next(level for threshold, level in LEVEL_STEPS if times_seen >= threshold)


def recommend(mood: str, confidence: float, crisis_flag: bool, history: Sequence[str]) -> Recommendation:
    """Pick a module for the mood, rotating through matches by how often each appears in history.

    history holds previously recommended module ids, oldest first.
    """
    if crisis_flag:
        return Recommendation(CRISIS_SUPPORT, "intro", "crisis_flag", [])

    effective_mood = mood if confidence >= LOW_CONFIDENCE else "neutral"
    candidates = [m for m in CATALOG if effective_mood in m.moods]

    last = history[-1] if history else None
    pool = [m for m in candidates if m.id != last] or candidates
    chosen = min(pool, key=lambda m: history.count(m.id))

    return Recommendation(
        module=chosen,
        level=level_for(history.count(chosen.id)),
        reason="mood_match" if effective_mood == mood else "low_confidence",
        alternatives=[m.id for m in candidates if m.id != chosen.id],
    )
