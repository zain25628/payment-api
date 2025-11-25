# Refactored by Copilot – Test Fixtures
import warnings
from fastapi.testclient import TestClient
# Silence DeprecationWarning about HTTP_422_UNPROCESSABLE_ENTITY coming from Starlette
warnings.filterwarnings(
    "ignore",
    message=r".*HTTP_422_UNPROCESSABLE_ENTITY.*",
    category=DeprecationWarning,
)
from app.main import app
import pytest

from app.dependencies.deps import get_current_company
from app.db.session import get_db


class _DummyCompany:
    def __init__(self):
        self.id = 1
        self.name = "Dummy"
        self.api_key = "dummy-key"
        self.is_active = True


@pytest.fixture(scope="module")
def client():
    # Override company dependency to avoid DB access during tests
    app.dependency_overrides[get_current_company] = lambda: _DummyCompany()

    # Provide a dummy DB session that safely responds to .query(...).filter(...).first()
    class _DummyQuery:
        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return None

    class _DummyDB:
        def query(self, *args, **kwargs):
            return _DummyQuery()

    app.dependency_overrides[get_db] = lambda: _DummyDB()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_current_company, None)
    app.dependency_overrides.pop(get_db, None)
