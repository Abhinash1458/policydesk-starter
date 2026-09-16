# Lab 1 Prompt Guide — The Quote feature

*100 minutes · Team of 3–4 · Driver / Prompter / Validator*

## The problem statement you were given

> **PolicyDesk** is an insurance desk for an agent. **Feature 1 — Quote:** *An agent selects a customer and a product, enters the sum insured, tenure and any add-ons, and gets an annual premium. The agent can see every quote ever made and whether it has become a policy.*
>
> **Premium rules** (from the product owner)
>
> `premium = sum_insured × base_rate × age_factor × tenure_factor × add_on_factor`, never below ₹1,000, rounded to 2 decimals.
>
> | Rule | Values |
> |---|---|
> | Age factor | under 25 → 1.2 for Motor, 0.8 for Health and Term Life · 25–45 → 1.0 · 46–60 → 1.3 · over 60 → 1.6 · negative age is an error |
> | Tenure factor | 1 yr → 1.0 · 2 yr → 0.95 · 3 yr → 0.90 · anything else is an error |
> | Add-ons | Health `CRITICAL_ILLNESS` +15 % · Motor `ZERO_DEPRECIATION` +10 % · each *adds* to the factor (1.0 + 0.15 + …) · an add-on the product doesn't offer is an error |
> | Sum insured | must be > 0 and inside the product's min/max |
>
> **Acceptance criteria**
>
> 1. `POST /api/quotes` returns **201** with the saved quote and its premium; **404** for an unknown customer or product; **422** with a readable message when a rule is broken.
> 2. Priya Nair (born 25 Aug 1990) · Health Shield (rate 0.03) · ₹5,00,000 · 1 year → **₹15,000.00**.
> 3. The *Get a quote* screen shows the premium; the *Quotes* page lists every quote with **Open** / **Converted**, filters by product and status, and offers *Issue policy* on open quotes.
> 4. Tests cover every rule and every boundary.

**Given to you:** models, database, seed data, all other screens, the quote form, `age_on()`, `parse_add_ons()`, the constants.
**You build:** the four pricing functions · `price_quote` + `create_quote` · the Quotes page · the tests.

---

## Before the first prompt (3 min)

1. Roles: Driver types, Prompter writes prompts, Validator reads every line and runs `pytest`. Swap after Part B.
2. `uvicorn app.main:app --reload` running; browser on http://127.0.0.1:8000 → *Get a quote* → it says **TODO Lab 1**.
3. Open `app/services/pricing.py`. The problem statement above is also in its docstring — **that docstring is what you attach to every prompt**.

> **How prompts are written in this guide** — 📎 what to attach in Copilot Chat (`#file:`) · 💬 the prompt (paste as-is) · ▶ what to run · 🔍 what to check · ⚠️ the mistake the AI usually makes here.

---

## Step 0 — Understand what you're extending (10 min)

**0.1 · Map the repo** — 📎 nothing (use `@workspace`)
```
@workspace I'm building Feature 1 — Quote: an agent gets a premium for a customer + product and can list all quotes.
Which files do I need to touch? For each, say what is already done and what is marked TODO (Lab 1).
Then tell me in 3 lines how a request flows: browser → router → service → database.
```
🔍 It should name `app/services/pricing.py`, `app/routers/quotes.py`, `app/routers/pages.py` (the `/quotes` placeholder) and `app/templates/`.

**0.2 · The data you'll use** — 📎 `#file:app/models.py`
```
For Feature 1 I need Customer, Product and Quote. For each: list the fields, which are user-supplied and which are
system-set, and how Quote links to Customer, Product and Policy. What does quote.policy contain before a policy exists?
```
🔍 `premium` and `created_at` are system-set; `quote.policy` is `None` until a policy is issued — you'll rely on that for "Open".

**0.3 · Copy the house style** — 📎 `#file:app/routers/customers.py`
```
/explain create_customer. Then list the conventions this file uses that I should copy in my own router:
how it fetches a row, how it raises errors, which status codes, how it saves.
```
🔍 `session.get(Model, id)` · `HTTPException(status.HTTP_404_NOT_FOUND, "…")` · `add / commit / refresh` · `status_code=201` on the decorator.

---

## Part A — The pricing rules (30 min) · `app/services/pricing.py`

