# Lab 4 — Approve or reject claims on the Claims page

*45 minutes · Part A: you write the prompt · Part B: the buttons · the tests decide when you're done*

In Lab 3 you were given the prompts. Now you write one. The skill being practised is **turning a business brief into a
prompt precise enough that the AI's first answer is nearly right** — and checking what comes back. Then you put the
decision on screen: **Approve / Reject buttons on every open claim** in the Claims page.

| Part | Min | You build | File |
|---|---|---|---|
| A | 25 | `PATCH /api/claims/{id}/status` — the review workflow, **with your own prompt** | `app/routers/claims.py` |
| B | 15 | **Review / Approve / Reject** buttons with a reason, on the Claims page | `app/routers/pages.py`, `app/templates/claims.html` |
| — | 5 | review, commit, push | |

Acceptance tests: `pytest tests/test_lab4_claim_approval.py -v` — 8 tests, **all red now**. Read them first: **they are the spec**.

---

## The brief (from the product owner)

> A claims officer works from a **queue of filed claims**. For each claim they either move it to *Under Review*, or decide:
> *Approve* or *Reject*, always with a **reason**. Once decided, a claim is final. A claim can only be approved if the policy
> still has enough cover left for it. The officer does all of this **from the Claims page**, without opening `/docs`.

### Rules

| # | Rule | HTTP result when broken |
|---|---|---|
| 1 | Allowed moves: **Filed → Under Review**, **Filed → Rejected**, **Under Review → Approved**, **Under Review → Rejected**. Nothing else. | **409** with a message naming both statuses |
| 2 | **Approved** and **Rejected** are final — no further changes | 409 |
| 3 | Approving is refused when `claim.amount` > remaining cover (sum insured − claims already Approved) | **422** with the remaining amount in the message |
| 4 | A `reason` sent with the change is stored on the claim; a move **without** a reason keeps the old one | — |
| 5 | Unknown claim id | 404 |
| 6 | The queue: `GET /api/claims?status=Filed` — already works from Lab 3 (the `?status=` filter). Confirm it. | — |

### Contract

```
PATCH /api/claims/{id}/status
body:     {"status": "Under Review" | "Approved" | "Rejected", "reason": "optional text"}
returns:  200 + the updated ClaimRead     (ClaimStatusUpdate already exists in models.py from Lab 3, Step 1)
```

---

## Part A — write your own prompt (25 min)

### A1 · Write it on paper first (5 min, as a team)

Fill every line before you type anything into Copilot.

```
ROLE:        ______________________________________________ (who should the AI be?)
CONTEXT:     which files will you attach?  ___________________________  (hint: the router you wrote in Lab 3, and models.py)
TASK:        one sentence — the endpoint to add and where
CONSTRAINTS: list every rule from the table above as an explicit statement, in the order they should be checked.
             Say where the allowed transitions should live (a dict? a function?) and that finals have NO allowed moves.
             Say which existing helper computes remaining cover (you already have one).
             Say what NOT to do: no new imports, don't touch file_claim, don't re-implement remaining cover.
FORMAT:      what do you want back — the whole file, or only the new code?
```

Things a weak prompt leaves out (and the AI then guesses wrong):
- that Filed → Approved is **not** allowed (it will allow it)
- that Approved/Rejected are final (it will allow Rejected → Under Review)
- that the cover check happens **only on Approved** (it will check on every change, or never)
- that `reason` is optional and must not wipe an existing reason with `None`

### A2 · Run it, read it, test it (15 min)

1. Paste your prompt with the attachments. Read the answer **before** pasting it in. Does it check the rules in your order?
2. Paste it into `app/routers/claims.py`. Run `pytest tests/test_lab4_claim_approval.py -v` — the **6 API tests** should go green (the 2 page tests wait for Part B).
3. For each red test: is the *code* wrong or was your *prompt* unclear? Fix the prompt, re-ask, compare. **That loop is the lesson.**
4. Try it live: `/docs` → `PATCH /api/claims/1/status` with `{"status": "Approved"}` straight from Filed → **409**. Then `Under Review` → 200 → `Approved` with a reason → 200. Check `GET /api/claims?status=Approved`.

### A3 · Stuck after 10 minutes? The reference prompt

Use it only after you have tried your own — then compare: what did yours miss?

📎 `#file:app/routers/claims.py` `#file:app/models.py`

