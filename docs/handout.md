# Student handout — quick reference & troubleshooting

*Keep this open in a tab for the whole session.*

## The session in one line each

| Phase | Min | You | Done when |
|---|---|---|---|
| 1 Fork & explore | 25 | fork → clone → run → 3 read-the-code prompts | app on :8000, `pytest -m "not lab"` = 15 passed, 1 commit |
| 2 Four prompts | 30 | Claim model → claim endpoints → DB tables → premium logic | `pytest` shows only `test_claims_admin.py` red, 4 commits |
| 3 Your prompt | 25 | admin approval workflow, prompt written by you | `pytest` = 80 passed, pushed, Actions green |

## Commands

```
.venv\Scripts\activate                      # macOS/Linux: source .venv/bin/activate
uvicorn app.main:app --reload               # http://127.0.0.1:8000  ·  API docs: /docs
pytest -m "not lab"                         # what CI runs — must stay green
pytest tests/test_claims.py -v              # one file, verbose
pytest                                      # everything (80 at the end)
python -m app.init_db                       # create missing tables + seed, list tables
git add -A && git commit -m "..." && git push
```

## The prompt pattern (every time)

```
ROLE        You are a senior Python/FastAPI engineer.
CONTEXT     #file:app/models.py #file:app/routers/policies.py   ← attach the real files
TASK        Implement <one function / one file> so that <behaviour>.
CONSTRAINTS Every rule, in order. Status codes. "No new imports." "Don't change X."
FORMAT      "Only the function" / "The complete file".
```
**Copilot Chat:** `Ctrl+Alt+I` · attach with `#file:path` · search with `@workspace` · `/explain` `/fix` `/tests` on selected code · inline edit with `Ctrl+I`.

## Validate every answer — 30 seconds

1. Does it import anything not in `requirements.txt`? (`fastapi`, `sqlmodel`, `pydantic`, `jinja2` only) → delete it, re-prompt.
2. Does it invent a column/field that isn't in `models.py`? → re-prompt: "use only the fields in the attached file".
3. Boundaries: `<` vs `<=`. Dates inclusive? Age 25 is *not* under 25.
4. Run the tests. Read the failing test name — it tells you the rule.
5. Can you explain every line to your teammate? If not, `/explain` it first.

## Where things are

| Need | File |
|---|---|
| Tables / fields | `app/models.py` |
| Premium rules | docstring at top of `app/services/pricing.py` |
| Example router to copy | `app/routers/policies.py` |
| Where routers are registered | `app/main.py` |
| DB connection | `app/db.py` (`DATABASE_URL`; the file is `policydesk.db`) |
| Seed data | `app/seed.py`, `data/*.csv` |
| Test fixtures (`client`, `ids`, `health_policy`, `motor_policy`) | `tests/conftest.py` |
| The four Phase 2 prompts + outputs | `docs/phase2-prompts.md` |
| Phase 3 brief + acceptance tests | `docs/phase3-admin-approval.md`, `tests/test_claims_admin.py` |
| Git steps | `docs/git-workflow.md` |

Seeded data: customers **Priya Nair** (id 1, Health policy `PD-HEALTH-2026-00001`, ₹5,00,000, 2026-01-01 → 2026-12-31) and **Rohan Das** (id 2, Motor policy `PD-MOTOR-2026-00002`, ₹8,00,000, vehicle `TS09AB1234`, 2026-03-01 → 2028-02-28).

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: fastapi` | venv not active — look for `(.venv)` in the prompt; activate; `pip install -r requirements.txt` |
| `'python' is not recognized` / opens Microsoft Store | reinstall Python with *Add to PATH* ticked, or use `py -3.12`; Settings → App execution aliases → turn off `python` |
| `Activate.ps1 cannot be loaded` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or use `.venv\Scripts\activate.bat` |
| `uvicorn: address already in use` | an old server is running — `Ctrl+C` there, or `--port 8001` |
| Page shows **501 "Phase 2, Example 4: implement calculate_premium"** | expected until Example 4 — the calculator isn't written yet |
| `/api/claims` → 404 Not Found | router not registered — Example 3 (`include_router` in `main.py`); restart uvicorn |
| `sqlite3.OperationalError: no such table: claim` | run `python -m app.init_db` (or delete `policydesk.db` and restart) |
| `ImportError: cannot import name 'Claim'` | Example 1 not saved, or `Claim` defined *after* it's used — check `models.py` order |
| `NameError: name 'Policy' is not defined` in models.py | `Claim` placed above `Policy` — move it to the end of the file |
| `pytest` → `No module named 'app'` | run from the repo root (where `pyproject.toml` is), or use `python -m pytest` |
| Test fails with `409` where you expected `200` | your transition table is too strict — read `ALLOWED_TRANSITIONS` you wrote |
| Test fails with `200` where you expected `409` | too loose — Filed → Approved must be refused; finals have no moves |
| `test_approved_claims_reduce_remaining_cover` fails | remaining cover must count **Approved** claims only |
| Copilot: "You've reached your monthly limit" | pair with a teammate's account for the session |
| `git push` → permission denied to `Abhinash1458/...` | you cloned the original — `git remote set-url origin https://github.com/<you>/policydesk-starter.git` |
| Actions tab empty on the fork | Settings → Actions → General → Allow all actions, then enable in the Actions tab |
| `TemplateNotFound` | template file name in `render(...)` doesn't match a file in `app/templates/` |

## What the AI got wrong today (fill in — 3 rows minimum)

| Phase | What we asked | What it got wrong | How we caught it | Fix |
|---|---|---|---|---|
| | | | | |
| | | | | |
| | | | | |

*TalentPath Academy · Train. Learn. Grow. Succeed.*
