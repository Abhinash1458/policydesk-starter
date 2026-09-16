"""HTML screen tests. Add one test per scenario as you build it (docs/scenarios.md)."""


def test_given_pages_render(client):
    for path in ["/", "/customers", "/products", "/quotes/new", "/policies", "/claims"]:
        r = client.get(path)
        assert r.status_code == 200, path
        assert "PolicyDesk" in r.text


def test_student_pages_are_placeholders_until_built(client):
    # These pass until each scenario is done — then REPLACE the line with a real test.
    assert "not built yet" in client.get("/claims/1").text        # Scenario 3 (Lab 3)


# ---- Scenario 1: quotes list (Lab 1) ------------------------------------------
def test_quotes_list_open_and_product_filter(client, ids):
    health_q = client.post("/api/quotes", json={"customer_id": ids["customers"]["Priya Nair"],
                                                "product_id": ids["products"]["HEALTH"],
                                                "sum_insured": 500000, "tenure_years": 1}).json()
    motor_q = client.post("/api/quotes", json={"customer_id": ids["customers"]["Rohan Das"],
                                               "product_id": ids["products"]["MOTOR"],
                                               "sum_insured": 300000, "tenure_years": 1}).json()
    r = client.get("/quotes")
    assert r.status_code == 200 and "2 shown" in r.text and "Open" in r.text

    assert f'href="/quotes/{motor_q["id"]}"' in client.get("/quotes?status=open").text
    assert f'href="/quotes/{motor_q["id"]}"' not in client.get("/quotes?status=converted").text
    motor_only = client.get("/quotes?product=MOTOR").text
    assert f'href="/quotes/{motor_q["id"]}"' in motor_only
    assert f'href="/quotes/{health_q["id"]}"' not in motor_only


# ---- Scenario 2: customer 360 (Lab 2) ------------------------------------------
def test_customer_360_lists_policies(client, health_policy):
    r = client.get(f"/customers/{health_policy['customer_id']}")
    assert r.status_code == 200
    assert "Priya Nair" in r.text
    assert health_policy["policy_number"] in r.text
    assert "₹15,000.00" in r.text  # annual premium total


def test_customer_360_empty_customer_and_404(client, ids):
    assert client.get(f"/customers/{ids['customers']['Rohan Das']}").status_code == 200
    assert client.get("/customers/999").status_code == 404


# TODO (Lab 3, Scenario 3): test_claim_review_page_and_workflow          +  unknown id -> 404
