FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false

RUN poetry install --only main --no-interaction --no-root

COPY petri/ ./petri/

CMD ["uvicorn", "petri.main:app", "--host", "0.0.0.0", "--port", "8000"]
