# Emotion Model Training

Offline scripts to build a training dataset from public data, fine-tune the emotion classifier, and evaluate any model through the same code the emotion service uses.

Exported data (`data/`), weights (`output/`), and reports (`reports/*.json`) are git-ignored. Every result here can be reproduced from pinned dataset and model revisions.

## Dataset

```bash
pip install -r requirements.txt
python export_dataset.py --out data
```

The script downloads [GoEmotions](https://huggingface.co/datasets/google-research-datasets/go_emotions) (Apache 2.0, `simplified` config, pinned revision): English Reddit comments with 28 emotion labels. Each example is mapped to the service's five emotions using the mapping in `emotion_analysis/classifier.py`, so training and serving can't drift apart.

An example is dropped if its labels map to more than one emotion. `data/dataset_card.json` records the source, revision, mapping, and counts.

| Split | Rows | joy | sadness | anger | fear | neutral | Dropped |
| --- | --- | --- | --- | --- | --- | --- | --- |
| train | 39,995 | 15,216 | 2,326 | 4,929 | 541 | 16,983 | 3,415 |
| validation | 4,999 | 1,941 | 266 | 631 | 72 | 2,089 | 427 |
| test | 5,037 | 1,863 | 283 | 672 | 80 | 2,139 | 390 |

Fear is rare (about 1.4%), so macro-F1 is the main metric.

No user data is used. Check-in text is never stored.

## Fine-tune

```bash
python finetune.py --data data --out output/emotion-5class
```

By default the script starts from the serving model and swaps its 28-label head for a 5-label softmax head. It keeps the checkpoint with the best validation macro-F1 and writes `training_summary.json` next to the weights. It uses CUDA or Apple Silicon (MPS) when available.

On an 8 GB machine, use `--freeze-layers 8 --max-length 48` and optionally `--max-train`. A full run with all layers unfrozen ran out of memory and stalled on an 8 GB M1.

## Evaluate

```bash
python evaluate.py --data data/test.jsonl --model lexicon --report reports/test_lexicon.json
python evaluate.py --data data/test.jsonl --report reports/test_baseline.json
python evaluate.py --data data/test.jsonl --model output/emotion-5class --report reports/test_finetuned.json
```

`--model` takes a Hub ID, a local directory, or `lexicon`. Predictions go through `TransformerClassifier`, so scores match what the service would return.

## Results (2026-11-05)

GoEmotions test split, 5,037 rows. "Fine-tuned" = `--epochs 1 --max-train 12000 --batch-size 16 --max-length 48 --freeze-layers 8`. That trains 28.9M of 125M parameters and took 4.2 minutes on an 8 GB M1.

| F1 | Keyword fallback | Current model | Fine-tuned |
| --- | --- | --- | --- |
| joy | 0.432 | 0.829 | 0.832 |
| sadness | 0.193 | 0.656 | 0.639 |
| anger | 0.032 | 0.594 | 0.626 |
| fear | 0.357 | 0.703 | 0.671 |
| neutral | 0.638 | 0.772 | 0.763 |
| **Accuracy** | 0.525 | 0.763 | 0.762 |
| **Macro-F1** | 0.330 | **0.711** | 0.706 |

The fine-tuned model is no better overall: anger improved and fear dropped, and fear has only 80 test examples. This is expected, because the serving model was already trained on GoEmotions. The service keeps the current model.

Fine-tuning should pay off once the app has data of its own, such as consented check-ins or user corrections.

To serve a fine-tuned model anyway, point the emotion service at it:

```bash
EMOTION_MODEL=/path/to/output/emotion-5class uvicorn main:app --port 8001
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The unit tests cover the label mapping, dataset building, and metrics. They need no ML dependencies.
