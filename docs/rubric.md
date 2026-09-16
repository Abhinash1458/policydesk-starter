# Rubric — PolicyDesk (100 points)

| Area | Points | What we look for |
|---|---|---|
| **Working features** | 40 | Claims module (20): claim can be filed from the policy screen and the API; all 4 validation rules enforced; workflow Filed → Under Review → Approved / Rejected; remaining cover updates. Student pages (20): Quotes list, Customer 360 and Claim review work end-to-end and match the given pages' look (see `docs/scenarios.md`). Deployed URL works. |
| **Tests** | 20 | pytest covers each claim rule with at least one passing and one failing case; boundary dates (first/last day of the period); the cancelled-policy auto-reject. Tests pass in CI/locally. |
| **AI-validation evidence** | 20 | Team shows at least 2 concrete things the AI got wrong (hallucinated API, wrong boundary, missing check) and how they caught it. Prompts and corrections in `docs/ai-log.md`. |
| **Demo** | 10 | 90 seconds: URL, one end-to-end flow, one AI mistake and the fix. Every team member speaks. |
| **Code quality** | 10 | Readable names, no dead code, validation in the service layer (not the router), README updated, no secrets committed. |

**Stretch (+5 each, max +10):** dashboard chart of claims by status · CSV export of claims · e-mail-style notification log on status change.

## Scoring bands

| Total | Band |
|---|---|
| 85–100 | Ship it |
| 70–84 | Solid — polish needed |
| 50–69 | Working, gaps in tests or validation |
| < 50 | Incomplete |
