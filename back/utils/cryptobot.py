from aiocryptopay import AioCryptoPay, Networks
from back.config import CRYPTOBOT_TOKEN, IS_TESTNET

class CryptoPayService:
    def __init__(self):
        self.crypto = AioCryptoPay(
            token=CRYPTOBOT_TOKEN,
            network=Networks.TEST_NET if IS_TESTNET else Networks.MAIN_NET
        )

    async def set_webhook(self, url: str):
        await self.crypto.set_webhook(url=url)

    async def create_invoice(
        self,
        user_id: int,
        amount: float,
        asset: str = "TON", # "JET" if IS_TESTNET else 
        description: str = "Пополнение баланса аккаунта BBT"
    ):
        description_with_id = f"{description} | UserID:{user_id}"
        # if IS_TESTNET and asset != "JET":
        #     raise ValueError("Testnet поддерживает только JET")
        
        return await self.crypto.create_invoice(
            asset=asset,
            amount=amount,
            description=description_with_id
        )

    async def create_withdrawal(
            self, 
            user_id: int, 
            amount: float, 
            asset: str = "TON",
    ):
        return await self.crypto.create_check(
            asset=asset,
            amount=amount,
            pin_to_user_id=user_id,
        )

    async def get_balance(self):
        return await self.crypto.get_balance()

    async def close(self):
        await self.crypto.close()

crypto_service = CryptoPayService()