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


    async def get_all_checks(self, status: str = None):
        all_checks = []
        offset = 0
        count = 1000  # API limit
        while True:
            current_checks = await self.crypto.get_checks(
                status=status, 
                offset=offset, 
                count=count
            )
            if not current_checks:
                break
            all_checks.extend(current_checks)
            if len(current_checks) < count:
                break
            offset += count
        return all_checks

    async def delete_check(self, check_id: int):
        return await self.crypto.delete_check(check_id=check_id)

    async def delete_all_checks(self):
        checks = await self.get_all_checks()
        for check in checks:
            await self.delete_check(check.check_id)
        return True

crypto_service = CryptoPayService()