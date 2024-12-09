FROM python:3.11-slim

RUN pip install poetry==1.8.5

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-dev  # Install only production dependencies

COPY ./back ./back
COPY ./bot ./bot

CMD ["poetry", "run", "uvicorn", "back.main:app", "--host", "0.0.0.0", "--port", "8000"]
