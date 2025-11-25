from datetime import date, timedelta
import pytest

from app.services import wallet_service
from app.models.wallet import Wallet


class _FakeSession:
    def __init__(self, wallet=None):
        self._added = []
        self.commits = 0
        self._wallet = wallet

    def add(self, obj):
        self._added.append(obj)

    def commit(self):
        self.commits += 1

    def refresh(self, obj):
        # no-op for fake session
        return obj

    class _FakeQuery:
        def __init__(self, result):
            self._result = result

        def filter(self, *args, **kwargs):
            return self

        def order_by(self, *args, **kwargs):
            return self

        def all(self):
            # if _result is a list, return as-is, else wrap
            return self._result if isinstance(self._result, list) else [self._result]

        def first(self):
            return self._result

    def query(self, model):
        return _FakeSession._FakeQuery(self._wallet)


def test_reset_wallet_if_needed_resets_on_new_day():
    # wallet with last_reset_date yesterday and used_today > 0
    w = Wallet()
    w.used_today = 10.0
    w.last_reset_date = date.today() - timedelta(days=1)

    db = _FakeSession()

    wallet_service.reset_wallet_if_needed(w, db)

    assert w.used_today == 0.0
    assert w.last_reset_date == date.today()
    assert db.commits >= 1


def test_reset_wallet_if_needed_same_day_no_reset():
    w = Wallet()
    w.used_today = 5.0
    w.last_reset_date = date.today()

    db = _FakeSession()

    wallet_service.reset_wallet_if_needed(w, db)

    assert w.used_today == 5.0
    # No commit when no changes needed
    assert db.commits == 0


def test_update_wallet_usage_increments_and_resets_if_needed(monkeypatch):
    # prepare a wallet with an old last_reset_date
    w = Wallet()
    w.id = 7
    w.used_today = 0.0
    w.last_reset_date = date.today() - timedelta(days=2)
    w.daily_limit = 100.0

    # FakeSession will return this wallet from query().first()
    db = _FakeSession(wallet=w)

    # Call update_wallet_usage
    updated = wallet_service.update_wallet_usage(db, wallet_id=7, amount=20.0)

    # wallet should have been reset then incremented
    assert updated is w
    assert w.last_reset_date == date.today()
    assert w.used_today == 20.0
    assert db.commits >= 1
