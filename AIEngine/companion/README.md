# Companion Service

FastAPI service that uses a local [Ollama](https://ollama.com) model for two things:

- `POST /reply`: a short supportive reply to a check-in that points to the suggested exercise.
- `POST /ask`: answers questions using only the question bank (RAG).

Nothing leaves the machine running Ollama, and nothing is stored.

## Setup

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
pip install -r requirements.txt
uvicorn main:app --port 8003
```

`llama3.2:3b` is under the Llama 3.2 Community License. `nomic-embed-text` is Apache 2.0. Swap either with the variables below.

| Variable | Default |
| --- | --- |
| `OLLAMA_URL` | `http://localhost:11434` (`http://host.docker.internal:11434` in Docker) |
| `COMPANION_CHAT_MODEL` | `llama3.2:3b` |
| `COMPANION_EMBED_MODEL` | `nomic-embed-text` |
| `OLLAMA_TIMEOUT_SECONDS` | `60` |
| `QUESTION_BANK_PATH` | `question_bank.yaml` |
| `COMPANION_INCLUDE_DRAFTS` | `false`; set to `true` only for local development |
| `COMPANION_TOP_K` | `3` |
| `COMPANION_MIN_SCORE` | `0.58` |

## Question bank

`question_bank.yaml` holds the Q&A entries. Only entries with `status: reviewed` are used. All entries ship as `draft`, so `/ask` returns the "no answer" message until someone reviews them.

To review an entry, check it for accuracy and tone, then set `status: reviewed` and add `reviewed_by` and `reviewed_on`.

The service embeds the entries on the first question and keeps them in memory, which is fine for a few hundred entries. A question with no entry scoring at least `COMPANION_MIN_SCORE` (cosine similarity) gets a fixed "no answer" message and never reaches the model.

On 7 test questions, relevant ones scored 0.60–0.78 and off-topic ones at most 0.52. Re-check the threshold as the bank grows.

## Safety

- If `crisis_flag` is true, both endpoints return a fixed crisis message and skip the model. The backend sets the flag using the emotion service's check.
- The system prompt forbids diagnosis, medication advice, and contact details.
- Any model output that contains a phone number, emergency number, or URL is replaced: replies fall back to a fixed template, and answers fall back to the best-matching entry, verbatim. In testing, the model made up an outdated US hotline number before this filter was added.
- Replies are generated text, not clinically reviewed. Keep them short and treat them as encouragement only.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The tests use a fake Ollama client and don't need Ollama running.
