from fastapi import APIRouter, Depends
from decimal import Decimal

from back.auth.auth import JWTBearer, get_user
from back.utils.cryptobot import crypto_service
from back.controllers.balance import BalanceController
from back.models import Users
from back.models.enums import TransactionCurrencyType
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
    user_id: int = Depends(JWTBearer())
) -> UserBalanceOut:
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