💬
```
ROLE: senior FastAPI engineer. CONTEXT: claims.py (attached) has file_claim, remaining_cover and the list/get endpoints.
TASK: add the claim review workflow at the end of claims.py.
 1. A dict ALLOWED_TRANSITIONS: dict[ClaimStatus, set[ClaimStatus]]:
    FILED -> {UNDER_REVIEW, REJECTED}; UNDER_REVIEW -> {APPROVED, REJECTED}; APPROVED -> set(); REJECTED -> set()
 2. PATCH "/{claim_id}/status" update_claim_status(claim_id, payload: ClaimStatusUpdate, session) -> ClaimRead, checking in this order:
    a. claim = session.get(Claim, claim_id); None -> 404 "Claim not found"
    b. payload.status not in ALLOWED_TRANSITIONS[claim.status] -> 409 "Cannot move a claim from <current> to <new>"
    c. only when payload.status is APPROVED: if claim.amount > remaining_cover(session, claim.policy)
       -> 422 "Claim amount exceeds remaining cover of {remaining:,.2f}"
    d. set claim.status; set claim.reason ONLY if payload.reason is not empty; add / commit / refresh / return
CONSTRAINTS: reuse remaining_cover (do not re-implement it). Add ClaimStatusUpdate to the existing app.models import;
no other new imports. Do not change file_claim or the other endpoints.
FORMAT: only the new code.
```

**Output** — end of `app/routers/claims.py` (and add `ClaimStatusUpdate` to its `from app.models import …` line):

```python
ALLOWED_TRANSITIONS: dict[ClaimStatus, set[ClaimStatus]] = {
    ClaimStatus.FILED: {ClaimStatus.UNDER_REVIEW, ClaimStatus.REJECTED},
    ClaimStatus.UNDER_REVIEW: {ClaimStatus.APPROVED, ClaimStatus.REJECTED},
    ClaimStatus.APPROVED: set(),
    ClaimStatus.REJECTED: set(),
}


@router.patch("/{claim_id}/status", response_model=ClaimRead)
def update_claim_status(claim_id: int, payload: ClaimStatusUpdate, session: Session = Depends(get_session)):
    claim = session.get(Claim, claim_id)
    if not claim:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Claim not found")

    # 1-2. only the allowed moves; Approved and Rejected have none
    if payload.status not in ALLOWED_TRANSITIONS[claim.status]:
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"Cannot move a claim from {claim.status.value} to {payload.status.value}"
        )

    # 3. approving must fit in the cover that is left
    if payload.status == ClaimStatus.APPROVED:
        remaining = remaining_cover(session, claim.policy)
        if claim.amount > remaining:
            raise HTTPException(422, f"Claim amount exceeds remaining cover of {remaining:,.2f}")

    # 4. store the decision; a move without a reason keeps the old one
    claim.status = payload.status
    if payload.reason:
        claim.reason = payload.reason
    session.add(claim)
    session.commit()
    session.refresh(claim)
    return claim
```

**Commit:** `git add -A && git commit -m "Lab 4A: claim review workflow"`

---

## Part B — Approve / Reject buttons on the Claims page (15 min)

The API works; the officer should never need `/docs`. Each **open** claim gets a small form in its row: a reason box and
the buttons that are allowed for its status. The buttons post to a page route that calls **your `update_claim_status`** —
the rules stay in one place — and come back to the Claims page with a green or red banner (the banner already works
from Lab 3, Step 5).

📎 `#file:app/routers/pages.py` `#file:app/templates/claims.html` `#file:app/routers/claims.py`

💬
```
ROLE: senior FastAPI + Jinja2 engineer. CONTEXT: pages.py has the Claims page and the File a claim form; claims.html shows
flash / error banners already; claims.py has update_claim_status(claim_id, payload, session).
TASK, two parts:
 1. In app/routers/pages.py: import update_claim_status (next to file_claim) and add ClaimStatusUpdate to the app.models import.
    Add POST "/claims/{claim_id}/status" -> claim_decision(claim_id, status: ClaimStatus = Form(...), reason: str = Form(""), session)
    that calls update_claim_status(claim_id, ClaimStatusUpdate(status=status, reason=reason.strip() or None), session).
    HTTPException -> redirect 303 to /claims?error=<exc.detail>. Success -> redirect 303 to /claims?flash=Claim+<id>+<status value>
 2. In claims.html add a last column "Decision". For a Filed or Under Review claim show
    <form class="inline-form" method="post" action="/claims/{{ c.id }}/status"> with a text input name="reason"
    (placeholder "Reason", maxlength 300, style="width:130px") and buttons name="status":
      Filed        -> "Review" (value "Under Review", btn--ghost btn--sm) and "Reject" (value "Rejected", btn--danger btn--sm)
      Under Review -> "Approve" (value "Approved", btn--ok btn--sm) and "Reject" (value "Rejected", btn--danger btn--sm)
    For Approved / Rejected show <span class="muted small">Final</span>.
CONSTRAINTS: existing CSS classes only, no JavaScript, no rule checks in the route or the template — update_claim_status decides.
FORMAT: the pages.py code and the complete claims.html.
```

