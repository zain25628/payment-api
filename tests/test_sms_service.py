from app.services import sms_service
from app.models.payment import Payment
import app.services.payment_service as payment_service
from sqlalchemy.orm import Session
import pytest


class _FakeSession:
    def __init__(self):
        self.added = []
        self.commits = 0

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.commits += 1

    def refresh(self, obj):
        pass


def test_parse_incoming_sms_basic():
    payload = {
        "payer_phone": "9715xxxxxxx",
        "receiver_phone": "9715yyyyyyy",
        "raw_message": "Your account has been credited...",
        "amount": "150.0",
        "currency": "AED",
        "txn_id": "ABC123",
    }

    parsed = sms_service.parse_incoming_sms(payload)

    assert parsed["payer_phone"] == "9715xxxxxxx"
    assert parsed["receiver_phone"] == "9715yyyyyyy"
    assert parsed["raw_message"].startswith("Your account")
    assert isinstance(parsed["amount"], float) and parsed["amount"] == 150.0
    assert parsed["currency"] == "AED"
    assert parsed["txn_id"] == "ABC123"


def test_store_payment_calls_create_payment_from_sms(monkeypatch):
    db = _FakeSession()

    def _fake_create_payment_from_sms(db_arg, data):
        # Ensure company_id, channel_id, status are merged
        assert data["company_id"] == 1
        assert data["channel_id"] == 2
        assert data["status"] == "new"
        # Return a lightweight object with an `id` attribute to avoid ORM behavior
        class _SimplePayment:
            def __init__(self, id):
                self.id = id

        return _SimplePayment(123)

    # sms_service imported the function directly, patch the name in sms_service module
    monkeypatch.setattr(sms_service, "create_payment_from_sms", _fake_create_payment_from_sms)

    parsed = {
        "payer_phone": "9715xxxxxxx",
        "receiver_phone": "9715yyyyyyy",
        "raw_message": "...",
        "amount": 150.0,
        "currency": "AED",
        "txn_id": "ABC123",
    }

    payment = sms_service.store_payment(db, channel_id=2, company_id=1, parsed_data=parsed)

    assert getattr(payment, "id", None) == 123


def test_parse_incoming_sms_missing_amount_defaults_to_zero():
    payload = {
        "payer_phone": "9715xxxxxxx",
        "receiver_phone": "9715yyyyyyy",
        "raw_message": "No amount here",
        "currency": "AED",
        "txn_id": "XYZ",
    }

    parsed = sms_service.parse_incoming_sms(payload)
    # Current behavior uses float(payload.get('amount', 0)) so missing amount -> 0.0
    assert parsed["amount"] == 0.0

