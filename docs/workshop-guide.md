# PolicyDesk workshop — 80 minutes, three phases

*TalentPath Academy · AI-Powered SDLC · one session*

You are given a working insurance app — customers, products, quotes and policies — and you add the **claims** feature with AI, then build an **admin approval** workflow with a prompt you write yourself.

| Phase | Min | What happens | You end with |
|---|---|---|---|
| **1 · Fork & explore** | 25 | Fork the repo, run it, read the code with Copilot | Your own fork, app running, one commit |
| **2 · Four prompts, real outputs** | 30 | Four worked prompts — Claim model → claim endpoints → database tables → premium logic | Claims API working, all tests green, four commits |
| **3 · Your own prompt** | 25 | Write the prompt for the admin approval feature; acceptance tests tell you when you're done | Admin queue + status workflow, one commit, pushed |

**One rule all session:** AI writes the first draft — you read every line, run the tests, and commit only what you understand.

---

## Before you start (done at home — see `docs/setup-guide.md`)

Python 3.12+, Git, VS Code with Copilot, a GitHub account. `python check_setup.py` prints **ALL CHECKS PASSED**.

---

## Phase 1 — Fork & explore (25 min)

### 1.1 Fork, clone, run (10 min) — full steps in `docs/git-workflow.md`

1. Open https://github.com/Abhinash1458/policydesk-starter → **Fork** → *Create fork* (your account, keep the name).
2. Clone **your fork** (not the original):
   ```
   git clone https://github.com/<your-username>/policydesk-starter.git
   cd policydesk-starter
   python -m venv .venv
   .venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
3. Open http://127.0.0.1:8000 — dashboard, 2 customers, 3 products, 2 policies already there. Open http://127.0.0.1:8000/docs — the API.
4. `pytest -m "not lab"` → **15 passed**. (`pytest -m lab` fails — those are your targets for Phases 2 and 3.)

### 1.2 Read the code with Copilot (15 min)

Open Copilot Chat (`Ctrl+Alt+I`). Run these three prompts and write the answers on your team sheet.

**Map** — `@workspace`
```
@workspace Summarise this project in one paragraph. Then give me a table of every file under app/ with one line each.
Which files mention "Phase 2" or "Phase 3"? Which feature is missing compared to the flow Customer -> Quote -> Policy -> Claim?
```
**Data** — `#file:app/models.py`
```
Explain the four tables and how they link (foreign keys and Relationship fields). For each table: which fields does the
user supply and which does the system set? What would a Claim table need to link to?
```
**House style** — `#file:app/routers/policies.py`
```
/explain issue_policy. Then list the conventions I must copy in a new router: how a row is fetched, how errors are raised
and with which status codes, how a row is saved, and how a router is registered in app/main.py.
```
✅ You should be able to say: `session.get(Model, id)` · `HTTPException(status.HTTP_404_NOT_FOUND, "…")` · `add / commit / refresh` · `status_code=201` on create · `app.include_router(...)` in `main.py`.

**Commit:** `git add -A && git commit -m "Phase 1: setup and explore" && git push`

---

## Phase 2 — Four prompts with real outputs (30 min)

Each example in `docs/phase2-prompts.md` has: the prompt to paste · what to attach · the **actual code it should produce** · how to check · the mistake AI usually makes. Do them in order, **commit after each**.

| # | Min | Example | File | Check |
|---|---|---|---|---|
| 1 | 6 | Add the **Claim model** | `app/models.py` | `python -c "from app.models import Claim; print(Claim.__tablename__)"` → `claim` |
| 2 | 10 | Add the **claim endpoints** | `app/routers/claims.py` (new) | file compiles; `POST /api/claims` appears in `/docs` after Example 3 |
| 3 | 6 | **Create the database tables** and register the router | `app/main.py`, `app/init_db.py` (new) | `python -m app.init_db` lists a `claim` table; `pytest tests/test_claims.py` → 8 passed |
| 4 | 8 | Add the **premium calculation logic** | `app/services/pricing.py` | `pytest tests/test_pricing.py tests/test_quotes.py` green; *Get a quote* → ₹15,000.00 |

After Example 4: `pytest -m "not lab"` still green, and `pytest tests/test_pricing.py tests/test_quotes.py tests/test_policies.py tests/test_claims.py tests/test_pages.py` → all green.

---

## Phase 3 — Your own prompt: admin approval (25 min)

**Feature:** a claims officer reviews filed claims from a queue and approves or rejects each one with a reason.
Brief, rules, a prompt-writing template and the acceptance tests are in `docs/phase3-admin-approval.md`.

- 0–5 · Read the brief. As a team, write your prompt on paper first (Role · Context · Task · Constraints · Format).
- 5–20 · Run it, read the output, run `pytest tests/test_claims_admin.py` (6 tests). Iterate on the *prompt*, not just the code.
- 20–25 · Commit, push, open the Actions tab on your fork — the CI pipeline runs smoke → regression.

**Done when:** `pytest` (everything, no marker) is green · `PATCH /api/claims/{id}/status` follows the workflow · `GET /api/claims?status=Filed` is the queue · pushed to your fork.

---

## Wrap-up (last 5 min of Phase 3)

Each team: one thing the AI got wrong today and how you caught it. The handout (`docs/handout.md`) has a table for it.
