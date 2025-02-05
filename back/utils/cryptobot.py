from aiocryptopay import AioCryptoPay, Networks
from aiocryptopay.exceptions import CodeErrorFactory
from back.config import CRYPTOBOT_TOKEN, IS_TESTNET

import logging 
import asyncio


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
        asset: str, # = "TON"
        description: str = "Пополнение баланса аккаунта BBT"
    ):
        description_with_id = f"{description} UserID:{user_id}"

        return await self.crypto.create_invoice(
            asset=asset,
            amount=amount,
            description=description_with_id
        )

    async def create_withdrawal(
            self, 
            user_id: int, 
            amount: float, 
            asset: str, # = "TON"
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

    async def delete_check(self, check_id: int) -> bool:
        try:
            check = await self.crypto.get_checks(check_id=check_id)
            if check.status != "active":
                logging.info(f"Check {check_id} is not active (status: {check.status})")
                return False
                
            result = await self.crypto.delete_check(check_id=check_id)
            logging.info(f"Check {check_id} deleted successfully")
            return bool(result)
        except CodeErrorFactory as e:
            if e.code == 400 and "CHECK_NOT_FOUND" in e.name:
                logging.warning(f"Check {check_id} not found")
                return False
            logging.error(f"Error deleting check {check_id}: {e}")
            logging
        except Exception as e:
            logging.error(f"Unexpected error deleting check {check_id}: {e}")
            raise

    async def delete_all_checks(self) -> bool:
        try:
            checks = await self.crypto.get_checks(status="active")
            
            if not isinstance(checks, list):
                checks = [checks] if checks else []

            await asyncio.gather(*[
                self._delete_single_check(check.check_id)
                for check in checks
            ])
            
            return True
        except Exception as e:
            logging.error(f"Ошибка удаления: {str(e)}")
            raise

    async def _delete_single_check(self, check_id: int):
        try:
            result = await self.crypto.delete_check(check_id=check_id)
            logging.info(f"Чек {check_id} удалён")
            return result
        except CodeErrorFactory as e:
            if "CHECK_NOT_FOUND" in e.name:
                logging.warning(f"Чек {check_id} уже удалён")
                return True
            raise

    # async def _safe_delete(self, check_id: int):
    #     retries = 0
    #     while retries < 3:
    #         try:
    #             return await self.delete_check(check_id)
    #         except CodeErrorFactory as e:
    #             if e.code == 429:
    #                 await asyncio.sleep(2**retries)
    #                 retries += 1
    #                 continue
    #             raise

crypto_service = CryptoPayService()