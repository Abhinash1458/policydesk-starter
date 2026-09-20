# PolicyDesk — starter

A small, real insurance app — **customers → products → quotes → policies** — that you extend with AI in one 80-minute session:
add the **claims** feature from four worked prompts, then build an **admin approval** workflow from a prompt you write yourself.

*TalentPath Academy · AI-Powered SDLC Workshop*

| Phase | Min | You do | Guide |
|---|---|---|---|
| 1 · Fork & explore | 25 | fork this repo, run it, read the code with Copilot | [docs/workshop-guide.md](docs/workshop-guide.md) · [docs/git-workflow.md](docs/git-workflow.md) |
| 2 · Four prompts, real outputs | 30 | Claim model → claim endpoints → database tables → premium logic | [docs/phase2-prompts.md](docs/phase2-prompts.md) |
| 3 · Your own prompt | 25 | admin approval: review queue + Approve / Reject with reason | [docs/phase3-admin-approval.md](docs/phase3-admin-approval.md) |

Keep [docs/handout.md](docs/handout.md) open — commands, the prompt pattern, where things are, troubleshooting.

## Start here

**Fork first** (top-right button) — you cannot push to this repo. Then clone **your fork**:

```bash
git clone https://github.com/<your-username>/policydesk-starter.git
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
pytest                  # everything — 80 green when Phase 3 is done
```

## What's given, what you build

| | Given | You build |
|---|---|---|
| Models | Customer, Product, Quote, Policy | **Claim** (Phase 2, Ex. 1) |
| API | customers, products, quotes, policies | **`/api/claims`** — file, list, get (Ex. 2) · **`PATCH …/status`** (Phase 3) |
| Database | SQLite, auto-created, seeded | **`app/init_db.py`** + register the router (Ex. 3) |
| Rules | claim rules in your prompt; policy rules in `policies.py` | **premium calculator** in `pricing.py` (Ex. 4) |
| Screens | dashboard, customers, customer 360, products, quotes, quote detail, policies, policy detail | — (stretch: a claims page) |
| Tests | smoke + regression (given features) | lab-marked tests are your acceptance criteria |

Search the code for `Phase 2` and `Phase 3` to find every spot.

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
| GET / POST | `/api/quotes` | ✓ (POST needs the premium calculator — Ex. 4) |
| GET / POST | `/api/policies` · PATCH `/api/policies/{id}/status` | ✓ |
| GET / POST | `/api/claims` · GET `/api/claims/{id}` · `?status=` `?policy_id=` | Ex. 2–3 |
| PATCH | `/api/claims/{id}/status` | Phase 3 |
| GET | `/health` | ✓ |

## CI/CD — GitHub Actions

Every push to your fork runs [`.github/workflows/ci.yml`](.github/workflows/ci.yml): **smoke (2) → regression (10)**. Tests marked `lab` are excluded, so the pipeline stays green while you work and only turns red if you break something that already worked. Enable Actions on your fork first (Settings → Actions → *Allow all actions*).

Deploy stages (Render / Vercel) run only on the upstream repo's `main`/`solution` with secrets set — ignore them on a fork.

## Project layout

```
app/
  main.py              FastAPI app, routers, startup seed         (Ex. 3: register claims)
  db.py                engine + session (DATABASE_URL)
  models.py            SQLModel tables + schemas                  (Ex. 1: add Claim)
  seed.py              products, customers, 2 policies
  services/pricing.py  premium rules                              (Ex. 4)
  routers/             customers · products · quotes · policies · pages (HTML)   (Ex. 2: + claims.py)
  templates/, static/  Jinja2 screens, TalentPath theme
tests/                 smoke · regression · lab-marked targets (pricing, quotes, policies, pages, claims, claims_admin)
docs/                  workshop-guide · phase2-prompts · phase3-admin-approval · git-workflow · handout · setup-guide · dbeaver-demo
data/                  seed CSVs
```

---

TalentPath Academy · *Train. Learn. Grow. Succeed.*
