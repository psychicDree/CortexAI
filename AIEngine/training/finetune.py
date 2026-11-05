"""Fine-tune a 5-emotion classifier on the exported dataset.

Starts from the serving model by default and replaces its 28-label head with a
5-label softmax head. Keeps the checkpoint with the best validation macro-F1.

Usage: python finetune.py --data data --out output/emotion-5class
"""
import argparse
import json
import random
import time
from pathlib import Path

from dataset import EMOTIONS, read_jsonl
from metrics import classification_report


def pick_device():
    import torch

    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def batches(rows, size, shuffle, rng):
    order = list(range(len(rows)))
    if shuffle:
        rng.shuffle(order)
    for i in range(0, len(order), size):
        yield [rows[j] for j in order[i:i + size]]


def predict(model, tokenizer, rows, batch_size, max_length, device):
    import torch

    model.eval()
    preds = []
    with torch.no_grad():
        for batch in batches(rows, batch_size, False, None):
            enc = tokenizer([r["text"] for r in batch], truncation=True, max_length=max_length, padding=True, return_tensors="pt")
            logits = model(**{k: v.to(device) for k, v in enc.items()}).logits
            preds.extend(EMOTIONS[i] for i in logits.argmax(dim=-1).tolist())
    return preds


def main() -> None:
    import torch
    from classifier import DEFAULT_MODEL, DEFAULT_REVISION
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data"))
    parser.add_argument("--out", type=Path, default=Path("output/emotion-5class"))
    parser.add_argument("--base-model", default=DEFAULT_MODEL)
    parser.add_argument("--revision", default=DEFAULT_REVISION)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--max-length", type=int, default=64)
    parser.add_argument("--max-train", type=int, default=None, help="Cap training rows for a quick run")
    parser.add_argument("--max-eval", type=int, default=None, help="Cap validation rows")
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument(
        "--freeze-layers",
        type=int,
        default=0,
        help="Freeze embeddings and the lowest N encoder layers to save memory (e.g. 8 of 12 on an 8 GB laptop)",
    )
    args = parser.parse_args()

    rng = random.Random(args.seed)
    torch.manual_seed(args.seed)
    device = pick_device()

    train = read_jsonl(args.data / "train.jsonl")
    rng.shuffle(train)
    train = train[: args.max_train] if args.max_train else train
    validation = read_jsonl(args.data / "validation.jsonl", args.max_eval)

    label2id = {e: i for i, e in enumerate(EMOTIONS)}
    tokenizer = AutoTokenizer.from_pretrained(args.base_model, revision=args.revision)
    model = AutoModelForSequenceClassification.from_pretrained(
        args.base_model,
        revision=args.revision,
        num_labels=len(EMOTIONS),
        id2label={i: e for e, i in label2id.items()},
        label2id=label2id,
        problem_type="single_label_classification",
        ignore_mismatched_sizes=True,
    ).to(device)

    if args.freeze_layers:
        base = model.base_model
        frozen = [base.embeddings, *base.encoder.layer[: args.freeze_layers]]
        for module in frozen:
            for param in module.parameters():
                param.requires_grad = False

    trainable = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable, lr=args.lr, weight_decay=0.01)
    steps = args.epochs * ((len(train) + args.batch_size - 1) // args.batch_size)
    scheduler = get_linear_schedule_with_warmup(optimizer, int(0.06 * steps), steps)

    print(
        f"device={device} train={len(train)} validation={len(validation)} steps={steps} "
        f"trainable_params={sum(p.numel() for p in trainable):,}"
    )
    best, history, start = -1.0, [], time.time()
    for epoch in range(1, args.epochs + 1):
        model.train()
        total, epoch_start = 0.0, time.time()
        for step, batch in enumerate(batches(train, args.batch_size, True, rng), 1):
            enc = tokenizer([r["text"] for r in batch], truncation=True, max_length=args.max_length, padding=True, return_tensors="pt")
            labels = torch.tensor([label2id[r["label"]] for r in batch], device=device)
            loss = model(**{k: v.to(device) for k, v in enc.items()}, labels=labels).loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()
            total += loss.item()
            if step % 50 == 0:
                rate = step / (time.time() - epoch_start)
                print(f"epoch {epoch} step {step} loss {total / step:.4f} {rate:.2f} steps/s")

        preds = predict(model, tokenizer, validation, args.batch_size * 2, args.max_length, device)
        report = classification_report([r["label"] for r in validation], preds, EMOTIONS)
        history.append({"epoch": epoch, "train_loss": round(total / max(step, 1), 4), "val_accuracy": report["accuracy"], "val_macro_f1": report["macro_f1"]})
        print(history[-1])
        if report["macro_f1"] > best:
            best = report["macro_f1"]
            model.save_pretrained(args.out)
            tokenizer.save_pretrained(args.out)

    summary = {
        "base_model": args.base_model,
        "base_revision": args.revision,
        "train_rows": len(train),
        "validation_rows": len(validation),
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "lr": args.lr,
        "max_length": args.max_length,
        "seed": args.seed,
        "freeze_layers": args.freeze_layers,
        "device": str(device),
        "minutes": round((time.time() - start) / 60, 1),
        "best_val_macro_f1": best,
        "history": history,
    }
    (args.out / "training_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"saved {args.out} best_val_macro_f1={best}")


if __name__ == "__main__":
    main()
