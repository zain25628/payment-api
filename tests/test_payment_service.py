import types
import pytest
from datetime import datetime, timezone

import app.services.payment_service as payment_service
from app.models.payment import Payment


class _FakeSession:
    """Minimal fake session for testing persistence helpers.

    This fake session stores added objects in a list and provides no real
    query/filter capabilities. It is intentionally minimal for unit tests
    that do not exercise SQLAlchemy behavior.
    """

    def __init__(self):
        self._store = []

    def add(self, obj):
        # mimic SQLAlchemy: adding registers the object
        if obj not in self._store:
            self._store.append(obj)

    def commit(self):
        pass

    def refresh(self, obj):
        # no-op: object is already mutable in-place
        return obj

    # Minimal `query` used in one test to simulate "no results" behavior
    def query(self, model):
        class _EmptyQuery:
            def filter(self, *args, **kwargs):
                return self

            def order_by(self, *args, **kwargs):
                return self

            def first(self):
                return None

        return _EmptyQuery()


def test_create_payment_from_sms_basic():
    db = _FakeSession()
    payload = {
        "company_id": 1,
        "channel_id": 2,
        "amount": 123.45,
        "payer_phone": "+10000000000",
        "receiver_phone": "+19999999999",
        "raw_message": "PAY 123.45",
        "currency": "USD",
    }

    payment = payment_service.create_payment_from_sms(db, payload)

    assert isinstance(payment, Payment)
    assert payment.company_id == payload["company_id"]
    assert payment.channel_id == payload["channel_id"]
    assert payment.amount == payload["amount"]
    assert payment.payer_phone == payload["payer_phone"]
    assert payment.receiver_phone == payload["receiver_phone"]


def test_confirm_payment_usage_updates_status_and_used_at(monkeypatch):
    db = _FakeSession()

    # create a Payment-like object (SQLAlchemy model instance)
    payment = Payment()
    payment.id = 999
    payment.wallet_id = 42
    payment.amount = 50.0
    payment.status = "pending_confirmation"
    payment.used_at = None

    called = {}

    def fake_update_wallet_usage(db_arg, wallet_id, amount):
        called["wallet_id"] = wallet_id
        called["amount"] = amount

    # Monkeypatch the update_wallet_usage used by the payment_service module
    monkeypatch.setattr(payment_service, "update_wallet_usage", fake_update_wallet_usage)

    ret = payment_service.confirm_payment_usage(db, payment)

    assert ret is payment
    assert payment.status == "used"
    assert payment.used_at is not None
    # used_at must be timezone-aware and set to UTC
    assert payment.used_at.tzinfo is not None
    assert payment.used_at.tzinfo == timezone.utc
    assert called.get("wallet_id") == 42
    assert called.get("amount") == 50.0


def test_match_payment_for_order_no_match_returns_none():
    db = _FakeSession()
    result = payment_service.match_payment_for_order(db, company_id=1, amount=10.0, currency="USD")
    assert result is None
