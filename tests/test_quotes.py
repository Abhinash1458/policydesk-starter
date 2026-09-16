"""Lab 1 — quotes API."""
import pytest

pytestmark = pytest.mark.regression


def test_create_quote_returns_201_with_premium(client, ids):
    r = client.post("/api/quotes", json={
        "customer_id": ids["customers"]["Priya Nair"], "product_id": ids["products"]["HEALTH"],
        "sum_insured": 500000, "tenure_years": 1,
    })
    assert r.status_code == 201
    body = r.json()
    assert body["premium"] == 15000.0          # 5,00,000 x 0.03 x 1.0 (age 36) x 1.0
    assert body["id"]
    assert client.get(f"/api/quotes/{body['id']}").json()["premium"] == 15000.0


def test_quote_with_add_on_and_tenure(client, ids):
    r = client.post("/api/quotes", json={
        "customer_id": ids["customers"]["Rohan Das"], "product_id": ids["products"]["MOTOR"],
        "sum_insured": 800000, "tenure_years": 2, "add_ons": "ZERO_DEPRECIATION",
    })
    assert r.status_code == 201
    # Rohan is 28 -> 1.0 ; 8,00,000 x 0.025 x 1.0 x 0.95 x 1.10 = 20,900
    assert r.json()["premium"] == pytest.approx(20900.0)


def test_unknown_customer_or_product_is_404(client, ids):
    base = {"sum_insured": 500000, "tenure_years": 1}
    assert client.post("/api/quotes", json={**base, "customer_id": 999, "product_id": ids["products"]["HEALTH"]}).status_code == 404
    assert client.post("/api/quotes", json={**base, "customer_id": ids["customers"]["Priya Nair"], "product_id": 999}).status_code == 404


def test_pricing_rule_violation_is_422_with_message(client, ids):
    r = client.post("/api/quotes", json={
        "customer_id": ids["customers"]["Priya Nair"], "product_id": ids["products"]["HEALTH"],
        "sum_insured": 50000, "tenure_years": 1,          # below Health minimum of 1,00,000
    })
    assert r.status_code == 422
    assert "at least" in r.json()["detail"]


def test_invalid_add_on_is_422(client, ids):
    r = client.post("/api/quotes", json={
        "customer_id": ids["customers"]["Priya Nair"], "product_id": ids["products"]["TERM_LIFE"],
        "sum_insured": 1000000, "tenure_years": 1, "add_ons": "CRITICAL_ILLNESS",
    })
    assert r.status_code == 422


def test_quotes_are_listed_newest_first(client, ids):
    for sum_insured in (500000, 600000):
        client.post("/api/quotes", json={
            "customer_id": ids["customers"]["Priya Nair"], "product_id": ids["products"]["HEALTH"],
            "sum_insured": sum_insured, "tenure_years": 1,
        })
    listed = client.get("/api/quotes").json()
    assert [q["sum_insured"] for q in listed] == [600000, 500000]


def test_quote_form_submission_redirects_to_detail(client, ids):
    r = client.post("/quotes/new", data={
        "customer_id": ids["customers"]["Priya Nair"], "product_id": ids["products"]["HEALTH"],
        "sum_insured": 500000, "tenure_years": 1,
    }, follow_redirects=False)
    assert r.status_code == 303
    detail = client.get(r.headers["location"])
    assert detail.status_code == 200 and "15,000.00" in detail.text
