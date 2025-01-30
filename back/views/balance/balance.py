from decimal import Decimal
from back.models.enums import TransactionCurrencyType
from pydantic import BaseModel

class BalanceDepositIn(BaseModel):
    currency: TransactionCurrencyType
    amount: Decimal


class BalanceWithdrawIn(BaseModel):
    currency: TransactionCurrencyType
    amount: Decimal


class UserBalanceOut(BaseModel):
    currency: TransactionCurrencyType
    balance: str