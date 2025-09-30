import requests
from typing import Optional

class Payvo:
    PRODUCTION_URL = "https://api.payvo.ru/public/"
    TEST_URL = "https://sandbox.payvo.ru/public/"

    def __init__(self, merchant_id: str, merchant_secret_key: str, test_mode: bool = False):
        self.merchant_id = merchant_id
        self.secret_key = merchant_secret_key
        self.base_url = self.TEST_URL if test_mode else self.PRODUCTION_URL
        self.headers = {
            "Content-Type": "application/json",
            "merchant-id": self.merchant_id,
            "merchant-secret-key": self.secret_key
        }

    def create_payment(self, amount: float, description: str, merchant_customer_id: Optional[str] = None,
                       save_payment_method: bool = False, extra: Optional[dict] = None):
        data = {
            "amount": amount,
            "description": description,
            "merchant_customer_id": merchant_customer_id,
            "save_payment_method": save_payment_method
        }
        if extra:
            data.update(extra)
        resp = requests.post(f"{self.base_url}payments", json=data, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def get_payment(self, payment_uuid: str):
        resp = requests.get(f"{self.base_url}payments/{payment_uuid}", headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def create_refund(self, payment_uuid: str, amount: float, description: Optional[str] = None):
        data = {"payment_uuid": payment_uuid, "amount": amount, "description": description}
        resp = requests.post(f"{self.base_url}refunds", json=data, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def get_refund(self, refund_uuid: str):
        resp = requests.get(f"{self.base_url}refunds/{refund_uuid}", headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def create_autopayment(self, customer_id: str, amount: float, description: str, save_payment_method: bool = True):
        return self.create_payment(amount=amount, description=description,
                                   merchant_customer_id=customer_id,
                                   save_payment_method=save_payment_method)

    @staticmethod
    def verify_webhook(data: dict, secret_key: str) -> bool:
        return data.get("secret_key") == secret_key
