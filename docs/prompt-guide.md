# PolicyDesk — Prompt Guide for the Coding Labs

*TalentPath Academy · AI-Powered SDLC Workshop*

This guide gives you a prompt for **every coding task** in the three labs — Lab 1 Quote, Lab 2 Policy, Lab 3 Claim — in the order you do them.
Copy the prompt, fill in the `<…>` parts, paste the files it asks for, run the result, and **validate** it.

> **The one rule:** AI writes the first draft. You own the code. If you can't explain a line, you're not done.

---

## 0. Before you start

### Where to type prompts

| Tool | Best for | How |
|---|---|---|
| **Copilot Chat** (VS Code, `Ctrl+Alt+I`) | Anything about *this* repo — it can see your files | Type `#file:app/services/pricing.py` to attach a file, `@workspace` to search the whole repo |
| **Copilot inline** (`Ctrl+I` in the editor) | "Implement this function", "add a docstring", small edits in place | Select the code first, then `Ctrl+I` |
| **Copilot autocomplete** | Filling in a function whose docstring and name are already clear | Write the docstring, press Enter, wait for the grey text, `Tab` to accept |
| **ChatGPT / Claude / Gemini** (browser) | Explaining concepts, generating tests, reviewing a whole file, debugging a traceback | You must paste the code yourself — paste the *real* code, not a summary |

Copilot Chat slash commands you'll use: `/explain` · `/fix` · `/tests` · `/doc`

### The prompt pattern — use it every time

```
ROLE        You are a senior Python backend engineer.
CONTEXT     We are building PolicyDesk: FastAPI + SQLModel (SQLite) + Jinja2. <paste the relevant file(s)>
TASK        Implement <exact function name> in <file> so that <behaviour>.
CONSTRAINTS Keep the existing signature. No new dependencies. Raise <ErrorType> for <cases>. Under N lines.
FORMAT      Return only the function, then 3 bullet points explaining the decisions.
```

The more precise the CONSTRAINTS, the less the AI invents. Vague prompt → invented columns, invented libraries, invented status codes.

### Golden rules

1. **One function at a time.** Never "implement Lab 1". Ask for `age_factor`, run the tests, then `tenure_factor`.
2. **Paste real code.** The AI cannot see your repo unless you attach it. Wrong context → wrong answer.
3. **Run it immediately.** `pytest -q` after every accepted answer. Green or red — you know where you stand.
4. **Read every line.** If a line surprises you, ask `/explain` on it before you keep it.
5. **Log what it got wrong.** `docs/ai-log.md` — one line per mistake. This is 20 % of your score.

---

## 1. Understand the codebase (first 10 minutes of Lab 1)

**1.1 — Map of the repo** *(Copilot Chat)*
```
@workspace Give me a one-paragraph summary of this project, then a table of every file under app/
with one line each on what it does. Which files contain a "TODO"?
```
✅ Check: it should find `pricing.py`, `quotes.py`, `policies.py`, `claims.py` (service + router) and `pages.py`.

**1.2 — The data model**
```
#file:app/models.py Explain the five tables and how they link (foreign keys and Relationship fields).
Draw it as a Mermaid erDiagram. Which fields are set by the system, not by the user?
```
✅ Check: `premium`, `policy_number`, `end_date`, `status`, `created_at` are system-set.

**1.3 — Trace one request**
```
#file:app/routers/customers.py #file:app/db.py #file:app/main.py
Walk me through what happens, step by step, when a browser sends POST /api/customers.
Start from main.py and end at the SQLite write. Mention where validation happens and where 409 comes from.
```
✅ Check: Pydantic validates the body → `Depends(get_session)` → duplicate-email check → commit → 201.

**1.4 — Explain a function you'll copy the style of**
```
/explain
```
*(select `list_policies` in `app/routers/policies.py`, then run `/explain` in Copilot Chat)*

---

## 2. Lab 1A — Premium calculator (`app/services/pricing.py`)

