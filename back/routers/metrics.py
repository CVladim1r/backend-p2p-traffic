from fastapi import APIRouter, HTTPException
from back.models.metrics import Metric

router = APIRouter(prefix="/metrics", tags=["Metrics"])

@router.post("/")
async def create_metric(event_type: str, user_id: str = None):
    """
    Создать запись метрики
    """
    metric = await Metric.create(event_type=event_type, user_id=user_id)
    return {"id": metric.id, "event_type": metric.event_type}
