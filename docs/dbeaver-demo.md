# Look inside the database — DBeaver demo (5 min)

*Use right after Lab 3, Step 3 — the moment the `claim` table appears.*

**The point:** the app is just Python writing rows into tables. When you `POST /api/claims`, `session.commit()` in
`file_claim()` inserts one row into `claim`. Nothing magic — and you can see it.

## Where the data is

| Where the app runs | The SQLite file | Survives? |
|---|---|---|
| Your laptop | `policydesk-starter/policydesk.db` (repo root, git-ignored) | Yes, until you delete it |
| Render | `./policydesk.db` on the instance | Until the next deploy — free tier has no persistent disk |
| Vercel | `/tmp/policydesk.db` | No — wiped on every cold start |

`DATABASE_URL` in `app/db.py` decides. That's the env var the deployment session breaks on purpose.

## Setup (once, 3 min)

1. Install **DBeaver Community** (free): https://dbeaver.io/download/ — or `winget install DBeaver.DBeaver.Community` on Windows.
2. Open DBeaver → **Database → New Database Connection → SQLite → Next**.
3. *Path* → **Browse** → pick `policydesk-starter/policydesk.db` → **Finish**. First time it asks to download the SQLite driver — click **Download**.
4. In the left panel expand **PolicyDesk → Databases → policydesk → Tables**. Five tables: `customer`, `product`, `quote`, `policy`, `claim`.

> Tip: keep `uvicorn` running — SQLite allows one writer, many readers. Press **F5** in DBeaver after doing something in the app.

## The demo

1. **Before:** open `claim` → *Data* tab. Zero rows.
2. In `/docs`: `POST /api/claims` with `{"policy_id": 1, "amount": 50000, "description": "Hospitalised for three days", "incident_date": "2026-03-10"}`.
3. **After:** back in DBeaver, **F5**. One new row: `status = FILED`, `reason = NULL`, `created_at` set by the system.
4. Open the **ER Diagram** tab on the database → the five tables and their foreign keys. Which table did you add today? Which foreign key links it?
5. **SQL Editor** (Ctrl+]) — run these, one at a time:

```sql
-- the join the Customer 360 page does in Python
SELECT c.name, p.policy_number, pr.name AS product, p.premium, p.status
FROM policy p
JOIN customer c ON c.id = p.customer_id
JOIN product  pr ON pr.id = p.product_id;

-- remaining cover: what validate_claim() checks (only APPROVED claims count)
SELECT p.policy_number,
       p.sum_insured,
       COALESCE(SUM(CASE WHEN cl.status = 'APPROVED' THEN cl.amount END), 0) AS approved,
       p.sum_insured - COALESCE(SUM(CASE WHEN cl.status = 'APPROVED' THEN cl.amount END), 0) AS remaining_cover
FROM policy p LEFT JOIN claim cl ON cl.policy_id = p.id
GROUP BY p.id;

-- open quotes = quotes with no policy (what the Quotes page filters in Python)
SELECT q.id, q.premium FROM quote q LEFT JOIN policy p ON p.quote_id = q.id WHERE p.id IS NULL;
```

6. **Break the rule from the outside:** in the `policy` Data tab, edit policy 2's `status` to `CANCELLED` and press **Save** (Ctrl+S). Back in `/docs`, file a claim on policy 2 → it comes back **201 with status Rejected** and the reason. *The rule lives in the code; the data lives in the table.*

## Questions to ask the room

- Why is `premium` stored on `policy` when it's already on `quote`? *(Prices change; a policy is a snapshot.)*
- Where would `remaining_cover` go if we added it as a column? What could go wrong? *(It's derived — storing it invites drift.)*
- What happens to this file when Render redeploys? So what would a real insurer use? *(Postgres — same `DATABASE_URL`, one line.)*
