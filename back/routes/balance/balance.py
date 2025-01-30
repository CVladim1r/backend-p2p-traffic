import logging

from fastapi import APIRouter, Body, Depends
from decimal import Decimal


from back.auth.auth import JWTBearer, get_user
from back.controllers.balance import BalanceController
from back.views.auth.user import AuthUserOut
from back.models import Users
from back.errors import APIException

router = APIRouter(dependencies=[Depends(JWTBearer())])

@router.post("/deposit")
async def create_deposit(
    amount: float,
    user_id: int = Depends(JWTBearer())
):
    deposit_url = await BalanceController.create_deposit(user_id, Decimal(amount))
    return {"url": deposit_url}

@router.post("/withdraw")
async def withdraw_funds(
    amount: float,
    user_in: AuthUserOut = Depends(get_user),
):
    user = await Users.get(tg_id=user_in.tg_id)
    if not user:
        raise APIException(detail="User not found", status_code=404)
    check_url = await BalanceController.process_withdrawal(user.uuid, Decimal(amount))
    return {"check_url": check_url}






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