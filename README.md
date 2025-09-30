# Payvo SDK

Python SDK для работы с [Payvo API](https://docs.payvo.ru/).
Позволяет интегрировать платёжный сервис в Python-приложения быстро и удобно.

---

## ⚡ Установка

### 🔹 Через PyPI

```bash
pip install payvo-sdk
```

---

## 🛠 Инициализация SDK

```python
from payvo_sdk import Payvo

# Инициализация
payvo = Payvo(
    merchant_id="ваш_merchant_id",
    merchant_secret_key="ваш_secret_key",
)
```

---

## 💳 Работа с платежами

### Создание платежа

```python
payment = payvo.create_payment(
    amount=200.0,
    description="Тестовый платеж"
)
print(payment)
```

### Получение информации о платеже

```python
info = payvo.get_payment(payment_uuid=payment["payment"]["uuid"])
print(info)
```

---

## 🔁 Работа с возвратами

### Создание возврата

```python
refund = payvo.create_refund(
    payment_uuid=payment["payment"]["uuid"],
    amount=50.0,
    description="Частичный возврат"
)
print(refund)
```

### Получение информации о возврате

```python
refund_info = payvo.get_refund(refund_uuid=refund["uuid"])
print(refund_info)
```

---

## 🔄 Автоплатежи

```python
autopayment = payvo.create_autopayment(
    customer_id="id_клиента",
    amount=150.0,
    description="Автоплатеж"
)
print(autopayment)
```

> ⚠️ Для автоплатежей необходимо согласовать с Payvo возможность сохранения платёжного метода.

---

## 🔔 Работа с вебхуками

### Проверка секретного ключа вебхука

```python
webhook_data = {"secret_key": "тестовый_ключ"}
is_valid = Payvo.verify_webhook(webhook_data, secret_key="тестовый_ключ")
print(is_valid)  # True или False
```

> 💡 Используйте `verify_webhook` для проверки, что уведомление пришло именно от Payvo.

---

## 📚 Полезные ссылки

* [Документация Payvo API](https://docs.payvo.ru/)
* [PyPI](https://pypi.org/)

---

## 📝 Пример полного скрипта

```python
from payvo_sdk import Payvo

payvo = Payvo(
    merchant_id="ваш_merchant_id",
    merchant_secret_key="ваш_secret_key"
)

# Список товаров (если включены Payvo.Чеки)
items = [
    {"description": "Товар 1", "amount": 42.80, "vat_code": 1, "quantity": 1},
    {"description": "Товар 2", "amount": 15.50, "vat_code": 2, "quantity": 2}
]

# Создать платеж
payment = payvo.create_payment(
    amount=58.30,  # общая сумма, для поля amount
    description="Заказ №1",
    return_url="https://www.example.com/return_url",
    email="user@example.com",
    items=items
)

# Проверка платежа
info = payvo.get_payment(payment["payment"]["uuid"])

# Частичный возврат
refund = payvo.create_refund(payment["uuid"], 50.0, "Частичный возврат")

# Проверка вебхука
webhook_data = {"secret_key": "тестовый_ключ"}
print(Payvo.verify_webhook(webhook_data, secret_key="тестовый_ключ"))
```
