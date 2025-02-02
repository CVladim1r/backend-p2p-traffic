from decimal import Decimal
from pydantic import BaseModel

from back.models.enums import TransactionCurrencyType


class BalanceDepositIn(BaseModel):
    currency: TransactionCurrencyType
    amount: Decimal

class BalanceWithdrawIn(BaseModel):
    currency: TransactionCurrencyType
    amount: Decimal

class UserBalanceOut(BaseModel):
    # currency: TransactionCurrencyType
    balance: str