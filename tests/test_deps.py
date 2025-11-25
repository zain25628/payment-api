import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

from app.db.base import Base
from app.models.company import Company
from app.models.channel import Channel
from app.dependencies.deps import get_current_company, get_current_channel

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


class _FakeHeader:
    def __init__(self, value):
        self.value = value

    def __call__(self, *args, **kwargs):
        return self.value


def test_get_current_company_valid_api_key(db_session):
    c = Company()
    c.api_key = "valid-company-key"
    c.is_active = True
    c.name = "TestCo"
    db_session.add(c)
    db_session.commit()

    # call the dependency function directly
    company = get_current_company("valid-company-key", db_session)
    assert company.id == c.id


def test_get_current_company_invalid_key_raises(db_session):
    with pytest.raises(HTTPException) as exc:
        get_current_company("nope", db_session)
    assert exc.value.status_code == 401


def test_get_current_channel_valid_key(db_session):
    co = Company()
    co.api_key = "co-key"
    co.is_active = True
    co.name = "CoName"
    db_session.add(co)
    db_session.commit()

    ch = Channel()
    ch.company_id = co.id
    ch.channel_api_key = "valid-channel-key"
    ch.is_active = True
    ch.name = "ChannelName"
    db_session.add(ch)
    db_session.commit()

    channel = get_current_channel("valid-channel-key", db_session)
    assert channel.id == ch.id


def test_get_current_channel_inactive_raises(db_session):
    co = Company()
    co.api_key = "co2"
    co.is_active = True
    co.name = "Co2"
    db_session.add(co)
    db_session.commit()

    ch = Channel()
    ch.company_id = co.id
    ch.channel_api_key = "inactive-key"
    ch.is_active = False
    ch.name = "Inactive"
    db_session.add(ch)
    db_session.commit()

    with pytest.raises(HTTPException):
        get_current_channel("inactive-key", db_session)
