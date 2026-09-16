"""API tests for /api/policies (Lab 2 reference)."""


def test_issue_policy_from_quote(client, health_policy):
    assert health_policy["policy_number"].startswith("PD-HEALTH-2026-")
    assert health_policy["status"] == "Active"
    assert health_policy["start_date"] == "2026-01-01"
    assert health_policy["end_date"] == "2026-12-31"
    assert health_policy["premium"] == 15000.0


def test_two_year_policy_end_date(client, motor_policy):
    assert motor_policy["end_date"] == "2027-12-31"
    assert motor_policy["vehicle_registration"] == "TS09AB1234"


def test_quote_cannot_be_issued_twice(client, health_policy):
    r = client.post("/api/policies", json={"quote_id": health_policy["quote_id"], "start_date": "2026-02-01"})
    assert r.status_code == 409


def test_motor_policy_requires_vehicle(client, ids):
    q = client.post("/api/quotes", json={"customer_id": ids["customers"]["Rohan Das"],
                                          "product_id": ids["products"]["MOTOR"],
                                          "sum_insured": 300000, "tenure_years": 1}).json()
    r = client.post("/api/policies", json={"quote_id": q["id"], "start_date": "2026-01-01"})
    assert r.status_code == 422


def test_list_policies_filter_by_status(client, health_policy):
    client.patch(f"/api/policies/{health_policy['id']}/status", json={"status": "Lapsed"})
    assert len(client.get("/api/policies", params={"status_filter": "Active"}).json()) == 0
    assert len(client.get("/api/policies", params={"status_filter": "Lapsed"}).json()) == 1


def test_cancelled_policy_is_final(client, health_policy):
    client.patch(f"/api/policies/{health_policy['id']}/status", json={"status": "Cancelled"})
    r = client.patch(f"/api/policies/{health_policy['id']}/status", json={"status": "Active"})
    assert r.status_code == 409
