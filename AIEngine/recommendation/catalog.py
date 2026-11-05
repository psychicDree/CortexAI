from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Module:
    id: str
    title: str
    description: str
    moods: Tuple[str, ...]
    minutes: int


CRISIS_SUPPORT = Module(
    id="crisis_support",
    title="Get support now",
    description=(
        "If you are thinking about harming yourself, contact local emergency services "
        "or a crisis line now, or reach out to someone you trust."
    ),
    moods=(),
    minutes=0,
)

# Order is priority: earlier modules are picked first when history is equal.
CATALOG = (
    Module("gratitude_practice", "Gratitude practice", "Write down three things that went well today.", ("joy", "neutral"), 5),
    Module("savoring", "Savoring", "Replay a good moment in detail and notice how it feels.", ("joy",), 5),
    Module("mood_journaling", "Mood journaling", "Name what you feel and what led up to it.", ("sadness", "neutral"), 10),
    Module("self_compassion_break", "Self-compassion break", "Speak to yourself as you would to a friend.", ("sadness", "anger"), 5),
    Module("gentle_movement", "Gentle movement", "A short walk or stretch to shift your energy.", ("sadness",), 10),
    Module("breathwork", "Breathwork", "Slow, paced breathing to settle your body.", ("anger", "fear"), 5),
    Module("grounding_exercises", "Grounding", "Use your senses to come back to the present.", ("fear", "anger"), 5),
    Module("progressive_muscle_relaxation", "Muscle relaxation", "Tense and release muscle groups one at a time.", ("fear",), 10),
    Module("mindfulness_check_in", "Mindfulness check-in", "Pause and notice your breath, body, and thoughts.", ("neutral",), 3),
)

MODULES_BY_ID = {m.id: m for m in CATALOG + (CRISIS_SUPPORT,)}
