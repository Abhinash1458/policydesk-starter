# Lab 3 — Claim form: file a claim against a policy

*50 minutes · five prompts, in order · commit after each*

Labs 1 and 2 gave you empty functions to fill in. This lab starts from **nothing**: there is no `Claim` table, no claims API
and no claims screen in the starter. You build all of it with five prompts, and finish with a **File a claim** form that any
customer-service agent could use.

| Step | Min | You build | File |
|---|---|---|---|
| 1 | 6 | the **Claim model** | `app/models.py` |
| 2 | 10 | the **claim endpoints** with the four business rules | `app/routers/claims.py` (new) |
| 3 | 6 | the **database table** + register the router | `app/main.py`, `app/init_db.py` (new) |
| 4 | 8 | the **Claims page** (list + status tabs) | `app/routers/pages.py`, `app/templates/claims.html` (new), nav link |
| 5 | 12 | the **File a claim form** | `app/routers/pages.py`, `app/templates/claim_form.html` (new), `claims.html` |

Acceptance tests: `pytest tests/test_lab3_claims.py -v` — **all red now**, all green when you finish Step 5.

How to read each step: 📎 attach these files in Copilot Chat (`#file:`) · 💬 paste the prompt · **Output** — the code you should end up with (compare line by line; AI wording may differ, behaviour must not) · ▶ run · 🔍 check · ⚠️ what AI usually gets wrong.

> Tip: in Copilot Chat, `#file:app/models.py` attaches the file. In ChatGPT/Claude/Gemini you paste the file yourself.

---

## Step 1 — Add the Claim model to `app/models.py` (6 min)

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

**Commit:** `git commit -am "Lab 3.1: Claim model"`

---

## Step 2 — Add the claim endpoints in a new `app/routers/claims.py` (10 min)

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
CONSTRAINTS: imports only from fastapi, sqlmodel, app.db, app.models. Same error style as policies.py. No PATCH endpoint yet (that is Lab 4).
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
🔍 prints `ok`. The endpoints are not live yet — that's Step 3.
⚠️ `start < incident < end` (exclusive — the rule is inclusive) · counts *all* claims in remaining cover instead of Approved only · raises 422 for a cancelled policy instead of saving it as Rejected · imports `dateutil` or `pydantic.validator` (not needed).

**Commit:** `git add app/routers/claims.py && git commit -m "Lab 3.2: claim endpoints"`

---

## Step 3 — Create the database tables and register the router (6 min)

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
  customer     2 rows      (more if you added customers)
  policy       2 rows      (more if you issued policies in Lab 2)
  product      3 rows
  quote        2 rows      (more if you created quotes in Lab 1)
```
▶ `pytest tests/test_lab3_claims.py -q` → the **8 API tests pass**; the 3 form tests stay red until Step 5. Restart `uvicorn`; `/docs` now shows the *claims* section. Try it: `POST /api/claims` with `{"policy_id": 1, "amount": 50000, "description": "Hospitalised for three days", "incident_date": "2026-03-10"}` → **201**, status `Filed`. Open `policydesk.db` in DBeaver (`docs/dbeaver-demo.md`) — the row is there.
⚠️ AI adds `create_all` calls into `models.py` or wants Alembic — not needed · forgets `if __name__ == "__main__"` · uses `DATABASE_URL.replace("sqlite:///", "")` which breaks on `sqlite:////tmp/…` (four slashes).

**Commit:** `git add -A && git commit -m "Lab 3.3: register claims router, init_db"`

---

## Step 4 — Add the Claims page (8 min)

The API works; now give the claims officer a screen. This step shows AI generating **UI** from an existing template — the pattern is "copy the style of page X".

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
🔍 The claim you filed in Step 3 is listed with a **Filed** pill; the *Filed* tab shows it, the *Approved* tab shows the empty state. The `pill` macro colours the status automatically. `pytest -m "not lab"` still green.
⚠️ AI writes `c.customer.name` (Claim has no customer — go through `c.policy.customer`) · forgets the `ClaimStatus` global, so the tabs loop crashes with `UndefinedError` · invents CSS classes that don't exist in `theme.css`.

**Commit:** `git add -A && git commit -m "Lab 3.4: claims page"`

---

## Step 5 — Add the File a claim form (12 min)

The API refuses bad claims; now a person needs a form to file good ones. The pattern is the one the starter already uses
for quotes: **GET shows the form, POST validates and either redirects on success or re-renders the form with the error**.
The form must call the **same `file_claim`** as the API — business rules live in one place only.

📎 `#file:app/routers/pages.py` `#file:app/templates/quote.html` `#file:app/templates/claims.html` `#file:app/routers/claims.py`

