from fastapi import APIRouter, Depends, Query
from decimal import Decimal
from typing import Optional
from datetime import datetime, timezone

from back.auth.auth import JWTBearer, get_user
from back.utils.cryptobot import crypto_service
from back.controllers.balance import BalanceController
from back.models import Users, ActivePrize
from back.models.enums import TransactionCurrencyType, PrizeType
from back.errors import APIException, APIExceptionModel
from back.views.balance import UserBalanceOut
from back.views.auth.user import AuthUserOut
from back.config import SECRET_KEY_DEALS


router = APIRouter(dependencies=[Depends(JWTBearer())])

@router.post(
    "/deposit",
    response_model=UserBalanceOut,   
    responses={400: {"model": APIExceptionModel}}, 
)
async def create_deposit(
    currency: TransactionCurrencyType,
    amount: float,
    user_id: int = Depends(JWTBearer()),
    use_deposit_bonus: Optional[bool] = Query(False, description="Использовать бонус DEPOSIT_03"),
) -> UserBalanceOut:
    if use_deposit_bonus:
        current_time = datetime.now(timezone.utc)
        bonus = await ActivePrize.get_or_none(
            user__tg_id=user_id,
            prize_type=PrizeType.DEPOSIT_03,
            expires_at__gt=current_time
        )
        if bonus:
            amount_bonus=Decimal("0.3")
            await BalanceController.update_balance(
                user_id=user_id,
                currency=TransactionCurrencyType.USDT,
                amount=amount_bonus
            )
            await bonus.delete()
        else:
            raise APIException("Бонус для депозита не найден или просрочен", 400)
        
    deposit_url = await BalanceController.create_deposit(user_id, Decimal(amount), currency)
    return {"balance": str(deposit_url)}

@router.post(
    "/withdraw",
    response_model=UserBalanceOut,   
    responses={400: {"model": APIExceptionModel}}, 
    )
async def withdraw_funds(
    amount: float,
    currency: TransactionCurrencyType,
    user_in: AuthUserOut = Depends(get_user),
) -> UserBalanceOut:
    user = await Users.get(tg_id=user_in.tg_id)
    if not user:
        raise APIException(detail="User not found", status_code=404)
    check_url = await BalanceController.process_withdrawal(user, Decimal(amount), currency)
    return {"balance": str(check_url)}

@router.get(
    "/checks/get_all_checks",
    responses={400: {"model": APIExceptionModel}}, 
    )
async def get_all_checks(
    key: str
):
    if SECRET_KEY_DEALS == key:
        all_checks = await crypto_service.get_all_checks(status="active")
        return all_checks
    return "Permission denied"

@router.delete(
    "/checks/delete_all_checks",
    responses={400: {"model": APIExceptionModel}}, 
    )
async def delete_all_checks(
    key: str
):
    if SECRET_KEY_DEALS == key:
        await crypto_service.delete_all_checks()
        return "Done"
    return "Permission denied"