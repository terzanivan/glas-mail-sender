FROM python:3.11-slim
RUN pip install poetry
RUN useradd -ms /bin/sh -u 1001 app

WORKDIR /app
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

USER app

COPY --chown=app:app . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
