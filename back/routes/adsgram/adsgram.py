import random

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query

from back.controllers.user import UserController
from back.models import Users, ActivePrize
from back.models.enums import PrizeType
from back.errors import APIExceptionModel, APIException
from back.views.prize import PrizeOut

router = APIRouter()

@router.get(
    "/spin_roulette",
    response_model=PrizeOut,
    responses={
        400: {"model": APIExceptionModel},
        404: {"model": APIExceptionModel}
    }
)
async def spin_roulette(
    userid: int = Query(..., description="User's Telegram ID (tg_id)")
) -> PrizeOut:
    user = await UserController.get_user_by_tg_id(userid)
    if not user:
        raise APIException(f"User with tg_id {userid} not found", 404)

    current_time = datetime.now(timezone.utc)
    
    if user.roulette_last_spin:
        elapsed_time = (current_time - user.roulette_last_spin).total_seconds()
        if elapsed_time < 86400:
            raise APIException("Next spin available in 24 hours", 400)

    user.roulette_last_spin = current_time
    await user.save()

    prizes = list(PrizeType)
    selected_prize = random.choice(prizes)

    expires_at = current_time + timedelta(days=1)
    await ActivePrize.create(
        user=user,
        prize_type=selected_prize,
        expires_at=expires_at
    )

    return PrizeOut(
        prize_type=selected_prize,
        expires_at=expires_at.isoformat()
    )