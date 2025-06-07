FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev git && \
    pip install poetry && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-root --only main
COPY . /app

CMD ["python", "-m", "src.main"]
