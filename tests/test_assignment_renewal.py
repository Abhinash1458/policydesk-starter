"""Assignment — renew a policy with a no-claim bonus: POST /api/policies/{id}/renewal-quote

Take-home, after Labs 1-4 (it re-uses the calculator, issue_policy and the claims workflow).
Run just these:  pytest -m assignment -v
"""
from datetime import date, timedelta

import pytest

from app.models import ProductCode
from app.services import pricing

pytestmark = [pytest.mark.lab, pytest.mark.assignment]


def full_price(client, policy, tenure, add_ons=""):
    """What Lab 1's calculator charges for the same cover today — the renewal price before any bonus."""
    product = client.get(f"/api/products/{policy['product_id']}").json()
    customer = next(c for c in client.get("/api/customers").json() if c["id"] == policy["customer_id"])
    return pricing.calculate_premium(
        sum_insured=policy["sum_insured"], base_rate=product["base_rate"],
        age=pricing.age_on(date.fromisoformat(customer["date_of_birth"])), tenure_years=tenure,
        product=ProductCode(product["code"]), add_ons=pricing.parse_add_ons(add_ons),
        min_sum_insured=product["min_sum_insured"], max_sum_insured=product["max_sum_insured"],
    )


def with_bonus(amount):
    return max(pricing.MIN_PREMIUM, round(amount * 0.90, 2))


def renew(client, policy_id):
    return client.post(f"/api/policies/{policy_id}/renewal-quote")


def file_claim(client, policy, amount=10000, **extra):
    payload = {"policy_id": policy["id"], "amount": amount, "description": "Claim for the renewal test",
               "incident_date": "2026-06-10", **extra}
    return client.post("/api/claims", json=payload).json()["id"]


def move(client, claim_id, *statuses):
    for s in statuses:
        client.patch(f"/api/claims/{claim_id}/status", json={"status": s})


def test_no_claims_earns_the_ten_percent_bonus(client, health_policy):
    r = renew(client, health_policy["id"])
    assert r.status_code == 201
    assert r.json()["premium"] == pytest.approx(with_bonus(full_price(client, health_policy, 1)))


def test_an_approved_claim_loses_the_bonus(client, health_policy):
    move(client, file_claim(client, health_policy), "Under Review", "Approved")
    r = renew(client, health_policy["id"])
    assert r.json()["premium"] == pytest.approx(full_price(client, health_policy, 1))


def test_filed_or_rejected_claims_keep_the_bonus(client, motor_policy):
    move(client, file_claim(client, motor_policy, vehicle_registration="TS09AB1234"), "Rejected")
    file_claim(client, motor_policy, vehicle_registration="TS09AB1234")            # still Filed
    r = renew(client, motor_policy["id"])
    assert r.json()["premium"] == pytest.approx(with_bonus(full_price(client, motor_policy, 2, "ZERO_DEPRECIATION")))


def test_renewal_quote_keeps_the_same_cover(client, motor_policy):
    q = renew(client, motor_policy["id"]).json()
    assert q["customer_id"] == motor_policy["customer_id"] and q["product_id"] == motor_policy["product_id"]
    assert q["sum_insured"] == motor_policy["sum_insured"]
    assert q["tenure_years"] == 2 and q["add_ons"] == "ZERO_DEPRECIATION"
    assert client.get(f"/api/quotes/{q['id']}").status_code == 200        # a normal, saved quote


def test_only_active_policies_can_be_renewed(client, health_policy, motor_policy):
    assert renew(client, 999).status_code == 404
    client.patch(f"/api/policies/{health_policy['id']}/status", json={"status": "Lapsed"})
    assert renew(client, health_policy["id"]).status_code == 409
    client.patch(f"/api/policies/{motor_policy['id']}/status", json={"status": "Cancelled"})
    assert renew(client, motor_policy["id"]).status_code == 409


def test_renewal_quote_can_be_issued_from_the_day_after_expiry(client, health_policy):
    q = renew(client, health_policy["id"]).json()
    start = date.fromisoformat(health_policy["end_date"]) + timedelta(days=1)
    r = client.post("/api/policies", json={"quote_id": q["id"], "start_date": start.isoformat()})
    assert r.status_code == 201
    assert r.json()["start_date"] == "2027-01-01" and r.json()["end_date"] == "2027-12-31"
