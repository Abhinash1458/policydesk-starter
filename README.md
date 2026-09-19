# PolicyDesk — starter

> **You are on the `solution` branch.** Every Lab 1/2/3 TODO and all three scenario pages are implemented and
> covered by 80 tests (`pytest`). Students clone `main`; trainers use this branch for live demos and as the
> answer key. Do not share it before Day 2.

A simplified insurance **quote → policy → claim** application, built for the
TalentPath Academy **AI-Powered SDLC Workshop** — small enough to read in an hour, real enough to
write tests, find bugs and deploy.

**This is the starter repo.** The app has **11 pages — 8 are given, 3 you build** (see the Screens table below
and [docs/scenarios.md](docs/scenarios.md)). The database, models, theme and the given screens are done.
You build the rest, lab by lab — every TODO is marked in the code:

Three labs, **one feature each** — rules → API → page → tests:

| Lab | Feature | Where | What you build |
|---|---|---|---|
| **Lab 1** | Quote | `app/services/pricing.py` | the premium calculator (4 small functions) |
| | | `app/routers/quotes.py` | `price_quote` + `POST /api/quotes` |
| | | `app/routers/pages.py` + `app/templates/quotes.html` | **Scenario 1 — Quotes list page** |
| | | `tests/test_pricing.py`, `tests/test_pages.py` | pricing tests (find the one the AI got wrong), one page test |
| **Lab 2** | Policy | `app/routers/policies.py` | `issue_policy` + `PATCH /api/policies/{id}/status` |
| | | `app/routers/pages.py` + `app/templates/customer_detail.html` | **Scenario 2 — Customer 360 page** |
| | | `tests/test_policies.py`, `tests/test_pages.py` | policy tests, Customer 360 tests |
| **Lab 3** | Claim | `app/services/claims.py`, `app/routers/claims.py` | claim rules + file / review endpoints (**tests first** in `tests/test_claims.py`) |
| | | `app/routers/pages.py` + `app/templates/claim_detail.html` | **Scenario 3 — Claim review page** |
| Ship | — | `README.md`, Render | docs + deploy + read the logs |
| Stretch | — | `git checkout bugs` | 5 seeded bugs, refactor, AI code review |

Search the code for `TODO (Lab 1)`, `TODO (Lab 2)`, `TODO (Lab 3)` to find every spot. In the app, the three student
pages show a placeholder with the brief until you replace them. Behind? `git checkout lab1-complete` or `lab2-complete`.

**Start here:** [docs/lab1-prompt-guide.md](docs/lab1-prompt-guide.md), [lab2](docs/lab2-prompt-guide.md), [lab3](docs/lab3-prompt-guide.md) — one guide per lab with every prompt,
in order, with what to paste and what to check. Log what the AI gets wrong in [docs/ai-log.md](docs/ai-log.md).

| Stack | |
|---|---|
| Backend | Python 3.12+ · FastAPI · SQLModel (SQLite) |
| UI | Jinja2 templates + vanilla CSS/JS (TalentPath Academy theme) |
| Tests | pytest + FastAPI TestClient |
| Deploy | Render.com free web service (`render.yaml`) |

## Run it

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- App: http://127.0.0.1:8000
- Swagger API docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

On first start the app creates `policydesk.db` and seeds 3 products and 2 demo customers from `data/`.
Delete the file to reset.

```bash
pytest            # run the test suite
pytest -v         # verbose
pytest -m smoke        # the 2 smoke tests CI runs first
pytest -m regression   # the 10 regression tests CI runs next
pytest -m "not lab"    # everything except student targets that are still TODO
```

## CI/CD — GitHub Actions

Every push and pull request to `main` runs [`.github/workflows/ci.yml`](.github/workflows/ci.yml) on GitHub's free
`ubuntu-latest` runner:

```
smoke (2 tests)  ──►  regression (10 tests)  ──►  deploy to Render (main only)
```

| Stage | What runs | If it fails |
|---|---|---|
| **Smoke** | `tests/test_smoke.py` — `/health` answers, home page serves HTML | pipeline stops here |
| **Regression** | `tests/test_regression.py` — seed data, customers API (201/409/422/404), given pages render; then `pytest -m "not lab"` | no deploy |
| **Deploy** | `POST` to the Render deploy hook in the `RENDER_DEPLOY_HOOK` secret | — (skipped with a notice if the secret is not set) |

Tests marked `@pytest.mark.lab` (e.g. `tests/test_pricing.py`) fail on the starter on purpose — they are your lab
targets. CI ignores them until you delete the marker, which you should do the moment your implementation passes.
Watch the **Actions** tab after you push: green means your feature did not break anything that was already working.

To enable deploys: Render → your service → Settings → **Deploy Hook** → copy the URL → GitHub repo → Settings →
Secrets and variables → Actions → **New repository secret** `RENDER_DEPLOY_HOOK`.

### Vercel (second target, also gated by the tests)