One function per prompt. After **each** one: `pytest tests/test_pricing.py -q`, then read the function aloud.

**A1 · `age_factor`** — 📎 `#file:app/services/pricing.py`
```
ROLE: senior Python engineer. CONTEXT: the attached file — the rules are in its module docstring.
TASK: implement age_factor(age, product) only.
CONSTRAINTS: raise PricingError("Age cannot be negative") for age < 0. Under 25 → 1.2 if product == ProductCode.MOTOR
else 0.8. 25 to 45 inclusive → 1.0. 46 to 60 inclusive → 1.3. Over 60 → 1.6. No other imports.
FORMAT: the function only, then the exact boundary ages I must test.
```
▶ In a Python shell: `from app.services.pricing import *; from app.models import ProductCode as P`
🔍 `age_factor(25, P.MOTOR)` → **1.0** · `age_factor(45, P.HEALTH)` → **1.0** · `age_factor(46, P.HEALTH)` → **1.3** · `age_factor(60, P.HEALTH)` → **1.3** · `age_factor(61, P.HEALTH)` → **1.6**
⚠️ `if age <= 25` — a 25-year-old gets the young-driver loading. **This is the most common bug in the room.** If you got it, log it.

**A2 · `tenure_factor`** — 📎 `#file:app/services/pricing.py`
```
Implement tenure_factor(tenure_years) only, using the TENURE_FACTORS dict already in the file.
If the tenure is not a key, raise PricingError with a message that includes the bad value.
Maximum four lines.
```
🔍 `tenure_factor(4)` raises **PricingError** (not `KeyError`); the message contains `4`.

**A3 · `add_on_factor`** — 📎 `#file:app/services/pricing.py`
```
Implement add_on_factor(product, add_ons) only. Start at 1.0. For each code in add_ons: strip spaces and upper-case
it; skip it if blank; look it up in ADD_ONS[product]; if it is not there raise PricingError saying the add-on is not
available for that product; otherwise ADD its loading to the running factor. Return the factor.
Example that must hold: add_on_factor(ProductCode.HEALTH, ["critical_illness"]) == 1.15.
```
🔍 `add_on_factor(P.HEALTH, ["", " "])` → **1.0** · `add_on_factor(P.TERM_LIFE, ["CRITICAL_ILLNESS"])` **raises**.
⚠️ It multiplies (`factor *= 1 + pct`) instead of adding. Same answer for one add-on, wrong with two — and wrong against the spec.

**A4 · `calculate_premium`** — 📎 `#file:app/services/pricing.py`
```
Implement calculate_premium(...) only, keeping its keyword-only signature. Order:
1. if sum_insured <= 0 raise PricingError("Sum insured must be positive")
2. if min_sum_insured is given and sum_insured < it, raise PricingError("Sum insured must be at least {min:,.0f}")
3. if max_sum_insured is given and sum_insured > it, raise PricingError("Sum insured cannot exceed {max:,.0f}")
4. premium = sum_insured * base_rate * age_factor(age, product) * tenure_factor(tenure_years) * add_on_factor(product, add_ons or [])
5. apply MIN_PREMIUM with max(), THEN round to 2 decimals, return a float.
```
▶ `pytest tests/test_pricing.py -q` — the given example test is green.
🔍 By hand: 5,00,000 × 0.03 × 1.0 × 1.0 × 1.0 = **15,000.0** ✓. And the minimum: `calculate_premium(sum_insured=10000, base_rate=0.004, age=30, tenure_years=1, product=P.TERM_LIFE)` → **1000.0**.
⚠️ Rounds *before* applying the minimum; returns `int`; forgets `add_ons or []` and crashes on `None`.

