"""Lab 2 — policies API."""
import pytest

pytestmark = pytest.mark.regression


def test_issue_policy_copies_quote_and_computes_period(client, health_policy):
    assert health_policy["policy_number"].startswith("PD-HEALTH-2026-")
    assert health_policy["sum_insured"] == 500000
    assert health_policy["premium"] == 15000.0
    assert health_policy["start_date"] == "2026-01-01"
    assert health_policy["end_date"] == "2026-12-31"           # 365 days - 1
    assert health_policy["status"] == "Active"


def test_two_year_motor_policy_ends_after_730_days(client, motor_policy):
    assert motor_policy["policy_number"].startswith("PD-MOTOR-2026-")
    assert motor_policy["end_date"] == "2027-12-31"
    assert motor_policy["vehicle_registration"] == "TS09AB1234"


def test_policy_numbers_are_sequential(client, health_policy, motor_policy):
    assert health_policy["policy_number"].endswith("-00001")
    assert motor_policy["policy_number"].endswith("-00002")


def test_unknown_quote_is_404(client):
    assert client.post("/api/policies", json={"quote_id": 999, "start_date": "2026-01-01"}).status_code == 404


def test_issuing_the_same_quote_twice_is_409(client, health_policy):
    r = client.post("/api/policies", json={"quote_id": health_policy["quote_id"], "start_date": "2026-02-01"})
    assert r.status_code == 409


def test_motor_without_registration_is_422(client, ids):
    q = client.post("/api/quotes", json={
        "customer_id": ids["customers"]["Rohan Das"], "product_id": ids["products"]["MOTOR"],
        "sum_insured": 300000, "tenure_years": 1,
    }).json()
    r = client.post("/api/policies", json={"quote_id": q["id"], "start_date": "2026-01-01"})
    assert r.status_code == 422


def test_status_update_and_cancelled_is_final(client, health_policy):
    pid = health_policy["id"]
    assert client.patch(f"/api/policies/{pid}/status", json={"status": "Lapsed"}).json()["status"] == "Lapsed"
    assert client.patch(f"/api/policies/{pid}/status", json={"status": "Cancelled"}).json()["status"] == "Cancelled"
    assert client.patch(f"/api/policies/{pid}/status", json={"status": "Active"}).status_code == 409
    assert client.patch("/api/policies/999/status", json={"status": "Active"}).status_code == 404


def test_list_filters_by_status(client, health_policy, motor_policy):
    client.patch(f"/api/policies/{motor_policy['id']}/status", json={"status": "Lapsed"})
    assert len(client.get("/api/policies").json()) == 2
    lapsed = client.get("/api/policies?status_filter=Lapsed").json()
    assert [p["id"] for p in lapsed] == [motor_policy["id"]]
