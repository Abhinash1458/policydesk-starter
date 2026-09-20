"""HTML screen tests — the given pages plus the three student scenarios (solution)."""
import pytest

pytestmark = pytest.mark.regression


def test_given_pages_render(client):
    for path in ["/", "/customers", "/products", "/quotes/new", "/policies", "/claims"]:
        r = client.get(path)
        assert r.status_code == 200, path
        assert "PolicyDesk" in r.text


# ---- Scenario 1: quotes list ----------------------------------------------------

def test_quotes_list_shows_open_and_converted(client, ids, health_policy):
    open_quote = client.post("/api/quotes", json={
        "customer_id": ids["customers"]["Rohan Das"], "product_id": ids["products"]["TERM_LIFE"],
        "sum_insured": 1000000, "tenure_years": 1,
    }).json()
    page = client.get("/quotes").text
    assert "3 shown" in page and "1 still open" in page   # 2 seeded (converted) + 1 new open quote
    assert "Issue policy" in page and "View policy" in page

    open_page = client.get("/quotes?status=open").text
    assert f'href="/quotes/{open_quote["id"]}"' in open_page
    assert health_policy["policy_number"] not in open_page and "View policy" not in open_page

    converted_page = client.get("/quotes?status=converted").text
    assert "View policy" in converted_page and "Issue policy" not in converted_page

    assert "1 shown" in client.get("/quotes?product=TERM_LIFE").text
    assert "No quotes" in client.get("/quotes?product=TERM_LIFE&status=converted").text   # seeded quotes are Health + Motor


# ---- Scenario 2: customer 360 ---------------------------------------------------

def test_customer_360_shows_policies_claims_and_premium_total(client, ids, health_policy):
    client.post("/api/claims", json={"policy_id": health_policy["id"], "amount": 20000,
                                     "description": "Day-care procedure", "incident_date": "2026-05-05"})
    page = client.get(f"/customers/{ids['customers']['Priya Nair']}").text
    assert "Priya Nair" in page
    assert health_policy["policy_number"] in page
    assert "15,000.00" in page                     # premium total
    assert "Day-care" not in page and "20,000.00" in page   # claims table shows amount, not description
    assert f'/quotes/new?customer_id={ids["customers"]["Priya Nair"]}' in page


def test_customer_360_with_no_policies_and_unknown_id(client, ids):
    # A brand-new customer has nothing yet — the page must still render.
    new = client.post("/api/customers", json={"name": "Meera Joshi", "email": "meera.joshi@example.com",
                                              "phone": "9700011122", "date_of_birth": "1984-03-09"}).json()
    page = client.get(f"/customers/{new['id']}")
    assert page.status_code == 200 and "No policies yet" in page.text
    assert client.get("/customers/999").status_code == 404


# ---- Scenario 3: claim review ---------------------------------------------------

def test_claim_review_offers_only_allowed_actions(client, health_policy):
    cid = client.post("/api/claims", json={"policy_id": health_policy["id"], "amount": 50000,
                                           "description": "Hospitalised for three days",
                                           "incident_date": "2026-03-10"}).json()["id"]
    page = client.get(f"/claims/{cid}").text
    assert "Move to review" in page and "Reject" in page
    assert 'value="Approved"' not in page                     # cannot approve straight from Filed

    r = client.post(f"/claims/{cid}/status", data={"status": "Under Review", "back": f"/claims/{cid}"}, follow_redirects=False)
    assert r.headers["location"].startswith(f"/claims/{cid}")
    page = client.get(f"/claims/{cid}").text
    assert 'value="Approved"' in page and "Move to review" not in page

    client.post(f"/claims/{cid}/status", data={"status": "Approved", "reason": "Bills verified", "back": f"/claims/{cid}"})
    page = client.get(f"/claims/{cid}").text
    assert "final state" in page and "Bills verified" in page


def test_claim_review_disables_approve_when_over_cover(client, health_policy):
    a = client.post("/api/claims", json={"policy_id": health_policy["id"], "amount": 300000,
                                         "description": "Surgery and stay", "incident_date": "2026-03-10"}).json()["id"]
    b = client.post("/api/claims", json={"policy_id": health_policy["id"], "amount": 300000,
                                         "description": "Follow-up surgery", "incident_date": "2026-04-10"}).json()["id"]
    for cid in (a, b):
        client.patch(f"/api/claims/{cid}/status", json={"status": "Under Review"})
    client.patch(f"/api/claims/{a}/status", json={"status": "Approved"})
    page = client.get(f"/claims/{b}").text
    assert "Within cover?" in page and ">No<" in page
    assert 'value="Approved" disabled' in page
    assert client.get("/claims/999").status_code == 404
