# Phase 3 — Your own prompt: the admin approval feature

*25 minutes · you write the prompt · the tests decide when you're done*

In Phase 2 you were given the prompts. Now you write one. The skill being practised is **turning a business brief into a prompt precise enough that the AI's first answer is nearly right** — and validating what comes back.

## The brief (from the product owner)

> A claims officer works from a **queue of filed claims**. For each claim they either move it to *Under Review*, or decide: *Approve* or *Reject*, always with a **reason**. Once decided, a claim is final. A claim can only be approved if the policy still has enough cover left for it.

### Rules

| # | Rule | HTTP result when broken |
|---|---|---|
| 1 | Allowed moves: **Filed → Under Review**, **Filed → Rejected**, **Under Review → Approved**, **Under Review → Rejected**. Nothing else. | **409** with a message naming both statuses |
| 2 | **Approved** and **Rejected** are final — no further changes | 409 |
| 3 | Approving is refused when `claim.amount` > remaining cover (sum insured − claims already Approved) | **422** with the remaining amount in the message |
| 4 | A `reason` sent with the change is stored on the claim | — |
| 5 | Unknown claim id | 404 |
| 6 | The queue: `GET /api/claims?status=Filed` — already works from Example 2 (`?status=` filter). Confirm it. | — |

### Contract

```
PATCH /api/claims/{id}/status
body:     {"status": "Under Review" | "Approved" | "Rejected", "reason": "optional text"}
returns:  200 + the updated ClaimRead     (ClaimStatusUpdate already exists in models.py)
```

## Acceptance tests — run them before you start

```
pytest tests/test_claims_admin.py -v
```
Six tests, all red. Read them — **they are the spec** (transitions, 409s, remaining cover, reason, the queue filter). When they're green, you're done.

## Write your prompt (5 min, on paper, as a team)

Use the pattern. Fill every line before you type anything into Copilot.

```
ROLE:        ______________________________________________ (who should the AI be?)
CONTEXT:     which files will you attach?  ___________________________  (hint: the router you wrote in Example 2, and models.py)
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

## Run it, read it, test it (15 min)

1. Paste your prompt with the attachments. Read the answer **before** pasting it in. Does it check the rules in your order?
2. Paste it into `app/routers/claims.py`. `pytest tests/test_claims_admin.py -v`.
3. For each red test: is the *code* wrong or was your *prompt* unclear? Fix the prompt, re-ask, compare. That loop is the lesson.
4. Try it live: `/docs` → `PATCH /api/claims/1/status` with `{"status": "Approved"}` straight from Filed → **409**. Then `Under Review` → 200 → `Approved` with a reason → 200. Check `GET /api/claims?status=Approved`.

## Done when

- [ ] `pytest` (no marker) — everything green, **80 passed**
- [ ] `git add -A && git commit -m "Phase 3: admin approval workflow" && git push`
- [ ] Actions tab on your fork: green run
- [ ] On the team sheet: your final prompt, and one thing the AI got wrong on the first try

## Stretch (if you finish early)

- Add `GET /api/claims/queue` returning only Filed and Under Review claims, oldest first.
- Add an HTML page `/claims` listing claims with Approve / Reject buttons (copy the style of `policies.html`; the form should POST to a small page route that calls `update_claim_status`).
- Ask the AI for a *review* of your router: "Which rule would break first if a second officer approved the same claim at the same time?"
