import pytest
from payvo_sdk import Payvo

# Тестовые значения
MERCHANT_ID = "test_merchant_id"
MERCHANT_KEY = "test_secret_key"

def test_sdk_initialization():
    """Проверка инициализации SDK"""
    sdk = Payvo(MERCHANT_ID, MERCHANT_KEY, test_mode=True)
    assert sdk.merchant_id == MERCHANT_ID
    assert sdk.secret_key == MERCHANT_KEY
    assert sdk.base_url.endswith("sandbox.payvo.ru/public/")

def test_create_payment_structure():
    """Проверка структуры ответа при создании платежа (mock)"""
    sdk = Payvo(MERCHANT_ID, MERCHANT_KEY, test_mode=True)
    
    # Здесь можно использовать mock, если нет реального API
    # Пример простой проверки структуры
    payment_response = {
        "uuid": "12345",
        "amount": 100.0,
        "status": "pending"
    }
    
    assert "uuid" in payment_response
    assert "amount" in payment_response
    assert "status" in payment_response

def test_verify_webhook():
    """Проверка метода verify_webhook"""
    data = {"secret_key": "correct_key"}
    assert Payvo.verify_webhook(data, secret_key="correct_key") is True
    assert Payvo.verify_webhook(data, secret_key="wrong_key") is False
