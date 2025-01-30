from datetime import timezone, datetime
from decimal import Decimal
from typing import Any, Dict, List

from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction

from back.controllers.base import BaseUserController, T
from back.errors import APIExceptionModel, APIException
from back.models import UserBalance
from back.models.enums import TransactionCurrencyType

import logging


class BalanceController:
    @staticmethod
    async def get_balance(user_id: int, currency: TransactionCurrencyType) -> Decimal:
        balance = await UserBalance.get_or_none(user_id=user_id, currency=currency)
        return balance.balance if balance else Decimal(0.0)

    @staticmethod
    async def update_balance(user_id: int, currency: TransactionCurrencyType, amount: Decimal):
        balance, _ = await UserBalance.get_or_create(user_id=user_id, currency=currency)
        balance.balance += amount
        if balance.balance < 0:
            raise APIException("Insufficient funds", 400)
        await balance.save()

    @staticmethod
    async def withdraw_balance(user_id: int, currency: TransactionCurrencyType, amount: Decimal):
        await BalanceController.update_balance(user_id, currency, -amount)