The rules are in the module docstring at the top of the file. Attach that file every time.

**2.1 — `age_factor`**
```
#file:app/services/pricing.py
Implement only the function age_factor(age, product). Follow the "Age factor" rules in the module docstring
exactly. Constraints: raise PricingError for a negative age; the under-25 rule differs by product
(1.2 for ProductCode.MOTOR, 0.8 otherwise); 25–45 → 1.0; 46–60 → 1.3; over 60 → 1.6.
Return only the function body. Then list the boundary ages I should test.
```
✅ Validate: `age_factor(25, MOTOR)` must be **1.0**, not 1.2. `age_factor(60, HEALTH)` must be **1.3**. `age_factor(61, HEALTH)` must be **1.6**.
⚠️ AI usually gets the boundaries wrong (`<=` vs `<`). Check all three.

**2.2 — `tenure_factor`**
```
#file:app/services/pricing.py
Implement tenure_factor(tenure_years) using the TENURE_FACTORS dict. Raise PricingError with a message
that includes the bad value if the tenure is not 1, 2 or 3. Two to four lines max.
```
✅ Validate: `tenure_factor(4)` raises `PricingError`, not `KeyError`.

**2.3 — `add_on_factor`**
```
#file:app/services/pricing.py
Implement add_on_factor(product, add_ons). Rules: start at 1.0; for each add-on code (strip spaces, uppercase,
skip blanks) look it up in ADD_ONS[product]; if it is not offered for that product raise PricingError;
otherwise add its loading. ["CRITICAL_ILLNESS"] for HEALTH must return 1.15. Return only the function.
```
✅ Validate: `add_on_factor(TERM_LIFE, ["CRITICAL_ILLNESS"])` raises. `add_on_factor(HEALTH, ["", " "])` returns 1.0.
⚠️ AI often *multiplies* loadings (1.0 × 1.15 × 1.10) instead of *adding* them (1.0 + 0.15 + 0.10). Read the docstring: "each adds to the factor".

**2.4 — `calculate_premium`**
```
#file:app/services/pricing.py
Implement calculate_premium(...) using the three helper functions. Order: validate sum_insured (> 0, then
>= min_sum_insured and <= max_sum_insured when those are given, raising PricingError with a helpful message),
then premium = sum_insured * base_rate * age_factor * tenure_factor * add_on_factor, then apply MIN_PREMIUM
with max(), then round to 2 decimals. Keyword-only arguments must stay as they are.
```
✅ Validate by hand: `calculate_premium(sum_insured=500000, base_rate=0.03, age=36, tenure_years=1, product=HEALTH)` → **15000.0**.
Then run `pytest tests/test_pricing.py` — the example test goes green.
⚠️ Watch for: rounding *before* applying the minimum; forgetting `add_ons or []`; returning an `int`.

**2.5 — If autocomplete is your style**
Put the cursor on the line after the docstring of `age_factor`, delete the `raise NotImplementedError`, press Enter and wait. Accept with `Tab`, then **still do the validate step**.

---

## 3. Lab 1B — Quotes API (`app/routers/quotes.py`)

**3.1 — `price_quote`**
```
#file:app/routers/quotes.py #file:app/services/pricing.py #file:app/models.py
Implement price_quote(payload, session). Steps are in the TODO comment. Use session.get for Customer and
Product and raise HTTPException(status.HTTP_404_NOT_FOUND, "...") if either is missing. Compute the age with
pricing.age_on(customer.date_of_birth). Call pricing.calculate_premium with the product's base_rate, code,
min_sum_insured, max_sum_insured and pricing.parse_add_ons(payload.add_ons). Catch pricing.PricingError and
re-raise it as HTTPException(422, str(exc)). Return (premium, customer, product). Only the function.
```
✅ Validate: start the app, open `/quotes/new`, pick Priya Nair · Health Shield · 5,00,000 · 1 year → premium ₹15,000.00.
⚠️ AI may query with `select(Customer).where(...)` — fine, but `session.get(Model, id)` is the idiom used everywhere else in this repo. Ask it to match.

