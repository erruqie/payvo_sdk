import aiohttp
import asyncio
import logging
from typing import Optional

# Настройка логирования
logger = logging.getLogger("PayvoSDK")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class Payvo:
    PRODUCTION_URL = "https://api.payvo.ru/public/"

    def __init__(self, merchant_id: str, merchant_secret_key: str):
        self.merchant_id = merchant_id
        self.secret_key = merchant_secret_key
        self.base_url = self.PRODUCTION_URL
        self.headers = {
            "Content-Type": "application/json",
            "merchant-id": self.merchant_id,
            "merchant-secret-key": self.secret_key
        }
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()

    async def create_payment(
        self,
        amount: float,
        description: str,
        return_url: str,
        email: str = None,
        items: list[dict] = None,
        payment_method_type: str = None,
        extra: Optional[dict] = None
    ):
        if not return_url:
            raise ValueError("return_url обязателен")

        amount_cents = int(round(amount * 100))

        data = {
            "amount": amount_cents,
            "description": description,
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            }
        }

        if payment_method_type:
            data["payment_method_type"] = payment_method_type

        if email and items:
            receipt_items = [
                {
                    "description": item["description"],
                    "amount": int(round(item["amount"] * 100)),
                    "vat_code": item["vat_code"],
                    "quantity": item["quantity"]
                }
                for item in items
            ]
            data["receipt"] = {
                "customer": {"email": email},
                "items": receipt_items
            }

        if extra:
            data.update(extra)

        logger.debug("Создание платежа: %s", data)

        try:
            async with self.session.post(f"{self.base_url}payments", json=data) as resp:
                text = await resp.text()
                if resp.status >= 400:
                    logger.error("HTTPError при создании платежа: %s %s", resp.status, text)
                    resp.raise_for_status()
                result = await resp.json()
                logger.info("Платеж успешно создан: %s", result)
                return result
        except Exception as e:
            logger.error("Ошибка запроса при создании платежа: %s", str(e))
            raise

    async def get_payment(self, payment_uuid: str):
        logger.debug("Получение информации о платеже: %s", payment_uuid)
        try:
            async with self.session.get(f"{self.base_url}payments/{payment_uuid}") as resp:
                text = await resp.text()
                if resp.status >= 400:
                    logger.error("HTTPError при получении платежа: %s %s", resp.status, text)
                    resp.raise_for_status()
                result = await resp.json()
                logger.info("Информация о платеже: %s", result)
                return result
        except Exception as e:
            logger.error("Ошибка запроса при получении платежа: %s", str(e))
            raise

    async def create_refund(self, payment_uuid: str, amount: float, description: Optional[str] = None):
        data = {"payment_uuid": payment_uuid, "amount": amount, "description": description}
        logger.debug("Создание возврата: %s", data)
        try:
            async with self.session.post(f"{self.base_url}refunds", json=data) as resp:
                text = await resp.text()
                if resp.status >= 400:
                    logger.error("HTTPError при создании возврата: %s %s", resp.status, text)
                    resp.raise_for_status()
                result = await resp.json()
                logger.info("Возврат успешно создан: %s", result)
                return result
        except Exception as e:
            logger.error("Ошибка запроса при создании возврата: %s", str(e))
            raise

    async def get_refund(self, refund_uuid: str):
        logger.debug("Получение информации о возврате: %s", refund_uuid)
        try:
            async with self.session.get(f"{self.base_url}refunds/{refund_uuid}") as resp:
                text = await resp.text()
                if resp.status >= 400:
                    logger.error("HTTPError при получении возврата: %s %s", resp.status, text)
                    resp.raise_for_status()
                result = await resp.json()
                logger.info("Информация о возврате: %s", result)
                return result
        except Exception as e:
            logger.error("Ошибка запроса при получении возврата: %s", str(e))
            raise

    async def create_autopayment(self, customer_id: str, amount: float, description: str, save_payment_method: bool = True):
        logger.debug("Создание автоплатежа для клиента: %s", customer_id)
        try:
            return await self.create_payment(
                amount=amount,
                description=description,
                return_url="https://example.com/return",
                extra={"merchant_customer_id": customer_id, "save_payment_method": save_payment_method}
            )
        except Exception as e:
            logger.error("Ошибка при создании автоплатежа: %s", str(e))
            raise

    @staticmethod
    def verify_webhook(data: dict, secret_key: str) -> bool:
        return data.get("secret_key") == secret_key


# Пример использования
async def main():
    async with Payvo("merchant_id", "merchant_secret_key") as client:
        payment = await client.create_payment(
            amount=100.0,
            description="Тестовый платеж",
            return_url="https://example.com/success",
            email="test@example.com",
            items=[{"description": "Товар 1", "amount": 100.0, "vat_code": 1, "quantity": 1}]
        )
        print(payment)


if __name__ == "__main__":
    asyncio.run(main())
