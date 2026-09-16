# Lab handbook — what you do in each session

Two days · 3 hours each. Three labs, **one feature each** — you build it end-to-end: rules → API → page → tests. Teams of 3–4: *Driver* types, *Prompter* writes prompts, *Validator* reads every line and runs the tests. **Rotate roles every lab.**

Every lab is **build → test → validate the AI**. Each ends with a **Done when** list — tick it before you move on.

| Day | Min | Session | You build |
|---|---|---|---|
| 1 | 20 | Setup check · intro · teams | Starter running on every laptop |
| 1 | 60 | AI-Powered SDLC | 3 short exercises: prompting, requirements, design |
| 1 | 100 | **Lab 1 · Quote feature** | Premium calculator · `POST /api/quotes` · Quotes list page · tests |
| 2 | 10 | Recap | Everyone at `lab1-complete` or better |
| 2 | 60 | **Lab 2 · Policy feature** | Issue policy · status change · Customer 360 page · tests |
| 2 | 60 | **Lab 3 · Claim feature** | Claim rules · file/review endpoints · Claim review page · tests |
| 2 | 35 | Deployment & Ship | README · live URL on Render · one outage diagnosed from logs |
| 2 | 15 | Demos | 90 seconds per team |

Behind? `git checkout lab1-complete` or `git checkout lab2-complete` and carry on from there — no penalty.

---

## Day 1 · AI-Powered SDLC — three exercises (10 min each)

**E1 — Prompting.** Ask an AI for a Python function that validates an Indian vehicle registration number (`TS09AB1234`) three ways:
1. Zero-shot: `Write a function to validate a vehicle registration number.`
2. Pattern: `You are a senior Python engineer. Write validate_registration(text) -> bool for Indian private-vehicle plates: 2 letters state code, 2 digits RTO, 1–3 letters series, 4 digits. Ignore spaces and case. One compiled regex. Include 3 valid and 3 invalid examples as asserts.`
3. Few-shot: the same, plus `Examples — valid: TS09AB1234, MH 12 DE 1433, KA01A0001. Invalid: TS9AB1234, TS09AB123, 09TSAB1234.`

*Validate:* run all three. Which accept `TS09AB123` (3 digits)? Which invented a rule you never gave?

**E2 — Requirements.** Problem statement: *"PolicyDesk lets an insurance agent quote a customer for Health, Motor or Term Life cover, issue the policy, and let the customer file a claim. Premiums depend on age, tenure and add-ons. Claims must be validated against the policy."*
Prompt: `Act as a business analyst. From this problem statement write 8 user stories ("As a … I want … so that …"), each with 3 acceptance criteria in Given/When/Then. Then list 5 assumptions and 5 edge cases to ask the client about.`
**Strike out 2 requirements the AI invented** (login? payments? e-mail? PDF policies?). Pick your 3 core stories.

**E3 — Design.** `From these stories <paste> produce a Mermaid erDiagram with Customer, Product, Quote, Policy, Claim, with cardinality and key fields. Then a table of REST endpoints: method, path, body, response, error codes.` Paste the ERD into mermaid.live. Then open `app/models.py` in the starter: *what did the AI miss?* (claim reason · policy end date · vehicle registration)

---

## Lab 1 — The Quote feature (100 min)

**Feature:** *An agent can get a premium quote for a customer and product, and see every quote with its status.*

**Setup (already done at home):** `git clone https://github.com/Abhinash1458/policydesk-starter` → venv → `pip install -r requirements.txt` → `uvicorn app.main:app --reload` → http://127.0.0.1:8000. Click *Get a quote* — it says "TODO Lab 1". That's yours.

**Read first (10 min):** prompt guide §1.1–1.4. Each member `/explain`s one given function to the others (`list_policies`, `money`, `seed`). Open `app/services/pricing.py` — **the rules are in the docstring at the top.**

| Part | Min | File | Build | Prompt guide | Check |
|---|---|---|---|---|---|
| A | 30 | `app/services/pricing.py` | `age_factor`, `tenure_factor`, `add_on_factor`, `calculate_premium` — **one function per prompt** | §2 | `pytest tests/test_pricing.py` green; `calculate_premium(500000, 0.03, age 36, 1 yr, HEALTH)` = **15000.0**; `age_factor(25, MOTOR)` = **1.0** |
| B | 15 | `app/routers/quotes.py` | `price_quote` + `create_quote` → 201 / 404 / 422 | §3 | `/quotes/new` → ₹15,000.00 for Priya · Health · 5,00,000 · 1 yr; Swagger `tenure_years: 4` → 422 |
| C | 25 | `app/routers/pages.py` + `app/templates/quotes.html` | **Scenario 1 — Quotes list page** (Open / Converted, product filter, *Issue policy* button) | §5 + scenarios | `/quotes?status=open` and `?product=MOTOR` work; tabs keep each other's filter |
| D | 15 | `tests/test_pricing.py`, `tests/test_pages.py` | AI-generated pricing suite — **find the one wrong test**; one page test | §7.1, §5.3 | `pytest` green, ≥ 15 pricing tests |

**Validate the AI:** one member explains a generated function line by line. Log ≥ 1 mistake in `docs/ai-log.md` (the `<= 25` boundary and the phantom `Quote.status` column are the usual ones).

**Done when:** all four checks pass · `pytest` green · AI log ≥ 1 row · `git commit -m "Lab 1: quote feature" && git push`.

