# Pre-workshop setup guide

*Software requirements and installation steps — for every participant*

Do all of this **before Day 1**. It takes about 60–90 minutes on a normal home connection. Every step ends with a way to check it worked, and `check_setup.py` verifies everything at the end.

| | |
|---|---|
| **Timing** | Sessions start at 9:00 AM IST · 3 hours of session each day, not counting the break |
| **Before Day 1** | Complete every step and bring the `check_setup.py` output (or a screenshot) with you |
| **Platforms** | Windows 10/11 (primary), macOS 12+, Ubuntu 22.04/24.04 |
| **Cost** | Everything in this guide is free — no credit card is needed anywhere |
| **Help** | info@talentpathacademy.com · +91 87900 02007 |

---

## 1. What you need and why

Nine things, all free. Install them **in this order** — later steps depend on earlier ones (Copilot needs VS Code and a GitHub account; the project needs Python and Git).

| # | Tool | Version | What we use it for |
|---|---|---|---|
| 1 | Python | 3.12 or newer (64-bit) | Runs the PolicyDesk backend (FastAPI), tests (pytest) and the setup checker |
| 2 | Git | 2.40 or newer | Version control; needed by Copilot, GitHub and Render |
| 3 | Visual Studio Code | Latest | The editor where AI writes and explains code with you |
| 4 | VS Code extensions | — | Python, Pylance, GitHub Copilot, GitHub Copilot Chat, SQLite Viewer |
| 5 | GitHub account | — | Hosts your team's repo, signs you into Copilot and Render |
| 6 | GitHub Copilot | Free tier, or Pro via Student Pack | AI code completion and chat inside VS Code |
| 7 | AI chat account | any one | ChatGPT, Claude.ai or Gemini — for requirements, design, test-case and review prompts |
| 8 | Render account | — | Deploys your app to a public URL on Day 2 |
| 9 | Project setup | — | Clone the starter, create a virtual environment, run `check_setup.py` |

### Minimum laptop requirements

| Item | Minimum | Recommended |
|---|---|---|
| Operating system | Windows 10 (64-bit), macOS 12, Ubuntu 22.04 | Windows 11, macOS 14, Ubuntu 24.04 |
| RAM | 8 GB | 16 GB |
| Free disk space | 5 GB | 10 GB |
| Internet | Required throughout both days (Copilot and AI chat are cloud services) | Mobile hotspot as backup |
| Admin rights | Needed to install Python, Git and VS Code | — |
| Charger | Bring it — sessions are 3 hours | Extension cord for your team |

> **Managed laptops** — A college laptop with a locked-down account can block installs and Copilot's network calls. If yours is managed by IT, do the installs early and ask IT to allow `github.com`, `*.githubcopilot.com` and `pypi.org`.

---

## 2. Step 1 — Install Python 3.12

We use 3.12 because every library in the workshop is tested against it. If you already have 3.12, 3.13 or 3.14, keep it. Python 3.11 or older is too old; uninstall it or install 3.12 alongside.

**Windows**

1. Open https://www.python.org/downloads/windows/ and download *Python 3.12.x — Windows installer (64-bit)*.
2. Run the installer. On the first screen tick **both** boxes at the bottom: *Use admin privileges when installing py.exe* and **Add python.exe to PATH**. This is the step people miss.
3. Click *Install Now*. At the end click *Disable path length limit* if it is offered, then Close.
4. Open a **new** PowerShell window (Start → type PowerShell) and check:

```
python --version
python -m pip --version
```

Expected: `Python 3.12.x` and a pip line. If PowerShell says "python is not recognized", see Troubleshooting.

> **Avoid** — Do not install Python from the Microsoft Store if the python.org installer is available — Store installs can confuse the `python` command and virtual environments.

**macOS**

1. Download *Python 3.12.x macOS 64-bit universal2 installer* from https://www.python.org/downloads/macos/ and run the `.pkg` (accept defaults). Alternative with Homebrew: `brew install python@3.12`
2. Open Terminal and check: `python3 --version` — expected `Python 3.12.x`. On macOS use `python3` wherever this guide says `python`.

**Ubuntu**

Ubuntu 24.04 ships Python 3.12. Install the pieces we need:

```
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
```

On Ubuntu 22.04 (Python 3.10 by default) add the deadsnakes PPA first: `sudo add-apt-repository ppa:deadsnakes/ppa && sudo apt install python3.12 python3.12-venv` and use `python3.12` in commands. Check: `python3 --version`

---

## 3. Step 2 — Install Git and set your identity

