FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update || (echo "nameserver 8.8.8.8" > /etc/resolv.conf && apt-get update)

RUN apt-get install -y --no-install-recommends \
    apt-transport-https \
    ca-certificates \
    build-essential \
    netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry==1.8.5

WORKDIR /app

COPY pyproject.toml poetry.lock ./

# RUN poetry install --no-dev  # Install only production dependencies
RUN poetry config virtualenvs.create false && poetry install --no-root

COPY ./ ./
# COPY ./back ./back
# COPY ./bot ./bot

ENV PYTHONPATH=/api


CMD ["poetry", "run", "uvicorn", "back.main:app", "--host", "0.0.0.0", "--port", "8000"]
