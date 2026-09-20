"""Phase 2, Examples 1–3 — the Claim model and POST /api/claims with its four rules. Fail on the starter by design."""
import pytest

from app.models import Policy, PolicyStatus

pytestmark = pytest.mark.lab


def claim_for(policy, **overrides):
    payload = {"policy_id": policy["id"], "amount": 50000, "description": "Hospitalised for three days",
               "incident_date": "2026-03-10"}
    payload.update(overrides)
    return payload


# ---- filing ---------------------------------------------------------------------

def set_policy_status(session, policy_id, new_status):
    """Change a policy's status straight in the database (the PATCH endpoint is a Day 2 lab)."""
    policy = session.get(Policy, policy_id)
    policy.status = new_status
    session.add(policy)
    session.commit()


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


def test_lapsed_policy_refuses_claim(client, session, health_policy):
    set_policy_status(session, health_policy["id"], PolicyStatus.LAPSED)
    assert client.post("/api/claims", json=claim_for(health_policy)).status_code == 422


def test_cancelled_policy_auto_rejects_claim(client, session, health_policy):
    set_policy_status(session, health_policy["id"], PolicyStatus.CANCELLED)
    r = client.post("/api/claims", json=claim_for(health_policy))
    assert r.status_code == 201
    assert r.json()["status"] == "Rejected"
    assert "cancelled" in r.json()["reason"].lower()


# ---- workflow -------------------------------------------------------------------

def test_list_claims_filters_by_policy(client, health_policy, motor_policy):
    client.post("/api/claims", json=claim_for(health_policy))
    client.post("/api/claims", json=claim_for(motor_policy, vehicle_registration="TS09AB1234"))
    assert len(client.get("/api/claims").json()) == 2
    assert len(client.get(f"/api/claims?policy_id={motor_policy['id']}").json()) == 1
