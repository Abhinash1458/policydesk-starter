# Final project brief — the Claims module

**Time:** 40 minutes (Day 2, 11:10–11:50) · **Team:** 3–4 · **Deliverable:** deployed URL + demo

## The ask

Customers with an **Active** policy must be able to **file a claim** and track its **status**. An
operator must be able to move the claim through **Filed → Under Review → Approved / Rejected**.

### Business rules (from the product owner)

1. Only Active policies can have claims. A claim on a **Cancelled** policy is recorded but auto-rejected with a reason.
2. The incident date must fall within the policy's start and end dates.
3. A claim cannot exceed the **remaining cover** = sum insured − claims already approved on that policy.
4. **Motor** claims must include a vehicle registration number.
5. Approved and Rejected are final.

### Done when

- [ ] `POST /api/claims` and `PATCH /api/claims/{id}/status` behave per the rules (check in `/docs`)
- [ ] The policy detail screen has a "File a claim" form and shows claims with Review / Approve / Reject actions
- [ ] `/claims` lists all claims, filterable by status
- [ ] `tests/test_claims.py` covers each rule — and passes
- [ ] Deployed to Render, URL in the demo

### Suggested order

1. **Read** — `Claim` in `app/models.py` and the claim form in `policy_detail.html` are given; read them with Copilot "explain" (3 min)
2. **Rules** — write `validate_claim()` in `app/services/claims.py` *first*, tests alongside in `tests/test_claims.py` (17 min)
3. **Endpoints** — `file_claim` and `update_claim_status` in `app/routers/claims.py`, thin: look up policy → call the service → save (8 min)
4. **Scenario 3 — Claim review page** `/claims/{id}` per `docs/scenarios.md` (9 min)
5. **Run it** — file a claim from the policy screen; open it; Review → Approve; check remaining cover drops (2 min)
6. **Deploy + demo prep** (1 min — you deployed in Lab 7, just push)

### Prompts that work

- "Here are the 5 claim rules and our `Policy` model. Write `validate_claim(session, policy, amount, incident_date, vehicle_registration)` that raises `ClaimValidationError` with a clear message. Then write parametrized pytest tests for every rule, including one boundary case each."
- "Here is my router. Review it: is any business logic that belongs in the service layer leaking into the router?"

### Validate the AI

Watch for these — the AI usually gets at least one wrong:
- Off-by-one on the policy period (is the end date inclusive?)
- Counting **Filed** or **Under Review** claims as if they were approved when computing remaining cover
- Returning 400 instead of 422, or 200 instead of 201
- Forgetting that a cancelled-policy claim must be **saved** as Rejected, not refused

Record what it got wrong in `docs/ai-log.md` — that's 20% of your score.