The `deploy-vercel` job runs after regression on pushes to `main` and `solution`. It uses the Vercel CLI on the
runner (`vercel pull` → `vercel build` → `vercel deploy --prebuilt --prod`) and then curls `/health` on the live URL.
Vercel's own push-to-deploy is disabled in `vercel.json` (`git.deploymentEnabled: false`) so **only green pipelines
ship**. Live: https://policydesk-jet.vercel.app

Three repository secrets are needed (the job skips with a notice until they exist):

| Secret | Where to get it |
|---|---|
| `VERCEL_TOKEN` | vercel.com → Account → Settings → **Tokens** → Create (scope: the team, expiry: your choice) |
| `VERCEL_ORG_ID` | `.vercel/project.json` → `orgId` after one `vercel link` / `vercel deploy` |
| `VERCEL_PROJECT_ID` | `.vercel/project.json` → `projectId` |

The app is unchanged for Vercel; [`api/index.py`](api/index.py) is the entry point and SQLite lives in `/tmp` (reset on
every cold start — demo only).

## The domain

```
Customer --+
           +--> Quote --(issue)--> Policy --(file)--> Claim
Product  --+
```

| Table | Key fields |
|---|---|
| **Customer** | name, email, phone, date_of_birth |
| **Product** | code (HEALTH / MOTOR / TERM_LIFE), base_rate, min/max sum insured |
| **Quote** | customer, product, sum_insured, tenure_years (1–3), add_ons, **premium** |
| **Policy** | policy_number, start/end date, status (Active / Lapsed / Cancelled), vehicle_registration |
| **Claim** | policy, amount, description, incident_date, status (Filed → Under Review → Approved / Rejected) |

### Premium rules — `app/services/pricing.py`

```
premium = sum_insured x base_rate x age_factor x tenure_factor x add_on_factor   (min Rs 1,000)
```

| Factor | Values |
|---|---|
| Age | < 25 → 1.2 Motor / 0.8 Health & Life · 25–45 → 1.0 · 46–60 → 1.3 · > 60 → 1.6 |
| Tenure | 1 yr → 1.0 · 2 yr → 0.95 · 3 yr → 0.90 |
| Add-ons | Health `CRITICAL_ILLNESS` +15% · Motor `ZERO_DEPRECIATION` +10% |

### Claim rules — `app/services/claims.py`

1. Policy must be **Active** (Cancelled → claim is stored as auto-**Rejected**; Lapsed → refused)
2. Incident date must be inside the policy period
3. Amount ≤ sum insured − already-approved claims
4. Motor claims need a vehicle registration number
5. Status flow: Filed → Under Review → Approved / Rejected (Approved and Rejected are final)

## API

| Method | Path | Purpose |
|---|---|---|
| GET / POST | `/api/customers` | list / create customers |
| GET | `/api/products` | list products |
| GET / POST | `/api/quotes` | list / **calculate & save a quote** |
| GET / POST | `/api/policies` | list (`?status_filter=`) / **issue a policy from a quote** |
| PATCH | `/api/policies/{id}/status` | Active / Lapsed / Cancelled |
| GET / POST | `/api/claims` | list (`?policy_id=`) / **file a claim** |
| PATCH | `/api/claims/{id}/status` | move a claim through its workflow |
| GET | `/health` | liveness check |

## Screens (11 pages)

| # | Page | Route | Status |
|---|---|---|---|
| 1 | Dashboard | `/` | given |
| 2 | Customers | `/customers` | given |
| 3 | Customer 360 | `/customers/{id}` | **you build — Scenario 2** |
| 4 | Products | `/products` | given |
| 5 | Get a quote | `/quotes/new` | given (pricing = Lab 1) |
| 6 | Quote detail / issue policy | `/quotes/{id}` | given |
| 7 | Quotes list | `/quotes` | **you build — Scenario 1** |
| 8 | Policies | `/policies` | given |
| 9 | Policy detail / file claim | `/policies/{id}` | given |
| 10 | Claims | `/claims` | given |
| 11 | Claim review | `/claims/{id}` | **you build — Scenario 3** |

## Project layout

```
app/
  main.py              FastAPI app, routers, startup seed
  db.py                engine + session
  models.py            SQLModel tables + request/response schemas
  seed.py              loads data/*.csv on first start
  services/pricing.py  premium rules (pure functions — unit-test these)
  services/claims.py   claim validation + status transitions
  routers/             customers · products · quotes · policies · claims · pages (HTML)
  templates/           Jinja2 screens
  static/              theme.css · app.js · favicon.svg
tests/                 pytest suite (you add test_pricing.py, test_claims.py, ...)
data/                  seed CSVs
docs/                  lab1|lab2|lab3-prompt-guide (start here), labs, scenarios, prompt-guide, prompts, rubric, ai-log, setup-guide
```

## Deploy to Render

1. Push this repo to GitHub.
2. Render → **New → Blueprint** → pick the repo. `render.yaml` sets the build/start commands.
3. Open the URL; `/health` should return `{"status": "ok"}`.

Environment variables: `DATABASE_URL` (default `sqlite:///./policydesk.db`), `APP_ENV` (`dev` / `prod`).

---

TalentPath Academy · *Train. Learn. Grow. Succeed.*
