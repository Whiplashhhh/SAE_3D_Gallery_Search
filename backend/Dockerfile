FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
COPY src ./src
RUN uv sync --locked --no-dev

COPY main.py ./
COPY scripts ./scripts
COPY seed ./seed

RUN mkdir -p /app/data/models /app/data/vector_store

EXPOSE 8000

CMD ["sh", "-c", "uv run --no-sync python -m scripts.preparer_donnees_demo && uv run --no-sync uvicorn main:app --host 0.0.0.0 --port 8000"]
