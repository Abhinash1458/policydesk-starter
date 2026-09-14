# Student scenarios — three pages you build end-to-end

PolicyDesk has 11 pages. Eight are given. **You build three**, each as a full vertical slice:
route in `app/routers/pages.py` → query → Jinja2 template in `app/templates/` → link it into the nav/tables → a test in `tests/test_pages.py`.

In the starter the nav links already exist; each of these pages shows a placeholder until you replace it.
Copy the structure of a given page (`policies.html` for lists, `policy_detail.html` for detail pages) — same cards, pills and tables.

| # | Page | Route | Template | When |
|---|---|---|---|---|
| 1 | Quotes list | `GET /quotes` | `quotes.html` | Day 1 · Lab 4 (after the quotes API works) |
| 2 | Customer 360 | `GET /customers/{id}` | `customer_detail.html` | Day 1 homework / Day 2 warm-up |
| 3 | Claim review | `GET /claims/{id}` | `claim_detail.html` | Day 2 · Final project (with the claims module) |

---

## Scenario 1 — Quotes list  (`/quotes`)

**As an** agent **I want** to see every quote and whether it became a policy **so that** I can follow up on open quotes.

**Done when**
- [ ] Table: #, customer (link to Customer 360), product, sum insured, tenure, premium, created date
- [ ] Status pill: **Open** (no policy yet) or **Converted** (links to the policy)
- [ ] Action: *Issue policy* button for open quotes → `/quotes/{id}`; *View policy* for converted
- [ ] Filter tabs: All / Open / Converted, and by product (`?status=open&product=MOTOR`)
- [ ] Header shows "N shown · M still open"
- [ ] Empty state when nothing matches
- [ ] Test: open quote appears under `?status=open` and not under `?status=converted`

**Hints** — `quote.policy` is `None` until a policy is issued. Join `Product` to filter by code. Look at `policies.html` for the tabs pattern.

**Validate the AI** — did it filter in SQL where it could (product) and in Python only where it must (open/converted)? Did it invent a `Quote.status` column that does not exist?

---

## Scenario 2 — Customer 360  (`/customers/{id}`)

**As an** agent **I want** one page with everything about a customer **so that** I can answer a phone call without clicking around.

**Done when**
- [ ] Header: name, email, phone, age; button *New quote for <first name>* → `/quotes/new?customer_id={id}` (the form pre-selects the customer)
- [ ] Four stat tiles: quotes, policies (with active count), annual premium total (excluding cancelled), claims
- [ ] Policies table (number → policy page, product, sum insured, premium, period, status)
- [ ] Claims table across all their policies (# → claim review, policy number, incident date, amount, status)
- [ ] Profile card and a compact quotes list (Open / Converted)
- [ ] 404 for an unknown id
- [ ] Customer names in the customers list, policy page and claims list link here
- [ ] Test: page shows the policy number and the premium total

**Hints** — `customer.policies` and `customer.quotes` are relationships; claims are `p.claims for p in customer.policies`. Sort newest first.

**Validate the AI** — is the premium total excluding cancelled policies? Does it crash for a customer with no policies?

---

## Scenario 3 — Claim review  (`/claims/{id}`)

**As a** claims officer **I want** the claim with its policy context and the allowed next actions **so that** I decide with the full picture.

**Done when**
- [ ] Three tiles: claimed amount, remaining cover (of sum insured), "within cover?" yes/no
- [ ] Claim card: incident date (with the policy period beside it), description, vehicle (Motor), filed time, status + reason
- [ ] Policy context card: customer (link), product, policy status, sum insured, other claims on the policy
- [ ] Decision card: workflow steps, a *reason* textarea, and **only the allowed next actions** as buttons
  (Filed → Move to review / Reject · Under Review → Approve / Reject · final states → an info note)
- [ ] *Approve* is disabled when the amount exceeds remaining cover
- [ ] Submitting posts to the existing `POST /claims/{id}/status` with a hidden `back=/claims/{id}` so you land back here with a flash
- [ ] 404 for an unknown id; claim ids in the claims list, policy page and dashboard link here
- [ ] Test: Filed claim shows *Move to review* but not *Approved*; after approving with a reason the page shows "final state" and the reason

**Hints** — `ALLOWED_TRANSITIONS` and `remaining_cover` in `app/services/claims.py` already know the rules; don't re-implement them in the template.

**Validate the AI** — did it put business rules (which transitions are allowed) into the template instead of reusing the service? Does *Approve* appear straight from *Filed*?

---

### Scoring (part of the final rubric)
Each scenario: works end-to-end 5 · matches the given pages' look 2 · test passes 2 · one AI mistake caught and noted in `docs/ai-log.md` 1 = **10 points each**.
