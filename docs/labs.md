# Lab handbook — what you do in each lab

Two days · 3 hours each · 30 % concepts, 70 % hands-on. Teams of 3–4. One laptop drives, the others prompt, read and validate — **rotate the driver every lab**.

Every lab ends with a **Validate the AI** step and a **Done when** list. Tick the list before you move on.

| Day | Time (IST) | Lab | You build |
|---|---|---|---|
| 1 | 9:15–9:45 | Lab 1 · Prompting | Three prompt patterns on the same task |
| 1 | 9:45–10:20 | Lab 2 · Requirements | User stories + acceptance criteria for PolicyDesk |
| 1 | 10:30–11:00 | Lab 3 · Design | ERD, API contract, architecture note |
| 1 | 11:00–12:10 | Lab 4 · Build | Premium calculator, quotes & policies API, Scenario 1 page |
| 1 | homework | Scenario 2 | Customer 360 page |
| 2 | 9:10–9:50 | Lab 5 · Test | pytest for the pricing rules, edge cases, coverage |
| 2 | 9:50–10:30 | Lab 6 · Quality | Fix 5 seeded bugs, refactor, AI code review |
| 2 | 10:40–11:10 | Lab 7 · Ship | README, deploy to Render, read the logs |
| 2 | 11:10–11:50 | Final project | Claims module + Scenario 3 page |
| 2 | 11:50–12:10 | Demos | 90 seconds per team |

---

## Lab 1 — Prompting (15 min)

**Goal:** feel the difference between a lazy prompt and a good one.

**Task:** ask an AI to write a Python function that validates an Indian vehicle registration number (e.g. `TS09AB1234`).

1. **Zero-shot:** `Write a function to validate a vehicle registration number.`
2. **Role + context + constraints:** `You are a senior Python engineer. Write validate_registration(text) -> bool for Indian private-vehicle plates: 2 letters state code, 2 digits RTO, 1–3 letters series, 4 digits. Ignore spaces and case. Use one compiled regex. Include 3 valid and 3 invalid examples as asserts.`
3. **Few-shot:** the same, plus: `Examples — valid: TS09AB1234, MH 12 DE 1433, KA01A0001. Invalid: TS9AB1234, TS09AB123, 09TSAB1234.`

Compare the three outputs side by side.

**Validate the AI:** run all three. Which ones accept `TS09AB123` (only 3 digits)? Which invented a rule you never gave?

**Done when:** the team can say in one sentence what each of *role*, *constraints* and *examples* changed in the output.

---

## Lab 2 — Requirements (25 min)

**Goal:** turn a one-paragraph problem statement into testable requirements — and catch what the AI invents.

**Problem statement:** *"PolicyDesk lets an insurance agent quote a customer for Health, Motor or Term Life cover, issue the policy, and let the customer file a claim. Premiums depend on age, tenure and add-ons. Claims must be validated against the policy."*

1. Prompt: `Act as a business analyst. From this problem statement write 8 user stories ("As a … I want … so that …"), each with 3 acceptance criteria in Given/When/Then. Then list 5 assumptions you made and 5 edge cases we should ask the client about.`
2. Read every story. **Strike out at least 2 requirements the AI invented** that are not in the statement (it will add things like login, payments, e-mail, PDF policy documents).
3. Pick the 3 stories your team thinks are the core flow. Write them on the team sheet.

**Validate the AI:** which acceptance criteria are not actually testable ("the system should be fast")? Rewrite one.

**Done when:** 8 stories, 2 struck out with a reason, 3 core stories agreed.

---

## Lab 3 — Design (22 min)

**Goal:** produce the three artefacts a developer needs before coding — and check them against the stories.

1. **ERD:** `From these user stories <paste> produce a Mermaid erDiagram with Customer, Product, Quote, Policy, Claim. Show cardinality and the key fields on each.` Paste into https://mermaid.live.
2. **API contract:** `List the REST endpoints for these stories as a table: method, path, request body, response, error codes (404/409/422).`
3. **Architecture note:** `Write a one-page architecture note for a FastAPI + SQLModel + Jinja2 app: layers (router → service → model), where validation lives, how SQLite is used, how it deploys to Render. Plain language, 250 words.`

**Validate the AI:** does the ERD have a field for every acceptance criterion? (Where is the claim *reason*? The policy *end date*?) Does the API return 201 for creates and 409 for "already exists"?

**Done when:** ERD renders, endpoint table has ≥ 8 rows with status codes, note fits one page. Compare with `app/models.py` in the starter — what did you miss, what did the AI miss?

---

## Lab 4 — Build (60 min)

**Goal:** implement the premium calculator, the quotes and policies API, and your first page — with Copilot, one function at a time.

**Setup (5 min):** `git clone https://github.com/Abhinash1458/policydesk-starter` → `python check_setup.py` → `python -m venv .venv` → activate → `pip install -r requirements.txt` → `uvicorn app.main:app --reload` → open http://127.0.0.1:8000. Click around: the three placeholder pages are yours.

**Read first (10 min):** prompts 1.1–1.4 in the prompt guide. Each team member `/explain`s one given function to the others.

