"""Lab 4 — approve / reject: the review workflow API and the Approve / Reject buttons on the Claims page.

Part A (6 tests): the API you build with your OWN prompt. Part B (2 tests): the buttons on the Claims page.
They fail until each part is done. Needs Lab 3 (claims are filed through POST /api/claims).
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


def test_reason_is_stored_and_kept_when_a_later_move_has_none(client, health_policy):
    c = client.post("/api/claims", json=claim_for(health_policy)).json()
    r = client.patch(f"/api/claims/{c['id']}/status", json={"status": "Rejected", "reason": "Pre-existing condition"})
    assert r.status_code == 200 and r.json()["reason"] == "Pre-existing condition"
    assert client.get(f"/api/claims/{c['id']}").json()["status"] == "Rejected"

    d = client.post("/api/claims", json=claim_for(health_policy, amount=10000)).json()
    client.patch(f"/api/claims/{d['id']}/status", json={"status": "Under Review", "reason": "Bills requested"})
    r = client.patch(f"/api/claims/{d['id']}/status", json={"status": "Approved"})          # no reason this time
    assert r.json()["reason"] == "Bills requested"


# ---- Part B: the buttons on the Claims page ----------------------------------------

def test_claims_page_shows_only_the_allowed_buttons(client, health_policy):
    cid = client.post("/api/claims", json=claim_for(health_policy)).json()["id"]
    page = client.get("/claims").text
    assert f'action="/claims/{cid}/status"' in page
    assert 'value="Under Review"' in page and 'value="Rejected"' in page and 'value="Approved"' not in page

    client.patch(f"/api/claims/{cid}/status", json={"status": "Under Review"})
    page = client.get("/claims").text
    assert 'value="Approved"' in page and 'value="Under Review"' not in page

    client.patch(f"/api/claims/{cid}/status", json={"status": "Approved"})
    page = client.get("/claims").text
    assert f'action="/claims/{cid}/status"' not in page and "Final" in page


def test_claims_page_buttons_move_the_claim_and_explain_refusals(client, health_policy):
    cid = client.post("/api/claims", json=claim_for(health_policy)).json()["id"]

    r = client.post(f"/claims/{cid}/status", data={"status": "Approved"}, follow_redirects=False)  # skips review
    assert r.status_code == 303 and "error=" in r.headers["location"]
    assert "alert--bad" in client.get(r.headers["location"]).text
    assert client.get(f"/api/claims/{cid}").json()["status"] == "Filed"

    r = client.post(f"/claims/{cid}/status", data={"status": "Under Review", "reason": ""}, follow_redirects=False)
    assert r.status_code == 303 and "flash=" in r.headers["location"]
    client.post(f"/claims/{cid}/status", data={"status": "Approved", "reason": "Bills verified"})
    assert client.get(f"/api/claims/{cid}").json()["status"] == "Approved"
    assert "Bills verified" in client.get("/claims").text
