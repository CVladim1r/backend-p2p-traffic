from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from datetime import datetime, timedelta, timezone

from back.views.auth import AuthUserOut
from back.auth.auth import get_user
from back.models import ActivePrize
from back.models.enums import PrizeType
from back.views.prize import PrizeOutAddUUID


router = APIRouter()

@router.get(
    "/active_bonuses", 
    response_model=List[PrizeOutAddUUID]
)
async def get_active_bonuses(
    user_in: AuthUserOut = Depends(get_user),
    prize_type: Optional[PrizeType] = Query(None, description="Фильтр по типу бонуса")
):
    current_time = datetime.now(timezone.utc)
    
    await ActivePrize.filter(expires_at__lte=current_time).delete()
    
    query = ActivePrize.filter(user__tg_id=user_in.tg_id, expires_at__gt=current_time)
    if prize_type:
        query = query.filter(prize_type=prize_type)
    active_prizes = await query.all()
    
    return [
        PrizeOutAddUUID(
            prize_uuid=prize.uuid,
            prize_type=prize.prize_type,
            expires_at=prize.expires_at.isoformat()
        ) for prize in active_prizes
    ]
