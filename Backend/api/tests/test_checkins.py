import pytest
from fastapi.testclient import TestClient

from conftest import _register_and_login


class FakeAIEngine:
    def __init__(self, emotion="fear", confidence=0.8, crisis_flag=False, fail=False, companion_fail=False):
        self.analysis = {"emotion": emotion, "confidence": confidence, "crisis_flag": crisis_flag}
        self.fail = fail
        self.companion_fail = companion_fail
        self.texts = []
        self.recommend_calls = []
        self.reply_calls = []
        self.ask_calls = []

    def analyze(self, text):
        from app.aiengine import AIEngineError

        if self.fail:
            raise AIEngineError("down")
        self.texts.append(text)
        return dict(self.analysis)

    def recommend(self, **kwargs):
        self.recommend_calls.append(kwargs)
        module = "crisis_support" if kwargs["crisis_flag"] else f"module_{len(self.recommend_calls)}"
        return {
            "module": module,
            "level": "intro",
            "title": "Title",
            "description": "Description",
            "minutes": 5,
            "alternatives": ["other"],
        }

    def reply(self, **kwargs):
        from app.aiengine import AIEngineError

        if self.companion_fail:
            raise AIEngineError("companion down")
        self.reply_calls.append(kwargs)
        return {"reply": "That sounds hard.", "model": "fake"}

    def ask(self, question, crisis_flag):
        from app.aiengine import AIEngineError

        if self.companion_fail:
            raise AIEngineError("companion down")
        self.ask_calls.append((question, crisis_flag))
        return {"answer": "Breathe slowly.", "sources": [{"id": "breath", "question": "Q", "score": 0.8}], "model": "fake"}


@pytest.fixture()
def use_engine(client: TestClient):
    from app.aiengine import get_aiengine

    def install(engine):
        client.app.dependency_overrides[get_aiengine] = lambda: engine
        return engine

    yield install
    client.app.dependency_overrides.clear()


def test_checkin_requires_auth(client: TestClient):
    assert client.post("/checkins/", json={"text": "hi"}).status_code == 401


