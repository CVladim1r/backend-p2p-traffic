FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


RUN python -m ensurepip --upgrade && \
    pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install poetry==1.8.5
    
WORKDIR /app

COPY pyproject.toml poetry.lock ./

# RUN poetry install --no-dev  # Install only production dependencies
RUN poetry config virtualenvs.create false && poetry install --no-root

COPY ./ ./
# COPY ./back ./back
# COPY ./bot ./bot

ENV PYTHONPATH=/app


CMD ["python", "-m", "uvicorn", "back.app:app", "--host", "0.0.0.0", "--port", "9100", "--workers", "2", "--limit-max-requests", "10000"]
