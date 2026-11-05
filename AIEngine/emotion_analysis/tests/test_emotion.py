import os

import pytest
from fastapi.testclient import TestClient

from classifier import (
    DEFAULT_MODEL,
    DEFAULT_REVISION,
    LexiconClassifier,
    TransformerClassifier,
    build_classifier,
)
from main import create_app
from safety import detect_crisis_language


def fake_pipe(labels):
    def pipe(texts):
        return [[{"label": label, "score": score} for label, score in labels.items()] for _ in texts]

    return pipe


def test_transformer_maps_goemotions_to_canonical_labels():
    clf = TransformerClassifier(
        fake_pipe({"nervousness": 0.7, "fear": 0.4, "joy": 0.1, "neutral": 0.05}), "fake"
    )
    p = clf.predict("I keep worrying about tomorrow")
    assert p.emotion == "fear"
    assert p.confidence == 0.7
    assert p.scores == {"joy": 0.1, "sadness": 0.0, "anger": 0.0, "fear": 0.7, "neutral": 0.05}
    assert p.model == "fake"


def test_transformer_ignores_unknown_labels():
    p = TransformerClassifier(fake_pipe({"mystery": 0.9, "grief": 0.3}), "fake").predict("x")
    assert p.emotion == "sadness"


@pytest.mark.parametrize(
    "text, emotion",
    [
        ("I feel great and grateful today", "joy"),
        ("so lonely and down lately", "sadness"),
        ("I'm furious with my boss", "anger"),
        ("anxious and worried about exams", "fear"),
        ("I am not happy", "neutral"),
        ("I don't feel sad at all", "neutral"),
        ("Went to the shops", "neutral"),
    ],
)
def test_lexicon(text, emotion):
    assert LexiconClassifier().predict(text).emotion == emotion


def test_lexicon_matches_whole_words_only():
    # "down" must not match inside "download".
    assert LexiconClassifier().predict("download finished").emotion == "neutral"


def test_build_classifier_falls_back_to_lexicon_when_model_fails(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("no model")

    monkeypatch.setattr(TransformerClassifier, "load", classmethod(boom))
    assert build_classifier("transformer", "x", "y").name == "lexicon"
    assert build_classifier("lexicon", "x", "y").name == "lexicon"


@pytest.mark.parametrize(
    "text",
    ["I want to die", "thinking about suicide", "I might hurt myself", "everyone is better off dead without me"],
)
def test_crisis_language_detected(text):
    assert detect_crisis_language(text)


@pytest.mark.parametrize("text", ["this homework is killing me", "I died laughing", "a hard day"])
def test_crisis_language_not_detected(text):
    assert not detect_crisis_language(text)


@pytest.fixture()
def client():
    with TestClient(create_app(classifier=LexiconClassifier())) as c:
        yield c


def test_analyze_endpoint(client):
    r = client.post("/analyze", json={"text": "I feel anxious and worried"})
    assert r.status_code == 200
    body = r.json()
    assert body["emotion"] == "fear"
    assert body["crisis_flag"] is False
    assert body["model"] == "lexicon"
    assert set(body["scores"]) == {"joy", "sadness", "anger", "fear", "neutral"}


def test_analyze_sets_crisis_flag(client):
    assert client.post("/analyze", json={"text": "I want to end my life"}).json()["crisis_flag"] is True


@pytest.mark.parametrize("text", ["", "x" * 5001])
def test_analyze_rejects_bad_length(client, text):
    assert client.post("/analyze", json={"text": text}).status_code == 422


def test_health_reports_model(client):
    assert client.get("/health").json() == {"status": "ok", "model": "lexicon"}


@pytest.mark.skipif(not os.getenv("RUN_MODEL_TESTS"), reason="set RUN_MODEL_TESTS=1 to download and run the model")
@pytest.mark.parametrize(
    "text, emotion",
    [
        ("Thank you so much, this made my whole week!", "joy"),
        ("I miss her so much, everything feels empty", "sadness"),
        ("I'm so sick of people ignoring me, it's infuriating", "anger"),
        ("I'm terrified about the test results tomorrow", "fear"),
        ("I had pasta for lunch", "neutral"),
    ],
)
def test_real_model(text, emotion):
    clf = TransformerClassifier.load(DEFAULT_MODEL, DEFAULT_REVISION)
    assert clf.predict(text).emotion == emotion
