"""Export GoEmotions as a 5-emotion JSONL dataset.

Usage: python export_dataset.py --out data
"""
import argparse
import json
from pathlib import Path

from dataset import (
    EMOTIONS,
    GOEMOTIONS_LICENSE,
    GOEMOTIONS_REPO,
    GOEMOTIONS_REVISION,
    GOEMOTIONS_TO_EMOTION,
    SPLITS,
    build_rows,
    write_jsonl,
)


def load_split(split: str) -> list:
    import pyarrow.parquet as pq
    from huggingface_hub import hf_hub_download

    path = hf_hub_download(
        GOEMOTIONS_REPO,
        f"simplified/{split}-00000-of-00001.parquet",
        repo_type="dataset",
        revision=GOEMOTIONS_REVISION,
    )
    return pq.read_table(path).to_pylist()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("data"))
    args = parser.parse_args()

    card = {
        "source": f"https://huggingface.co/datasets/{GOEMOTIONS_REPO}",
        "config": "simplified",
        "revision": GOEMOTIONS_REVISION,
        "license": GOEMOTIONS_LICENSE,
        "labels": list(EMOTIONS),
        "label_mapping": GOEMOTIONS_TO_EMOTION,
        "note": "Examples whose GoEmotions labels map to more than one emotion are dropped.",
        "splits": {},
    }
    for split in SPLITS:
        rows, stats = build_rows(load_split(split), source=f"goemotions/{split}")
        write_jsonl(rows, args.out / f"{split}.jsonl")
        card["splits"][split] = {"rows": len(rows), **stats}
        print(split, card["splits"][split])

    (args.out / "dataset_card.json").write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
