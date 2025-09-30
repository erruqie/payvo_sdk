import requests
from typing import Optional
import logging

# Настройка логирования
logger = logging.getLogger("PayvoSDK")
logger.setLevel(logging.DEBUG)  # Можно менять на INFO для меньше подробностей
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

    def create_payment(self, amount: float, description: str,
                    return_url: str,
                    email: str = None,
                    items: list[dict] = None,
                    payment_method_type: str = None,
                    extra: Optional[dict] = None):
        """
        Создаёт платёж в Payvo с поддержкой receipt.
        :param amount: сумма в рублях (float)
        :param description: описание платежа (для платежа)
        :param return_url: URL редиректа
        :param email: email покупателя (для receipt)
        :param items: список товаров для receipt, каждый словарь должен содержать:
                    'description', 'amount' (рубли), 'vat_code', 'quantity'
        :param payment_method_type: тип оплаты (необязательно)
        :param extra: дополнительные поля API
        """
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
            # конвертируем amount каждого товара в копейки
            receipt_items = []
            for item in items:
                receipt_items.append({
                    "description": item["description"],
                    "amount": int(round(item["amount"] * 100)),
                    "vat_code": item["vat_code"],
                    "quantity": item["quantity"]
                })
            data["receipt"] = {
                "customer": {"email": email},
                "items": receipt_items
            }

        if extra:
            data.update(extra)

        logger.debug("Создание платежа: %s", data)

        try:
            resp = requests.post(f"{self.base_url}payments", json=data, headers=self.headers)
            resp.raise_for_status()
            logger.info("Платеж успешно создан: %s", resp.json())
            return resp.json()
        except requests.exceptions.HTTPError as e:
            logger.error("HTTPError при создании платежа: %s %s", e.response.status_code, e.response.text)
            raise
        except requests.exceptions.RequestException as e:
            logger.error("Ошибка запроса при создании платежа: %s", str(e))
            raise

    def get_payment(self, payment_uuid: str):
        logger.debug("Получение информации о платеже: %s", payment_uuid)
        try:
            resp = requests.get(f"{self.base_url}payments/{payment_uuid}", headers=self.headers)
            resp.raise_for_status()
            logger.info("Информация о платеже: %s", resp.json())
            return resp.json()
        except requests.exceptions.HTTPError as e:
            logger.error("HTTPError при получении платежа: %s %s", e.response.status_code, e.response.text)
            raise
        except requests.exceptions.RequestException as e:
            logger.error("Ошибка запроса при получении платежа: %s", str(e))
            raise

    def create_refund(self, payment_uuid: str, amount: float, description: Optional[str] = None):
        data = {"payment_uuid": payment_uuid, "amount": amount, "description": description}
        logger.debug("Создание возврата: %s", data)
        try:
            resp = requests.post(f"{self.base_url}refunds", json=data, headers=self.headers)
            resp.raise_for_status()
            logger.info("Возврат успешно создан: %s", resp.json())
            return resp.json()
        except requests.exceptions.HTTPError as e:
            logger.error("HTTPError при создании возврата: %s %s", e.response.status_code, e.response.text)
            raise
        except requests.exceptions.RequestException as e:
            logger.error("Ошибка запроса при создании возврата: %s", str(e))
            raise

    def get_refund(self, refund_uuid: str):
        logger.debug("Получение информации о возврате: %s", refund_uuid)
        try:
            resp = requests.get(f"{self.base_url}refunds/{refund_uuid}", headers=self.headers)
            resp.raise_for_status()
            logger.info("Информация о возврате: %s", resp.json())
            return resp.json()
        except requests.exceptions.HTTPError as e:
            logger.error("HTTPError при получении возврата: %s %s", e.response.status_code, e.response.text)
            raise
        except requests.exceptions.RequestException as e:
            logger.error("Ошибка запроса при получении возврата: %s", str(e))
            raise

    def create_autopayment(self, customer_id: str, amount: float, description: str, save_payment_method: bool = True):
        logger.debug("Создание автоплатежа для клиента: %s", customer_id)
        try:
            return self.create_payment(
                amount=amount,
                description=description,
                return_url="https://example.com/return",  # Можно сделать параметром метода
                extra={"merchant_customer_id": customer_id, "save_payment_method": save_payment_method}
            )
        except Exception as e:
            logger.error("Ошибка при создании автоплатежа: %s", str(e))
            raise

    @staticmethod
    def verify_webhook(data: dict, secret_key: str) -> bool:
        return data.get("secret_key") == secret_key