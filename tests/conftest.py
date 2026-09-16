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


# The two fixtures below need Lab 1 (quotes) AND Lab 2 (policies) done. Use them in Lab 2 and Lab 3 tests.
@pytest.fixture
def health_policy(client, ids):
    """An active 1-year Health policy for Priya Nair (age ~36), sum insured 5,00,000."""
    q = client.post(
        "/api/quotes",
        json={"customer_id": ids["customers"]["Priya Nair"], "product_id": ids["products"]["HEALTH"],
              "sum_insured": 500000, "tenure_years": 1},
    ).json()
    return client.post("/api/policies", json={"quote_id": q["id"], "start_date": "2026-01-01"}).json()


@pytest.fixture
def motor_policy(client, ids):
    q = client.post(
        "/api/quotes",
        json={"customer_id": ids["customers"]["Rohan Das"], "product_id": ids["products"]["MOTOR"],
              "sum_insured": 800000, "tenure_years": 2, "add_ons": "ZERO_DEPRECIATION"},
    ).json()
    return client.post(
        "/api/policies",
        json={"quote_id": q["id"], "start_date": "2026-01-01", "vehicle_registration": "TS09AB1234"},
    ).json()
