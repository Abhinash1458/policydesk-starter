# Day 2 · second half — Deployment pipeline (30 min)

*Branch → push → pull request → merge → Vercel deploys. That's the whole thing.*

```
your fork                          upstream: Abhinash1458/policydesk-starter                    Vercel
────────────────                   ──────────────────────────────────────────                  ──────────────────
git push -u origin <branch>  ──►   Pull request → branch `workshop`  ──►  CI on the PR:          
                                   smoke (2) → regression (10) ✓                                
                                   instructor clicks Merge  ──►  push to `workshop`  ──►  CI again  ──►  deploy-vercel  ──►  live URL /health
```

**Every team** does steps 1–2. **One team** (chosen by the instructor) does step 3 on the projector. Everyone watches step 4.

## 1 · Put your work on a branch (5 min, every team)

You've been committing on `main` of your fork. Move today's work to a named branch and push it:

```
git checkout -b team-<name>-claims          # e.g. team-falcon-claims
git push -u origin team-<name>-claims
```
Your fork on GitHub now shows the branch. *Actions* tab → the push ran **smoke → regression** on it.

> Why a branch? A pull request is a request to merge **a branch** into another. `main` on your fork is your safety copy; the branch is what you offer upstream.

## 2 · Check the pipeline is green on your branch (5 min, every team)

Fork → **Actions** → the latest run → both jobs green. If red: click the job, read the failing test name, fix, commit, push again. **A PR with a red pipeline will not be merged.**

## 3 · One team opens the pull request (5 min, on the projector)

On your fork's page: **Contribute → Open pull request** (or *Compare & pull request* banner).

| Field | Value |
|---|---|
| base repository | `Abhinash1458/policydesk-starter` |
| **base branch** | **`workshop`** ← not `main` (main is the starter every other student clones) |
| head repository | `<your-username>/policydesk-starter` |
| compare | `team-<name>-claims` |
| title | `Team <name>: claims feature + admin approval` |
| description | 3 lines: what you built · `pytest` count · one thing the AI got wrong |

*Create pull request.* Watch the **Checks** section on the PR: the same smoke → regression run, this time on the merged result. Green tick = safe to merge.

## 4 · Merge → deploy (10 min, instructor drives, everyone watches)

1. Instructor: **Merge pull request → Confirm merge**.
2. Upstream → **Actions**: a new run on `workshop` — smoke ✓ → regression ✓ → **Deploy to Vercel** runs (this job only runs on the upstream repo, where the Vercel secrets live — it's *skipped* on forks).
3. Open the *Deploy to Vercel* job: `vercel pull` → `vercel build` → `vercel deploy --prebuilt --prod` → `curl /health`.
4. Open the live URL → **https://policydesk-jet.vercel.app/health** → `{"status":"ok"}` → the dashboard → *Claims* in the nav — the team's code, live.

That's the pipeline: **tests gate the merge, the merge triggers the deploy.** Nobody deployed by hand.

## 5 · Three questions to close (5 min)

1. What would have happened if a regression test had failed on the PR? *(Red check — the merge button turns grey by policy, nothing ships.)*
2. Why do the deploy secrets live on the upstream repo and not on your fork? *(Forks can't read upstream secrets — a PR from a stranger can't deploy your app.)*
3. Where is the data on Vercel, and what happens on the next cold start? *(`/tmp/policydesk.db` — reset. Demo only; a real app needs Postgres, one `DATABASE_URL` away.)*

## Cheat-sheet

```
git checkout -b team-<name>-claims       # branch
git push -u origin team-<name>-claims    # push (runs CI on your fork)
# then on GitHub: Contribute → Open pull request → base: Abhinash1458/policydesk-starter  branch: workshop
```

| Problem | Fix |
|---|---|
| "Compare & pull request" offers base `main` | change the base branch dropdown to **`workshop`** |
| PR checks red | fix on your branch, `git push` — the PR updates itself |
| "This branch has conflicts" | `git fetch upstream && git merge upstream/workshop`, resolve, push |
| Deploy job *skipped* on my fork | expected — secrets are upstream only |
| Live site shows old data / no claims | Vercel cold start reset `/tmp` — file a claim again from `/docs` |
