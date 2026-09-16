# Lab 3 Prompt Guide — The Claim feature

*60 minutes · Team of 3–4 · rotate roles · **tests first today***

## The problem statement you were given

> **Feature 3 — Claim:** *A customer files a claim on their policy — an amount, what happened, and when. The claim is only accepted if the policy allows it. A claims officer then reviews it with the full picture — the policy, how much cover is left, other claims — and approves or rejects it with a reason.*
>
> **Business rules**
>
> | # | Rule | Outcome when broken |
> |---|---|---|
> | 1 | The policy must be **Active** | **Cancelled** policy → the claim is *saved* with status **Rejected** and the reason "Policy is cancelled" · **Lapsed** policy → the request is *refused* (422) |
> | 2 | The incident date must be inside the policy period, **start and end dates inclusive** | 422 |
> | 3 | The amount must not exceed **remaining cover** = sum insured − claims already **Approved** on that policy (Filed / Under Review claims don't count) | 422 |
> | 4 | A **Motor** claim needs a vehicle registration number | 422 |
>
> **Workflow:** Filed → Under Review → Approved *or* Rejected. Filed → Rejected is also allowed. Approved and Rejected are final. An illegal move is a **409**. Approving more than the remaining cover is a **422**. A reason can be stored with any status change.
>
> **Acceptance criteria**
>
> 1. `POST /api/claims` → 201 (status Filed, or Rejected with reason for a cancelled policy); 404 unknown policy; 422 for rules 1 (lapsed), 2, 3, 4.
> 2. `PATCH /api/claims/{id}/status` follows the workflow; remaining cover shrinks after an approval.
> 3. The policy page's *File a claim* form works. `/claims/{id}` shows: claimed amount, remaining cover, within-cover yes/no; the claim; the policy context (customer, product, status, sum insured, other claims); and **only the actions allowed from the current status**, with a reason box. *Approve* is disabled when the amount exceeds remaining cover. Final states show a note instead of buttons.
> 4. Tests cover every rule, every boundary date, and the workflow — **written before the code**.

**Given:** `Claim` model, `ClaimValidationError(auto_reject=…)`, `approved_total()`, `remaining_cover()`, `ALLOWED_TRANSITIONS`, `can_transition()`, the list/get endpoints, the claim form on the policy page, the `POST /claims/{id}/status` form handler (accepts a hidden `back` field).
**You build:** `validate_claim` · `file_claim` · `update_claim_status` · `tests/test_claims.py` · the Claim review page + tests.

---

## Before the first prompt (2 min)

- Behind on Lab 2? `git stash && git checkout lab2-complete`.
- Open `app/services/claims.py` — rules in the docstring. Note what is **already there**: `remaining_cover()` and `ALLOWED_TRANSITIONS`. You call them; you don't rewrite them.
- Say out loud the difference between rule 1's two cases: *cancelled → saved as Rejected; lapsed → refused.* The AI will blur them.

---

## Part A — Tests first (12 min) · `tests/test_claims.py`

📎 `#file:tests/conftest.py` `#file:app/services/claims.py` `#file:app/routers/claims.py`
```
Write tests/test_claims.py BEFORE the implementation exists (everything will fail with 501 for now). Use the client, health_policy
(Active, Health, 5,00,000, 2026-01-01 → 2026-12-31) and motor_policy (Active, Motor, 2-year, vehicle TS09AB1234) fixtures.
Add a helper claim(client, policy, amount=50000, incident="2026-03-10", **extra) that POSTs /api/claims with policy_id, amount,
incident_date and description "Hospitalised after a fall" plus extra fields.
Tests, one behaviour each:
1. file on Active policy → 201, status "Filed"
2. incident "2026-01-01" → 201 and "2026-12-31" → 201 (boundaries inclusive); "2025-12-31" → 422 and "2027-01-01" → 422
3. amount 500001 → 422 and the detail mentions "remaining cover"
4. motor_policy without vehicle_registration → 422; with vehicle_registration="TS09AB1234" → 201
5. PATCH the policy to "Cancelled", then file → 201 with status "Rejected" and a reason containing "cancelled"
6. PATCH the policy to "Lapsed", then file → 422
7. workflow: file 300000 → PATCH status "Approved" → 409; PATCH "Under Review" → 200; PATCH "Approved" → 200;
   now file 200001 → 422 and file 200000 → 201; PATCH the first claim to "Rejected" → 409 (final)
8. PATCH to "Rejected" with reason "Pre-existing condition" → 200 and reason echoed back
9. GET /api/claims?policy_id=<health id> lists only that policy's claims
Plain asserts. No mocking.
```
▶ `pytest tests/test_claims.py -q` → **all fail with 501**. Correct.
🔍 Read test 2 with the Validator: does it really test the first *and* last day? Read test 7: does it check that Filed/Under-Review claims are *not* deducted (the 200001 → 422 line proves only the approved 3,00,000 counts)?
⚠️ The AI writes test 2 with only one boundary, or expects the cancelled-policy claim to be a 422 (it's a **201 + Rejected**).

**Checkpoint A (12')** — 9+ tests written, all red, team has read them. Commit `Lab 3A: tests`.

---

## Part B — The rules (13 min) · `app/services/claims.py`

📎 `#file:app/services/claims.py` `#file:app/models.py`
```
Implement validate_claim(session, policy, *, amount, incident_date, vehicle_registration) only, rules in this exact order:
1. if policy.status == PolicyStatus.CANCELLED: raise ClaimValidationError("Policy is cancelled", auto_reject=True)
   elif policy.status != PolicyStatus.ACTIVE: raise ClaimValidationError(f"Policy is {policy.status.value.lower()}, not active")
2. if not (policy.start_date <= incident_date <= policy.end_date): raise ClaimValidationError(f"Incident date must be between {policy.start_date} and {policy.end_date}")
3. remaining = remaining_cover(session, policy)  (already defined in this file — do NOT recompute it);
   if amount > remaining: raise ClaimValidationError(f"Claim exceeds remaining cover of {remaining:,.2f}")
4. if policy.product.code == ProductCode.MOTOR and not (vehicle_registration or "").strip(): raise ClaimValidationError("Motor claims need a vehicle registration number")
Return None otherwise. Only the function.
```
▶ Nothing to run yet at the API level (the router still returns 501) — test the function directly if you like, or go straight to Part C.
⚠️ `start < incident < end` (exclusive) · recomputes the cover by summing *all* claims · one `ClaimValidationError` for both cancelled and lapsed without `auto_reject`.

**Checkpoint B (25')** — function reads exactly like the four rules. Commit.

---

## Part C — The endpoints (12 min) · `app/routers/claims.py`

📎 `#file:app/routers/claims.py` `#file:app/services/claims.py`
```
Implement file_claim and update_claim_status only.
file_claim(payload, session): policy = session.get(Policy, payload.policy_id) → 404 "Policy not found" if None.
claim = Claim.model_validate(payload). try: claim_rules.validate_claim(session, policy, amount=payload.amount,
incident_date=payload.incident_date, vehicle_registration=payload.vehicle_registration)
except claim_rules.ClaimValidationError as exc: if not exc.auto_reject: raise HTTPException(422, str(exc)) from exc;
else: claim.status = ClaimStatus.REJECTED; claim.reason = str(exc)   # the claim IS SAVED in this case
Then add / commit / refresh / return claim.
update_claim_status(claim_id, payload, session): claim = session.get(Claim, claim_id) → 404 "Claim not found";
if not claim_rules.can_transition(claim.status, payload.status): raise HTTPException(status.HTTP_409_CONFLICT,
f"Cannot move a claim from {claim.status.value} to {payload.status.value}"); if payload.status == ClaimStatus.APPROVED:
remaining = claim_rules.remaining_cover(session, claim.policy); if claim.amount > remaining: raise HTTPException(422, f"Only {remaining:,.2f} cover remains");
claim.status = payload.status; claim.reason = payload.reason; add / commit / refresh / return.
```
▶ `pytest tests/test_claims.py -q`
🔍 All 9 green. If test 5 fails with 422: your `file_claim` raised on `auto_reject` instead of saving. If test 7's 200001 line fails: remaining cover is counting non-approved claims.
▶ UI: `/policies/1` → file a claim → it appears Filed. Change the policy to Cancelled → file another → appears **Rejected** with the reason.
⚠️ Raises for the cancelled case (most common) · forgets `from exc` · approves without the cover check.

**Checkpoint C (37')** — `test_claims.py` fully green; cancelled-policy claim visible as Rejected in the UI. Commit `Lab 3C`.

---

## Part D — Claim review page (20 min) · Scenario 3

Read *Student scenarios → Scenario 3*. Model page: `/policies/1`.

**D1 · Route** — 📎 `#file:app/routers/pages.py` `#file:app/services/claims.py` `#file:docs/scenarios.md`
```
Replace ONLY the body of claim_detail in pages.py with Scenario 3:
claim = session.get(Claim, claim_id); if None raise HTTPException(404, "Claim not found"). policy = claim.policy.
remaining = remaining_cover(session, policy).
next_states = [s for s in (ClaimStatus.UNDER_REVIEW, ClaimStatus.APPROVED, ClaimStatus.REJECTED) if s in ALLOWED_TRANSITIONS[claim.status]]
(ALLOWED_TRANSITIONS is already imported at the top of pages.py — do not redefine the rules here).
other_claims = [c for c in policy.claims if c.id != claim.id].
Render "claim_detail.html" with claim, policy, remaining, next_states, other_claims, flash=request.query_params.get("flash"), error=request.query_params.get("error").
```
⚠️ Hard-codes the allowed transitions in the route or the template instead of using `ALLOWED_TRANSITIONS`.

**D2 · Template** — 📎 `#file:app/templates/policy_detail.html` `#file:app/templates/_macros.html` `#file:docs/scenarios.md`
```
Write app/templates/claim_detail.html for Scenario 3 in the style of policy_detail.html. Start with {% from "_macros.html" import pill, alerts %}.
page-head: eyebrow "Claim review", h1 "Claim #{{ claim.id }}", p with customer name, policy number linking to /policies/{{ policy.id }} and pill(claim.status); a btn--ghost "← All claims" → /claims.
Then {{ alerts(flash=flash, error=error) }}.
grid--3 stat cards: Claimed {{ claim.amount|money }} · Remaining cover {{ remaining|money }} with hint "of {{ policy.sum_insured|money }}" · "Within cover?" Yes/No based on claim.amount <= remaining.
grid--side: left — Claim card (incident date with the policy period beside it, description, vehicle if any, filed time, status + reason) and Policy context card (customer link → /customers/{{ policy.customer_id }}, product with code pill, pill(policy.status), sum insured, other_claims as links → /claims/{{ c.id }} with amount and status pill, or "None");
right — Decision card: if next_states: the 3 workflow steps as .steps, then a form method="post" action="/claims/{{ claim.id }}/status" containing
<input type="hidden" name="back" value="/claims/{{ claim.id }}">, a textarea name="reason", and for each s in next_states a
<button name="status" value="{{ s.value }}"> labelled "Move to review" for Under Review else s.value, class btn--ok for Approved, btn--danger for Rejected, btn--primary otherwise;
add the attribute disabled when s.value == "Approved" and claim.amount > remaining. If next_states is empty: an alert--info saying the claim is in a final state. Complete file.
```
▶ File a fresh claim → open it from the Claims page.
🔍 Filed: buttons are **Move to review** and **Rejected** — *no Approve*. Click Move to review → back on the same page (the `back` field) → now **Approved** and **Rejected**. Approve with reason "Bills verified" → page shows *final state*, the reason, and **remaining cover reduced by the amount**. Claim over the remaining cover → Approve button disabled.
⚠️ Approve offered straight from Filed (template ignores `next_states`) · form posts without the `back` field → you land on the policy page instead · `claim.policy.customer.name` written as `claim.customer.name` (no such relationship).

**Checkpoint D (57')** — full review flow works from the page. 

---

## Part E — Page tests + ship (3 min)

📎 `#file:tests/test_pages.py` `#file:tests/conftest.py`
```
Add test_claim_review_page_and_workflow(client, health_policy): file a 50000 claim via POST /api/claims; GET /claims/{id} is 200,
contains the description, contains "Move to review" and 'value="Rejected"' but NOT 'value="Approved"';
POST /claims/{id}/status with data status="Under Review", back="/claims/{id}", follow_redirects=False → 303 to /claims/{id};
GET again now contains 'value="Approved"'; POST status="Approved", reason="Bills verified" → GET shows "final state", "Bills verified" and "₹4,50,000.00".
Add test_claim_review_unknown_404(client): /claims/999 → 404. Remove the "/claims/1" placeholder assertion.
```
▶ `pytest -q` → green. `git commit -m "Lab 3: claim feature" && git push` — this push is your deployment in the next session.

---

## Before you commit — the review prompt (2 min)

📎 `#file:app/services/claims.py` `#file:app/routers/claims.py` `#file:app/routers/pages.py`
```
Review the claim feature. Report only real problems: 1. Are both incident-date boundaries inclusive? 2. Is remaining cover
computed only from Approved claims, and only via remaining_cover()? 3. On a cancelled policy is the claim SAVED as Rejected
(not raised)? 4. Are the allowed transitions defined in exactly one place (ALLOWED_TRANSITIONS) and used by both the router and the page?
5. Can Approve be reached from Filed anywhere?
```

## Done when

- [ ] `pytest -q` green — 9+ claim tests, 2 page tests
- [ ] UI: file → review → approve with reason → remaining cover drops · cancelled policy → Rejected claim with reason
- [ ] Review page never offers an illegal action
- [ ] AI log ≥ 3 rows total
- [ ] Pushed

## Your AI log — rows we expect from this lab

| Lab | Asked | AI got wrong | Caught by | Fix |
|---|---|---|---|---|
| 3B | validate_claim | `start < incident < end` | boundary tests (test 2) | `<=` both sides |
| 3B | validate_claim | summed all claims for cover | test 7: 200001 → 422 failed | call `remaining_cover()` |
| 3C | file_claim | raised 422 on cancelled policy | test 5 expected 201 + Rejected | save with status Rejected |
| 3D | template | Approve shown from Filed | opened a fresh claim | loop over `next_states` |
