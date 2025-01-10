from fastapi import APIRouter, Depends
from back.models.metrics import Metric
from back.auth.auth import JWTBearer

router = APIRouter(dependencies=[Depends(JWTBearer())])

@router.post("/create_metric")
async def create_metric(event_type: str, user_id: str = None):
    metric = await Metric.create(event_type=event_type, user_id=user_id)
    return {"id": metric.id, "event_type": metric.event_type}
