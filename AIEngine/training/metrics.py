from typing import Dict, Sequence


def classification_report(y_true: Sequence[str], y_pred: Sequence[str], labels: Sequence[str]) -> Dict:
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred differ in length")

    confusion = {t: {p: 0 for p in labels} for t in labels}
    for t, p in zip(y_true, y_pred):
        confusion[t][p] += 1

    per_class = {}
    for label in labels:
        tp = confusion[label][label]
        predicted = sum(confusion[t][label] for t in labels)
        actual = sum(confusion[label].values())
        precision = tp / predicted if predicted else 0.0
        recall = tp / actual if actual else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[label] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": actual,
        }

    correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    return {
        "n": len(y_true),
        "accuracy": round(correct / len(y_true), 4) if y_true else 0.0,
        "macro_f1": round(sum(c["f1"] for c in per_class.values()) / len(labels), 4),
        "per_class": per_class,
        "confusion": confusion,
    }
