# Refactored by Copilot – Incoming SMS Tests
from types import SimpleNamespace


def test_incoming_sms_missing_raw_message(client):
    response = client.post(
        "/incoming-sms",
        json={
            "payer_phone": "9715xxxxxxx",
            "receiver_phone": "9715yyyyyyy",
            "amount": 100.0,
        },
        headers={"X-API-Key": "dummy-key"},
    )
    assert response.status_code == 422


def test_incoming_sms_minimal_valid_payload(client):
    # Ensure store_payment is stubbed to avoid DB operations and return id
    try:
        import app.services.sms_service as sms_service
        original = sms_service.store_payment
        sms_service.store_payment = lambda db, channel_id, company_id, parsed: SimpleNamespace(id=1)
    except Exception:
        original = None

    response = client.post(
        "/incoming-sms",
        json={
            "payer_phone": "9715xxxxxxx",
            "receiver_phone": "9715yyyyyyy",
            "raw_message": "Payment 150.00 AED to account 9715yyyyyyy",
            "amount": 150.0,
        },
        headers={"X-API-Key": "dummy-key"},
    )

    # Restore original
    if original is not None:
        sms_service.store_payment = original

    assert response.status_code == 200
    body = response.json()
    assert "payment_id" in body
    assert body["payment_id"] == 1


def test_incoming_sms_invalid_amount_type(client):
    # amount provided as non-numeric string should cause Pydantic validation (422)
    response = client.post(
        "/incoming-sms",
        json={
            "payer_phone": "9715xxxxxxx",
            "receiver_phone": "9715yyyyyyy",
            "raw_message": "Payment...",
            "amount": "not-a-number",
        },
        headers={"X-API-Key": "dummy-key"},
    )

    assert response.status_code == 422
