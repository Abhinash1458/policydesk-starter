# PolicyDesk workshop — four labs

*TalentPath Academy · AI-Powered SDLC*

You are given a working insurance app — customers, products, quotes and policies — with the important parts missing.
In four labs you **build them yourself with AI prompts**: the premium calculator, policy issuing, the claim form, and the
claim approval screen. Then you ship it through a **CI → Vercel pipeline**, and finish a renewal feature at home.

| # | Session | Min | You build with prompts | Guide | Tests |
|---|---|---|---|---|---|
| 0 | Setup & explore | 30 | fork, `setup.bat`, read the code with Copilot | this page | `pytest -m "not lab"` |
| 1 | **Lab 1 · Premium calculator** | 45 | the four premium functions in `pricing.py` | [lab1-premium-calculator](lab1-premium-calculator.md) | `tests/test_lab1_*.py` |
| 2 | **Lab 2 · Issue a policy** | 45 | `issue_policy` + policy status change | [lab2-issue-policy](lab2-issue-policy.md) | `tests/test_lab2_policies.py` |
| 3 | **Lab 3 · Claim form** | 50 | Claim model → claims API → Claims page → *File a claim* form | [lab3-claim-form](lab3-claim-form.md) | `tests/test_lab3_claims.py` |
| 4 | **Lab 4 · Approve / reject claims** | 45 | review workflow (your own prompt) + Approve / Reject buttons on the Claims page | [lab4-claim-approval](lab4-claim-approval.md) | `tests/test_lab4_claim_approval.py` |
| — | Deployment pipeline | 30 | branch → PR → merge → Vercel deploys | [deployment](deployment.md) | CI on GitHub |
| 5 | **Assignment** (take-home) | 60–90 | renewal quote with a 10% no-claim bonus — every prompt yours | [assignment-renewal](assignment-renewal.md) | `pytest -m assignment` |

Run it in one day, or split it: **Day 1** setup + Labs 1–2 · **Day 2** Labs 3–4 + deployment.

**One rule all session:** AI writes the first draft — you read every line, run the tests, and commit only what you understand.

---

## 0 · Setup & explore (30 min)

### 0.1 Fork, clone, one-click setup (10 min) — full git steps in [git-workflow](git-workflow.md)

1. Open https://github.com/Abhinash1458/policydesk-starter → **Fork** → *Create fork* (your account, keep the name).
2. Clone **your fork** (not the original):
   ```
   git clone https://github.com/<your-username>/policydesk-starter.git
   ```
3. **Windows:** open the cloned `policydesk-starter` folder and double-click **`setup.bat`**. It installs Python 3.12, Git
   and VS Code if they are missing, creates and activates `.venv`, installs `requirements.txt` and starts the app.
   (*"Windows protected your PC"* → **More info → Run anyway**.)
   **macOS / Linux**, or if `setup.bat` says FAILED:
   ```
   cd policydesk-starter
   python -m venv .venv
   source .venv/bin/activate          # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
4. Open http://127.0.0.1:8000 — dashboard, 2 customers, 3 products, 2 policies already there. Open http://127.0.0.1:8000/docs — the API.
5. `pytest -m "not lab"` → **15 passed**. (`pytest -m lab` fails — those are your targets for the four labs.)

### 0.2 Read the code with Copilot (15 min)

Open Copilot Chat (`Ctrl+Alt+I`). Run these three prompts and write the answers on your team sheet.

**Map** — `@workspace`
```
@workspace Summarise this project in one paragraph. Then give me a table of every file under app/ with one line each.
Which files mention "Lab 1", "Lab 2" or "Lab 3"? Which feature is missing compared to the flow Customer -> Quote -> Policy -> Claim?
```
**Data** — `#file:app/models.py`
```
Explain the four tables and how they link (foreign keys and Relationship fields). For each table: which fields does the
user supply and which does the system set? What would a Claim table need to link to?
```
**House style** — `#file:app/routers/policies.py`
```
Read the module docstring and the given functions. List the conventions I must copy in new code: how a row is fetched,
how errors are raised and with which status codes, how a row is saved, and how a router is registered in app/main.py.
```
✅ You should be able to say: `session.get(Model, id)` · `HTTPException(status.HTTP_404_NOT_FOUND, "…")` · `add / commit / refresh` · `status_code=201` on create · `app.include_router(...)` in `main.py`.

**Commit:** `git add -A && git commit -m "Setup and explore" && git push`

---

## Labs 1–4 — the loop every time

1. **Read the problem statement** in the lab guide and run the lab's tests — see them fail.
2. **Prompt:** attach the files the guide lists, paste (or write) the prompt.
3. **Read** the answer before pasting it. Compare with the guide's *Output* — wording may differ, behaviour must not.
4. **Test** — the lab's test file. Red? Decide: was the *code* wrong or the *prompt* unclear? Fix the prompt first.
5. **Commit** after every step (the guides give the message), push at the end of the lab.

| Lab | Done when |
|---|---|
| **1 · Premium calculator** | `pytest tests/test_lab1_pricing.py tests/test_lab1_quotes.py tests/test_lab1_pages.py` green · *Get a quote* → ₹15,000.00 |
| **2 · Issue a policy** | `pytest tests/test_lab2_policies.py` → 8 passed · issue → 31 Dec end date → re-issue 409 → cancel → 409 |
| **3 · Claim form** | `pytest tests/test_lab3_claims.py` → 11 passed · **File a claim** works and shows rule errors in red |
| **4 · Approve / reject** | `pytest tests/test_lab4_claim_approval.py` → 8 passed · a claim goes Filed → Under Review → Approved from the Claims page |

After Lab 4: `pytest -m "not assignment"` → **everything green** (the assignment tests stay red until you do it at home).

**Behind?** Every step's expected code is printed in its guide — paste the *Output* blocks, read them, run the tests, and
move on. Lab 3 does not need Labs 1–2 (it uses the two seeded policies), so a team stuck on the calculator can still do the claims labs.

---

## Wrap-up (last 5 min of each day)

Each team: one thing the AI got wrong and how you caught it. The handout ([handout](handout.md)) has a table for it.
