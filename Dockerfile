FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

# Ensure DNS resolution works
RUN echo "options ndots:0" > /etc/resolvconf/resolv.conf.d/base

# Update and install dependencies with retries
RUN apt-get update -o Acquire::Retries=5 && apt-get install -y --no-install-recommends \
    build-essential \
    netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.8.5

WORKDIR /app

COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false && poetry install --no-root

COPY ./ ./

ENV PYTHONPATH=/api

CMD ["poetry", "run", "uvicorn", "back.main:app", "--host", "0.0.0.0", "--port", "8000"]
