"""
TalentPath Academy - AI-Powered SDLC Workshop
Pre-workshop setup checker.

Run:  python check_setup.py
Every line should end with [OK]. Bring the output (or a screenshot) if something fails.
"""
import platform
import shutil
import socket
import subprocess
import sys

MIN_PY = (3, 12)
REQUIRED_EXTENSIONS = {
    "ms-python.python": "Python",
    "ms-python.vscode-pylance": "Pylance",
    "github.copilot": "GitHub Copilot",
    "github.copilot-chat": "GitHub Copilot Chat",
}
OPTIONAL_EXTENSIONS = {
    "qwtel.sqlite-viewer": "SQLite Viewer",
}
HOSTS = ["github.com", "pypi.org", "api.github.com", "render.com"]

results = []


def report(name, ok, detail="", warn=False):
    tag = "[OK]  " if ok else ("[WARN]" if warn else "[FAIL]")
    print(f"{tag} {name:<34} {detail}")
    results.append((name, ok, warn))


def cmd(args):
    try:
        out = subprocess.run(args, capture_output=True, text=True, timeout=30, shell=(platform.system() == "Windows"))
        return out.returncode, (out.stdout or out.stderr).strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return 1, ""


print("=" * 70)
print(" TalentPath Academy - Workshop setup check")
print(f" {platform.system()} {platform.release()} - {platform.machine()}")
print("=" * 70)

# 1. Python
v = sys.version_info
report("Python version", v >= MIN_PY, f"{v.major}.{v.minor}.{v.micro}  (need {MIN_PY[0]}.{MIN_PY[1]}+)")

# 2. pip
rc, out = cmd([sys.executable, "-m", "pip", "--version"])
report("pip", rc == 0, out.split(" from ")[0] if out else "python -m pip not working")

# 3. venv module
try:
    import venv  # noqa: F401
    report("venv module", True)
except ImportError:
    report("venv module", False, "on Ubuntu: sudo apt install python3.12-venv")

# 4. Git
rc, out = cmd(["git", "--version"])
report("Git", rc == 0, out if out else "git not on PATH")
if rc == 0:
    _, name = cmd(["git", "config", "--global", "user.name"])
    _, email = cmd(["git", "config", "--global", "user.email"])
    report("Git identity", bool(name and email), f"{name} <{email}>" if name and email else "run git config --global user.name / user.email")

# 5. VS Code + extensions
code = shutil.which("code") or shutil.which("code.cmd")
report("VS Code 'code' command", bool(code), "" if code else "reinstall VS Code with 'Add to PATH' or open VS Code -> Ctrl+Shift+P -> 'Shell Command: Install code command'")
if code:
    rc, out = cmd([code, "--list-extensions"])
    installed = {e.strip().lower() for e in out.splitlines()} if rc == 0 else set()
    for ext_id, label in REQUIRED_EXTENSIONS.items():
        report(f"Extension: {label}", ext_id in installed, "" if ext_id in installed else f"code --install-extension {ext_id}")
    for ext_id, label in OPTIONAL_EXTENSIONS.items():
        report(f"Extension: {label} (optional)", ext_id in installed, "" if ext_id in installed else f"code --install-extension {ext_id}", warn=True)

# 6. Internet reachability
for host in HOSTS:
    try:
        socket.create_connection((host, 443), timeout=5).close()
        report(f"Reach {host}", True)
    except OSError:
        report(f"Reach {host}", False, "check Wi-Fi / college proxy")

# 7. Project dependencies (only meaningful after 'pip install -r requirements.txt')
missing = []
for mod in ("fastapi", "uvicorn", "sqlmodel", "jinja2", "pytest", "httpx"):
    try:
        __import__(mod)
    except ImportError:
        missing.append(mod)
report("Project packages", not missing, "all installed" if not missing else f"missing: {', '.join(missing)} -> activate .venv and pip install -r requirements.txt", warn=True)

# Summary
print("-" * 70)
fails = [n for n, ok, warn in results if not ok and not warn]
warns = [n for n, ok, warn in results if not ok and warn]
if not fails and not warns:
    print(" ALL CHECKS PASSED - you are ready for the workshop.")
elif not fails:
    print(f" READY, with {len(warns)} optional item(s) to finish: {', '.join(warns)}")
else:
    print(f" {len(fails)} check(s) FAILED: {', '.join(fails)}")
    print(" Fix these using the setup guide, then run this script again.")
print("=" * 70)
sys.exit(0 if not fails else 1)
