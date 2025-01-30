from decimal import Decimal

from fastapi.exceptions import HTTPException

from back.models.transactions import Transactions
from back.models.users import UserBalance
from back.utils.cryptobot import crypto_service
from back.models.enums import TransactionType, TransactionStatus, TransactionCurrencyType
from back.config import IS_TESTNET

class BalanceController:
    @staticmethod
    async def _create_transaction(
        user_id: int,
        amount: Decimal,
        currency: TransactionCurrencyType,
        transaction_type: TransactionType,
        cryptobot_data: dict = None
    ) -> Transactions:
        transaction = await Transactions.create(
            user_id=user_id,
            amount=amount,
            type=currency,
            status=TransactionStatus.PENDING,
            transaction_type=transaction_type,
            **({} if not cryptobot_data else cryptobot_data)
        )
        return transaction

    @staticmethod
    async def create_deposit(user_id: int, amount: Decimal):
        currency = "JET" if IS_TESTNET else "TON"
        
        invoice = await crypto_service.create_invoice(
            user_id=user_id,
            amount=float(amount),
            asset=currency,
        )
        
        return invoice.bot_invoice_url

    @staticmethod
    async def process_withdrawal(user_id: int, amount: Decimal, currency: TransactionCurrencyType):
        commission = amount * Decimal('0.02')
        withdraw_amount = amount - commission
        
        check = await crypto_service.create_withdrawal(
            user_id=user_id,
            amount=float(withdraw_amount),
            asset=currency.value
        )
        
        await BalanceController.update_balance(user_id, currency, -amount)
        
        await BalanceController._create_transaction(
            user_id=user_id,
            amount=withdraw_amount,
            currency=currency,
            transaction_type=TransactionType.WITHDRAWAL,
            cryptobot_data={
                "cryptobot_check_id": check.check_id
            }
        )
        
        await BalanceController._create_transaction(
            user_id=user_id,
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
        """
        Обновляет баланс пользователя.
        Если баланса нет, создает новую запись.
        """
        balance, created = await UserBalance.get_or_create(
            user_id=user_id,
            currency=currency,
            defaults={"balance": Decimal(0.0)}
        )
        
        if not created and balance.balance + amount < 0:
            raise HTTPException("Insufficient funds", 400)
        
        balance.balance += amount
        await balance.save()