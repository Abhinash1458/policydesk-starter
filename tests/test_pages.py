"""HTML screen tests. The given pages are covered; add one test per scenario as you build it (docs/scenarios.md)."""


def test_given_pages_render(client):
    for path in ["/", "/customers", "/products", "/quotes/new", "/policies", "/claims"]:
        r = client.get(path)
        assert r.status_code == 200, path
        assert "PolicyDesk" in r.text


def test_student_pages_are_placeholders_until_built(client):
    # These pass on the starter and should be REPLACED by real tests once each scenario is done.
    assert "not built yet" in client.get("/quotes").text          # Scenario 1
    assert "not built yet" in client.get("/claims/1").text        # Scenario 3


# Scenario 2 — Customer 360
def test_customer_360_lists_policies(client, health_policy):
    r = client.get(f"/customers/{health_policy['customer_id']}")
    assert r.status_code == 200
    assert "Priya Nair" in r.text
    assert health_policy["policy_number"] in r.text
    assert "₹15,000.00" in r.text
    assert "New quote for Priya" in r.text


def test_customer_360_excludes_cancelled_premium(client, health_policy):
    client.patch(f"/api/policies/{health_policy['id']}/status", json={"status": "Cancelled"})
    r = client.get(f"/customers/{health_policy['customer_id']}")
    assert r.status_code == 200
    assert "₹0.00" in r.text
    assert "0 active" in r.text


def test_customer_360_empty_customer_and_404(client, ids):
    r = client.get(f"/customers/{ids['customers']['Rohan Das']}")
    assert r.status_code == 200
    assert "Rohan Das" in r.text
    assert "No policies yet." in r.text
    assert client.get("/customers/999").status_code == 404


# TODO (Scenario 1): test_quotes_list_shows_open_and_converted
# TODO (Scenario 3): test_claim_review_page_and_workflow          +  unknown id -> 404
