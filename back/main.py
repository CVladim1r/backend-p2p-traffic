import os
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from dotenv import load_dotenv

from back.routers import metrics

load_dotenv()

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "q1q1q1q1")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_NAME = os.getenv("POSTGRES_DB", "metrics_db")
DB_URL = f"postgres://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

app = FastAPI(
    title="Metrics Backend",
    description="Backend service for metrics tracking.",
    version="1.0.0",
    debug=DEBUG,
)

app.include_router(metrics.router)

register_tortoise(
    app,
    db_url=DB_URL,
    modules={"models": ["back.models", "aerich.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

TORTOISE_ORM = {
    "connections": {"default": DB_URL},
    "apps": {
        "models": {
            "models": ["back.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "use_tz": True,
    "timezone": "UTC",
}

@app.get("/", summary="Root Endpoint", description="Check API health")
async def root():
    return {"message": "Metrics Backend is running"}
