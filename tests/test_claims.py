"""Lab 3 — claim rules, filing and the status workflow."""
import pytest

pytestmark = pytest.mark.regression


def claim_for(policy, **overrides):
    payload = {"policy_id": policy["id"], "amount": 50000, "description": "Hospitalised for three days",
               "incident_date": "2026-03-10"}
    payload.update(overrides)
    return payload


# ---- filing ---------------------------------------------------------------------

def test_valid_claim_is_filed(client, health_policy):
    r = client.post("/api/claims", json=claim_for(health_policy))
    assert r.status_code == 201
    assert r.json()["status"] == "Filed"


def test_unknown_policy_is_404(client):
    assert client.post("/api/claims", json=claim_for({"id": 999})).status_code == 404


def test_incident_outside_policy_period_is_422(client, health_policy):
    r = client.post("/api/claims", json=claim_for(health_policy, incident_date="2027-01-15"))
    assert r.status_code == 422 and "policy period" in r.json()["detail"]


def test_amount_above_remaining_cover_is_422(client, health_policy):
    r = client.post("/api/claims", json=claim_for(health_policy, amount=600000))
    assert r.status_code == 422 and "remaining cover" in r.json()["detail"]


def test_motor_claim_needs_vehicle_registration(client, motor_policy):
    payload = claim_for(motor_policy, description="Rear-ended at a signal")
    assert client.post("/api/claims", json=payload).status_code == 422
    payload["vehicle_registration"] = "TS09AB1234"
    assert client.post("/api/claims", json=payload).status_code == 201


def test_lapsed_policy_refuses_claim(client, health_policy):
    client.patch(f"/api/policies/{health_policy['id']}/status", json={"status": "Lapsed"})
    assert client.post("/api/claims", json=claim_for(health_policy)).status_code == 422


def test_cancelled_policy_auto_rejects_claim(client, health_policy):
    client.patch(f"/api/policies/{health_policy['id']}/status", json={"status": "Cancelled"})
    r = client.post("/api/claims", json=claim_for(health_policy))
    assert r.status_code == 201
    assert r.json()["status"] == "Rejected"
    assert "cancelled" in r.json()["reason"].lower()


# ---- workflow -------------------------------------------------------------------

def test_happy_path_filed_review_approved(client, health_policy):
    cid = client.post("/api/claims", json=claim_for(health_policy)).json()["id"]
    assert client.patch(f"/api/claims/{cid}/status", json={"status": "Under Review"}).json()["status"] == "Under Review"
    r = client.patch(f"/api/claims/{cid}/status", json={"status": "Approved", "reason": "Bills verified"})
    assert r.json()["status"] == "Approved" and r.json()["reason"] == "Bills verified"


def test_illegal_transitions_are_409(client, health_policy):
    cid = client.post("/api/claims", json=claim_for(health_policy)).json()["id"]
    assert client.patch(f"/api/claims/{cid}/status", json={"status": "Approved"}).status_code == 409   # skip review
    client.patch(f"/api/claims/{cid}/status", json={"status": "Rejected", "reason": "Not covered"})
    assert client.patch(f"/api/claims/{cid}/status", json={"status": "Under Review"}).status_code == 409  # final
    assert client.patch("/api/claims/999/status", json={"status": "Under Review"}).status_code == 404


def test_approved_claims_reduce_remaining_cover(client, health_policy):
    first = client.post("/api/claims", json=claim_for(health_policy, amount=400000)).json()["id"]
    client.patch(f"/api/claims/{first}/status", json={"status": "Under Review"})
    client.patch(f"/api/claims/{first}/status", json={"status": "Approved"})
    # only 1,00,000 of cover is left now
    assert client.post("/api/claims", json=claim_for(health_policy, amount=150000)).status_code == 422
    second = client.post("/api/claims", json=claim_for(health_policy, amount=100000)).json()["id"]
    client.patch(f"/api/claims/{second}/status", json={"status": "Under Review"})
    assert client.patch(f"/api/claims/{second}/status", json={"status": "Approved"}).status_code == 200


def test_approval_above_remaining_cover_is_422(client, health_policy):
    a = client.post("/api/claims", json=claim_for(health_policy, amount=300000)).json()["id"]
    b = client.post("/api/claims", json=claim_for(health_policy, amount=300000)).json()["id"]   # both fit when filed
    for cid in (a, b):
        client.patch(f"/api/claims/{cid}/status", json={"status": "Under Review"})
    assert client.patch(f"/api/claims/{a}/status", json={"status": "Approved"}).status_code == 200
    assert client.patch(f"/api/claims/{b}/status", json={"status": "Approved"}).status_code == 422   # only 2,00,000 left


def test_list_claims_filters_by_policy(client, health_policy, motor_policy):
    client.post("/api/claims", json=claim_for(health_policy))
    client.post("/api/claims", json=claim_for(motor_policy, vehicle_registration="TS09AB1234"))
    assert len(client.get("/api/claims").json()) == 2
    assert len(client.get(f"/api/claims?policy_id={motor_policy['id']}").json()) == 1
