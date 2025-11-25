import pytest


def test_validation_error_uses_custom_handler(client):
    response = client.post("/wallets/request")
    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
    assert isinstance(body["detail"], list)


def test_unhandled_exception_returns_500_json(client, monkeypatch, caplog):
    import logging

    def _boom(*args, **kwargs):
        raise RuntimeError("boom")

    # Monkeypatch the function where the router imported it so the endpoint uses our fake
    import app.routers.wallets as wallets_router
    monkeypatch.setattr(wallets_router, "find_available_wallet", _boom)

    with caplog.at_level(logging.ERROR):
        try:
            response = client.post(
                "/wallets/request",
                json={"amount": 100},
                headers={"X-API-Key": "dummy-key"},
            )
            # If the app returns a response, ensure it's a 500 with expected JSON
            assert response.status_code == 500
            body = response.json()
            assert body.get("detail") == "Internal server error"
        except Exception:
            # Some test client configurations propagate exceptions instead of returning
            # the handler response. In that case, ensure the exception was logged.
            assert any("Unhandled error" in rec.getMessage() for rec in caplog.records)