💬
```
ROLE: senior FastAPI + Jinja2 engineer. CONTEXT: pages.py has the /claims list and a quote form (quote_form / quote_submit) — copy
that pattern exactly. claims.py has file_claim(payload, session), which raises HTTPException (404 / 422) when a rule is broken.
TASK, three parts:
 1. In app/routers/pages.py
    - imports: add ClaimCreate to the app.models import, `from app.routers.claims import file_claim`, `from pydantic import ValidationError`
    - change claims_list so it ALSO passes flash=request.query_params.get("flash") and error=request.query_params.get("error")
    - helper active_policies(session) -> the Active policies ordered by policy_number
    - GET "/claims/new" -> claim_form(request, policy_id: int | None = None, session) renders "claim_form.html"
      with policies=active_policies(session) and form={"policy_id": policy_id}
    - POST "/claims/new" -> claim_submit(request, policy_id, amount, incident_date: date, description,
      vehicle_registration: str = "", session) — every field is a Form(...). Keep the typed values in a form dict.
      Build ClaimCreate (vehicle_registration stripped and upper-cased, "" becomes None) and call file_claim.
      pydantic ValidationError -> error = exc.errors()[0]["msg"];  HTTPException -> error = exc.detail.
      On error re-render claim_form.html with policies, form and error. On success redirect (303) to
      /claims?flash=Claim+<id>+<status value>
 2. Create app/templates/claim_form.html in the style of quote.html: page-head (eyebrow "Claims", h1 File a <span class="hl">claim</span>),
    a card with {{ alerts(error=error) }} and <form class="form" method="post" action="/claims/new"> containing:
    policy_id select (required; option text "policy number · customer name · product name"; selected when form.policy_id == p.id),
    amount (number, min 1, step 100, required), incident_date (date, default today(), required),
    description (textarea, minlength 5, maxlength 500, required), vehicle_registration (text, hint "Motor policies only"),
    and form__actions with "File claim →" (btn--primary) and Cancel (btn--ghost, href /claims).
    Keep typed values on re-render (value="{{ form.amount or '' }}" etc.).
 3. claims.html: import alerts as well as pill, show {{ alerts(flash=flash, error=error) }} above the tabs, and replace the
    "Browse policies" button with <a class="btn btn--primary" href="/claims/new">File a claim</a>.
CONSTRAINTS: existing CSS classes only, no JavaScript, do NOT change file_claim.
FORMAT: the pages.py code, the complete claim_form.html, the complete claims.html.
```

**Output** — `app/routers/pages.py`, new imports:

```python
from pydantic import ValidationError                  # with the other third-party imports

from app.models import (                              # add ClaimCreate to the existing list
    Claim,
    ClaimCreate,
    ClaimStatus,
    ...
)
from app.routers.claims import file_claim             # next to the other app.routers imports
```

**Output** — `claims_list` now passes the messages to the page:

```python
@router.get("/claims", response_class=HTMLResponse)
def claims_list(request: Request, status: str | None = None, session: Session = Depends(get_session)):
    stmt = select(Claim).order_by(Claim.created_at.desc())
    if status:
        stmt = stmt.where(Claim.status == status)
    return render(
        request,
        "claims.html",
        claims=session.exec(stmt).all(),
        status=status,
        flash=request.query_params.get("flash"),
        error=request.query_params.get("error"),
    )
```

**Output** — the form routes (end of `pages.py`, in the Claims section):

```python
def active_policies(session: Session) -> list[Policy]:
    return session.exec(
        select(Policy).where(Policy.status == PolicyStatus.ACTIVE).order_by(Policy.policy_number)
    ).all()


@router.get("/claims/new", response_class=HTMLResponse)
def claim_form(request: Request, policy_id: int | None = None, session: Session = Depends(get_session)):
    return render(request, "claim_form.html", policies=active_policies(session), form={"policy_id": policy_id})


@router.post("/claims/new", response_class=HTMLResponse)
def claim_submit(
    request: Request,
    policy_id: int = Form(...),
    amount: float = Form(...),
    incident_date: date = Form(...),
    description: str = Form(...),
    vehicle_registration: str = Form(""),
    session: Session = Depends(get_session),
):
    form = {
        "policy_id": policy_id,
        "amount": amount,
        "incident_date": incident_date,
        "description": description,
        "vehicle_registration": vehicle_registration,
    }
    try:
        claim = file_claim(
            ClaimCreate(
                policy_id=policy_id,
                amount=amount,
                incident_date=incident_date,
                description=description,
                vehicle_registration=vehicle_registration.strip().upper() or None,
            ),
            session,
        )
    except ValidationError as exc:  # a field broke the model rules, e.g. description too short
        error = exc.errors()[0]["msg"]
    except HTTPException as exc:  # a business rule refused the claim (404 / 422)
        error = exc.detail
    else:
        return RedirectResponse(f"/claims?flash=Claim+{claim.id}+{claim.status.value}", status_code=303)
    return render(request, "claim_form.html", policies=active_policies(session), form=form, error=error)
```

