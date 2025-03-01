import logging

from uuid import UUID
from decimal import Decimal
from tortoise.transactions import in_transaction
from aiocryptopay.exceptions import CodeErrorFactory

from back.config import IS_TESTNET
from back.errors import APIException
from back.models.transactions import Transactions
from back.models.users import UserBalance
from back.utils.cryptobot import crypto_service
from back.models.enums import TransactionType, TransactionStatus, TransactionCurrencyType
from back.controllers.user import UserController
from back.errors import APIException
from back.config import IS_TESTNET


class BalanceController:
    @staticmethod
    async def _create_transaction(
        user_id: UUID,
        amount: Decimal,
        currency: TransactionCurrencyType,
        transaction_type: TransactionType,
        cryptobot_data: dict = None
    ) -> Transactions:
        user = await  UserController.get_by_tg_id(user_id)

        return await Transactions.create(
            user_id=user,
            amount=amount,
            type=currency,
            status=TransactionStatus.PENDING,
            transaction_type=transaction_type,
            **(cryptobot_data or {})
        )

    @staticmethod
    async def create_deposit(
        user_id: int, 
        amount: Decimal,
        currency: TransactionCurrencyType
    ):        
        invoice = await crypto_service.create_invoice(
            user_id=user_id,
            amount=float(amount),
            asset=currency.value,
        )
        
        return invoice.bot_invoice_url

    @staticmethod
    async def process_withdrawal(
        user, 
        amount: Decimal,
        currency: TransactionCurrencyType
    ):
        if amount <= 0:
            raise APIException(status_code=400, error="Invalid withdrawal amount")
        
        commission = amount * Decimal("0.02")
        withdraw_amount = amount - commission

        balance = await UserBalance.get_or_none(
            user_id=user.uuid, 
            currency=currency
        )
        
        reserved_balance = balance.reserved if balance and balance.reserved is not None else Decimal(0)
        available_balance = balance.balance - reserved_balance if balance else Decimal(0)

        if available_balance < amount:
            raise APIException(
                status_code=402,
                error=f"Insufficient funds in {currency.value} currency"
            )

        try:
            check = await crypto_service.create_withdrawal(
                user_id=user.tg_id,
                amount=withdraw_amount,
                asset=currency.value
            )
        except Exception as e:
            if isinstance(e, CodeErrorFactory) and e.code == 400 and "NOT_ENOUGH_COINS" in str(e):
                raise APIException(
                    status_code=400,
                    error="Not enough coins in the CryptoPay account to process the withdrawal."
                )
            else:
                logging.error(f"CryptoPay API Error: {e}")
                raise APIException(
                    status_code=500,
                    error="An error occurred while processing the withdrawal."
                )

        async with in_transaction():
            await BalanceController.update_balance(
                user_id=user.tg_id,
                currency=currency,
                amount=-amount
            )
            
            await BalanceController._create_transaction(
                user_id=user.tg_id,
                amount=withdraw_amount,
                currency=currency,
                transaction_type=TransactionType.WITHDRAWAL,
                cryptobot_data={"cryptobot_check_id": check.check_id}
            )
            
            await BalanceController._create_transaction(
                user_id=user.tg_id,
                amount=commission,
                currency=currency,
                transaction_type=TransactionType.FEE
            )
        
        return check.bot_check_url

    @staticmethod
    async def update_balance(
        user_id: int,
        currency: TransactionCurrencyType,
        amount: Decimal
    ):
        user = await  UserController.get_by_tg_id(user_id)
        balance, _ = await UserBalance.get_or_create(
            user=user,
            currency=currency,
            defaults={
                "balance": Decimal("0.0"),
                "reserved": Decimal("0.0")
            }
        )

        new_balance = balance.balance + amount
        if new_balance < 0:
            raise APIException(
                status_code=400,
                error=f"Insufficient {currency.value} funds"
            )
            
        balance.balance = new_balance
        await balance.save()
        
    @staticmethod
    async def reserve_funds(user_id: int, currency: TransactionCurrencyType, amount: Decimal):
        balance, _ = await UserBalance.get_or_create(
            user_id=user_id,
            currency=currency,
            defaults={"balance": Decimal("0.0"), "reserved": Decimal("0.0")}
        )
        
        if balance.balance < amount:
            raise APIException(error="Insufficient funds", status_code=400)
            
        balance.balance -= amount
        balance.reserved += amount
        await balance.save()

    @staticmethod
    async def release_reserved(user_id: int, currency: TransactionCurrencyType, amount: Decimal):
        balance = await UserBalance.get_or_none(user_id=user_id, currency=currency)
        if not balance or balance.reserved < amount:
            raise APIException(error="Invalid reservation release", status_code=400)
            
        balance.reserved -= amount
        balance.balance += amount
        await balance.save()