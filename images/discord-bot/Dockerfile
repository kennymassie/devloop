# syntax=docker/dockerfile:1
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.18 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock .
RUN UV_HTTP_TIMEOUT=300 uv pip install --system --no-cache .

# Only main.py here — all business logic is in the devloop.messaging package.
COPY main.py ./

EXPOSE 8080

CMD ["python", "main.py"]
