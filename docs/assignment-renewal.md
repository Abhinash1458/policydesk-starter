# Assignment — Renew a policy with a no-claim bonus

*Take-home · after Labs 1–4 · about 60–90 minutes · you write every prompt*

This assignment puts all four labs together. There is no worked prompt and no expected code — only the brief, the rules,
the contract and the acceptance tests. Plan it, prompt it, read what comes back, and let the tests tell you when it is right.

## The brief (from the product owner)

> When a policy is about to expire, the customer should get a **renewal quote**: the same cover for another term, priced at
> **today's** rates and the customer's **current age**. Customers who made **no approved claim** on the policy get a
> **10% no-claim bonus**. A renewal quote is an ordinary quote — the agent issues it the usual way, starting the day after
> the old policy ends.

## Rules

| # | Rule | Result when broken |
|---|---|---|
| 1 | Unknown policy | **404** |
| 2 | Only **Active** policies can be renewed (Lapsed and Cancelled cannot) | **409** |
| 3 | Same customer, product, sum insured, tenure and add-ons as the policy's **original quote** | — |
| 4 | Price it with **your Lab 1 calculator** — current age (`age_on`), the product's base rate and sum-insured limits | 422 if the calculator refuses |
| 5 | **No-claim bonus:** if the policy has **no Approved claim**, take 10% off. Filed, Under Review and Rejected claims do **not** cost the bonus | — |
| 6 | The bonus never takes the premium below `MIN_PREMIUM`; round to 2 decimals | — |
| 7 | Save it as a normal `Quote`, so Lab 2's `issue_policy` can turn it into a policy | — |

## Contract

```
POST /api/policies/{policy_id}/renewal-quote        (no body)
returns: 201 + QuoteRead   (the new quote, with its premium)
```

Worked example — Priya's seeded Health policy (₹5,00,000, 1 year, no add-ons), no claims approved:
full price today = 5,00,000 × 0.03 × age factor × 1.0 → with the bonus, **90%** of that.
Once one of her claims is **Approved**, the renewal quote costs the full price.

## Acceptance tests

```
pytest -m assignment -v
```

Six tests, all red now. Read them before you write a single prompt — they show exactly how the endpoint is called and
what counts as a correct answer (they even compute the expected premium with your own Lab 1 functions).

## Plan your prompts

You will probably need **two or three** prompts. Fill this in for each one before you open Copilot:

```
ROLE:        ______________________________________________
CONTEXT:     which files will you attach?   (hint: policies.py, pricing.py, models.py — what does each give the AI?)
TASK:        one sentence
CONSTRAINTS: every rule above that this prompt is responsible for, in the order they must be checked.
             Which EXISTING functions must be re-used, not re-written?  (calculate_premium, age_on, parse_add_ons …)
             Where does the 10% live — a constant in pricing.py, or a magic number in the router?
FORMAT:      only the new code, or the whole file?
```

Questions to settle **before** you prompt (the AI will guess if you don't):
- Where do the tenure and add-ons come from — the policy, or the policy's original quote?
- Which claims count against the bonus — all claims, or only Approved ones?
- What happens to the bonus on a premium that is already at the ₹1,000 minimum?
- Does renewing change the old policy? (It must not — the renewal is just a quote.)

## Try it end to end

1. `/docs` → `POST /api/policies/1/renewal-quote` → **201**; note the premium.
2. Approve a claim on policy 1 from the **Claims page** (Lab 4) and ask again → higher premium, no bonus.
3. `POST /api/policies` with the new `quote_id` and `start_date` = the day after the old `end_date` → a new policy (Lab 2).
4. `PATCH /api/policies/1/status` → `Cancelled`, ask again → **409**.

## Hand in

- [ ] `pytest -m assignment` → **6 passed**, and `pytest` → everything green
- [ ] A commit `Assignment: renewal quote with no-claim bonus`, pushed to your fork, green in Actions
- [ ] `docs/my-assignment-notes.md` in your fork with: your final prompts, one thing the AI got wrong, and how the tests caught it

## Stretch

- A **Renew** button on the policy detail page that creates the renewal quote and opens it (`/quotes/{id}`), ready to issue.
- Show the bonus on the quote page: "10% no-claim bonus applied" — without adding a column to the database (hint: compare with the full price).
- Make the bonus grow with loyalty: 10% after one claim-free term, 15% after two. What would you need to store?
