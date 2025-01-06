import os
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from dotenv import load_dotenv

from back.routers import metrics

load_dotenv()

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# print("Loaded Environment Variables:")
# print(f"POSTGRES_USER: {os.getenv('POSTGRES_USER')}")
# print(f"POSTGRES_PASSWORD: {os.getenv('POSTGRES_PASSWORD')}")
# print(f"POSTGRES_PORT: {os.getenv('POSTGRES_PORT')}")
# print(f"POSTGRES_HOST: {os.getenv('POSTGRES_HOST')}")
# print(f"POSTGRES_DB: {os.getenv('POSTGRES_DB')}")

DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_NAME = os.getenv("POSTGRES_DB")
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
    generate_schemas=False,
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
