from datetime import datetime
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.wallet import Wallet
import app.repositories.wallet_repository as wallet_repository

# Setup in-memory SQLite
engine = create_engine("sqlite:///:memory:", future=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def _make_wallet(**kwargs) -> Wallet:
    w = Wallet()
    w.company_id = kwargs.get("company_id", 1)
    w.channel_id = kwargs.get("channel_id", 1)
    w.wallet_label = kwargs.get("wallet_label", "w")
    w.wallet_identifier = kwargs.get("wallet_identifier", "id")
    w.daily_limit = kwargs.get("daily_limit", 100.0)
    w.used_today = kwargs.get("used_today", 0.0)
    w.last_reset_date = kwargs.get("last_reset_date")
    w.is_active = kwargs.get("is_active", True)
    return w


def test_get_by_id_returns_none_for_missing(db_session):
    res = wallet_repository.get_by_id(db_session, wallet_id=999)
    assert res is None


def test_get_by_id_returns_wallet(db_session):
    w = _make_wallet(company_id=3)
    db_session.add(w)
    db_session.commit()
    got = wallet_repository.get_by_id(db_session, wallet_id=w.id)
    assert got is not None
    assert got.company_id == 3


def test_get_company_active_wallets_filters_and_orders(db_session):
    # create active and inactive wallets
    w1 = _make_wallet(company_id=10, is_active=False)
    w2 = _make_wallet(company_id=10, is_active=True)
    w3 = _make_wallet(company_id=10, is_active=True)
    db_session.add_all([w1, w2, w3])
    db_session.commit()

    res = wallet_repository.get_company_active_wallets(db_session, company_id=10)
    assert all(w.company_id == 10 for w in res)
    assert all(w.is_active for w in res)


def test_get_company_channel_active_wallets_scopes(db_session):
    w1 = _make_wallet(company_id=20, channel_id=1, is_active=True)
    w2 = _make_wallet(company_id=20, channel_id=2, is_active=True)
    db_session.add_all([w1, w2])
    db_session.commit()

    res = wallet_repository.get_company_channel_active_wallets(db_session, company_id=20, channel_id=1)
    assert len(res) == 1
    assert res[0].channel_id == 1