**Windows** — Download *64-bit Git for Windows Setup* from https://git-scm.com/downloads/win and run it. Accept the defaults on every screen. Two worth confirming: *Git from the command line and also from 3rd-party software* (PATH), and *Use Visual Studio Code as Git's default editor* if VS Code is already installed. Open a new PowerShell and check: `git --version`

**macOS** — Run `git --version` in Terminal. If Git is missing, macOS offers to install the Command Line Tools — click Install. Or: `brew install git`.

**Ubuntu** — Already installed in Step 1. Check: `git --version`

**All platforms — tell Git who you are.** Use the same email you will use for GitHub. Run once:

```
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
git config --global --list
```

The last command should print your name and email.

---

## 4. Step 3 — Install Visual Studio Code

**Windows** — Download the *User Installer, 64-bit* from https://code.visualstudio.com/download and run it. On the *Select Additional Tasks* screen tick: *Add "Open with Code" action to Windows Explorer file context menu*, *… to directory context menu*, *Register Code as an editor for supported file types* and **Add to PATH** (usually pre-ticked). Finish and launch VS Code once so it completes its first-run setup.

**macOS** — Download the *Mac Universal* build, unzip, and drag *Visual Studio Code.app* into Applications. Open VS Code, press `Cmd+Shift+P`, type *Shell Command: Install 'code' command in PATH* and press Enter.

**Ubuntu** — Download the `.deb` and install: `sudo apt install ./code_*.deb`

**Check (all platforms)** — Open a new terminal and run `code --version`. Three lines print (version, commit, architecture).

---

## 5. Step 4 — Install the VS Code extensions

Five extensions. Install them from the terminal (fastest) or from the Extensions view inside VS Code.

**Option A — one command per extension (any platform)**

```
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension github.copilot
code --install-extension github.copilot-chat
code --install-extension qwtel.sqlite-viewer
```

**Option B — inside VS Code** — Click the Extensions icon in the left bar (`Ctrl+Shift+X` / `Cmd+Shift+X`). Search each name and click Install. **Check the publisher — it matters.**

| Extension | Publisher | Extension ID | Why |
|---|---|---|---|
| Python | Microsoft | `ms-python.python` | Run, debug and test Python; picks the virtual environment |
| Pylance | Microsoft | `ms-python.vscode-pylance` | Fast IntelliSense and type checking |
| GitHub Copilot | GitHub | `github.copilot` | Inline AI code completions |
| GitHub Copilot Chat | GitHub | `github.copilot-chat` | Chat, `/explain`, `/tests`, `/fix` inside the editor |
| SQLite Viewer | Florian Klampfer | `qwtel.sqlite-viewer` | Open the `policydesk.db` file and look at the tables |

**Check** — Run `code --list-extensions` — all five IDs should be in the list.

---

## 6. Step 5 — Create a GitHub account

Skip this if you already have one — but do complete the email verification and 2FA parts.

1. Go to https://github.com/signup. Use an email you can open on your phone during the workshop (your college email is ideal — it also unlocks the Student Pack in Step 6).
2. Pick a professional username; it will appear on your project URL and in your demo.
3. Open the verification email and click the link. **Unverified accounts cannot enable Copilot.**
4. Turn on two-factor authentication: *Settings → Password and authentication → Enable two-factor authentication → Authenticator app* (Google Authenticator / Microsoft Authenticator). It takes 3 minutes now versus a blocked morning on Day 1.
5. Sign in to GitHub from VS Code: click the Accounts icon (bottom-left, person silhouette) → *Sign in with GitHub* → authorise in the browser.

**Check** — In VS Code the Accounts icon shows your GitHub username when clicked.

---

## 7. Step 6 — Enable GitHub Copilot

Copilot has a **Free** tier that needs nothing but a GitHub account, and a **Pro** tier that students get free through the GitHub Student Developer Pack. Do the Free tier now — it takes two minutes — and apply for the Pack in parallel; approval can take from a few hours to a week.

**6a · Copilot Free (do this today)**

1. Sign in to GitHub and open https://github.com/settings/copilot.
2. Click *Get started with Copilot Free*. No card is asked for.
3. On the settings page make sure *Suggestions matching public code* is set to **Allowed** (blocking it removes many useful completions).
4. Back in VS Code, click the Copilot icon in the status bar (bottom-right). If it asks you to sign in, choose the same GitHub account. The icon should now show no warning badge.

> **Limits** — Copilot Free currently gives 2,000 code completions and 50 chat messages per month. That covers the workshop comfortably, but if you burn through it playing beforehand, the Student Pack (Pro) removes the limit.

