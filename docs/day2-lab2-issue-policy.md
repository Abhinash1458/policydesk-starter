# Day 2 · Lab 2 — Issue a policy

*45 minutes · `app/routers/policies.py` · tests: `tests/test_policies.py`*

## The problem statement

> **Once a customer accepts a quote, the agent issues a policy from it. The agent can later lapse or cancel the policy.**
>
> | Rule | Detail |
> |---|---|
> | One policy per quote | a quote that already has a policy → **409** |
> | Policy number | `PD-<PRODUCT CODE>-<start year>-<5-digit sequence>` — `next_policy_number()` is given |
> | Period | `end_date = start_date + 365 × tenure_years days − 1 day` (1 Jan 2026, 1 year → 31 Dec 2026) |
> | Motor needs a vehicle | Motor quote issued without a vehicle registration → **422**; store it upper-cased |
> | Copy from the quote | customer, product, sum insured, premium come from the quote — never from the request |
> | Status | Active (default) → Lapsed / Cancelled. **Cancelled is final** → any later change is **409** |
>
> **Acceptance:** `POST /api/policies {quote_id, start_date}` → 201 with `policy_number`, `end_date`, `status: Active`; 404 unknown quote; 409 already issued; 422 Motor without vehicle. `PATCH /api/policies/{id}/status` → 200, or 409 once Cancelled. The quote page's *Issue policy* button works.

The rules are in the docstring of `policies.py` — attach it. Until done, *Issue policy* on a quote page answers **501 "Day 2, Lab 2: implement issue_policy"**.

**Needs Lab 1:** creating a *new* quote to issue needs the calculator. If Lab 1 isn't done, use the two seeded quotes' policies for the status part and skip the issue part for now.

## Step 0 — predict (2 min)

Read the six rules. Write down, as a team, **which one the AI will get wrong**. (Answer at the bottom.)

## Part A — `issue_policy` (15 min)

📎 `#file:app/routers/policies.py` `#file:app/models.py`
```
ROLE: senior FastAPI engineer. CONTEXT: attached; the rules are in the module docstring. TASK: implement issue_policy(payload, session) only, in this order:
1. quote = session.get(Quote, payload.quote_id); None -> HTTPException(status.HTTP_404_NOT_FOUND, "Quote not found")
2. if quote.policy is not None -> HTTPException(status.HTTP_409_CONFLICT, "This quote has already been converted to a policy")
3. if quote.product.code == ProductCode.MOTOR and not (payload.vehicle_registration or "").strip() -> HTTPException(422, "Motor policies need a vehicle registration number")
4. end_date = payload.start_date + timedelta(days=365 * quote.tenure_years) - timedelta(days=1)   # datetime.timedelta only — dateutil is NOT installed
5. Policy(quote_id=quote.id, policy_number=next_policy_number(session, quote.product.code, payload.start_date), customer_id=quote.customer_id,
   product_id=quote.product_id, sum_insured=quote.sum_insured, premium=quote.premium, start_date=payload.start_date, end_date=end_date,
   vehicle_registration=(payload.vehicle_registration or "").strip().upper() or None)
6. add / commit / refresh / return.  CONSTRAINTS: no new imports (timedelta is already imported). FORMAT: the function only.
```
▶ Browser: *Get a quote* → new quote → *Issue policy* with start 2026-01-01.
🔍 lands on `PD-HEALTH-2026-00003`, period **01 Jan 2026 → 31 Dec 2026**. Issue the same quote again → 409 shown on the quote page.
⚠️ `relativedelta` (not installed) · forgets the **−1 day** (ends 1 Jan) · `start_date.replace(year=…)` (breaks on 29 Feb).

## Part B — `update_policy_status` (8 min)

```
Implement update_policy_status only: session.get(Policy, policy_id) -> 404 "Policy not found"; if policy.status == PolicyStatus.CANCELLED
-> HTTPException(status.HTTP_409_CONFLICT, "A cancelled policy cannot be changed"); policy.status = payload.status; add / commit / refresh; return.
```
▶ Swagger: `PATCH /api/policies/1/status` `{"status": "Cancelled"}` → 200; again `{"status": "Active"}` → **409**.
⚠️ compares to the string `"Cancelled"` instead of `PolicyStatus.CANCELLED`.

### The code you should end up with

```python
def issue_policy(payload: PolicyCreate, session: Session) -> Policy:
    """Shared by the API and the HTML form. Raise HTTPException with the right status code on failure."""
    quote = session.get(Quote, payload.quote_id)
    if not quote:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Quote not found")
    if quote.policy:
        raise HTTPException(status.HTTP_409_CONFLICT, "This quote has already been converted to a policy")
    if quote.product.code == ProductCode.MOTOR and not (payload.vehicle_registration or "").strip():
        raise HTTPException(422, "Motor policies need a vehicle registration number")

    end_date = payload.start_date + timedelta(days=365 * quote.tenure_years) - timedelta(days=1)
    policy = Policy(
        quote_id=quote.id,
        policy_number=next_policy_number(session, quote.product.code, payload.start_date),
        customer_id=quote.customer_id,
        product_id=quote.product_id,
        sum_insured=quote.sum_insured,
        premium=quote.premium,
        start_date=payload.start_date,
        end_date=end_date,
        vehicle_registration=(payload.vehicle_registration or "").strip().upper() or None,
    )
    session.add(policy)
    session.commit()
    session.refresh(policy)
    return policy
```
```python
@router.patch("/{policy_id}/status", response_model=PolicyRead)
def update_policy_status(policy_id: int, payload: PolicyStatusUpdate, session: Session = Depends(get_session)):
    policy = session.get(Policy, policy_id)
    if not policy:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Policy not found")
    if policy.status == PolicyStatus.CANCELLED:
        raise HTTPException(status.HTTP_409_CONFLICT, "A cancelled policy cannot be changed")
    policy.status = payload.status
    session.add(policy)
    session.commit()
    session.refresh(policy)
    return policy
```

## Part C — tests, review, commit (20 min)

1. `pytest tests/test_policies.py -v` — read each name; the 2-year case is the one that catches the −1 day.
2. Add one test of your own: a **3-year** policy from 2026-06-15 must end **2029-06-13** (3 × 365 = 1095 days, minus 1). Ask the AI to write it; check its expected date by hand first.
3. Review — 📎 `#file:app/routers/policies.py`
   ```
   Report only real problems: 1. any date arithmetic not based on timedelta, or missing the -1 day? 2. is "cancelled is final" checked with the enum?
   3. is anything copied from the request that must come from the quote? 4. right status codes: 404 / 409 / 422 / 201?
   ```
4. `git add -A && git commit -m "Day 2 Lab 2: issue policy and status" && git push` → Actions green.

**Done when:** `pytest` (everything) → **80 passed** · issue → correct period → re-issue 409 → cancel → change 409 · pushed.

**The prediction:** the rule the AI most often breaks is the **end date** (−1 day / `dateutil`); second, **cancelled is final**. Did you guess right?
