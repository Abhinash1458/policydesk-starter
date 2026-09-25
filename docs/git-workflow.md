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
git commit -m "Lab 3.1: Claim model"      # short, says what, not how
```

The commits you should have by the end:

| After | Message |
|---|---|
| Setup | `Setup and explore` |
| Lab 1 | `Lab 1: premium calculator` |
| Lab 2 | `Lab 2: issue policy and status` |
| Lab 3, Step 1 | `Lab 3.1: Claim model` |
| Lab 3, Step 2 | `Lab 3.2: claim endpoints` |
| Lab 3, Step 3 | `Lab 3.3: register claims router, init_db` |
| Lab 3, Step 4 | `Lab 3.4: claims page` |
| Lab 3, Step 5 | `Lab 3.5: File a claim form` |
| Lab 4, Part A | `Lab 4A: claim review workflow` |
| Lab 4, Part B | `Lab 4B: Approve / Reject on the Claims page` |
| Assignment | `Assignment: renewal quote with no-claim bonus` |

`git log --oneline` should read like a story of the session.

## 4 · Push and watch CI

```
git push                                  # first time: git push -u origin main
```
Then open **your fork → Actions**. The pipeline runs **smoke (2) → regression (10)** on every push. Green = you didn't break anything that was already working. Red = click the job, read the failing test name, fix, commit, push again.

The pipeline ignores tests marked `lab` (your unfinished targets) — so it stays green while you work, and only your regressions turn it red.

## 5 · Branch → pull request (the deployment session)

```
git checkout -b team-<name>-claims
git push -u origin team-<name>-claims
```
Then on GitHub: your fork → **Contribute → Open pull request** → base repository `Abhinash1458/policydesk-starter`, base branch `main`, compare `team-<name>-claims`. The PR runs the pipeline; when the instructor merges it, upstream `main` deploys to Vercel. Full steps: `docs/deployment.md`.

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
| compare with the expected code | every step's **Output** block is in its lab guide (`docs/lab*.md`) |

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `remote: Permission to Abhinash1458/policydesk-starter.git denied` | cloned the original, not your fork | `git remote set-url origin https://github.com/<you>/policydesk-starter.git` |
| `git push` asks for a password and rejects it | GitHub doesn't accept passwords | sign in to GitHub in VS Code (Accounts icon) — it sets up the credential helper — then push again |
| Actions tab says "Workflows aren't being run on this forked repository" | Actions not enabled on the fork | Settings → Actions → General → Allow all actions; Actions tab → enable |
| `policydesk.db` shows up in `git status` | it shouldn't — it's in `.gitignore` | `git rm --cached policydesk.db` if you force-added it |
| committed with the wrong name/email | identity not set | set it (above), then `git commit --amend --reset-author --no-edit` |