**6b · GitHub Student Developer Pack → Copilot Pro (apply today, may take days)**

1. Go to https://education.github.com/pack and click *Sign up for Student Developer Pack*.
2. Add your college email under *Settings → Emails* if it is not already on the account and verify it.
3. Fill the application: school name, how you plan to use GitHub, and upload proof — a photo of your college ID card or a current bonafide/fee receipt with your name and the current date. **Take the photo in good light; blurry uploads are the number-one rejection reason.**
4. Allow location access when the form asks (GitHub uses it to match you to the campus).
5. Wait for the approval email. Then https://github.com/settings/copilot will show *Pro (via GitHub Education)*. Nothing else to change in VS Code.

**Check** — In VS Code create a file called `test.py` and type this line, then press Enter and wait two seconds:

```
# function that returns the nth fibonacci number
```

Grey ghost text with a function should appear. Press `Tab` to accept it. Press `Ctrl+Alt+I` (`Cmd+Ctrl+I` on Mac) to open Copilot Chat and ask *"explain this file"*. A reply means chat works too.

---

## 8. Step 7 — Create one AI chat account

The labs on requirements, design, test cases and code review use a chat assistant in the browser. Any one of these free tiers is enough; the prompts we give you work in all of them.

| Assistant | Sign up at | Notes |
|---|---|---|
| ChatGPT | https://chatgpt.com | Sign in with Google or email. Free tier has a rolling message limit on the best model; fine for the labs. |
| Claude | https://claude.ai | Sign in with Google or email. Strong at long code and documents. Free tier resets every few hours. |
| Gemini | https://gemini.google.com | Any Google account. Generous free limits; also gives you the free Gemini CLI if you want to experiment. |

**Check** — log in on your laptop browser, ask *"write a Python function to validate an Indian vehicle registration number"* and confirm you get code back.

> **Good practice** — Use a personal login you can access without SMS delays in the venue. Do not paste real personal data (Aadhaar numbers, real customer records) into any assistant — the workshop uses fake seed data only.

---

## 9. Step 8 — Create a Render account

Render hosts the app on a public URL on Day 2. The free plan needs no card.

1. Go to https://render.com and click *Get Started → Sign up with GitHub*.
2. Authorise Render to access your GitHub account. When asked which repositories, choose **All repositories** (or you will have to come back for your team repo on Day 2).
3. Verify your email if Render asks. You land on the Dashboard — that is enough for now; we create the web service together in the deployment session on Day 2.

**Check** — https://dashboard.render.com opens and shows your GitHub username at top-right.

---

## 10. Step 9 — Set up the project and run the checker

The starter repository is public: **https://github.com/Abhinash1458/policydesk-starter**. These commands clone it, create an isolated Python environment, install the libraries, and run the app once.

**Windows (PowerShell)**

```
cd $HOME\Documents
git clone https://github.com/Abhinash1458/policydesk-starter.git
cd policydesk-starter
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python check_setup.py
uvicorn app.main:app --reload
```