**Output** — `app/routers/pages.py` (imports: `from app.routers.claims import file_claim, update_claim_status` and add
`ClaimStatusUpdate` to the `app.models` list), then in the Claims section:

```python
@router.post("/claims/{claim_id}/status")
def claim_decision(
    claim_id: int,
    status: ClaimStatus = Form(...),
    reason: str = Form(""),
    session: Session = Depends(get_session),
):
    try:
        update_claim_status(claim_id, ClaimStatusUpdate(status=status, reason=reason.strip() or None), session)
    except HTTPException as exc:
        return RedirectResponse(f"/claims?error={exc.detail}", status_code=303)
    return RedirectResponse(f"/claims?flash=Claim+{claim_id}+{status.value}", status_code=303)
```

**Output** — `app/templates/claims.html`:

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
        <thead><tr><th>#</th><th>Policy</th><th>Customer</th><th>Incident</th><th>Description</th><th class="num">Amount</th><th>Status</th><th>Decision</th></tr></thead>
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
            <td>
              {% if c.status.value in ['Filed', 'Under Review'] %}
              <form class="inline-form" method="post" action="/claims/{{ c.id }}/status">
                <input type="text" name="reason" maxlength="300" placeholder="Reason" aria-label="Reason for claim {{ c.id }}" style="width:130px">
                {% if c.status.value == 'Filed' %}
                <button class="btn btn--ghost btn--sm" name="status" value="Under Review">Review</button>
                {% else %}
                <button class="btn btn--ok btn--sm" name="status" value="Approved">Approve</button>
                {% endif %}
                <button class="btn btn--danger btn--sm" name="status" value="Rejected">Reject</button>
              </form>
              {% else %}<span class="muted small">Final</span>{% endif %}
            </td>
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

▶ Restart `uvicorn` → http://127.0.0.1:8000/claims
🔍 Walk one claim through the whole workflow from the page:
- a **Filed** claim shows **Review** and **Reject** — no Approve
- click **Review** → green *"Claim 1 Under Review"* banner; the row now shows **Approve** and **Reject**
- type a reason, click **Approve** → **Approved** pill, *Reason: …* under the description, and the row says **Final**
- file a second claim larger than the cover that is left, Review it, click Approve → red banner *"…exceeds remaining cover…"* and the claim stays *Under Review*

▶ `pytest tests/test_lab4_claim_approval.py -v` → **8 passed**.
⚠️ AI re-checks the transitions inside the page route or hides buttons "cleverly" in the template and skips the server check (the server must still refuse — try a hand-made POST) · redirects with 302 · forgets `name="status"` on the buttons, so the route gets no status and answers 422 · shows Approve on a Filed claim.

**Commit:** `git add -A && git commit -m "Lab 4B: Approve / Reject on the Claims page"` then `git push`.

---

## Done when

- [ ] `pytest tests/test_lab4_claim_approval.py` → **8 passed** · `pytest -m "not lab"` still green
- [ ] A claim goes Filed → Under Review → Approved from the **Claims page**, with the reason shown
- [ ] Pushed to your fork; the Actions tab shows a green run
- [ ] On the team sheet: **your** final prompt from Part A, and one thing the AI got wrong on the first try

## Stretch (if you finish early)

- Drive the buttons from `ALLOWED_TRANSITIONS` (pass it to the template) instead of hard-coding the statuses in `claims.html` — then the rules really live in one place.
- Add `GET /api/claims/queue` returning only Filed and Under Review claims, oldest first.
- Ask the AI for a *review* of your router: "Which rule would break first if two officers approved claims on the same policy at the same time?"
