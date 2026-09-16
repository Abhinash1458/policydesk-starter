# Lab 2 Prompt Guide — The Policy feature

*60 minutes · Team of 3–4 · rotate roles from Lab 1*

## The problem statement you were given

> **Feature 2 — Policy:** *Once a customer accepts a quote, the agent issues a policy from it. A policy has a number, a start and end date, and a status. The agent can lapse or cancel a policy. For a customer on the phone, the agent needs one page with everything about them — quotes, policies and claims.*
>
> **Business rules**
>
> | Rule | Detail |
> |---|---|
> | One policy per quote | Issuing a quote that already has a policy is a **conflict (409)** |
> | Policy number | `PD-<PRODUCT CODE>-<start year>-<5-digit sequence>`, e.g. `PD-MOTOR-2026-00007` |
> | Period | `end_date = start_date + 365 × tenure_years days − 1 day` (a 1-year policy from 1 Jan ends 31 Dec) |
> | Motor needs a vehicle | A Motor policy without a vehicle registration is **invalid (422)**; store it upper-cased |
> | Copy from the quote | customer, product, sum insured and premium come from the quote — never from the request |
> | Status | Active (default) → Lapsed or Cancelled. **Cancelled is final**: any further change is a **409** |
>
> **Acceptance criteria**
>
> 1. `POST /api/policies` with a quote id and start date → **201** with `policy_number`, `end_date`, status Active; 404 unknown quote; 409 already issued; 422 Motor without vehicle.
> 2. `PATCH /api/policies/{id}/status` changes status; 409 once Cancelled.
> 3. The quote page's *Issue policy* button works; the policy page opens with the right period.
> 4. `/customers/{id}` shows the customer's profile, four totals (quotes, policies + active count, annual premium excluding cancelled, claims), their policies, claims and quotes, and a *New quote for <name>* button that pre-selects them. Unknown id → 404. A customer with nothing yet must still render.
> 5. Tests cover each rule — including the **2-year end date**.

**Given:** `Policy` model, `next_policy_number()`, the list/get endpoints, the quote page's issue form, the policy detail page, `PolicyStatusUpdate`.
**You build:** `issue_policy` · `update_policy_status` · `tests/test_policies.py` · the Customer 360 page + its tests.

---

## Before the first prompt (2 min)

- Behind on Lab 1? `git stash && git checkout lab1-complete` — now, not later.
- Open `app/routers/policies.py` — the rules above are in its docstring. Attach it to every Part A prompt.
- Predict, as a team: *which rule will the AI get wrong?* Write it down. (Answer at the end.)

---

## Step 0 — Orient (3 min)

📎 `#file:app/models.py` `#file:app/routers/policies.py`
```
I'm building Feature 2 — Policy. From these files: which fields of Policy are derived (not in PolicyCreate) and where
does each come from? What does next_policy_number() already do for me? What is quote.policy before issuing?
Answer as a table: field → source.
```
🔍 `policy_number` ← `next_policy_number()` · `end_date` ← computed · `customer_id/product_id/sum_insured/premium` ← quote · `status` ← default Active · `vehicle_registration` ← request, upper-cased.

---

## Part A — Issue a policy and change its status (20 min) · `app/routers/policies.py`

**A1 · `issue_policy`** — 📎 `#file:app/routers/policies.py` `#file:app/models.py`
```
Implement issue_policy(payload, session) only, following "Rules for issuing" in the module docstring in this order:
1. quote = session.get(Quote, payload.quote_id); if None → HTTPException(status.HTTP_404_NOT_FOUND, "Quote not found")
2. if quote.policy is not None → HTTPException(status.HTTP_409_CONFLICT, "This quote has already been converted to a policy")
3. if quote.product.code == ProductCode.MOTOR and not (payload.vehicle_registration or "").strip() → HTTPException(422, "Motor policies need a vehicle registration number")
4. end_date = payload.start_date + timedelta(days=365 * quote.tenure_years) - timedelta(days=1)   # use datetime.timedelta ONLY — dateutil is NOT installed
5. Policy(quote_id=quote.id, policy_number=next_policy_number(session, quote.product.code, payload.start_date),
   customer_id=quote.customer_id, product_id=quote.product_id, sum_insured=quote.sum_insured, premium=quote.premium,
   start_date=payload.start_date, end_date=end_date, vehicle_registration=(payload.vehicle_registration or "").strip().upper() or None)
6. add / commit / refresh / return. Only the function.
```
▶ Browser: `/quotes/1` → start date 2026-01-01 → *Issue policy*.
🔍 Lands on `PD-HEALTH-2026-00001` · period **01 Jan 2026 → 31 Dec 2026**. Go back to `/quotes/1` → *Issue* again → the page shows the 409 message. A Motor quote without a registration → 422 message.
⚠️ `relativedelta(years=…)` (not installed) · `+ timedelta(days=365)` without the −1 day → ends 1 Jan · `end_date = start_date.replace(year=…)` breaks on 29 Feb.

