"""API tests for /api/quotes (Lab 1 reference)."""


def test_create_quote_returns_premium(client, ids):
    r = client.post(
        "/api/quotes",
        json={"customer_id": ids["customers"]["Priya Nair"], "product_id": ids["products"]["HEALTH"],
              "sum_insured": 500000, "tenure_years": 1},
    )
    assert r.status_code == 201
    assert r.json()["premium"] == 15000.0


def test_quote_unknown_customer_404(client, ids):
    r = client.post("/api/quotes", json={"customer_id": 999, "product_id": ids["products"]["HEALTH"],
                                          "sum_insured": 500000, "tenure_years": 1})
    assert r.status_code == 404


def test_quote_below_min_sum_insured_422(client, ids):
    r = client.post("/api/quotes", json={"customer_id": ids["customers"]["Priya Nair"],
                                          "product_id": ids["products"]["HEALTH"],
                                          "sum_insured": 5000, "tenure_years": 1})
    assert r.status_code == 422
    assert "at least" in r.json()["detail"]


def test_quote_invalid_tenure_422(client, ids):
    r = client.post("/api/quotes", json={"customer_id": ids["customers"]["Priya Nair"],
                                          "product_id": ids["products"]["HEALTH"],
                                          "sum_insured": 500000, "tenure_years": 4})
    assert r.status_code == 422


def test_create_customer_duplicate_email_409(client):
    payload = {"name": "Test User", "email": "priya.nair@example.com", "phone": "9999999999", "date_of_birth": "1995-01-01"}
    assert client.post("/api/customers", json=payload).status_code == 409
