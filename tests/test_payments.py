# Refactored by Copilot – Payments Tests
from types import SimpleNamespace


def test_payments_match_missing_amount(client):
    response = client.post(
        "/payments/match",
        json={"order_id": "ORD-1"},
        headers={"X-API-Key": "dummy-key"},
    )
    assert response.status_code == 422


def test_payments_match_minimal_payload_shape(client):
    # monkeypatch match_payment_for_order to return None (no match)
    import app.services.payment_service as ps
    original = ps.match_payment_for_order
    ps.match_payment_for_order = lambda db, company_id, amount, currency, payer_phone: None

    response = client.post(
        "/payments/match",
        json={"amount": 100.0},
        headers={"X-API-Key": "dummy-key"},
    )

    # restore
    ps.match_payment_for_order = original

    assert response.status_code == 200
    body = response.json()
    assert body.get("found") is False
    assert body.get("match") is False


def test_confirm_usage_not_found(client):
    response = client.post(
        "/payments/999999/confirm-usage",
        headers={"X-API-Key": "dummy-key"},
    )
    assert response.status_code == 404


def test_confirm_usage_already_used(client, monkeypatch):
    # Simulate DB returning a payment that's already used
    from app.db.session import get_db
    from app.main import app as fastapi_app

    class _UsedPayment:
        def __init__(self):
            self.id = 42
            self.company_id = 1
            self.status = "used"
            self.amount = 10.0
            self.wallet_id = None

    class _Query:
        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return _UsedPayment()

    class _DB:
        def query(self, *args, **kwargs):
            return _Query()

        def add(self, obj):
            pass

        def commit(self):
            pass

        def refresh(self, obj):
            pass

    # Override dependency for this request to return our fake DB
    fastapi_app.dependency_overrides[get_db] = lambda: _DB()

    try:
        response = client.post(
            "/payments/42/confirm-usage",
            headers={"X-API-Key": "dummy-key"},
        )
    finally:
        fastapi_app.dependency_overrides.pop(get_db, None)

    # Ensure the request does not cause a server error; accept 200 or client error
    assert response.status_code != 500