**Optional homework — Scenario 2 (Customer 360 page):** prompt guide §6. If you bring it working, you'll finish Lab 2 early and help others.

---

## Lab 2 — The Policy feature (60 min)

**Feature:** *An agent can convert a quote into a policy, change its status, and see everything about a customer on one page.*

New ideas: **state** (Active / Lapsed / Cancelled — and *cancelled is final*), **derived data** (end date = start + 365 × tenure − 1 day; policy number), **relationships** (one customer → many quotes, policies, claims). Rules are in the docstring of `app/routers/policies.py`.

| Part | Min | File | Build | Prompt guide | Check |
|---|---|---|---|---|---|
| A | 20 | `app/routers/policies.py` | `issue_policy` (404 / 409 / 422, policy number, end date, Motor needs a vehicle) · `update_policy_status` (Cancelled → 409) | §4 | From `/quotes/1`, start 2026-01-01 → `PD-HEALTH-2026-00001`, end **31 Dec 2026**; issue again → 409 |
| B | 10 | `tests/test_policies.py` | Issue from quote · 2-yr end date = `2027-12-31` · issue twice → 409 · Motor without vehicle → 422 · Cancelled → Active → 409 | §7.1 pattern | `pytest` green — the 2-yr case catches the −1 day |
| C | 25 | `app/routers/pages.py` + `app/templates/customer_detail.html` | **Scenario 2 — Customer 360** (profile, 4 stat tiles, policies, claims, quotes; *New quote for …* pre-selects the customer) | §6 + scenarios | `/customers/1` shows Priya's policy and premium total; `/customers/999` → 404; works for a customer with nothing |
| D | 5 | `tests/test_pages.py` | Customer 360 test + 404 test; delete the placeholder line | §6 | `pytest` green |

**Validate the AI:** did it reach for `dateutil` (not installed)? Did it forget the −1 day? Does the premium total exclude cancelled policies? Does the page crash for an empty customer?

**Done when:** checks pass · `pytest` green · AI log ≥ 2 rows · commit + push. Safety net: `git checkout lab2-complete`.

---

## Lab 3 — The Claim feature (60 min)

**Feature:** *A customer can file a claim on an active policy; a claims officer reviews it with the full picture and approves or rejects it.*

Rules are in the docstring of `app/services/claims.py`. Workflow: Filed → Under Review → Approved / Rejected (finals). **Today: tests first.**

| Part | Min | File | Build | Prompt guide | Check |
|---|---|---|---|---|---|
| A | 12 | `tests/test_claims.py` | **Tests first** — 4 rules, Cancelled → auto-Rejected, Lapsed → 422, transitions, remaining cover shrinks | §9.2 | All red (501) — correct for now |
| B | 13 | `app/services/claims.py` | `validate_claim` — rules 1–4 in order; `auto_reject=True` for Cancelled; dates **inclusive**; use the given `remaining_cover()` | §9.1 | Rule tests green |
| C | 12 | `app/routers/claims.py` | `file_claim` (save as Rejected on auto_reject, else 422) · `update_claim_status` (409 bad transition, 422 over cover) | §9.3 | `pytest tests/test_claims.py` green; cancel a policy → new claim appears as Rejected with reason |
| D | 20 | `app/routers/pages.py` + `app/templates/claim_detail.html` | **Scenario 3 — Claim review page**: tiles, claim + policy context, **only the allowed next actions**, reason box, Approve disabled over cover | §9.4 + scenarios | Filed → *Move to review* (no *Approve*) → Approve with reason → "final state", remaining cover dropped |
| — | 3 | — | Run the whole flow in the UI, commit, push | | |

**Validate the AI:** `start < incident < end` is exclusive — the rule is inclusive. Did it count Filed claims in remaining cover? Did it *raise* on a cancelled policy instead of *saving* the claim as Rejected? Did it put transition rules in the template instead of using `ALLOWED_TRANSITIONS`?

**Done when:** checks pass · `pytest` green · AI log ≥ 3 rows · pushed. If time runs out, ship without Part D — the API and tests are the core.

---

## Day 2 · Deployment & Ship (35 min)

1. **Docs (5):** `Here is our repo tree and app/main.py: <paste>. Update README.md — what it does, run, test, API table, project layout.` Then `/doc` on two functions. Commit.
2. **Deploy (10):** push → Render → *New → Blueprint* → your repo → *Apply*. Wait for *Live*. Open `/health` → `{"status":"ok"}`, then the dashboard.
3. **Break it (10):** Render → Environment → `DATABASE_URL=sqlite:///./no/such/dir/x.db` → rebuild → site fails → **Logs** tab. Prompt: `These are the Render deploy logs: <paste>. What failed, why, and what is the exact change to fix it?` Fix, redeploy.
4. **Ship check (5):** paste your URL in the shared sheet.

*Validate:* did the AI point at the actual log line (`unable to open database file`) or guess? Free instances sleep — first load takes ~30 s; open your URL before the demo.

---

## Demo (90 seconds per team)

1. The URL. One flow: quote → policy → claim → approve.
2. **One thing the AI got wrong and how you caught it** — from `docs/ai-log.md`.
3. Every team member says something.

Scoring: `docs/rubric.md` — working features 40 · tests 20 · AI-validation evidence 20 · demo 10 · code quality 10.

---

## Stretch (only if you finish early)

`git checkout bugs` — 5 seeded bugs on top of `lab2-complete`. `pytest` finds 3; the other 2 need the edge-case prompt and the code-review prompt (prompt guide §8). Can you name all five?
