import aiohttp
import logging

from fastapi import APIRouter, Body, Depends, HTTPException
from decimal import Decimal
from back.auth.auth import JWTBearer

from back.controllers.balance import BalanceController
from back.views.balance.balance import BalanceDepositIn, BalanceWithdrawIn, UserBalanceOut
from back.views.auth.user import AuthUserOut
from back.auth.auth import get_user

router = APIRouter(dependencies=[Depends(JWTBearer())])



@router.post("/balance/deposit", response_model=UserBalanceOut)
async def deposit_balance(
    deposit_data: BalanceDepositIn = Body(...),
    user_in: AuthUserOut = Depends(get_user),
):
    try:
        return {"invoice_url"}
    except Exception as error:
        logging.error(f"Deposit error: {error}")
        raise HTTPException(f"Deposit failed: {error}", 400)

@router.post("/balance/webhook")
async def cryptobot_webhook(payload: dict = Body(...)):
    try:
        user_id = payload["user_id"]
        currency = payload["currency"]
        amount = Decimal(payload["amount"])
        await BalanceController.update_balance(user_id, currency, amount)
        return {"status": "success"}
    except Exception as error:
        logging.error(f"Webhook processing failed: {error}")
        raise HTTPException(f"Webhook failed: {error}", 400)

@router.post("/balance/withdraw", response_model=UserBalanceOut)
async def withdraw_balance(
    withdraw_data: BalanceWithdrawIn = Body(...),
    user_in: AuthUserOut = Depends(get_user),
):
    try:
        await BalanceController.withdraw_balance(user_in.tg_id, withdraw_data.currency, withdraw_data.amount)
        return {"payout_id"}
    except Exception as error:
        logging.error(f"Withdraw error: {error}")
        raise HTTPException(f"Withdraw failed: {error}", 400)












# @router.post(
#     "/balance/deposit",
#     response_model=UserBalanceOut,
#     responses={400: {"model": APIExceptionModel}},
# )
# async def deposit_balance(
#     deposit_data: BalanceDepositIn = Body(...),
#     user_in: AuthUserOut = Depends(get_user),
# ):
#     try:
#         await BalanceController.update_balance(
#             user_id=user_in.tg_id,
#             currency=deposit_data.currency,
#             amount=deposit_data.amount,
#         )
#         balance = await BalanceController.get_balance(user_in.tg_id, deposit_data.currency)
#         return {"currency": deposit_data.currency, "balance": str(balance)}
#     except Exception as error:
#         raise HTTPException(f"Deposit failed: {error}", 400)


# @router.post(
#     "/balance/withdraw",
#     response_model=UserBalanceOut,
#     responses={400: {"model": APIExceptionModel}},
# )
# async def withdraw_balance(
#     withdraw_data: BalanceWithdrawIn = Body(...),
#     user_in: AuthUserOut = Depends(get_user),
# ):
#     try:
#         await BalanceController.withdraw_balance(
#             user_id=user_in.tg_id,
#             currency=withdraw_data.currency,
#             amount=withdraw_data.amount,
#         )
#         balance = await BalanceController.get_balance(user_in.tg_id, withdraw_data.currency)
#         return {"currency": withdraw_data.currency, "balance": str(balance)}
#     except Exception as error:
#         raise HTTPException(f"Withdraw failed: {error}", 400)