**Checkpoint A (30')** — four functions, example test green, `age_factor(25, MOTOR) == 1.0`. Commit: `git commit -am "Lab 1A: pricing rules"`.

---

## Part B — The quotes API (15 min) · `app/routers/quotes.py`

**B1 · `price_quote`** — 📎 `#file:app/routers/quotes.py` `#file:app/services/pricing.py` `#file:app/models.py`
```
Implement price_quote(payload, session) only — the TODO comment lists the steps.
Use session.get(Customer, payload.customer_id) and session.get(Product, payload.product_id); raise
HTTPException(status.HTTP_404_NOT_FOUND, "Customer not found" / "Product not found") if missing.
age = pricing.age_on(customer.date_of_birth). Call pricing.calculate_premium with sum_insured=payload.sum_insured,
base_rate=product.base_rate, age=age, tenure_years=payload.tenure_years, product=product.code,
add_ons=pricing.parse_add_ons(payload.add_ons), min_sum_insured=product.min_sum_insured, max_sum_insured=product.max_sum_insured.
Wrap that call: except pricing.PricingError as exc → raise HTTPException(422, str(exc)) from exc.
Return (premium, customer, product). Match the style of app/routers/customers.py.
```
▶ Browser → *Get a quote* → Priya Nair · Health Shield · 500000 · 1 year → **₹15,000.00** on the quote page.
🔍 Try sum insured 5,000 → the form shows *"Sum insured must be at least 100,000"* (422 surfaced as a message, not a crash).
⚠️ Writes `select(Customer).where(Customer.id == …)` — works, but not the house style; ask it to use `session.get`. Or forgets `from exc`.

**B2 · `create_quote`** — 📎 `#file:app/routers/quotes.py`
```
Implement create_quote only: premium, _, _ = price_quote(payload, session); quote = Quote(**payload.model_dump(), premium=premium);
session.add, commit, refresh; return quote. Leave the decorator's status_code=201 exactly as it is.
```
▶ http://127.0.0.1:8000/docs → `POST /api/quotes` → body `{"customer_id": 1, "product_id": 1, "sum_insured": 500000, "tenure_years": 1}`
🔍 Response **201**, `"premium": 15000.0`. Now `"tenure_years": 4` → **422** with *"Tenure must be 1, 2 or 3 years (got 4)"*. `"customer_id": 99` → **404**.

**Checkpoint B (45')** — three status codes seen in Swagger. Swap roles. Commit.

---

## Part C — The Quotes page (25 min) · Scenario 1

Read the brief: *Student scenarios → Scenario 1*. Look at `/policies` in the browser — you are building its twin for quotes.

**C1 · Route** — 📎 `#file:app/routers/pages.py` `#file:app/models.py` `#file:docs/scenarios.md`
```
Replace ONLY the body of quotes_list in pages.py with Scenario 1. Signature becomes
quotes_list(request, status: str | None = None, product: str | None = None, session = Depends(get_session)).
Query: select(Quote).order_by(Quote.created_at.desc()); if product, .join(Product).where(Product.code == product).
After executing, if status == "open" keep quotes where q.policy is None; if "converted" keep where q.policy is not None.
Render "quotes.html" with quotes, status, product, products (all Product ordered by id) and open_count.
Do not touch customer_detail or claim_detail. There is NO Quote.status column — "open" means no policy yet.
```
⚠️ It invents `Quote.status` or `Quote.converted`. Neither exists. Re-prompt with the last sentence in capitals if needed.

**C2 · Template** — 📎 `#file:app/templates/policies.html` `#file:app/templates/_macros.html` `#file:docs/scenarios.md`
```
Write app/templates/quotes.html for Scenario 1, copying the structure and CSS classes of policies.html exactly
(extends base.html, page-head with eyebrow/h1/p, tabs, card, table-wrap, pill, btn). Start with {% from "_macros.html" import pill %}.
Header p: "{{ quotes|length }} shown · {{ open_count }} still open".
Tabs: All / Open / Converted (hrefs keep the current ?product=), then one tab per product (hrefs keep the current ?status=).
Columns: #, customer (link /customers/{{ q.customer_id }}), product, sum insured (money filter), tenure, premium (money, bold),
created (%d %b %Y), status — <span class="pill pill--info">Open</span> if not q.policy else an <a class="pill pill--ok"> to /policies/{{ q.policy.id }} saying Converted —
and an action: <a class="btn btn--accent btn--sm" href="/quotes/{{ q.id }}">Issue policy</a> when open, else <a class="btn btn--ghost btn--sm" href="/policies/{{ q.policy.id }}">View policy</a>.
Empty state: <div class="empty">No quotes match. <a href="/quotes/new">Create one</a>.</div>. Return the complete file.
```
▶ Create two quotes (one Health, one Motor). Open http://127.0.0.1:8000/quotes.
🔍 "2 shown · 2 still open" · both rows Open · `?status=converted` → empty state · `?product=MOTOR` → one row · click *Open* then *Motor Secure*: **both filters stay applied** (check the URL has both params).
⚠️ Tabs that drop the other filter · missing macro import (`pill` undefined) · `q.customer.name` fine, but `q.customer_name` isn't a thing.

**Checkpoint C (70')** — Quotes page live with working filters. Commit.

---

## Part D — Tests (15 min)

**D1 · Generate the pricing suite** — browser AI (paste the file) or Copilot `/tests` with 📎 `#file:app/services/pricing.py`
```
Write tests/test_pricing.py (replace the existing file) for the attached module. Requirements:
- @pytest.mark.parametrize over age bands for MOTOR and HEALTH including the boundaries 24/25, 45/46, 60/61 and age 0
- negative age raises PricingError
- tenure 1, 2, 3 values and tenure 4 raising PricingError
- add-ons: HEALTH critical illness == approx 1.15, MOTOR "zero_depreciation" (lower-case) == approx 1.10, TERM_LIFE with any add-on raises, blanks ignored
- calculate_premium: the worked example 500000/0.03/age 36/1 yr/HEALTH == 15000.0; a case with every factor
  (800000, 0.025, age 22, 2 yr, MOTOR, ["ZERO_DEPRECIATION"]) == approx 25080.0; the ₹1,000 minimum; rounding to 2 dp;
  sum insured 0 and negative raise; below min and above max raise
- one test per behaviour, plain asserts, pytest.approx for floats. No mocking.
```
▶ `pytest -q`
🔍 **Find the wrong one.** Read every expected value against the rules. Typical: it expects `age_factor(25, MOTOR) == 1.2`, or computes 25,080 wrongly, or tests `tenure_factor(0)` expecting `1.0`. Fix the test (or your code, if the test is right and you were wrong) and **log it**.

**D2 · The page test** — 📎 `#file:tests/conftest.py` `#file:tests/test_pages.py`
```
Add test_quotes_list_open_and_product_filter(client, ids) to tests/test_pages.py: create a HEALTH quote for "Priya Nair"
and a MOTOR quote for "Rohan Das" via POST /api/quotes; assert GET /quotes is 200 and contains "2 shown";
assert the motor quote's link href="/quotes/{id}" appears in ?status=open and not in ?status=converted;
assert ?product=MOTOR contains the motor link and not the health link. Do not use the health_policy fixture (policies are Lab 2).
```
▶ `pytest -q` → all green. Delete the `/quotes` line from `test_student_pages_are_placeholders_until_built`.

---

## Before you commit — the review prompt (3 min)

📎 `#file:app/services/pricing.py` `#file:app/routers/quotes.py`
```
Review these two files against this checklist and answer only with problems found (or "none"):
1. Does any boundary use <= where the rule says "under"/"over"? 2. Is MIN_PREMIUM applied before rounding?
3. Any import not in requirements.txt (fastapi, sqlmodel, pydantic, jinja2 only)? 4. Any error that returns 500 instead of 404/422?
5. Any logic in the router that belongs in the service?
```

## Done when

- [ ] `pytest -q` green, ≥ 15 pricing tests, 1 page test
- [ ] Swagger: 201 / 404 / 422 seen · Get-a-quote screen shows ₹15,000.00 for the worked example
- [ ] `/quotes` filters work and keep each other
- [ ] `docs/ai-log.md` has ≥ 1 row (what the AI got wrong · how you caught it · fix)
- [ ] `git add -A && git commit -m "Lab 1: quote feature" && git push`

## Your AI log — rows we expect to see from this lab

| Lab | Asked | AI got wrong | Caught by | Fix |
|---|---|---|---|---|
| 1A | age_factor | `<= 25` | boundary check 25/MOTOR → 1.2 | `< 25` |
| 1A | add_on_factor | multiplied loadings | read vs docstring "adds" | `factor += pct` |
| 1C | quotes route | used `Quote.status` (no such column) | `AttributeError` on first load | `q.policy is None` |
| 1D | tests | expected value wrong in one case | hand-calculated | fixed the expected value |