**Build (40 min)** — follow the prompt guide sections 2 → 3 → 4 → 5, in order:

| Step | File | Prompt guide | Check |
|---|---|---|---|
| A | `app/services/pricing.py` — 4 functions | §2 | `pytest tests/test_pricing.py` green; ₹15,000 for the worked example |
| B | `app/routers/quotes.py` | §3 | `/quotes/new` gives a premium; Swagger POST returns 201 |
| C | `app/routers/policies.py` | §4 | Issue a policy → `PD-HEALTH-2026-00001`, end date 31 Dec; re-issue → 409 |
| D | Scenario 1 — `/quotes` page | §5 + `docs/scenarios.md` | Open / Converted pills, filters keep each other |

**Instructor demo (10 min, watch):** the same Lab 4 done by an agentic tool (Claude Code / Gemini CLI) end-to-end — notice what it checks and what it skips.

**Validate the AI:** one team member explains a generated function line by line to the group. Write at least one entry in `docs/ai-log.md`.

**Done when:** the four checks above pass, `pytest` is green, the AI log has ≥ 1 row. `git commit` and `git push`.

**Homework — Scenario 2 (Customer 360):** prompt guide §6. Bring it working tomorrow.

---

## Lab 5 — Test (30 min)

**Goal:** get AI to write the tests, then find the one it got wrong.

1. Prompt guide §7.1 — generate `tests/test_pricing.py` (replace the one-test starter file). Run it.
2. **Find the wrong test.** There is almost always one: a wrong expected number, a boundary on the wrong side, a test that passes for the wrong reason. Fix it, log it.
3. §7.2 — ask for 10 edge cases. Turn the 3 best into tests.
4. §7.3 — `pytest --cov=app --cov-report=term-missing`. What is uncovered and does it matter?

**Validate the AI:** compute one expected premium **by hand** on paper and compare with the test's expected value.

**Done when:** ≥ 15 pricing tests, all green, one AI-generated test corrected and logged, coverage of `pricing.py` at 100 %.

---

## Lab 6 — Quality (32 min)

**Goal:** debug, review and refactor with AI — and learn that green tests are not the end.

1. `git checkout bugs` → `pytest` → **3 failures**. Prompt guide §8.1: fix each from its traceback with a *minimal* diff.
2. Tests are green. §8.2: there are **2 more bugs** with no failing test. Find them with the edge-case prompt (pricing) and the review prompt (dashboard).
3. §8.3: run the code-review checklist on `app/routers/policies.py`. Fix one *high* item.
4. §8.4: refactor `dashboard()` — extract the counts. Tests must stay green.
5. `git diff day1-complete` — can you name all five bugs?

**Validate the AI:** did any "fix" rewrite more than it needed to? Did the review flag something that isn't actually a problem?

**Done when:** 5 bugs fixed and named, refactor committed, tests green, 2+ rows in the AI log.

---

## Lab 7 — Ship (22 min)

**Goal:** document, deploy, and diagnose a production error from logs.

1. **Docs:** `Here is our repo tree and app/main.py: <paste>. Update README.md: what it does, run, test, API table, project layout. Keep the existing structure.` Then `/doc` on two functions that lack docstrings.
2. **Deploy:** push to GitHub → Render → *New → Blueprint* → pick your repo (the `render.yaml` does the rest) → wait for *Live* → open `/health`.
3. **Break it on purpose:** in Render → Environment, change `DATABASE_URL` to `sqlite:///./no/such/dir/x.db` → redeploy → open the site → **read the logs**.
4. **Diagnose with AI:** `These are the Render deploy logs: <paste>. What failed, why, and what is the exact change to fix it?` Fix it. Redeploy.

**Validate the AI:** did the diagnosis point at the right line of the log, or at a guess?

**Done when:** public URL works, `/health` is `ok`, README updated, one broken deploy diagnosed and fixed.

---

## Final project — Claims module + Claim review page (40 min)

Brief: `docs/final-project.md` · Prompts: prompt guide §9 · Page spec: `docs/scenarios.md` Scenario 3 · Scoring: `docs/rubric.md`.

| Min | Step |
|---|---|
| 0–3 | Read `Claim` in `models.py` and the claim form in `policy_detail.html` (given) |
| 3–20 | `validate_claim` in `app/services/claims.py`, **tests first** in `tests/test_claims.py` |
| 20–28 | `file_claim` + `update_claim_status` in `app/routers/claims.py` |
| 28–37 | Scenario 3 — `/claims/{id}` review page |
| 37–39 | Run the full flow in the UI: file → review → approve → remaining cover drops |
| 39–40 | `git push` — Render redeploys |

**Done when:** claim rules enforced (4 rules, cancelled → auto-rejected), workflow works from the review page, `pytest` green, deployed, AI log has ≥ 3 rows.

---

## Demo (90 seconds per team)

1. The URL. One end-to-end flow: quote → policy → claim → approve.
2. **One thing the AI got wrong and how you caught it** (from your AI log).
3. Every team member says something.

Scoring: `docs/rubric.md`.
