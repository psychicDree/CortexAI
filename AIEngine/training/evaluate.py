"""Evaluate an emotion model on an exported split, exactly as the service runs it.

Usage: python evaluate.py --data data/test.jsonl --model SamLowe/roberta-base-go_emotions
       python evaluate.py --data data/test.jsonl --model output/emotion-5class
"""
import argparse
import json
import time
from pathlib import Path

from dataset import EMOTIONS, read_jsonl
from metrics import classification_report


def main() -> None:
    from classifier import DEFAULT_MODEL, DEFAULT_REVISION, LexiconClassifier, TransformerClassifier

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Hub id, local directory, or 'lexicon'")
    parser.add_argument("--revision", default=DEFAULT_REVISION, help="Ignored for local directories")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--report", type=Path, default=None, help="Write the report as JSON")
    args = parser.parse_args()

    rows = read_jsonl(args.data, args.limit)
    if args.model == "lexicon":
        clf = LexiconClassifier()
    else:
        clf = TransformerClassifier.load(args.model, args.revision)

    start = time.time()
    y_pred = [clf.predict(r["text"]).emotion for r in rows]
    elapsed = time.time() - start

    report = classification_report([r["label"] for r in rows], y_pred, EMOTIONS)
    report.update({"model": args.model, "data": str(args.data), "seconds": round(elapsed, 1)})

    print(f"{args.model}: n={report['n']} accuracy={report['accuracy']} macro_f1={report['macro_f1']}")
    for label, m in report["per_class"].items():
        print(f"  {label:8} p={m['precision']:.3f} r={m['recall']:.3f} f1={m['f1']:.3f} n={m['support']}")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