**3.2 — `create_quote`**
```
#file:app/routers/quotes.py
Implement create_quote. Call price_quote, build Quote(**payload.model_dump(), premium=premium),
session.add / commit / refresh, return the quote. Keep status_code=201 on the decorator.
```
✅ Validate in Swagger (`/docs`): POST `/api/quotes` with `{"customer_id":1,"product_id":1,"sum_insured":500000,"tenure_years":1}` → **201** and `"premium": 15000.0`. Try `tenure_years: 4` → **422** with a readable message.

---

## 4. Lab 2A — Policies API (`app/routers/policies.py`)

**4.1 — `issue_policy`**
```
#file:app/routers/policies.py #file:app/models.py
Implement issue_policy(payload, session) following the "Rules for issuing" in the module docstring, in that
order: 404 if the quote is missing; 409 if quote.policy is not None; 422 if quote.product.code is
ProductCode.MOTOR and vehicle_registration is blank. end_date = start_date + timedelta(days=365 * tenure_years)
- timedelta(days=1). Use next_policy_number(). Copy customer_id, product_id, sum_insured and premium from the
quote. Store the registration stripped and upper-cased, or None. add / commit / refresh / return.
```
✅ Validate: issue the ₹15,000 quote from `/quotes/1` with start 2026-01-01 → policy number `PD-HEALTH-2026-00001`, end date **31 Dec 2026**. Try issuing the same quote again → 409.
⚠️ AI likes `relativedelta` from `dateutil` — **not installed**. Insist on `timedelta` as the docstring says.

**4.2 — `update_policy_status`**
```
#file:app/routers/policies.py
Implement update_policy_status: 404 if missing; 409 if policy.status is already PolicyStatus.CANCELLED;
otherwise set policy.status = payload.status, add / commit / refresh, return.
```
✅ Validate in Swagger: cancel a policy, then try to set it Active → 409. Then write `tests/test_policies.py` (§7.1 pattern; cases in the handbook Lab 2) — the 2-year end-date case catches the −1 day.

---

## 5. Lab 1C — Scenario 1, Quotes list page (`/quotes`)

Read the brief first: `docs/scenarios.md` → Scenario 1.

**5.1 — Route**
```
#file:app/routers/pages.py #file:app/models.py #file:docs/scenarios.md
Replace the placeholder in quotes_list with a real implementation of Scenario 1. Accept optional query params
status ("open" | "converted") and product (a ProductCode value). Query Quote ordered by created_at desc; filter
by product with a join on Product in SQL; filter open/converted in Python using quote.policy is None.
Render "quotes.html" with: quotes, status, product, products (all products), open_count. Keep the other
placeholders untouched. Return only the new function.
```
**5.2 — Template**
```
#file:app/templates/policies.html #file:app/templates/_macros.html #file:docs/scenarios.md
Write app/templates/quotes.html for Scenario 1 in the same style as policies.html (extends base.html, same
page-head, tabs, card, table, pill and btn classes). Columns: #, customer (link to /customers/{id}), product,
sum insured, tenure, premium, created, status pill (Open / Converted linking to the policy), and an action
button: "Issue policy" → /quotes/{id} when open, "View policy" → /policies/{id} when converted. Tabs: All /
Open / Converted and one per product, preserving the other filter in the link. Empty state when no rows.
Use the money filter for amounts. Return the complete file.
```
✅ Validate: create two quotes, issue one. `/quotes` shows one Open, one Converted; `?status=open` hides the converted one; `?product=MOTOR` shows only motor quotes. **The tabs must keep the other filter** (click Open, then Motor Secure — both should stay applied).
⚠️ AI frequently invents `Quote.status` (there is no such column) or forgets `{% from "_macros.html" import pill %}`.

