# Phase 2 — Four prompts with actual code outputs

*Day 1 · 30 minutes · do them in order · commit after each*

How to read each example: 📎 attach these files in Copilot Chat (`#file:`) · 💬 paste the prompt · **Output** — the code you should end up with (compare line by line; AI wording may differ, behaviour must not) · ▶ run · 🔍 check · ⚠️ what AI usually gets wrong.

> Tip: in Copilot Chat, `#file:app/models.py` attaches the file. In ChatGPT/Claude/Gemini you paste the file yourself.

---

## Example 1 — Add the Claim model to `app/models.py` (6 min)

📎 `#file:app/models.py`

💬
```
ROLE: senior Python engineer using SQLModel.
CONTEXT: the attached models.py has Customer, Product, Quote and Policy, each with a Base / table / Create / Read class.
TASK: add a Claim entity at the END of the file, following the same pattern exactly:
 1. class ClaimStatus(str, Enum) with FILED="Filed", UNDER_REVIEW="Under Review", APPROVED="Approved", REJECTED="Rejected" — put it next to the other enums.
 2. class ClaimBase(SQLModel): policy_id (foreign_key="policy.id"), amount (float, gt=0), description (str, min_length=5, max_length=500),
    incident_date (date), vehicle_registration (str | None, default None, description "Required for Motor claims").
 3. class Claim(ClaimBase, table=True): id primary key, status ClaimStatus default FILED, reason (str | None, default None),
    created_at datetime default_factory utcnow, and a Relationship policy: Policy back_populates="claims".
 4. class ClaimCreate(ClaimBase): pass.   class ClaimRead(ClaimBase): id, status, reason, created_at.
 5. class ClaimStatusUpdate(SQLModel): status: ClaimStatus, reason: str | None = None.
 6. On Policy add:  claims: list["Claim"] = Relationship(back_populates="policy")
CONSTRAINTS: no new imports beyond what the file already has. Do not change any existing class.
FORMAT: show only the new/changed code blocks with a one-line comment saying where each goes.
```

**Output** — what `models.py` gains:

```python
class ClaimStatus(str, Enum):          # next to PolicyStatus
    FILED = "Filed"
    UNDER_REVIEW = "Under Review"
    APPROVED = "Approved"
    REJECTED = "Rejected"
```
```python
    # inside class Policy(PolicyBase, table=True), after the other Relationships
    claims: list["Claim"] = Relationship(back_populates="policy")
```
```python
# --------------------------------------------------------------------------- #
# Claim                                                     (end of the file)
# --------------------------------------------------------------------------- #
class ClaimBase(SQLModel):
    policy_id: int = Field(foreign_key="policy.id")
    amount: float = Field(gt=0)
    description: str = Field(min_length=5, max_length=500)
    incident_date: date
    vehicle_registration: str | None = Field(default=None, description="Required for Motor claims")


class Claim(ClaimBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    status: ClaimStatus = Field(default=ClaimStatus.FILED)
    reason: str | None = Field(default=None, description="Why a claim was rejected")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    policy: Policy = Relationship(back_populates="claims")


class ClaimCreate(ClaimBase):
    pass


class ClaimRead(ClaimBase):
    id: int
    status: ClaimStatus
    reason: str | None
    created_at: datetime


class ClaimStatusUpdate(SQLModel):
    status: ClaimStatus
    reason: str | None = None
```