**Output** — `app/templates/claim_form.html`:

```html
{% extends "base.html" %}
{% from "_macros.html" import alerts %}
{% block title %}File a claim{% endblock %}
{% block content %}
<div class="page-head">
  <div class="container">
    <div>
      <span class="eyebrow">Claims</span>
      <h1>File a <span class="hl">claim</span></h1>
      <p>Pick an Active policy and describe what happened. The same rules as <span class="mono">POST /api/claims</span> apply.</p>
    </div>
  </div>
</div>

<section>
  <div class="container">
    <div class="card">
      {{ alerts(error=error) }}
      <form class="form" method="post" action="/claims/new">
        <div class="field">
          <label for="policy_id">Policy</label>
          <select name="policy_id" id="policy_id" required>
            <option value="" disabled {{ 'selected' if not form.policy_id }}>Select a policy…</option>
            {% for p in policies %}
            <option value="{{ p.id }}" {{ 'selected' if form.policy_id == p.id }}>{{ p.policy_number }} · {{ p.customer.name }} · {{ p.product.name }}</option>
            {% endfor %}
          </select>
        </div>
        <div class="form__row">
          <div class="field">
            <label for="amount">Claim amount (₹)</label>
            <input type="number" name="amount" id="amount" min="1" step="100" value="{{ form.amount or '' }}" required>
          </div>
          <div class="field">
            <label for="incident_date">Incident date</label>
            <input type="date" name="incident_date" id="incident_date" value="{{ form.incident_date or today().isoformat() }}" required>
          </div>
        </div>
        <div class="field">
          <label for="description">What happened?</label>
          <textarea name="description" id="description" rows="3" minlength="5" maxlength="500" required>{{ form.description or '' }}</textarea>
        </div>
        <div class="field">
          <label for="vehicle_registration">Vehicle registration</label>
          <input type="text" name="vehicle_registration" id="vehicle_registration" value="{{ form.vehicle_registration or '' }}">
          <span class="hint">Motor policies only.</span>
        </div>
        <div class="form__actions">
          <button class="btn btn--primary" type="submit">File claim →</button>
          <a class="btn btn--ghost" href="/claims">Cancel</a>
        </div>
      </form>
    </div>
  </div>
</section>
{% endblock %}
```

**Output** — `app/templates/claims.html` (the top changes; the table is the same as Step 4):

```html
{% extends "base.html" %}
{% from "_macros.html" import pill, alerts %}
{% block title %}Claims{% endblock %}
{% block content %}
<div class="page-head">
  <div class="container">
    <div>
      <span class="eyebrow">Claims</span>
      <h1>Claim <span class="hl">status</span></h1>
      <p>{{ claims | length }} shown{% if status %} · filtered by {{ status }}{% endif %}.</p>
    </div>
    <a class="btn btn--primary" href="/claims/new">File a claim</a>
  </div>
</div>

<section>
  <div class="container">
    {{ alerts(flash=flash, error=error) }}
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

▶ Restart `uvicorn` → http://127.0.0.1:8000/claims → **File a claim**
🔍 Try all three outcomes:
- a good Health claim (₹25,000, a date in 2026) → back on the Claims page with a green **"Claim … Filed"** banner
- the same claim dated **2027-02-01** → the form comes back with the red *"Incident date must fall within the policy period…"* message and **your typed values still filled in**
- a Motor claim without a vehicle number → *"Motor claims need a vehicle registration number"*

▶ `pytest tests/test_lab3_claims.py -v` → **11 passed**.
⚠️ AI writes its own validation in the form route (duplicate rules that drift from the API — delete them, call `file_claim`) · catches only `HTTPException`, so a 3-letter description crashes with a 500 (`ValidationError` must be caught too) · redirects with `status_code=302` (use **303** after a POST) · forgets to keep the typed values, so one mistake means retyping everything.

**Commit:** `git add -A && git commit -m "Lab 3.5: File a claim form"` then `git push`.

---

## End of Lab 3 — checklist

- [ ] `pytest tests/test_lab3_claims.py` → **11 passed** · `pytest -m "not lab"` still green
- [ ] `/docs` lists the *claims* section · the **Claims** page is in the nav · **File a claim** works and shows rule errors in red
- [ ] Five commits on your fork, pushed; the Actions tab shows a green run
- [ ] You can explain every function you committed — especially why the form calls `file_claim` instead of re-checking the rules
