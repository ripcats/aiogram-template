FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

FROM base AS builder
RUN pip install uv
COPY pyproject.toml ./
COPY app ./app
RUN uv venv /opt/venv && uv pip install --python /opt/venv/bin/python ".[dev]"

FROM base AS runtime
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY . .
CMD ["python", "-m", "app.main"]
