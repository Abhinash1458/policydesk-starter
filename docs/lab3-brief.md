# Lab 3 brief — the Claim feature

**Time:** 60 minutes (Day 2) · **Team:** 3–4 · **Deliverable:** claims API + Claim review page, tested, pushed (deployed in the next session)

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

1. **Model** — add `Claim` to `app/models.py` (5 min)
2. **Rules** — write `validate_claim()` in `app/services/claims.py` as a pure function *first*, tests alongside (15 min)
3. **Endpoints** — `app/routers/claims.py`, thin: look up policy → call the service → save (10 min)
4. **Screen** — form + table in `policy_detail.html` (7 min)
5. **Deploy + demo prep** (3 min)

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