**5.3 — Test**
```
#file:tests/conftest.py #file:tests/test_pages.py
Write test_quotes_list_shows_open_and_converted using the client, ids and health_policy fixtures: create one
open Motor quote via POST /api/quotes, then assert GET /quotes is 200 and contains both "Open" and "Converted";
assert the open quote's link href="/quotes/{id}" appears under ?status=open and not under ?status=converted;
assert ?product=MOTOR contains the open quote's link but not the health policy's quote link.
```
Then delete the `/quotes` line from `test_student_pages_are_placeholders_until_built`.

---

## 6. Lab 2B — Scenario 2, Customer 360 (`/customers/{id}`)

**6.1 — Route**
```
#file:app/routers/pages.py #file:app/models.py #file:docs/scenarios.md
Replace the placeholder in customer_detail with Scenario 2. session.get(Customer, customer_id), 404 if missing.
policies = customer.policies sorted newest first; claims = every claim of every one of those policies, newest
first; quotes = customer.quotes newest first. premium_total = sum of premium for policies whose status is not
Cancelled; active_count = number with status Active; age = pricing.age_on(customer.date_of_birth).
Render "customer_detail.html" with all of those plus customer. Only the function.
```
**6.2 — Template**
```
#file:app/templates/policy_detail.html #file:app/templates/dashboard.html #file:docs/scenarios.md
Write app/templates/customer_detail.html for Scenario 2, matching the style of policy_detail.html: page-head
with name / email / phone / age and a primary button "New quote for <first name>" linking to
/quotes/new?customer_id={{ customer.id }}; a grid--4 row of stat cards (quotes, policies with active count,
annual premium via the money filter, claims); a grid--side with policies table + claims table on the left and
a tinted profile card + compact quotes list on the right. Policy numbers link to /policies/{id}, claim ids to
/claims/{id}. Empty states for each list. Return the complete file.
```
✅ Validate: `/customers/1` for Priya shows her policy, premium total, and the claim you filed. `/customers/999` → 404. The "New quote" button pre-selects her on the quote form.
⚠️ AI may compute `premium_total` including cancelled policies, or crash on a customer with no policies (`max()` of empty list). Test the second seeded customer with nothing on them.

---

## 7. Tests — used in every lab (Lab 1D shown; same pattern for Lab 2 and Lab 3)

**7.1 — Generate the suite** *(browser AI or Copilot `/tests`)*
```
Here is app/services/pricing.py: <paste>. Write a pytest module tests/test_pricing.py that covers:
every age band and its boundaries (24/25, 45/46, 60/61) for MOTOR and HEALTH using @pytest.mark.parametrize;
each tenure value and tenure 4 raising PricingError; add-ons (valid, invalid for the product, blank entries);
a worked example I can verify by hand; the minimum premium; rounding to 2 decimals; sum insured 0, negative,
below min and above max. Use pytest.approx for floats. Do not test private details, only behaviour.
```
✅ Validate: run it. **Find the one test the AI got wrong** (there is almost always one — a wrong expected number, a boundary on the wrong side, or a test that passes for the wrong reason). Fix it and log it.

**7.2 — Edge cases you didn't think of**
```
List 10 inputs that could break calculate_premium that a careless developer would miss. For each: the input,
what should happen, and whether the current code handles it. Include type problems (age as a string,
sum_insured as None), huge values, and float precision.
```

**7.3 — Coverage**
```
pip install pytest-cov
pytest --cov=app --cov-report=term-missing
```
then: `Here is the coverage report: <paste>. Which uncovered lines matter most and what test would cover each?`

---

## 8. Stretch — Debug, review, refactor (`git checkout bugs`, if you finish early)

**8.1 — From a failing test**
```
This pytest failure: <paste the full FAILED block including the assert diff>. And here is the function it
tests: <paste>. Explain the root cause in two sentences, then give the minimal fix (a diff, not a rewrite).
```
⚠️ Ask for the *minimal* fix. Otherwise the AI rewrites the function and introduces a new bug.