def test_checkin_runs_pipeline_and_stores_result(client: TestClient, use_engine):
    headers = _register_and_login(client, "checkin1@example.com", "secret123")
    engine = use_engine(FakeAIEngine(emotion="fear", confidence=0.8))

    r = client.post("/checkins/", json={"text": "I am worried about tomorrow"}, headers=headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["emotion"] == "fear"
    assert body["confidence"] == 0.8
    assert body["module"] == "module_1"
    assert body["minutes"] == 5
    assert body["session_id"] is None
    assert "text" not in body

    assert engine.texts == ["I am worried about tomorrow"]
    assert engine.recommend_calls[0]["mood"] == "fear"
    assert engine.recommend_calls[0]["history"] == []

    listed = client.get("/checkins/", headers=headers).json()
    assert [c["id"] for c in listed] == [body["id"]]


def test_history_is_oldest_first_and_per_user(client: TestClient, use_engine):
    headers = _register_and_login(client, "checkin2@example.com", "secret123")
    other = _register_and_login(client, "checkin3@example.com", "secret123")
    engine = use_engine(FakeAIEngine())

    client.post("/checkins/", json={"text": "a"}, headers=other)
    client.post("/checkins/", json={"text": "b"}, headers=headers)
    client.post("/checkins/", json={"text": "c"}, headers=headers)
    client.post("/checkins/", json={"text": "d"}, headers=headers)

    assert engine.recommend_calls[-1]["history"] == ["module_2", "module_3"]
    assert len(client.get("/checkins/", headers=headers).json()) == 3


def test_checkin_sets_session_mood(client: TestClient, use_engine):
    headers = _register_and_login(client, "checkin4@example.com", "secret123")
    use_engine(FakeAIEngine(emotion="sadness", confidence=0.7))
    session = client.post("/sessions/", json={"duration_seconds": 60}, headers=headers).json()

    r = client.post("/checkins/", json={"text": "feeling low", "session_id": session["id"]}, headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["session_id"] == session["id"]

    sessions = client.get("/sessions/", headers=headers).json()
    assert next(s for s in sessions if s["id"] == session["id"])["mood"] == "sadness"


def test_checkin_rejects_other_users_session(client: TestClient, use_engine):
    owner = _register_and_login(client, "checkin5@example.com", "secret123")
    intruder = _register_and_login(client, "checkin6@example.com", "secret123")
    use_engine(FakeAIEngine())
    session = client.post("/sessions/", json={}, headers=owner).json()

    r = client.post("/checkins/", json={"text": "x", "session_id": session["id"]}, headers=intruder)
    assert r.status_code == 404


def test_checkin_passes_crisis_flag(client: TestClient, use_engine):
    headers = _register_and_login(client, "checkin7@example.com", "secret123")
    engine = use_engine(FakeAIEngine(emotion="sadness", crisis_flag=True))

    body = client.post("/checkins/", json={"text": "..."}, headers=headers).json()
    assert body["crisis_flag"] is True
    assert body["module"] == "crisis_support"
    assert engine.recommend_calls[0]["crisis_flag"] is True


def test_crisis_checkin_does_not_record_model_label(client: TestClient, use_engine):
    # The real model labelled "I want to end my life" as joy; that must not reach mood history.
    headers = _register_and_login(client, "checkin10@example.com", "secret123")
    use_engine(FakeAIEngine(emotion="joy", confidence=0.58, crisis_flag=True))
    session = client.post("/sessions/", json={"mood": "neutral"}, headers=headers).json()

    body = client.post("/checkins/", json={"text": "...", "session_id": session["id"]}, headers=headers).json()
    assert body["emotion"] == "crisis"
    assert body["confidence"] == 0.0

    stored = client.get("/checkins/", headers=headers).json()[0]
    assert (stored["emotion"], stored["confidence"], stored["crisis_flag"]) == ("crisis", 0.0, True)
    sessions = client.get("/sessions/", headers=headers).json()
    assert next(s for s in sessions if s["id"] == session["id"])["mood"] == "crisis"


def test_checkin_returns_503_when_engine_down(client: TestClient, use_engine):
    headers = _register_and_login(client, "checkin8@example.com", "secret123")
    use_engine(FakeAIEngine(fail=True))

    r = client.post("/checkins/", json={"text": "hello"}, headers=headers)
    assert r.status_code == 503
    assert client.get("/checkins/", headers=headers).json() == []


@pytest.mark.parametrize("text", ["", "x" * 5001])
def test_checkin_validates_text(client: TestClient, use_engine, text):
    headers = _register_and_login(client, "checkin9@example.com", "secret123")
    use_engine(FakeAIEngine())
    assert client.post("/checkins/", json={"text": text}, headers=headers).status_code == 422


def test_checkin_includes_companion_reply(client: TestClient, use_engine):
    headers = _register_and_login(client, "reply1@example.com", "secret123")
    engine = use_engine(FakeAIEngine(emotion="fear"))

    body = client.post("/checkins/", json={"text": "nervous"}, headers=headers).json()
    assert body["reply"] == "That sounds hard."
    assert engine.reply_calls[0]["text"] == "nervous"
    assert engine.reply_calls[0]["module_title"] == "Title"


def test_checkin_succeeds_when_companion_down(client: TestClient, use_engine):
    headers = _register_and_login(client, "reply2@example.com", "secret123")
    use_engine(FakeAIEngine(companion_fail=True))

    r = client.post("/checkins/", json={"text": "nervous"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["reply"] is None
    assert len(client.get("/checkins/", headers=headers).json()) == 1


def test_ask_requires_auth(client: TestClient):
    assert client.post("/ask/", json={"question": "hi"}).status_code == 401


def test_ask_screens_then_answers(client: TestClient, use_engine):
    headers = _register_and_login(client, "ask1@example.com", "secret123")
    engine = use_engine(FakeAIEngine(crisis_flag=False))

    r = client.post("/ask/", json={"question": "How do I calm down?"}, headers=headers)
    assert r.status_code == 200, r.text
    assert r.json() == {
        "answer": "Breathe slowly.",
        "sources": [{"id": "breath", "question": "Q", "score": 0.8}],
        "crisis_flag": False,
    }
    assert engine.texts == ["How do I calm down?"]
    assert engine.ask_calls == [("How do I calm down?", False)]


def test_ask_passes_crisis_flag(client: TestClient, use_engine):
    headers = _register_and_login(client, "ask2@example.com", "secret123")
    engine = use_engine(FakeAIEngine(crisis_flag=True))

    assert client.post("/ask/", json={"question": "..."}, headers=headers).json()["crisis_flag"] is True
    assert engine.ask_calls == [("...", True)]


def test_ask_503_when_companion_down(client: TestClient, use_engine):
    headers = _register_and_login(client, "ask3@example.com", "secret123")
    use_engine(FakeAIEngine(companion_fail=True))
    assert client.post("/ask/", json={"question": "hi"}, headers=headers).status_code == 503
