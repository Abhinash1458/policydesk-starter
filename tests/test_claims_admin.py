"""Phase 3 — admin approval: review queue and status workflow. Acceptance tests for YOUR prompt.

These are the acceptance tests for the feature you build with your OWN prompt. They fail until it is done.
"""
import pytest

pytestmark = pytest.mark.lab


def claim_for(policy, **overrides):
    payload = {"policy_id": policy["id"], "amount": 50000, "description": "Hospitalised for three days",
               "incident_date": "2026-03-10"}
    payload.update(overrides)
    return payload


# ---- filing ---------------------------------------------------------------------

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




def test_admin_queue_filters_by_status(client, health_policy):
    a = client.post("/api/claims", json=claim_for(health_policy, amount=10000)).json()
    b = client.post("/api/claims", json=claim_for(health_policy, amount=20000)).json()
    client.patch(f"/api/claims/{b['id']}/status", json={"status": "Under Review"})
    queue = client.get("/api/claims", params={"status": "Filed"}).json()
    assert [c["id"] for c in queue] == [a["id"]]
    assert [c["id"] for c in client.get("/api/claims", params={"status": "Under Review"}).json()] == [b["id"]]


def test_reason_is_stored_with_decision(client, health_policy):
    c = client.post("/api/claims", json=claim_for(health_policy)).json()
    r = client.patch(f"/api/claims/{c['id']}/status", json={"status": "Rejected", "reason": "Pre-existing condition"})
    assert r.status_code == 200 and r.json()["reason"] == "Pre-existing condition"
    assert client.get(f"/api/claims/{c['id']}").json()["status"] == "Rejected"