**8.2 — Tests are green — are you done?** *(they aren't; 2 bugs have no test)*
```
Here is app/services/pricing.py: <paste>. All tests pass. Give me 5 concrete inputs where this code could
still return a wrong premium, with the expected vs actual value for each.
```
```
#file:app/routers/pages.py
Review the dashboard() function for performance problems. How many SQL queries does it run for N products?
Show me a single-query version using a join and group_by.
```

**8.3 — Code review checklist**
```
Review this file as a strict senior engineer: <paste file>. Check, in this order: (1) correctness vs the
docstring rules, (2) error handling and HTTP status codes, (3) N+1 or unnecessary queries, (4) input
validation / injection, (5) naming and duplication. Output a table: line, severity (high/med/low), issue,
suggested fix. Do not rewrite the file.
```

**8.4 — Refactor without changing behaviour**
```
Refactor dashboard() in app/routers/pages.py: extract the six count queries into a helper that returns the
counts dict. Keep the route's signature and the template context identical. Explain each change in one line.
```
✅ Validate: `pytest` still green, `/` looks identical.

---

## 9. Lab 3 — Claim feature: rules, endpoints, Scenario 3 review page

**9.1 — `validate_claim`** (`app/services/claims.py`)
```
#file:app/services/claims.py #file:app/models.py
Implement validate_claim(session, policy, *, amount, incident_date, vehicle_registration) following rules 1–4
in the module docstring, in that order. Rule 1: Cancelled → raise ClaimValidationError("Policy is cancelled",
auto_reject=True); any other non-Active status → ClaimValidationError without auto_reject. Rule 2: incident_date
must satisfy policy.start_date <= incident_date <= policy.end_date (both inclusive). Rule 3: amount must not
exceed remaining_cover(session, policy). Rule 4: if policy.product.code is ProductCode.MOTOR the registration
must be non-blank. Return None when valid. Only the function.
```
⚠️ AI often makes the end date *exclusive*, or counts Filed/Under Review claims in remaining cover (only **Approved** count — `remaining_cover` is given, use it).

**9.2 — Tests first** (`tests/test_claims.py`)
```
#file:tests/conftest.py #file:app/services/claims.py
Write tests/test_claims.py using the client, health_policy and motor_policy fixtures. Cover: filing on an Active
policy → 201 and status "Filed"; incident date one day before start and one day after end → 422; amount above
sum insured → 422 mentioning "remaining cover"; Motor claim without registration → 422 and with it → 201;
claim on a Cancelled policy → 201 with status "Rejected" and a reason; claim on a Lapsed policy → 422;
the workflow Filed → Under Review → Approved with Filed → Approved refused (409) and Approved → Rejected refused
(409); remaining cover shrinking after an approval. Use a small helper to POST a claim.
```

**9.3 — `file_claim` and `update_claim_status`** (`app/routers/claims.py`)
```
#file:app/routers/claims.py #file:app/services/claims.py
Implement file_claim and update_claim_status exactly as the TODO comments and module docstring describe.
file_claim: 404 if the policy is missing; Claim.model_validate(payload); call validate_claim; on
ClaimValidationError with auto_reject set status = ClaimStatus.REJECTED and reason = str(exc) and still save;
otherwise raise HTTPException(422, str(exc)); add / commit / refresh / return.
update_claim_status: 404; 409 unless can_transition; when approving, 422 if amount > remaining_cover;
set status and reason; save; return. Only the two functions.
```
✅ Validate: `pytest tests/test_claims.py` green. In the UI: file a claim on a policy, then cancel the policy and file another → it appears as Rejected with the reason.

**9.4 — Scenario 3 — Claim review page** (`/claims/{id}`)
```
#file:app/routers/pages.py #file:app/services/claims.py #file:docs/scenarios.md
Replace the placeholder in claim_detail with Scenario 3. session.get(Claim, claim_id), 404 if missing.
policy = claim.policy; remaining = remaining_cover(session, policy); next_states = the statuses in
ALLOWED_TRANSITIONS[claim.status], ordered Under Review, Approved, Rejected; other_claims = the policy's other
claims. Render "claim_detail.html" with claim, policy, remaining, next_states, other_claims, and flash / error
read from request.query_params. Do not re-implement the transition rules — use ALLOWED_TRANSITIONS.
```
```
#file:app/templates/policy_detail.html #file:app/templates/_macros.html #file:docs/scenarios.md
Write app/templates/claim_detail.html for Scenario 3 in the style of policy_detail.html: page-head (Claim #id,
customer, policy number link, status pill, "← All claims" button); grid--3 stat cards (claimed, remaining cover
of sum insured, within cover? yes/no); grid--side with a claim card and a policy-context card on the left, and a
Decision card on the right containing: the three workflow steps, a reason textarea, and one submit button per
item in next_states posting to /claims/{{ claim.id }}/status with a hidden input back="/claims/{{ claim.id }}".
Disable the Approved button when claim.amount > remaining. If next_states is empty show an info alert that the
claim is in a final state. Use alerts(flash, error) and pill from _macros.html. Complete file.
```
✅ Validate: a Filed claim shows *Move to review* and *Reject* but **not** *Approve*. After moving to review, *Approve* appears. After approving with a reason, the page shows the reason and "final state", and remaining cover has dropped.

---

## 10. When you're stuck

| Symptom | Prompt |
|---|---|
| A traceback in the terminal | `Here is the full traceback: <paste>. And the function at the bottom of it: <paste>. Root cause in 2 sentences, then the minimal fix.` |
| `501 TODO Lab 1…` (or Lab 2 / Lab 3) in the browser | That's the placeholder — you haven't replaced that function yet. Search the file for `TODO`. |
| `jinja2.exceptions.TemplateNotFound` | The file name in `render(...)` doesn't match a file in `app/templates/`. Check spelling. |
| `UndefinedError: 'x' is undefined` in a template | The route didn't pass `x` in the context. `Compare the variables used in <template> with the keys passed by <route function>; list what is missing.` |
| Test passes but the page looks wrong | `#file:<template> This renders but <describe>. What in the template causes it? Fix only that.` |
| AI answer uses something that doesn't exist | `That uses <thing>, which does not exist in this project (see <file>). Redo it using only what is in the files I attached.` |
| Answer is too long / rewrites everything | `Give me only the changed lines as a diff.` |
| You don't understand the answer | Select it → `/explain`. Then: `Explain it again for a second-year student, one line at a time.` |

---

## 11. Your AI log (`docs/ai-log.md`)

Create this file in your repo on Day 1 and add to it every time the AI is wrong. Format:

```
| # | Lab | What I asked | What the AI got wrong | How I caught it | Fix |
|---|-----|--------------|-----------------------|-----------------|-----|
| 1 | 1A  | age_factor   | used <= 25 instead of < 25 | boundary test (25, MOTOR) → 1.2 not 1.0 | changed to < |
```

Three good entries is the target. This log is what you show in the demo.

---

## 12. Quick reference card

```
 PATTERN      role → context (paste files) → task (one function) → constraints → format
 COPILOT      Ctrl+Alt+I chat · Ctrl+I inline · #file:path attach · @workspace search · /explain /fix /tests
 AFTER EVERY  pytest -q   →   read every line   →   run the page   →   log any mistake
 NEVER        accept code that imports something not in requirements.txt
              accept a test you haven't read
              ask for "the whole feature" in one prompt
 RULE FILES   pricing rules → app/services/pricing.py docstring
              claim rules  → app/services/claims.py docstring
              page briefs  → docs/scenarios.md
              API contract → app/routers/*.py docstrings and /docs (Swagger)
```