**A2 · `update_policy_status`** — 📎 `#file:app/routers/policies.py`
```
Implement update_policy_status only: session.get(Policy, policy_id) → 404 "Policy not found" if missing;
if policy.status == PolicyStatus.CANCELLED → HTTPException(status.HTTP_409_CONFLICT, "A cancelled policy cannot be changed");
policy.status = payload.status; add / commit / refresh; return policy.
```
▶ Swagger: `PATCH /api/policies/1/status` body `{"status": "Cancelled"}` → 200. Again with `{"status": "Active"}` → **409**.
⚠️ Compares to the string `"Cancelled"` instead of the enum — works by accident in SQLite, but ask for the enum.

**Checkpoint A (25')** — policy issued from the UI with the right end date; 409 on re-issue; cancelled is final. Commit `Lab 2A`.

---

## Part B — Tests first for the rules (10 min) · `tests/test_policies.py`

📎 `#file:tests/conftest.py` `#file:app/routers/policies.py`
```
Write tests/test_policies.py using the client, ids, health_policy and motor_policy fixtures from conftest (health_policy is a
1-year Health policy starting 2026-01-01; motor_policy is a 2-year Motor policy starting 2026-01-01 with vehicle TS09AB1234).
Tests:
1. health_policy: policy_number starts with "PD-HEALTH-2026-", status "Active", start "2026-01-01", end "2026-12-31", premium 15000.0
2. motor_policy: end date is "2027-12-31" and vehicle_registration == "TS09AB1234"
3. POST /api/policies again with health_policy["quote_id"] → 409
4. a new MOTOR quote for "Rohan Das" (300000, 1 yr) issued without vehicle_registration → 422
5. PATCH status to "Lapsed" then list ?status_filter=Active is empty and ?status_filter=Lapsed has one
6. PATCH to "Cancelled", then PATCH to "Active" → 409
Plain asserts, no mocking.
```
▶ `pytest -q`
🔍 Test 2 is the one that matters: if your end date is `2028-01-01` or `2027-12-30`, the −1 day or the 365×2 is wrong. Fix the code, not the test — the rule is explicit.
⚠️ The AI writes `"2027-12-30"` or `"2028-01-01"` as the expected date. Compute it: 1 Jan 2026 + 730 days = 1 Jan 2028, minus 1 day = **31 Dec 2027**.

**Checkpoint B (35')** — 6 policy tests green. Swap roles. Commit.

---

## Part C — Customer 360 (20 min) · Scenario 2

Read *Student scenarios → Scenario 2*. Model page to copy: `/policies/1` (policy detail) for the layout, the dashboard for stat tiles.

**C1 · Route** — 📎 `#file:app/routers/pages.py` `#file:app/models.py` `#file:docs/scenarios.md`
```
Replace ONLY the body of customer_detail in pages.py with Scenario 2:
customer = session.get(Customer, customer_id); if None raise HTTPException(404, "Customer not found").
policies = customer.policies sorted by created_at desc; claims = every claim of every one of those policies, sorted by created_at desc;
quotes = customer.quotes sorted by created_at desc; age = pricing.age_on(customer.date_of_birth);
premium_total = sum of p.premium for policies whose status != PolicyStatus.CANCELLED (0 when none);
active_count = number of policies with status == PolicyStatus.ACTIVE.
Render "customer_detail.html" with customer, age, quotes, policies, claims, premium_total, active_count.
Must work when the customer has no quotes, policies or claims. Do not touch claim_detail.
```
⚠️ `max(...)`/`min(...)` on an empty list · counts cancelled premiums · loads claims with a separate query per policy (fine for today, but note it).

**C2 · Template** — 📎 `#file:app/templates/policy_detail.html` `#file:app/templates/dashboard.html` `#file:app/templates/_macros.html` `#file:docs/scenarios.md`
```
Write app/templates/customer_detail.html for Scenario 2 in the same style as policy_detail.html. Start with {% from "_macros.html" import pill %}.
page-head: eyebrow "Customer 360", h1 {{ customer.name }}, p "{{ customer.email }} · {{ customer.phone }} · age {{ age }}",
and a primary button "New quote for {{ customer.name.split(' ')[0] }}" → /quotes/new?customer_id={{ customer.id }}.
Then a grid--4 of card stat tiles: Quotes {{ quotes|length }}, Policies {{ policies|length }} with hint "{{ active_count }} active",
Annual premium {{ premium_total|money }}, Claims {{ claims|length }}.
Then grid--side: left column — Policies card with a table (policy_number → /policies/{{ p.id }}, product, sum insured, premium, period start→end %d %b %Y, pill(p.status)) and a Claims card with a table (# → /claims/{{ c.id }}, policy number, incident date, amount, pill(c.status));
right column — a card--tint Profile (name, email, phone, DOB with age, customer since) and a Quotes card listing each quote (#id → /quotes/{{ q.id }}, product, sum insured · tenure, premium, Open/Converted pill).
Each list needs an empty state ("No policies yet." etc.). Money via the money filter. Complete file.
```
▶ `/customers/1` (Priya, has a policy) and `/customers/2` (Rohan, may have nothing) and `/customers/999`.
🔍 Priya: policy number, ₹15,000.00 total, *New quote for Priya* → the form opens with her pre-selected. Rohan: renders with zeros and empty states. 999 → 404. Cancel Priya's policy → total drops to ₹0.00.
⚠️ Premium total includes the cancelled policy (it's in `policies`, filter by status) · `customer.name.split(' ')[0]` written as `customer.first_name` (no such field).

**Checkpoint C (55')** — Customer 360 works for full, empty and unknown customers. Commit.

---

## Part D — Page tests (5 min)

📎 `#file:tests/conftest.py` `#file:tests/test_pages.py`
```
Add to tests/test_pages.py: test_customer_360_lists_policies(client, health_policy) — GET /customers/{health_policy["customer_id"]}
is 200 and contains "Priya Nair", the policy_number and "₹15,000.00"; and test_customer_360_empty_customer_and_404(client, ids) —
/customers/{ids["customers"]["Rohan Das"]} is 200 and /customers/999 is 404.
Then remove the "/customers/1" placeholder assertion from test_student_pages_are_placeholders_until_built.
```
▶ `pytest -q` → green.

---

## Before you commit — the review prompt (2 min)

📎 `#file:app/routers/policies.py` `#file:app/routers/pages.py`
```
Review issue_policy, update_policy_status and customer_detail. Report only real problems:
1. Any date arithmetic that is not timedelta-based or misses the -1 day? 2. Is "cancelled is final" enforced with the enum?
3. Is anything copied from the request that should come from the quote? 4. Does customer_detail survive an empty customer?
5. Is premium_total excluding cancelled policies?
```

## Done when

- [ ] `pytest -q` green — 6 policy tests + 2 page tests
- [ ] From the UI: issue → correct period → re-issue 409 → cancel → change 409
- [ ] `/customers/{id}` correct for Priya, Rohan, and 999
- [ ] AI log ≥ 2 rows total
- [ ] `git commit -m "Lab 2: policy feature" && git push` — safety net for others: `git checkout lab2-complete`

**The prediction:** the rule the AI most often gets wrong is the **end date** (−1 day / `dateutil`). Second: **cancelled is final**. Did your team guess right?
