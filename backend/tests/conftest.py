import os
import tempfile
from pathlib import Path

_TEST_DB = Path(tempfile.mkdtemp(prefix="dealroom-tests-")) / "test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB.as_posix()}"
os.environ.setdefault("SECRET_KEY", "test-secret-key")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def register(client):
    counter = {"n": 0}

    def _register(
        email: str | None = None,
        password: str = "password123",
        full_name: str = "Test User",
        company_name: str = "Acme Corp",
    ) -> dict:
        counter["n"] += 1
        email = email or f"user{counter['n']}@example.com"
        resp = client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": password,
                "full_name": full_name,
                "company_name": company_name,
            },
        )
        assert resp.status_code == 200, resp.text
        return {
            "email": email,
            "token": resp.json()["access_token"],
            "headers": {"Authorization": f"Bearer {resp.json()['access_token']}"},
        }

    return _register
