import pytest
from fastapi.testclient import TestClient

from catalog import CATALOG, MODULES_BY_ID
from engine import level_for, recommend
from main import app

client = TestClient(app)


@pytest.mark.parametrize(
    "mood, module",
    [
        ("joy", "gratitude_practice"),
        ("sadness", "mood_journaling"),
        ("anger", "self_compassion_break"),
        ("fear", "breathwork"),
        ("neutral", "gratitude_practice"),
    ],
)
def test_first_recommendation_per_mood(mood, module):
    rec = recommend(mood, 0.9, False, [])
    assert rec.module.id == module
    assert rec.level == "intro"
    assert rec.reason == "mood_match"


def test_every_mood_has_at_least_two_modules():
    for mood in ("joy", "sadness", "anger", "fear", "neutral"):
        assert len([m for m in CATALOG if mood in m.moods]) >= 2, mood


def test_does_not_repeat_last_module():
    assert recommend("fear", 0.9, False, ["breathwork"]).module.id != "breathwork"


def test_rotates_to_least_used_module():
    history = ["breathwork", "grounding_exercises", "breathwork", "grounding_exercises"]
    assert recommend("fear", 0.9, False, history).module.id == "progressive_muscle_relaxation"


@pytest.mark.parametrize("times, level", [(0, "intro"), (2, "intro"), (3, "intermediate"), (7, "intermediate"), (8, "advanced")])
def test_level_for(times, level):
    assert level_for(times) == level


def test_level_increases_with_history():
    history = ["breathwork", "grounding_exercises", "progressive_muscle_relaxation"] * 3
    rec = recommend("fear", 0.9, False, history)
    assert rec.level == "intermediate"


def test_low_confidence_falls_back_to_neutral():
    rec = recommend("anger", 0.2, False, [])
    assert rec.reason == "low_confidence"
    assert "neutral" in rec.module.moods


def test_crisis_flag_overrides_mood():
    rec = recommend("joy", 0.99, True, [])
    assert rec.module.id == "crisis_support"
    assert rec.reason == "crisis_flag"
    assert rec.alternatives == []


def test_unknown_history_ids_are_ignored():
    assert recommend("sadness", 0.9, False, ["not_a_module"]).module.id == "mood_journaling"


def test_alternatives_are_real_modules():
    rec = recommend("sadness", 0.9, False, [])
    assert rec.alternatives and all(a in MODULES_BY_ID for a in rec.alternatives)
    assert rec.module.id not in rec.alternatives


def test_endpoint_accepts_original_request_shape():
    r = client.post("/recommend", json={"user_id": "abc123", "mood": "sadness"})
    assert r.status_code == 200
    body = r.json()
    assert body["module"] == "mood_journaling"
    assert body["level"] == "intro"
    assert body["minutes"] > 0


def test_endpoint_crisis():
    r = client.post("/recommend", json={"user_id": "abc123", "mood": "sadness", "crisis_flag": True})
    assert r.json()["module"] == "crisis_support"


@pytest.mark.parametrize(
    "payload",
    [
        {"user_id": "abc123", "mood": "bored"},
        {"user_id": "abc123", "mood": "joy", "confidence": 1.5},
        {"user_id": "", "mood": "joy"},
    ],
)
def test_endpoint_validation(payload):
    assert client.post("/recommend", json=payload).status_code == 422
