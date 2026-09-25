# PolicyDesk — starter

A small, real insurance app — **customers → products → quotes → policies** — that you extend with AI over two days:
the **claims** feature from four worked prompts, an **admin approval** workflow from a prompt you write yourself, then the
**quotation calculator** and **issue-policy** rules, shipped through a **CI → Vercel** pipeline.

*TalentPath Academy · AI-Powered SDLC Workshop* — start with [docs/workshop-guide.md](docs/workshop-guide.md)

| Day | Session | Min | You do | Guide |
|---|---|---|---|---|
| 1 | Phase 1 · Fork & explore | 25 | fork this repo, run it, read the code with Copilot | [workshop-guide](docs/workshop-guide.md) · [git-workflow](docs/git-workflow.md) |
| 1 | Phase 2 · Four prompts, real outputs | 30 | Claim model → claim endpoints → database tables → Claims page | [phase2-prompts](docs/phase2-prompts.md) |
| 1 | Phase 3 · Your own prompt | 25 | admin approval: review queue + Approve / Reject with reason | [phase3-admin-approval](docs/phase3-admin-approval.md) |
| 2 | Lab 1 · Quotation calculator | 45 | the four premium functions | [day2-lab1-quotation](docs/day2-lab1-quotation.md) |
| 2 | Lab 2 · Issue a policy | 45 | `issue_policy` + status change | [day2-lab2-issue-policy](docs/day2-lab2-issue-policy.md) |
| 2 | Deployment pipeline | 30 | branch → PR → merge → Vercel deploys | [day2-deployment](docs/day2-deployment.md) |

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
pytest -m "not lab"     # 15 tests — what CI runs; must stay green
pytest -m lab           # your targets — fail on the starter by design
pytest                  # everything — 80 green at the end of Day 2
```

## What's given, what you build

| | Given | You build |
|---|---|---|
| Models | Customer, Product, Quote, Policy | **Claim** (Phase 2, Ex. 1) |
| API | customers, products, quotes, policies | **`/api/claims`** — file, list, get (Ex. 2) · **`PATCH …/status`** (Phase 3) |
| Database | SQLite, auto-created, seeded | **`app/init_db.py`** + register the router (Ex. 3) |
| Rules | claim rules in your prompt; policy rules in the `policies.py` docstring | **premium calculator** `pricing.py` (Day 2 Lab 1) · **`issue_policy` + status** (Day 2 Lab 2) |
| Screens | dashboard, customers, customer 360, products, quotes, quote detail, policies, policy detail | **Claims page** (Phase 2, Ex. 4) |
| Tests | smoke + regression (given features) | lab-marked tests are your acceptance criteria |

Search the code for `Phase 2`, `Phase 3`, `Day 2, Lab 1` and `Day 2, Lab 2` to find every spot.

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
| GET / POST | `/api/quotes` | ✓ (POST needs the premium calculator — Day 2 Lab 1) |
| GET / POST | `/api/policies` · PATCH `/api/policies/{id}/status` | GET ✓ · POST + PATCH: Day 2 Lab 2 |
| GET / POST | `/api/claims` · GET `/api/claims/{id}` · `?status=` `?policy_id=` | Ex. 2–3 |
| PATCH | `/api/claims/{id}/status` | Phase 3 |
| GET | `/health` | ✓ |

## CI/CD — GitHub Actions

Every push to your fork runs [`.github/workflows/ci.yml`](.github/workflows/ci.yml): **smoke (2) → regression (10)**. Tests marked `lab` are excluded, so the pipeline stays green while you work and only turns red if you break something that already worked. Enable Actions on your fork first (Settings → Actions → *Allow all actions*).

Deploy stages run only on the upstream repo (`main`) where the secrets live — they show as *skipped* on a fork. On Day 2 one team's PR into upstream `main` is merged and deploys to Vercel: https://policydesk-jet.vercel.app

## Project layout

```
app/
  main.py              FastAPI app, routers, startup seed         (Ex. 3: register claims)
  db.py                engine + session (DATABASE_URL)
  models.py            SQLModel tables + schemas                  (Ex. 1: add Claim)
  seed.py              products, customers, 2 policies
  services/pricing.py  premium rules                              (Day 2 Lab 1)
  routers/             customers · products · quotes · policies (Day 2 Lab 2) · pages (HTML)   (Ex. 2: + claims.py · Ex. 4: /claims page)
  templates/, static/  Jinja2 screens, TalentPath theme
tests/                 smoke · regression · lab-marked targets (pricing, quotes, policies, pages, claims, claims_admin)
docs/                  workshop-guide · phase2-prompts · phase3-admin-approval · day2-lab1-quotation · day2-lab2-issue-policy · day2-deployment · git-workflow · handout · setup-guide · dbeaver-demo
data/                  seed CSVs
```

---

TalentPath Academy · *Train. Learn. Grow. Succeed.*