> **Windows** — If `Activate.ps1` is blocked ("running scripts is disabled on this system"), run this once and try again: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`. Or use Command Prompt instead: `.venv\Scripts\activate.bat`

**macOS / Ubuntu (Terminal)**

```
cd ~/Documents
git clone https://github.com/Abhinash1458/policydesk-starter.git
cd policydesk-starter
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python check_setup.py
uvicorn app.main:app --reload
```

**What you should see**

- After activating, the prompt starts with `(.venv)`.
- `pip install` ends with *Successfully installed fastapi-… uvicorn-… sqlmodel-…*
- `python check_setup.py` prints `[OK]` on every line and **ALL CHECKS PASSED** at the bottom. **Screenshot this** — it is your ticket for the setup-check at 9:00 AM on Day 1.
- `uvicorn` prints *Uvicorn running on http://127.0.0.1:8000*. Open **http://127.0.0.1:8000** in a browser — the PolicyDesk dashboard loads (and http://127.0.0.1:8000/docs shows the API). Press `Ctrl+C` to stop it.
- Open the folder in VS Code (`code .`). Bottom-right, the Python interpreter should read *3.12.x ('.venv')*. If it shows a different Python, press `Ctrl+Shift+P` → *Python: Select Interpreter* → choose the `.venv` entry.

You can also run the checker standalone before cloning: download `check_setup.py` from the email attachment and run `python check_setup.py` from any folder. The only line that may warn is *Project packages* — that clears after Step 9.

---

## 11. Final checklist — tick every line before Day 1

| ✔ | Check | Command / where to look | Expected |
|---|---|---|---|
| ☐ | Python 3.12+ | `python --version` | Python 3.12.x or newer |
| ☐ | pip works | `python -m pip --version` | pip 24+ … |
| ☐ | Git installed | `git --version` | git version 2.4x |
| ☐ | Git identity set | `git config --global --list` | user.name and user.email lines |
| ☐ | VS Code on PATH | `code --version` | three lines |
| ☐ | 5 extensions | `code --list-extensions` | ms-python.python, ms-python.vscode-pylance, github.copilot, github.copilot-chat, qwtel.sqlite-viewer |
| ☐ | GitHub account, verified, 2FA on | github.com/settings/security | 2FA: Enabled |
| ☐ | Signed in to GitHub in VS Code | Accounts icon, bottom-left | your username |
| ☐ | Copilot Free (or Pro) active | github.com/settings/copilot | Copilot Free / Pro |
| ☐ | Copilot suggests in a .py file | type a comment, wait | grey ghost text |
| ☐ | Student Pack applied | education.github.com | Pending or Approved |
| ☐ | AI chat account | chatgpt.com / claude.ai / gemini.google.com | logged in |
| ☐ | Render account | dashboard.render.com | dashboard opens |
| ☐ | Starter cloned, venv, packages | `pip install -r requirements.txt` | Successfully installed … |
| ☐ | check_setup.py | `python check_setup.py` | ALL CHECKS PASSED |
| ☐ | App runs | `uvicorn app.main:app --reload` | http://127.0.0.1:8000 loads |

---

## 12. Troubleshooting — the problems we see most, and the fix

| Symptom | Cause | Fix |
|---|---|---|
| 'python' is not recognized (Windows) | PATH box was not ticked during install | Re-run the Python installer → Modify → Next → tick *Add Python to environment variables* → Install. Open a NEW terminal. |
| 'python' opens the Microsoft Store | Windows app-execution alias | Settings → Apps → Advanced app settings → App execution aliases → turn off both "python" entries. Or use the py launcher: `py -3.12 …` |
| `python --version` shows 3.10 / 3.11 | Older Python first on PATH | Use `py -3.12 -m venv .venv` on Windows or `python3.12` on macOS/Linux; VS Code: select the .venv interpreter. |
| Activate.ps1 cannot be loaded, scripts disabled | PowerShell execution policy | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then re-run. Or use Command Prompt with `activate.bat`. |
| pip install fails with SSL / proxy / timeout | College proxy or firewall | Try a mobile hotspot. If behind a proxy: `pip install --proxy http://user:pass@proxy:port -r requirements.txt` |
| ensurepip / venv missing (Ubuntu) | venv package not installed | `sudo apt install python3.12-venv`, then recreate: `rm -rf .venv && python3 -m venv .venv` |
| 'code' is not recognized | VS Code not on PATH | Windows: reinstall VS Code and tick *Add to PATH*. macOS: `Cmd+Shift+P` → *Shell Command: Install 'code' command*. |
| Copilot icon has a warning badge / no suggestions | Not signed in, Free tier not enabled, or extension disabled | Click the icon → Sign in. Confirm github.com/settings/copilot shows Free or Pro. Check Copilot is enabled for Python: icon → *Enable completions*. |
| Copilot: "You've reached your monthly limit" | Free tier exhausted | Wait for the Student Pack approval (Pro), or pair with a teammate for the day. |
| Student Pack rejected | Proof not clear / not dated / name mismatch | Re-apply with a clearer photo of a document that has your name, college name and a current date. A bonafide certificate works best. |
| uvicorn: address already in use | An old server is still running | `Ctrl+C` in the old terminal, or run `uvicorn app.main:app --reload --port 8001` |
| ModuleNotFoundError: fastapi | Virtual environment not activated | Look for `(.venv)` in the prompt. Activate it, then `pip install -r requirements.txt` again. |
| git clone asks for a password and rejects it | GitHub no longer accepts passwords over HTTPS | Sign in to GitHub in VS Code first (it configures the credential helper), or use GitHub Desktop, or create a Personal Access Token. |
| VS Code shows 'Select Interpreter' / squiggles everywhere | Wrong Python picked | `Ctrl+Shift+P` → *Python: Select Interpreter* → the entry ending in `.venv`. |

---

*TalentPath Academy · Train. Learn. Grow. Succeed. · info@talentpathacademy.com · +91 87900 02007*
