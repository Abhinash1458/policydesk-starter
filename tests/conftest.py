"""Shared fixtures: every test gets a fresh in-memory SQLite database with seed data."""
import os

# Must be set before `app` is imported so the app engine never touches policydesk.db.
os.environ["DATABASE_URL"] = "sqlite://"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402
from sqlmodel import Session, SQLModel, create_engine  # noqa: E402

from app.db import get_session  # noqa: E402
from app.main import app  # noqa: E402
from app.seed import seed  # noqa: E402


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        seed(s)
        yield s


@pytest.fixture
def client(session):
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def ids(client):
    """Handy lookup of seeded customer/product ids by name/code."""
    customers = {c["name"]: c["id"] for c in client.get("/api/customers").json()}
    products = {p["code"]: p["id"] for p in client.get("/api/products").json()}
    return {"customers": customers, "products": products}


# Two policies are seeded on startup (app/seed.py) so claims can be tested before the premium calculator exists.
@pytest.fixture
def health_policy(client):
    """Seeded: Priya Nair · Health Shield · sum insured 5,00,000 · 1 year · 2026-01-01 -> 2026-12-31 · premium 15,000."""
    return next(p for p in client.get("/api/policies").json() if p["policy_number"].startswith("PD-HEALTH-"))


@pytest.fixture
def motor_policy(client):
    """Seeded: Rohan Das · Motor Secure · 8,00,000 · 2 years · 2026-03-01 -> 2028-02-28 · vehicle TS09AB1234."""
    return next(p for p in client.get("/api/policies").json() if p["policy_number"].startswith("PD-MOTOR-"))
