from decimal import Decimal
from typing import Any, Dict, List
from uuid import uuid4
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction

from back.controllers.base import BaseUserController, T
from back.controllers.balance import BalanceController
from back.errors import APIExceptionModel, APIException
from back.models import UserBalance
from back.models.enums import TransactionCurrencyType
from back.utils.cryptobot import crypto_service

import logging


class ReferralController:
    @staticmethod
    async def process_referral_bonus(referrer_id: int, amount: Decimal):
        bonus = amount * Decimal('0.05')
        try:
            await crypto_service.crypto.transfer(
                user_id=referrer_id,
                amount=float(bonus),
                asset="TON",
                spend_id=str(uuid4()),
                comment="Реферальный бонус"
            )
            await BalanceController.update_balance(
                user_id=referrer_id,
                currency=TransactionCurrencyType.TON,
                amount=bonus
            )
        except Exception as e:
            logging.error(f"Referral bonus error: {str(e)}")