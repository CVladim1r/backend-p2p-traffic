FROM python:3.11-slim

RUN pip install poetry

WORKDIR /app
COPY ./backend ./backend
COPY ./bot ./bot
COPY pyproject.toml poetry.lock ./

RUN poetry install --no-dev

CMD ["poetry", "run", "uvicorn", "back.main:app", "--host", "0.0.0.0", "--port", "8000"]
