ARG EMBEDDING_MODEL_NAME=intfloat/multilingual-e5-small

FROM python:3.14-slim AS builder

ARG EMBEDDING_MODEL_NAME
ARG HTTP_PROXY
ARG HTTPS_PROXY

ENV http_proxy=${HTTP_PROXY} \
    https_proxy=${HTTPS_PROXY} \
    HTTP_PROXY=${HTTP_PROXY} \
    HTTPS_PROXY=${HTTPS_PROXY} \
    no_proxy=localhost,127.0.0.1,postgres,redis \
    NO_PROXY=localhost,127.0.0.1,postgres,redis \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    HF_HOME=/opt/huggingface \
    PATH="/opt/venv/bin:$PATH"

ENV EMBEDDING_MODEL_NAME=${EMBEDDING_MODEL_NAME}

WORKDIR /app

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ca-certificates libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.11.17 /uv /uvx /bin/
COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project

RUN python -c "import os; from sentence_transformers import SentenceTransformer; SentenceTransformer(os.environ['EMBEDDING_MODEL_NAME'])"


FROM python:3.14-slim AS runtime

ARG EMBEDDING_MODEL_NAME
ARG HTTP_PROXY
ARG HTTPS_PROXY

ENV http_proxy=${HTTP_PROXY} \
    https_proxy=${HTTPS_PROXY} \
    HTTP_PROXY=${HTTP_PROXY} \
    HTTPS_PROXY=${HTTPS_PROXY} \
    no_proxy=localhost,127.0.0.1,postgres,redis \
    NO_PROXY=localhost,127.0.0.1,postgres,redis \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    EMBEDDING_MODEL_NAME=${EMBEDDING_MODEL_NAME} \
    HF_HOME=/opt/huggingface \
    HF_HUB_OFFLINE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH=/app/src

WORKDIR /app

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ca-certificates libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 app

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /opt/huggingface /opt/huggingface
COPY alembic.ini ./
COPY migrations ./migrations
COPY src ./src
COPY data ./data

USER app

CMD ["uvicorn", "app:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
