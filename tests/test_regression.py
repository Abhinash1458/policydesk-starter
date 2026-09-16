"""Regression tests — ten checks on the features the starter already gives you.

They protect what works today so a change in Lab 1/2/3 cannot silently break it. CI runs them after the
smoke tests on every push and pull request. When you finish a lab, add its tests to this file (or mark them
`regression`) so the pipeline guards your feature too.
"""
import pytest

pytestmark = pytest.mark.regression


# ---- data & API -------------------------------------------------------------

def test_three_products_are_seeded_with_codes(client):
    products = client.get("/api/products").json()
    assert {p["code"] for p in products} == {"HEALTH", "MOTOR", "TERM_LIFE"}


def test_product_carries_rate_and_cover_limits(client):
    health = next(p for p in client.get("/api/products").json() if p["code"] == "HEALTH")
    assert health["base_rate"] == pytest.approx(0.03)
    assert health["min_sum_insured"] == 100000
    assert health["max_sum_insured"] == 5000000


def test_unknown_product_returns_404(client):
    assert client.get("/api/products/999").status_code == 404


def test_two_demo_customers_are_seeded(client):
    names = {c["name"] for c in client.get("/api/customers").json()}
    assert names == {"Priya Nair", "Rohan Das"}


def test_create_customer_returns_201_and_is_listed(client):
    payload = {"name": "Asha Verma", "email": "asha.verma@example.com", "phone": "9000011111", "date_of_birth": "1995-03-12"}
    r = client.post("/api/customers", json=payload)
    assert r.status_code == 201
    assert r.json()["id"]
    assert "Asha Verma" in {c["name"] for c in client.get("/api/customers").json()}


def test_duplicate_customer_email_is_rejected_with_409(client):
    payload = {"name": "Priya Again", "email": "priya.nair@example.com", "phone": "9111122222", "date_of_birth": "1990-08-25"}
    assert client.post("/api/customers", json=payload).status_code == 409


def test_invalid_customer_email_is_rejected_with_422(client):
    payload = {"name": "Bad Email", "email": "not-an-email", "phone": "9111122222", "date_of_birth": "1990-08-25"}
    assert client.post("/api/customers", json=payload).status_code == 422


def test_policies_and_claims_lists_start_empty(client):
    assert client.get("/api/policies").json() == []
    assert client.get("/api/claims").json() == []


# ---- screens ---------------------------------------------------------------

def test_given_pages_render(client):
    for path in ["/customers", "/products", "/quotes/new", "/policies", "/claims"]:
        r = client.get(path)
        assert r.status_code == 200, path
        assert "PolicyDesk" in r.text, path


def test_quote_form_lists_customers_and_products(client):
    html = client.get("/quotes/new").text
    assert "Priya Nair" in html and "Rohan Das" in html
    assert "Health Shield" in html and "Motor Secure" in html and "Term Life Plus" in html
