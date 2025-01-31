import logging

from decimal import Decimal
from uuid import UUID

from back.config import IS_TESTNET
from back.errors import APIException
from back.models.transactions import Transactions
from back.models.users import UserBalance
from back.utils.cryptobot import crypto_service
from back.models.enums import TransactionType, TransactionStatus, TransactionCurrencyType
from back.models.users import Users
from back.controllers.user import UserController


class BalanceController:
    @staticmethod
    async def _create_transaction(
        user_id: int,
        amount: Decimal,
        currency: TransactionCurrencyType,
        transaction_type: TransactionType,
        cryptobot_data: dict = None
    ) -> Transactions:
        return await Transactions.create(
            user_id=user_id,
            amount=amount,
            type=currency,
            status=TransactionStatus.PENDING,
            transaction_type=transaction_type,
            **(cryptobot_data or {})
        )

    @staticmethod
    async def create_deposit(user_id: int, amount: Decimal):
        currency = TransactionCurrencyType.TON # TransactionCurrencyType.JET if IS_TESTNET else 
        
        invoice = await crypto_service.create_invoice(
            user_id=user_id,
            amount=float(amount),
            asset=currency.value,
        )
        
        return invoice.bot_invoice_url

    @staticmethod
    async def process_withdrawal(user_uuid: UUID, amount: Decimal):
        user = await Users.get(uuid=user_uuid)
        if not user or not user.tg_id:
            raise APIException(status_code=404, error="User not found")
        
        min_withdrawal = Decimal("3.0")  # CryptoPay minimum
        commission_rate = Decimal("0.02")
        
        min_required = (min_withdrawal / (1 - commission_rate)).quantize(Decimal('0.0001'))
        if amount < min_required:
            raise APIException(
                status_code=400,
                error=f"Minimum withdrawal amount is {min_required} TON (3 TON after 2% fee)"
            )
        
        commission = (amount * commission_rate).quantize(Decimal('0.0001'))
        withdraw_amount = (amount - commission).quantize(Decimal('0.0001'))

        currency = TransactionCurrencyType.TON
        balance = await UserBalance.get_or_none(user=user, currency=currency)
        if not balance or balance.balance < amount:
            raise APIException(status_code=402, error="Insufficient funds")


        check = await crypto_service.create_withdrawal(
            user_id=user.tg_id,
            amount=float(withdraw_amount),
            asset=currency.value
        )
        
        await BalanceController.update_balance(user.uuid, currency, -amount)
        
        await BalanceController._create_transaction(
            user_id=user.uuid,
            amount=withdraw_amount,
            currency=currency,
            transaction_type=TransactionType.WITHDRAWAL,
            cryptobot_data={"cryptobot_check_id": check.check_id}
        )
        
        await BalanceController._create_transaction(
            user_id=user.uuid,
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
        logging.info(F"user: {user}")
        balance, _ = await UserBalance.get_or_create(
            user=user,
            currency=currency,
            defaults={"balance": Decimal("0.0")}
        )
        
        if balance.balance + amount < 0:
            raise APIException(status_code=400, detail="Insufficient funds")
        
        balance.balance += amount
        await balance.save()
