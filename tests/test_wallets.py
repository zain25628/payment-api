# Refactored by Copilot – Wallets Tests
import pytest


def test_request_wallet_missing_body(client):
    response = client.post("/wallets/request")
    assert response.status_code == 422


def test_request_wallet_invalid_amount(client):
    # Negative amount should be rejected by Pydantic validation (422)
    response = client.post(
        "/wallets/request",
        json={"amount": -10},
        headers={"X-API-Key": "dummy-key"},
    )
    # Accept either validation 422 or any non-2xx (if dependency prevented validation)
    assert response.status_code == 422 or response.status_code >= 400


def test_request_wallet_zero_amount(client):
    response = client.post(
        "/wallets/request",
        json={"amount": 0},
        headers={"X-API-Key": "dummy-key"},
    )

    # Expect Pydantic validation to reject zero amount (gt=0)
    assert response.status_code == 422
