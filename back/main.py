from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from back.routers import metrics

app = FastAPI(title="Metrics Backend")

app.include_router(metrics.router)

register_tortoise(
    app,
    db_url="postgres://postgres:q1q1q1q1@db/metrics_db",
    modules={"models": ["back.models.metrics"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
