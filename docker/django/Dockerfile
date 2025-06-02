FROM python:3.12-slim

ENV POETRY_VIRTUALENVS_CREATE=false \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY ../../pyproject.toml poetry.lock* ./
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry install --no-root --no-interaction --no-ansi

COPY ../.. .

RUN mkdir -p /app/static /app/media && \
    chown -R 1000:1000 /app/static /app/media && \
    chmod -R 755 /app/static /app/media

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]