from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import DEFAULT_BANK_PATH, create_app
from ollama_client import OllamaError
from prompts import CRISIS_MESSAGE, NO_ANSWER_MESSAGE
from question_bank import Entry, QuestionBank, cosine, load_entries


# Fake embeddings: one dimension per keyword, so similarity is predictable.
KEYWORDS = ("breath", "sleep", "angry", "lonely")


def fake_embed(texts):
    return [[1.0 if k in t.lower() else 0.0 for k in KEYWORDS] + [0.01] for t in texts]


class FakeOllama:
    chat_model = "fake-chat"
    embed_model = "fake-embed"

    def __init__(self, reply="You sound worried. Try the breathing exercise.", fail=False):
        self.reply = reply
        self.fail = fail
        self.messages = []

    def chat(self, messages, max_tokens=200, temperature=0.4):
        if self.fail:
            raise OllamaError("down")
        self.messages.append(messages)
        return self.reply

    def embed(self, texts):
        if self.fail:
            raise OllamaError("down")
        return fake_embed(texts)


ENTRIES = [
    Entry("breath", "How do I do breathwork?", "Breathe in for four, out for six.", ("exercise",), "reviewed"),
    Entry("sleep", "How can I sleep better?", "Keep a regular sleep schedule.", ("sleep",), "reviewed"),
]


@pytest.fixture()
def ollama():
    return FakeOllama()


@pytest.fixture()
def client(ollama):
    bank = QuestionBank(list(ENTRIES), ollama.embed)
    with TestClient(create_app(ollama=ollama, bank=bank)) as c:
        yield c


def test_reply_uses_model_and_includes_context(client, ollama):
    r = client.post(
        "/reply",
        json={"text": "exam tomorrow", "emotion": "fear", "module_title": "Breathwork", "module_description": "Slow breathing"},
    )
    assert r.status_code == 200
    assert r.json() == {"reply": ollama.reply, "model": "fake-chat"}
    user_message = ollama.messages[0][-1]["content"]
    assert "exam tomorrow" in user_message and "Breathwork" in user_message and "fear" in user_message


def test_reply_crisis_is_fixed_text(client, ollama):
    r = client.post(
        "/reply",
        json={"text": "...", "emotion": "sadness", "crisis_flag": True, "module_title": "Get support now"},
    )
    assert r.json() == {"reply": CRISIS_MESSAGE, "model": "none"}
    assert ollama.messages == []


def test_reply_503_when_ollama_down():
    bad = FakeOllama(fail=True)
    with TestClient(create_app(ollama=bad, bank=QuestionBank([], bad.embed))) as c:
        r = c.post("/reply", json={"text": "hi", "emotion": "joy", "module_title": "Savoring"})
    assert r.status_code == 503


def test_ask_retrieves_and_grounds_answer(client, ollama):
    r = client.post("/ask", json={"question": "Any breath tips?"})
    assert r.status_code == 200
    body = r.json()
    assert [s["id"] for s in body["sources"]] == ["breath"]
    assert body["model"] == "fake-chat"
    prompt = ollama.messages[0][-1]["content"]
    assert "[breath]" in prompt and "[sleep]" not in prompt


def test_ask_without_match_does_not_call_model(client, ollama):
    r = client.post("/ask", json={"question": "What is the capital of France?"})
    assert r.json() == {"answer": NO_ANSWER_MESSAGE, "sources": [], "model": "none"}
    assert ollama.messages == []


def test_ask_crisis_skips_retrieval(client, ollama):
    r = client.post("/ask", json={"question": "breath", "crisis_flag": True})
    assert r.json()["answer"] == CRISIS_MESSAGE
    assert ollama.messages == []


def test_health(client):
    body = client.get("/health").json()
    assert body["entries"] == 2
    assert body["chat_model"] == "fake-chat"


def test_cosine():
    assert cosine([1, 0], [1, 0]) == 1.0
    assert cosine([1, 0], [0, 1]) == 0.0
    assert cosine([0, 0], [1, 1]) == 0.0


def test_search_embeds_documents_once():
    calls = []

    def counting_embed(texts):
        calls.append(len(texts))
        return fake_embed(texts)

    bank = QuestionBank(list(ENTRIES), counting_embed)
    bank.search("breath", 3, 0.5)
    bank.search("sleep", 3, 0.5)
    assert calls == [2, 1, 1]


def test_load_entries_filters_drafts(tmp_path: Path):
    path = tmp_path / "bank.yaml"
    path.write_text(
        "- {id: a, question: Q1, answer: A1, status: reviewed}\n- {id: b, question: Q2, answer: A2, status: draft}\n"
    )
    assert [e.id for e in load_entries(path, include_drafts=False)] == ["a"]
    assert [e.id for e in load_entries(path, include_drafts=True)] == ["a", "b"]


@pytest.mark.parametrize(
    "content, error",
    [
        ("- {id: a, question: Q, answer: A, status: approved}\n", "status"),
        ("- {id: a, question: Q, answer: A}\n- {id: a, question: Q, answer: A}\n", "duplicate"),
    ],
)
def test_load_entries_validates(tmp_path: Path, content, error):
    path = tmp_path / "bank.yaml"
    path.write_text(content)
    with pytest.raises(ValueError, match=error):
        load_entries(path, include_drafts=True)


def test_shipped_bank_is_valid_and_unreviewed():
    entries = load_entries(DEFAULT_BANK_PATH, include_drafts=True)
    assert len(entries) >= 15
    assert all(e.question and e.answer for e in entries)
    # Nothing ships as reviewed until a person approves it.
    assert load_entries(DEFAULT_BANK_PATH, include_drafts=False) == []


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Call 1-800-273-8255 now", True),
        ("Text 988 or call (555) 123-4567", True),
        ("You can text 988 any time", True),
        ("Visit https://example.org for help", True),
        ("See samaritans.org", True),
        ("Breathe in for 4 counts and out for 6.", False),
        ("Try this for 5-10 minutes.", False),
    ],
)
def test_has_contact_details(text, expected):
    from prompts import has_contact_details

    assert has_contact_details(text) is expected


def test_reply_with_contact_details_falls_back(ollama):
    ollama.reply = "Please call 1-800-273-8255."
    with TestClient(create_app(ollama=ollama, bank=QuestionBank([], ollama.embed))) as c:
        r = c.post("/reply", json={"text": "x", "emotion": "sadness", "module_title": "Mood journaling", "module_description": "Write it down."})
    assert r.json() == {
        "reply": "Thanks for sharing how you're feeling. When you're ready, try Mood journaling: Write it down.",
        "model": "fallback",
    }


def test_ask_with_contact_details_returns_entry_verbatim(ollama):
    ollama.reply = "See www.example.com"
    with TestClient(create_app(ollama=ollama, bank=QuestionBank(list(ENTRIES), ollama.embed))) as c:
        body = c.post("/ask", json={"question": "breath help"}).json()
    assert body["answer"] == ENTRIES[0].answer
    assert body["model"] == "fallback"
    assert [s["id"] for s in body["sources"]] == ["breath"]
