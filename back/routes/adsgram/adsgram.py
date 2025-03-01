import random

from decimal import Decimal
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Query

from back.controllers.user import UserController
from back.controllers.balance import BalanceController
from back.models import ActivePrize
from back.models.enums import PrizeType, TransactionCurrencyType
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

    expires_at = current_time + timedelta(days=3)

    if selected_prize == PrizeType.DEPOSIT_03:
        try:
            await BalanceController.update_balance(
                user_id=user.tg_id,
                currency=TransactionCurrencyType.USD,
                amount=Decimal('0.3')
            )
            expires_at = current_time
        except Exception as e:
            raise APIException(f"Failed to apply deposit: {str(e)}", 500)
    else:
        await ActivePrize.create(
            user=user,
            prize_type=selected_prize,
            expires_at=expires_at
        )

    return PrizeOut(
        prize_type=selected_prize,
        expires_at=expires_at.isoformat()
    )