▶ `python -c "from app.models import Claim, ClaimStatus; print(Claim.__tablename__, list(ClaimStatus))"`
🔍 prints `claim [<ClaimStatus.FILED: 'Filed'>, …]`. Also `pytest -m "not lab"` still 15 passed (nothing existing broke).
⚠️ AI puts `Claim` **before** `Policy` (then `Policy` is undefined in the type hint — use the string `"Claim"` on Policy's side as shown) · forgets the `claims` relationship on `Policy` · invents `Field(sa_column=...)`.

**Commit:** `git commit -am "Phase 2.1: Claim model"`

---

## Example 2 — Add the claim endpoints in a new `app/routers/claims.py` (10 min)

Business rules (put them in your prompt — never assume AI knows them):

| # | Rule | Result |
|---|---|---|
| 1 | Policy must be **Active** | Cancelled → claim is *saved* as **Rejected** with reason "Policy is cancelled" · Lapsed → **422** |
| 2 | Incident date inside the policy period, **both ends inclusive** | 422 |
| 3 | Amount ≤ remaining cover = sum insured − **Approved** claims on the policy | 422 |
| 4 | Motor policy → vehicle registration required | 422 |

📎 `#file:app/routers/policies.py` `#file:app/models.py`

💬
```
ROLE: senior FastAPI engineer. CONTEXT: models.py now has Claim, ClaimCreate, ClaimRead, ClaimStatus; policies.py shows the house style.
TASK: create app/routers/claims.py with router = APIRouter(prefix="/api/claims", tags=["claims"]) and:
 - a helper approved_total(session, policy_id) -> float: sum of Claim.amount where status == APPROVED (use select + sum, 0.0 if none)
 - a helper remaining_cover(session, policy) -> float: policy.sum_insured - approved_total
 - a function file_claim(payload: ClaimCreate, session) -> Claim that enforces, in this order:
     1. policy = session.get(Policy, payload.policy_id); None -> HTTPException(status.HTTP_404_NOT_FOUND, "Policy not found")
     2. if policy.status == PolicyStatus.CANCELLED: build the Claim, set status=REJECTED and reason="Policy is cancelled", SAVE it and return it (201, not an error)
     3. if policy.status != PolicyStatus.ACTIVE: 422 "Policy is <status>; only Active policies accept claims"
     4. if not (policy.start_date <= payload.incident_date <= policy.end_date): 422 with the period in the message
     5. if payload.amount > remaining_cover(...): 422 "Claim amount exceeds remaining cover of {remaining:,.2f}"
     6. if policy.product.code == ProductCode.MOTOR and not (payload.vehicle_registration or "").strip(): 422 "Motor claims need a vehicle registration number"
     then Claim.model_validate(payload), add / commit / refresh, return
 - GET ""  list_claims(policy_id: int | None = None, status: ClaimStatus | None = None) -> list[ClaimRead], newest first, both filters optional
 - POST "" create_claim(payload) -> ClaimRead, status_code=201, calls file_claim
 - GET "/{claim_id}" -> 404 if missing
CONSTRAINTS: imports only from fastapi, sqlmodel, app.db, app.models. Same error style as policies.py. No PATCH endpoint yet (that is Phase 3).
FORMAT: the complete file.
```

**Output** — `app/routers/claims.py`:

```python
"""Claims API — file a claim against a policy and read claims back."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.models import Claim, ClaimCreate, ClaimRead, ClaimStatus, Policy, PolicyStatus, ProductCode

router = APIRouter(prefix="/api/claims", tags=["claims"])


def approved_total(session: Session, policy_id: int) -> float:
    rows = session.exec(
        select(Claim.amount).where(Claim.policy_id == policy_id, Claim.status == ClaimStatus.APPROVED)
    ).all()
    return float(sum(rows))


def remaining_cover(session: Session, policy: Policy) -> float:
    return policy.sum_insured - approved_total(session, policy.id)


def file_claim(payload: ClaimCreate, session: Session) -> Claim:
    policy = session.get(Policy, payload.policy_id)
    if not policy:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Policy not found")

    claim = Claim.model_validate(payload)

    # 1. policy status — cancelled is recorded as Rejected, lapsed is refused
    if policy.status == PolicyStatus.CANCELLED:
        claim.status = ClaimStatus.REJECTED
        claim.reason = "Policy is cancelled"
        session.add(claim)
        session.commit()
        session.refresh(claim)
        return claim
    if policy.status != PolicyStatus.ACTIVE:
        raise HTTPException(422, f"Policy is {policy.status.value.lower()}; only Active policies accept claims")

    # 2. incident inside the policy period (inclusive)
    if not (policy.start_date <= payload.incident_date <= policy.end_date):
        raise HTTPException(422, f"Incident date must fall within the policy period {policy.start_date} to {policy.end_date}")

    # 3. amount within remaining cover
    remaining = remaining_cover(session, policy)
    if payload.amount > remaining:
        raise HTTPException(422, f"Claim amount exceeds remaining cover of {remaining:,.2f}")

    # 4. Motor claims need a vehicle registration
    if policy.product.code == ProductCode.MOTOR and not (payload.vehicle_registration or "").strip():
        raise HTTPException(422, "Motor claims need a vehicle registration number")

    session.add(claim)
    session.commit()
    session.refresh(claim)
    return claim


@router.get("", response_model=list[ClaimRead])
def list_claims(
    policy_id: int | None = None,
    status: ClaimStatus | None = None,
    session: Session = Depends(get_session),
):
    stmt = select(Claim).order_by(Claim.created_at.desc())
    if policy_id:
        stmt = stmt.where(Claim.policy_id == policy_id)
    if status:
        stmt = stmt.where(Claim.status == status)
    return session.exec(stmt).all()


@router.post("", response_model=ClaimRead, status_code=status.HTTP_201_CREATED)
def create_claim(payload: ClaimCreate, session: Session = Depends(get_session)):
    return file_claim(payload, session)


@router.get("/{claim_id}", response_model=ClaimRead)
def get_claim(claim_id: int, session: Session = Depends(get_session)):
    claim = session.get(Claim, claim_id)
    if not claim:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Claim not found")
    return claim
```

▶ `python -c "import app.routers.claims; print('ok')"`
🔍 prints `ok`. The endpoints are not live yet — that's Example 3.
⚠️ `start < incident < end` (exclusive — the rule is inclusive) · counts *all* claims in remaining cover instead of Approved only · raises 422 for a cancelled policy instead of saving it as Rejected · imports `dateutil` or `pydantic.validator` (not needed).

**Commit:** `git add app/routers/claims.py && git commit -m "Phase 2.2: claim endpoints"`

---

## Example 3 — Create the database tables and register the router (6 min)

Two things must happen before `/api/claims` works: FastAPI must know the router, and SQLite must have a `claim` table. `SQLModel.metadata.create_all` creates any **missing** table; it never alters existing ones — which is exactly what we need here.

📎 `#file:app/main.py` `#file:app/db.py` `#file:app/seed.py`

💬
```
TASK (two parts, house style of the attached files):
1. In app/main.py: import claims from app.routers and add app.include_router(claims.router) right after the policies router.
2. Create app/init_db.py — a script run as `python -m app.init_db` that: calls create_db_and_tables() from app.db,
   opens a Session on `engine` and calls seed(session) from app.seed, then prints DATABASE_URL and, if it is SQLite,
   every table name with its row count (use the sqlite3 module and sqlite_master). Guard with if __name__ == "__main__".
   Module docstring must say it is safe to re-run (create_all only adds missing tables; seed only fills empty ones).
FORMAT: the two-line change to main.py, then the complete init_db.py.
```

**Output** — `app/main.py` (two lines):

```python
from app.routers import claims, customers, pages, policies, products, quotes
...
app.include_router(policies.router)
app.include_router(claims.router)
app.include_router(pages.router)
```

**Output** — `app/init_db.py`:

```python
"""Create every table declared in app/models.py and load the seed data.

Run from the repo root:   python -m app.init_db

Safe to run again: create_all only adds tables that are missing, and seed() only inserts when a table is empty.
Use it after adding a new model (e.g. Claim) so the table exists before you call the API.
"""
import sqlite3

from sqlmodel import Session

from app.db import DATABASE_URL, create_db_and_tables, engine
from app.seed import seed


def main() -> None:
    create_db_and_tables()
    with Session(engine) as session:
        seed(session)

    print(f"Database: {DATABASE_URL}")
    if DATABASE_URL.startswith("sqlite"):
        path = DATABASE_URL.split("sqlite:///", 1)[1]
        with sqlite3.connect(path) as conn:
            for (name,) in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
                (count,) = conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()
                print(f"  {name:<10} {count:>3} rows")


if __name__ == "__main__":
    main()
```

▶ `python -m app.init_db`
🔍
```
Database: sqlite:///./policydesk.db
  claim        0 rows
  customer     2 rows
  policy       2 rows
  product      3 rows
  quote        2 rows
```
▶ `pytest tests/test_claims.py -q` → **8 passed**. Restart `uvicorn`; `/docs` now shows the *claims* section. Try it: `POST /api/claims` with `{"policy_id": 1, "amount": 50000, "description": "Hospitalised for three days", "incident_date": "2026-03-10"}` → **201**, status `Filed`. Open `policydesk.db` in DBeaver (`docs/dbeaver-demo.md`) — the row is there.
⚠️ AI adds `create_all` calls into `models.py` or wants Alembic — not needed · forgets `if __name__ == "__main__"` · uses `DATABASE_URL.replace("sqlite:///", "")` which breaks on `sqlite:////tmp/…` (four slashes).

**Commit:** `git add -A && git commit -m "Phase 2.3: register claims router, init_db"`

---

## Example 4 — Add the Claims page (8 min)

The API works; now give the claims officer a screen. This example shows AI generating **UI** from an existing template — the pattern is "copy the style of page X".

📎 `#file:app/routers/pages.py` `#file:app/templates/policies.html` `#file:app/templates/_macros.html` `#file:app/templates/base.html`

💬
```
ROLE: senior FastAPI + Jinja2 engineer. CONTEXT: pages.py renders the HTML screens; policies.html is the list page to copy.
TASK, three parts:
 1. In app/routers/pages.py: import Claim and ClaimStatus from app.models; add templates.env.globals["ClaimStatus"] = ClaimStatus
    next to the PolicyStatus global; add a route GET "/claims" -> claims_list(request, status: str | None = None, session)
    that selects Claim ordered by created_at desc, filters by status when given, and renders "claims.html" with claims and status.
 2. Create app/templates/claims.html in exactly the style of policies.html: page-head (eyebrow "Claims", h1 "Claim <span class="hl">status</span>",
    p "{{ claims|length }} shown" plus "· filtered by {{ status }}" when set), tabs All + one per ClaimStatus value (?status=<value>),
    a card with a table: # · policy number (link /policies/{{ c.policy_id }}) · customer name (link /customers/{{ c.policy.customer_id }}) ·
    incident date (%d %b %Y) · description with "Reason: …" underneath when c.reason · amount via the money filter · pill(c.status).
    Empty state: "No claims" (+ " with status X" when filtered). Start with {% from "_macros.html" import pill %}.
 3. In app/templates/base.html add a nav link <a href="/claims" class="{{ 'active' if path.startswith('/claims') }}">Claims</a> after Policies.
CONSTRAINTS: reuse the existing CSS classes only (page-head, eyebrow, hl, tabs, card, table-wrap, pill, btn); no new CSS, no JS.
FORMAT: the pages.py additions, the complete claims.html, the one base.html line.
```

**Output** — `app/routers/pages.py` additions:

```python
from app.models import (          # add Claim and ClaimStatus to the existing import list
    Claim,
    ClaimStatus,
    ...
)

templates.env.globals["ClaimStatus"] = ClaimStatus     # next to the PolicyStatus global


# --------------------------------------------------------------------------- #
# Claims
# --------------------------------------------------------------------------- #
@router.get("/claims", response_class=HTMLResponse)
def claims_list(request: Request, status: str | None = None, session: Session = Depends(get_session)):
    stmt = select(Claim).order_by(Claim.created_at.desc())
    if status:
        stmt = stmt.where(Claim.status == status)
    return render(request, "claims.html", claims=session.exec(stmt).all(), status=status)
```

**Output** — `app/templates/claims.html`:

```html
{% extends "base.html" %}
{% from "_macros.html" import pill %}
{% block title %}Claims{% endblock %}
{% block content %}
<div class="page-head">
  <div class="container">
    <div>
      <span class="eyebrow">Claims</span>
      <h1>Claim <span class="hl">status</span></h1>
      <p>{{ claims | length }} shown{% if status %} · filtered by {{ status }}{% endif %}.</p>
    </div>
    <a class="btn btn--ghost" href="/policies">Browse policies</a>
  </div>
</div>

<section>
  <div class="container">
    <div class="tabs">
      <a href="/claims" class="{{ 'on' if not status }}">All</a>
      {% for s in ClaimStatus %}<a href="/claims?status={{ s.value }}" class="{{ 'on' if status == s.value }}">{{ s.value }}</a>{% endfor %}
    </div>
    <div class="card" style="padding:0">
      {% if claims %}
      <div class="table-wrap"><table>
        <thead><tr><th>#</th><th>Policy</th><th>Customer</th><th>Incident</th><th>Description</th><th class="num">Amount</th><th>Status</th></tr></thead>
        <tbody>
        {% for c in claims %}
          <tr>
            <td class="mono">{{ c.id }}</td>
            <td><a class="mono" href="/policies/{{ c.policy_id }}">{{ c.policy.policy_number }}</a></td>
            <td><a href="/customers/{{ c.policy.customer_id }}">{{ c.policy.customer.name }}</a></td>
            <td class="small">{{ c.incident_date.strftime('%d %b %Y') }}</td>
            <td class="small">{{ c.description }}{% if c.reason %}<br><span class="muted">Reason: {{ c.reason }}</span>{% endif %}</td>
            <td class="num">{{ c.amount | money }}</td>
            <td>{{ pill(c.status) }}</td>
          </tr>
        {% endfor %}
        </tbody>
      </table></div>
      {% else %}
      <div class="empty">No claims{% if status %} with status {{ status }}{% endif %}.</div>
      {% endif %}
    </div>
  </div>
</section>
{% endblock %}
```

**Output** — `app/templates/base.html` (one line, after the Policies link):

```html
        <a href="/claims" class="{{ 'active' if path.startswith('/claims') }}">Claims</a>
```

▶ Restart `uvicorn` (templates reload; new routes need a restart) → http://127.0.0.1:8000/claims
🔍 The claim you filed in Example 3 is listed with a **Filed** pill; the *Filed* tab shows it, the *Approved* tab shows the empty state. The `pill` macro colours the status automatically. `pytest -m "not lab"` still green.
⚠️ AI writes `c.customer.name` (Claim has no customer — go through `c.policy.customer`) · forgets the `ClaimStatus` global, so the tabs loop crashes with `UndefinedError` · invents CSS classes that don't exist in `theme.css`.

**Commit:** `git add -A && git commit -m "Phase 2.4: claims page"` then `git push`.

---

## End of Phase 2 — checklist

- [ ] `pytest -m "not lab"` green; `pytest tests/test_claims.py` → 8 passed (the remaining `lab` tests are Phase 3 and Day 2)
- [ ] `/docs` lists customers, products, quotes, policies, **claims** · the **Claims** page is in the nav
- [ ] Four commits on your fork, pushed; the Actions tab shows a green run
- [ ] You can explain every function you committed
