"""HTML screen tests. The given pages are covered; add one test per scenario as you build it (docs/scenarios.md)."""


def test_given_pages_render(client):
    for path in ["/", "/customers", "/products", "/quotes/new", "/policies", "/claims"]:
        r = client.get(path)
        assert r.status_code == 200, path
        assert "PolicyDesk" in r.text


def test_student_pages_are_placeholders_until_built(client):
    # These pass on the starter and should be REPLACED by real tests once each scenario is done.
    assert "not built yet" in client.get("/quotes").text          # Scenario 1
    assert "not built yet" in client.get("/customers/1").text     # Scenario 2
    assert "not built yet" in client.get("/claims/1").text        # Scenario 3


# TODO (Scenario 1): test_quotes_list_shows_open_and_converted
# TODO (Scenario 2): test_customer_360_lists_policies_and_claims  +  unknown id -> 404
# TODO (Scenario 3): test_claim_review_page_and_workflow          +  unknown id -> 404
