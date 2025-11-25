from datetime import datetime, timedelta, timezone
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.payment import Payment
import app.repositories.payment_repository as payment_repository


# Setup an in-memory SQLite for repository unit tests
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


def _make_payment(**kwargs) -> Payment:
    p = Payment()
    # set some sensible defaults
    p.company_id = kwargs.get("company_id", 1)
    p.channel_id = kwargs.get("channel_id", 1)
    p.amount = kwargs.get("amount", 10.0)
    p.currency = kwargs.get("currency", "USD")
    p.payer_phone = kwargs.get("payer_phone", "+10000000000")
    p.receiver_phone = kwargs.get("receiver_phone", "+19999999999")
    p.raw_message = kwargs.get("raw_message", "PAY")
    p.status = kwargs.get("status", "new")
    # allow explicit created_at for testing
    p.created_at = kwargs.get("created_at")
    return p


def test_create_persists_payment(db_session):
    p = _make_payment(company_id=5)
    created = payment_repository.create(db_session, p)

    assert created.id is not None

    # read back
    got = db_session.query(Payment).filter(Payment.id == created.id).first()
    assert got is not None
    assert got.company_id == 5


def test_find_most_recent_matching_returns_latest_within_window(db_session):
    now = datetime.now(timezone.utc)
    old = _make_payment(company_id=1, currency="USD", created_at=now - timedelta(hours=2))
    recent = _make_payment(company_id=1, currency="USD", created_at=now - timedelta(minutes=5))
    db_session.add(old)
    db_session.add(recent)
    db_session.commit()

    # Ask for matches within last 60 minutes -> should return 'recent'
    found = payment_repository.find_most_recent_matching(db_session, company_id=1, currency="USD", max_age_minutes=60)
    assert found is not None
    assert found.created_at >= recent.created_at

    # If window is small, no match
    none_found = payment_repository.find_most_recent_matching(db_session, company_id=1, currency="USD", max_age_minutes=1)
    assert none_found is None


def test_get_by_id_for_company_scopes_to_company(db_session):
    p1 = _make_payment(company_id=1)
    p2 = _make_payment(company_id=2)
    db_session.add(p1)
    db_session.add(p2)
    db_session.commit()

    # p2.id exists but belongs to company 2
    res = payment_repository.get_by_id_for_company(db_session, company_id=1, payment_id=p2.id)
    assert res is None

    res2 = payment_repository.get_by_id_for_company(db_session, company_id=2, payment_id=p2.id)
    assert res2 is not None
    assert res2.id == p2.id
