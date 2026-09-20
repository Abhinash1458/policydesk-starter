"""HTML screen tests that create new quotes — they pass once the premium calculator (Phase 2, Example 4) is done."""
import pytest

pytestmark = pytest.mark.lab


def test_given_pages_render(client):
    for path in ["/", "/customers", "/products", "/quotes/new", "/policies"]:
        r = client.get(path)
        assert r.status_code == 200, path
        assert "PolicyDesk" in r.text


# ---- Quotes list --------------------------------------------------------------------

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


# ---- Customer 360 -------------------------------------------------------------------

def test_customer_360_shows_policies_and_premium_total(client, ids, health_policy):
    page = client.get(f"/customers/{ids['customers']['Priya Nair']}").text
    assert "Priya Nair" in page
    assert health_policy["policy_number"] in page
    assert "15,000.00" in page                     # premium total
    assert f'/quotes/new?customer_id={ids["customers"]["Priya Nair"]}' in page


def test_customer_360_with_no_policies_and_unknown_id(client, ids):
    # A brand-new customer has nothing yet — the page must still render.
    new = client.post("/api/customers", json={"name": "Meera Joshi", "email": "meera.joshi@example.com",
                                              "phone": "9700011122", "date_of_birth": "1984-03-09"}).json()
    page = client.get(f"/customers/{new['id']}")
    assert page.status_code == 200 and "No policies yet" in page.text
    assert client.get("/customers/999").status_code == 404
