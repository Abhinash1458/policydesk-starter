# Git workflow — fork, commit after every step, push, watch CI

You cannot push to `Abhinash1458/policydesk-starter` — it isn't yours. You work on **your own fork**. Every step below is copy-paste.

## 1 · Fork (once, in the browser)

1. https://github.com/Abhinash1458/policydesk-starter → **Fork** (top right) → keep the name → **Create fork**.
2. You now have `https://github.com/<your-username>/policydesk-starter`. **Every command below uses that URL.**
3. On your fork: **Settings → Actions → General → Allow all actions** (forks have Actions disabled by default). Then the **Actions** tab → *I understand my workflows, go ahead and enable them*.

## 2 · Clone your fork (once)

```
git clone https://github.com/<your-username>/policydesk-starter.git
cd policydesk-starter
git remote -v            # origin must be YOUR username, not Abhinash1458
```
If `origin` shows `Abhinash1458`, you cloned the original — delete the folder and clone your fork.

Set your identity once (any machine): `git config --global user.name "Your Name"` · `git config --global user.email "you@example.com"`

## 3 · Commit after every step

The rhythm for the whole session: **change → test → commit**. Never commit red tests.

```
pytest -m "not lab"                       # must be green
git status                                # see what changed
git add -A
git commit -m "Phase 2.1: Claim model"    # short, says what, not how
```

The commits you should have by the end:

| After | Message |
|---|---|
| Phase 1 | `Phase 1: setup and explore` |
| Example 1 | `Phase 2.1: Claim model` |
| Example 2 | `Phase 2.2: claim endpoints` |
| Example 3 | `Phase 2.3: register claims router, init_db` |
| Example 4 | `Phase 2.4: premium calculation` |
| Phase 3 | `Phase 3: admin approval workflow` |
| Day 2 Lab 1 | `Day 2 Lab 1: quotation calculator` |
| Day 2 Lab 2 | `Day 2 Lab 2: issue policy and status` |

`git log --oneline` should read like a story of the session.

## 4 · Push and watch CI

```
git push                                  # first time: git push -u origin main
```
Then open **your fork → Actions**. The pipeline runs **smoke (2) → regression (10)** on every push. Green = you didn't break anything that was already working. Red = click the job, read the failing test name, fix, commit, push again.

The pipeline ignores tests marked `lab` (your unfinished targets) — so it stays green while you work, and only your regressions turn it red.

## 5 · Day 2: branch → pull request (the deployment session)

```
git checkout -b team-<name>-claims
git push -u origin team-<name>-claims
```
Then on GitHub: your fork → **Contribute → Open pull request** → base repository `Abhinash1458/policydesk-starter`, **base branch `workshop`** (not `main`), compare `team-<name>-claims`. The PR runs the pipeline; when the instructor merges it, the upstream `workshop` branch deploys to Vercel. Full steps: `docs/day2-deployment.md`.

## 6 · If the original repo changes during the day (instructor says "pull the fix")

```
git remote add upstream https://github.com/Abhinash1458/policydesk-starter.git   # once
git fetch upstream
git merge upstream/main                   # resolve conflicts if any, then commit
```

## 7 · Undo safely

| I want to… | Command |
|---|---|
| throw away uncommitted changes in one file | `git checkout -- app/routers/claims.py` |
| throw away all uncommitted changes | `git stash` (recoverable with `git stash pop`) |
| see what a commit changed | `git show --stat HEAD` |
| go back one commit but keep the changes | `git reset --soft HEAD~1` |
| see the solution for comparison (after the session) | `git fetch upstream && git checkout upstream/solution -- app/routers/claims.py` |

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `remote: Permission to Abhinash1458/policydesk-starter.git denied` | cloned the original, not your fork | `git remote set-url origin https://github.com/<you>/policydesk-starter.git` |
| `git push` asks for a password and rejects it | GitHub doesn't accept passwords | sign in to GitHub in VS Code (Accounts icon) — it sets up the credential helper — then push again |
| Actions tab says "Workflows aren't being run on this forked repository" | Actions not enabled on the fork | Settings → Actions → General → Allow all actions; Actions tab → enable |
| `policydesk.db` shows up in `git status` | it shouldn't — it's in `.gitignore` | `git rm --cached policydesk.db` if you force-added it |
| committed with the wrong name/email | identity not set | set it (above), then `git commit --amend --reset-author --no-edit` |
