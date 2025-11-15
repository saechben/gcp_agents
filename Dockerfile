FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=0

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-ansi --no-root

COPY . .

EXPOSE 8080

CMD ["uvicorn", "followup.api.main:app", "--host=0.0.0.0", "--port=8080"]
