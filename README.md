# PolicyDesk — starter

A small, real insurance app — **customers → products → quotes → policies** — with the important parts missing.
In four labs you **build them yourself with AI prompts**: the **premium calculator**, **policy issuing**, the **claim form**
and the **claim approval** screen — then ship it through a **CI → Vercel** pipeline and finish a renewal feature at home.

*TalentPath Academy · AI-Powered SDLC Workshop* — start with [docs/workshop-guide.md](docs/workshop-guide.md)

| # | Session | Min | You build with prompts | Guide |
|---|---|---|---|---|
| 0 | Setup & explore | 30 | fork, `setup.bat`, read the code with Copilot | [workshop-guide](docs/workshop-guide.md) · [git-workflow](docs/git-workflow.md) |
| 1 | **Lab 1 · Premium calculator** | 45 | the four premium functions | [lab1-premium-calculator](docs/lab1-premium-calculator.md) |
| 2 | **Lab 2 · Issue a policy** | 45 | `issue_policy` + status change | [lab2-issue-policy](docs/lab2-issue-policy.md) |
| 3 | **Lab 3 · Claim form** | 50 | Claim model → claims API → Claims page → *File a claim* form | [lab3-claim-form](docs/lab3-claim-form.md) |
| 4 | **Lab 4 · Approve / reject** | 45 | review workflow (your own prompt) + Approve / Reject buttons on the Claims page | [lab4-claim-approval](docs/lab4-claim-approval.md) |
| — | Deployment pipeline | 30 | branch → PR → merge → Vercel deploys | [deployment](docs/deployment.md) |
| 5 | **Assignment** (take-home) | 60–90 | renewal quote with a 10% no-claim bonus | [assignment-renewal](docs/assignment-renewal.md) |

Keep [docs/handout.md](docs/handout.md) open — commands, the prompt pattern, where things are, troubleshooting.

## Start here

**Fork first** (top-right button) — you cannot push to this repo. Then clone **your fork**:

```bash
git clone https://github.com/<your-username>/policydesk-starter.git
```

### Windows — one click

Open the cloned `policydesk-starter` folder and **double-click `setup.bat`**. It:

1. checks **Python 3.12+** — installs it if missing
2. checks **Git** — installs it if missing (you need it to push)
3. checks **VS Code** — installs it if missing
4. creates and activates **`.venv`**
5. runs **`pip install -r requirements.txt`**

…then starts PolicyDesk and opens http://127.0.0.1:8000. No admin rights needed; safe to run again.
If Windows shows *"Windows protected your PC"*, click **More info → Run anyway**.

### By hand (macOS / Linux, or if `setup.bat` reports a problem)

```bash
cd policydesk-starter
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python check_setup.py           # everything [OK]?
uvicorn app.main:app --reload
```

- App: http://127.0.0.1:8000 · API docs: http://127.0.0.1:8000/docs · Health: http://127.0.0.1:8000/health
- On first start the app creates `policydesk.db` and seeds 3 products, 2 customers and 2 policies. Delete the file to reset.

```bash
pytest -m "not lab"               # 15 tests — what CI runs; must stay green
pytest tests/test_lab3_claims.py  # one lab's acceptance tests (red until you build it)
pytest -m "not assignment"        # everything — all green after Lab 4
pytest -m assignment              # the take-home assignment
```

## What's given, what you build

| | Given | You build |
|---|---|---|
| Models | Customer, Product, Quote, Policy | **Claim** (Lab 3) |
| API | customers, products, quotes, policies (read) | **`POST /api/policies`** + status (Lab 2) · **`/api/claims`** (Lab 3) · **`PATCH /api/claims/{id}/status`** (Lab 4) · **renewal quote** (assignment) |
| Rules | premium rules in the `pricing.py` docstring; policy rules in the `policies.py` docstring | **premium calculator** (Lab 1) · **`issue_policy`** (Lab 2) · claim rules (Lab 3) · approval workflow (Lab 4) |
| Screens | dashboard, customers, customer 360, products, quotes, quote detail, policies, policy detail | **Claims page** + **File a claim** form (Lab 3) · **Approve / Reject** buttons (Lab 4) |
| Tests | smoke + regression (given features) | `tests/test_lab1_*` … `test_lab4_*` and `test_assignment_*` are your acceptance criteria |

Search the code for `Lab 1`, `Lab 2` and `Lab 3` to find every spot you will change.

## The domain

```
Customer --+
           +--> Quote --(issue)--> Policy --(file)--> Claim --(review)--> Approved / Rejected
Product  --+
```

| Table | Key fields |
|---|---|
| **Customer** | name, email, phone, date_of_birth |
| **Product** | code (HEALTH / MOTOR / TERM_LIFE), base_rate, min/max sum insured |
| **Quote** | customer, product, sum_insured, tenure_years (1–3), add_ons, **premium** |
| **Policy** | policy_number, start/end date, status (Active / Lapsed / Cancelled), vehicle_registration |
| **Claim** *(you add)* | policy, amount, description, incident_date, status (Filed → Under Review → Approved / Rejected), reason |

**Premium** — `sum_insured × base_rate × age_factor × tenure_factor × add_on_factor`, min ₹1,000 (rules in `app/services/pricing.py`).
**Claim rules** — Active policy only (Cancelled → auto-Rejected, Lapsed → 422) · incident inside the period · amount ≤ sum insured − Approved claims · Motor needs a vehicle registration.

## API

| Method | Path | Given? |
|---|---|---|
| GET / POST | `/api/customers` | ✓ |
| GET | `/api/products` | ✓ |
| GET / POST | `/api/quotes` | ✓ (POST needs the premium calculator — Lab 1) |
| GET / POST | `/api/policies` · PATCH `/api/policies/{id}/status` | GET ✓ · POST + PATCH: Lab 2 |
| GET / POST | `/api/claims` · GET `/api/claims/{id}` · `?status=` `?policy_id=` | Lab 3 |
| PATCH | `/api/claims/{id}/status` | Lab 4 |
| POST | `/api/policies/{id}/renewal-quote` | Assignment |
| GET | `/health` | ✓ |

## CI/CD — GitHub Actions

Every push to your fork runs [`.github/workflows/ci.yml`](.github/workflows/ci.yml): **smoke (2) → regression (10)**. Tests marked `lab` are excluded, so the pipeline stays green while you work and only turns red if you break something that already worked. Enable Actions on your fork first (Settings → Actions → *Allow all actions*).

Deploy stages run only on the upstream repo (`main`) where the secrets live — they show as *skipped* on a fork. In the deployment session one team's PR into upstream `main` is merged and deploys to Vercel: https://policydesk-jet.vercel.app

## Project layout

```
app/
  main.py              FastAPI app, routers, startup seed         (Lab 3: register claims)
  db.py                engine + session (DATABASE_URL)
  models.py            SQLModel tables + schemas                  (Lab 3: add Claim)
  seed.py              products, customers, 2 policies
  services/pricing.py  premium rules                              (Lab 1)
  routers/             customers · products · quotes · policies (Lab 2) · pages (HTML)   (Lab 3: + claims.py, Claims page, form · Lab 4: buttons)
  templates/, static/  Jinja2 screens, TalentPath theme
tests/                 smoke · regression · test_lab1_* · test_lab2_* · test_lab3_* · test_lab4_* · test_assignment_*
docs/                  workshop-guide · lab1…lab4 guides · assignment-renewal · deployment · git-workflow · handout · setup-guide · dbeaver-demo
data/                  seed CSVs
```

---

TalentPath Academy · *Train. Learn. Grow. Succeed.*
