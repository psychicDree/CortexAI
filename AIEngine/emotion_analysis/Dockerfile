FROM python:3.11-slim

ARG EMOTION_MODEL=SamLowe/roberta-base-go_emotions
ARG EMOTION_MODEL_REVISION=d75048347613a25d77de8cf6412eaae9fa7b26be

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/app/.hf \
    EMOTION_MODEL=${EMOTION_MODEL} \
    EMOTION_MODEL_REVISION=${EMOTION_MODEL_REVISION}

WORKDIR /app

COPY requirements.txt requirements-ml.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements-ml.txt

# Bake the model into the image so the container needs no network at runtime.
RUN python -c "from huggingface_hub import snapshot_download as d; d('${EMOTION_MODEL}', revision='${EMOTION_MODEL_REVISION}', allow_patterns=['*.json', '*.txt', 'model.safetensors'])"
ENV HF_HUB_OFFLINE=1

COPY main.py classifier.py safety.py ./

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
