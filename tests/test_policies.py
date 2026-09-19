"""Lab 2 — policy rules: issue from a quote, the period, one-per-quote, Motor needs a vehicle, cancelled is final."""


def test_health_policy_is_issued_from_the_quote(health_policy):
    assert health_policy["policy_number"].startswith("PD-HEALTH-2026-")
    assert health_policy["status"] == "Active"
    assert health_policy["start_date"] == "2026-01-01"
    assert health_policy["end_date"] == "2026-12-31"
    assert health_policy["premium"] == 15000.0


def test_two_year_motor_policy_end_date_and_vehicle(motor_policy):
    # 1 Jan 2026 + 730 days = 1 Jan 2028, minus 1 day = 31 Dec 2027
    assert motor_policy["end_date"] == "2027-12-31"
    assert motor_policy["vehicle_registration"] == "TS09AB1234"


def test_issuing_the_same_quote_twice_is_a_conflict(client, health_policy):
    r = client.post("/api/policies", json={"quote_id": health_policy["quote_id"], "start_date": "2026-01-01"})
    assert r.status_code == 409


def test_motor_policy_without_vehicle_is_rejected(client, ids):
    q = client.post(
        "/api/quotes",
        json={"customer_id": ids["customers"]["Rohan Das"], "product_id": ids["products"]["MOTOR"],
              "sum_insured": 300000, "tenure_years": 1},
    ).json()
    r = client.post("/api/policies", json={"quote_id": q["id"], "start_date": "2026-01-01"})
    assert r.status_code == 422


def test_unknown_quote_is_404(client):
    r = client.post("/api/policies", json={"quote_id": 999, "start_date": "2026-01-01"})
    assert r.status_code == 404


def test_lapsed_policy_moves_between_status_filters(client, health_policy):
    r = client.patch(f"/api/policies/{health_policy['id']}/status", json={"status": "Lapsed"})
    assert r.status_code == 200
    assert r.json()["status"] == "Lapsed"
    assert client.get("/api/policies", params={"status_filter": "Active"}).json() == []
    assert len(client.get("/api/policies", params={"status_filter": "Lapsed"}).json()) == 1


def test_cancelled_policy_is_final(client, health_policy):
    url = f"/api/policies/{health_policy['id']}/status"
    assert client.patch(url, json={"status": "Cancelled"}).status_code == 200
    assert client.patch(url, json={"status": "Active"}).status_code == 409
