import pytest

from dataset import EMOTIONS, GOEMOTIONS_LABELS, GOEMOTIONS_TO_EMOTION, build_rows, read_jsonl, to_canonical, write_jsonl
from metrics import classification_report


def ids(*names):
    return [GOEMOTIONS_LABELS.index(n) for n in names]


def test_every_goemotions_label_is_mapped():
    assert len(GOEMOTIONS_LABELS) == 28
    assert set(GOEMOTIONS_LABELS) == set(GOEMOTIONS_TO_EMOTION)
    assert set(GOEMOTIONS_TO_EMOTION.values()) == set(EMOTIONS)


@pytest.mark.parametrize(
    "labels, expected",
    [
        (ids("joy"), "joy"),
        (ids("gratitude", "love"), "joy"),
        (ids("nervousness", "fear"), "fear"),
        (ids("disgust"), "anger"),
        (ids("surprise"), "neutral"),
        (ids("joy", "sadness"), None),
        ([], None),
    ],
)
def test_to_canonical(labels, expected):
    assert to_canonical(labels) == expected


def test_build_rows_drops_ambiguous_and_empty():
    records = [
        {"id": "1", "text": "thank you!", "labels": ids("gratitude")},
        {"id": "2", "text": "ugh but yay", "labels": ids("annoyance", "joy")},
        {"id": "3", "text": "  ", "labels": ids("joy")},
        {"id": "4", "text": "so scared", "labels": ids("fear")},
    ]
    rows, stats = build_rows(records, "test")
    assert [r["id"] for r in rows] == ["1", "4"]
    assert rows[0] == {"id": "1", "text": "thank you!", "label": "joy", "source": "test"}
    assert stats["joy"] == 1 and stats["fear"] == 1 and stats["dropped_ambiguous_or_empty"] == 2


def test_jsonl_round_trip(tmp_path):
    rows = [{"text": "a", "label": "joy"}, {"text": "é", "label": "fear"}]
    write_jsonl(rows, tmp_path / "x" / "rows.jsonl")
    assert read_jsonl(tmp_path / "x" / "rows.jsonl") == rows
    assert read_jsonl(tmp_path / "x" / "rows.jsonl", limit=1) == rows[:1]


def test_classification_report():
    y_true = ["joy", "joy", "fear", "neutral"]
    y_pred = ["joy", "fear", "fear", "neutral"]
    r = classification_report(y_true, y_pred, ["joy", "fear", "neutral"])
    assert r["accuracy"] == 0.75
    assert r["per_class"]["joy"] == {"precision": 1.0, "recall": 0.5, "f1": 0.6667, "support": 2}
    assert r["per_class"]["fear"]["precision"] == 0.5
    assert r["macro_f1"] == round((0.6667 + 0.6667 + 1.0) / 3, 4)
    assert r["confusion"]["joy"]["fear"] == 1


def test_classification_report_rejects_mismatch():
    with pytest.raises(ValueError):
        classification_report(["joy"], [], ["joy"])
