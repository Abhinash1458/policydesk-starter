<#
    PolicyDesk - one-click setup (Windows)
    TalentPath Academy - AI-Powered SDLC Workshop

    Launched by setup.bat. Five steps, in order:

        1. Python 3.12+      installed if missing
        2. Git               installed if missing (needed to clone and push)
        3. VS Code           installed if missing
        4. .venv             created and activated
        5. requirements.txt  installed
        then                 PolicyDesk starts in the browser

    Safe to run again - every step is skipped when it is already done.
    Nothing needs administrator rights: Python, Git and VS Code are
    installed for the current user only.
#>
param(
    [switch]$Quiet,    # never ask anything (unattended / lab imaging)
    [switch]$SkipApp   # set everything up but do not start the app
)

$ProgressPreference = 'SilentlyContinue'   # a visible progress bar makes downloads far slower
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$PyMin = [version]'3.12'
$PyFallbackVersions = @('3.12.10', '3.12.9', '3.12.7')

$script:Problems = @()
$script:Notes    = @()

# ---------------------------------------------------------------- output ---

function Step([int]$n, [string]$text) {
    Write-Host ''
    Write-Host "  [$n/5] $text" -ForegroundColor Cyan
}

function Ok    ([string]$t) { Write-Host "        OK      $t" -ForegroundColor Green }
function Doing ([string]$t) { Write-Host "        ...     $t" -ForegroundColor Gray }
function Warn  ([string]$t) { Write-Host "        WARN    $t" -ForegroundColor Yellow; $script:Notes += $t }
function Bad   ([string]$t) { Write-Host "        FAILED  $t" -ForegroundColor Red;    $script:Problems += $t }

# --------------------------------------------------------------- helpers ---

function Sync-Path {
    # A fresh install writes PATH into the registry; this window does not see it yet.
    $machine = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $user    = [Environment]::GetEnvironmentVariable('Path', 'User')
    $env:Path = ($machine, $user | Where-Object { $_ }) -join ';'
}

function Have([string]$name) {
    return [bool](Get-Command $name -ErrorAction SilentlyContinue)
}

function Get-VersionFrom([string]$text) {
    if ($text -and $text -match '\d+\.\d+(\.\d+)?') {
        try { return [version]$Matches[0] } catch { return $null }
    }
    return $null
}

function Invoke-Download([string]$url, [string]$outFile) {
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $url -OutFile $outFile -UseBasicParsing -TimeoutSec 900 -ErrorAction Stop
        return (Test-Path $outFile)
    } catch {
        return $false
    }
}

function Invoke-Winget([string[]]$wingetArgs) {
    if (-not (Have 'winget')) { return $false }
    try {
        & winget @wingetArgs | Out-Host
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    }
}

# ------------------------------------------------------------- 1. Python ---

function Probe-Python([string]$exe, [string[]]$prefix) {
    # stderr is swallowed inside cmd so the Microsoft Store stub
    # ("Python was not found...") cannot be mistaken for a real version.
    $line = (@($exe) + @($prefix) + @('--version')) -join ' '
    return (Get-VersionFrom ((cmd /c "$line 2>nul") -join ' '))
}

function Find-Python {
    $candidates = @(
        @{ exe = 'py';      prefix = @('-3.12') },
        @{ exe = 'py';      prefix = @('-3')    },
        @{ exe = 'python';  prefix = @()        },
        @{ exe = 'python3'; prefix = @()        }
    )
    foreach ($c in $candidates) {
        if (-not (Have $c.exe)) { continue }
        $v = Probe-Python $c.exe $c.prefix
        if ($v -and $v -ge $PyMin) { return @{ Exe = $c.exe; Prefix = $c.prefix; Version = $v } }
    }
    # A per-user install is not on PATH in this window yet - look where it lands.
    foreach ($dir in @("$env:LOCALAPPDATA\Programs\Python\Python313",
                       "$env:LOCALAPPDATA\Programs\Python\Python312",
                       "$env:ProgramFiles\Python313",
                       "$env:ProgramFiles\Python312")) {
        $exe = Join-Path $dir 'python.exe'
        if (-not (Test-Path $exe)) { continue }
        $v = Get-VersionFrom ((cmd /c """$exe"" --version 2>nul") -join ' ')
        if ($v -and $v -ge $PyMin) { return @{ Exe = $exe; Prefix = @(); Version = $v } }
    }
    return $null
}

function Install-Python {
    Doing 'Python 3.12+ is missing - installing it for your user account'

    if (Invoke-Winget @('install', '--id', 'Python.Python.3.12', '-e', '--scope', 'user',
                        '--silent', '--accept-package-agreements', '--accept-source-agreements')) {
        Sync-Path
        $found = Find-Python
        if ($found) { return $found }
    }

    Doing 'falling back to the installer from python.org'
    $tmp = Join-Path $env:TEMP 'policydesk-python-setup.exe'
    $got = $false
    foreach ($v in $PyFallbackVersions) {
        Doing "downloading Python $v (about 25 MB)"
        if (Invoke-Download "https://www.python.org/ftp/python/$v/python-$v-amd64.exe" $tmp) { $got = $true; break }
    }
    if (-not $got) { return $null }

    Doing 'running the installer - about a minute'
    # InstallAllUsers=0 keeps it per-user, so no administrator prompt appears.
    Start-Process -FilePath $tmp -Wait -ArgumentList @(
        '/quiet', 'InstallAllUsers=0', 'PrependPath=1', 'Include_pip=1',
        'Include_launcher=1', 'Include_test=0'
    ) | Out-Null
    Remove-Item $tmp -Force -ErrorAction SilentlyContinue
    Sync-Path
    return (Find-Python)
}

# ---------------------------------------------------------------- 2. Git ---

function Initialize-Git {
    if (-not (Have 'git')) {
        Doing 'Git is missing - installing it'
        if (Invoke-Winget @('install', '--id', 'Git.Git', '-e', '--silent',
                            '--accept-package-agreements', '--accept-source-agreements')) {
            Sync-Path
        }
    }

    if (-not (Have 'git')) {
        Warn 'Git could not be installed automatically. You need it to push your work - get it from https://git-scm.com/download/win'
        return
    }

    Ok "Git $(Get-VersionFrom ((cmd /c 'git --version 2>nul') -join ' '))"

    $name  = (cmd /c 'git config --global user.name 2>nul')  -join ''
    $email = (cmd /c 'git config --global user.email 2>nul') -join ''
    if ($name -and $email) {
        Ok "Git identity: $name <$email>"
    } else {
        Warn 'Git has no name/email yet - run these two lines before your first commit:'
        Write-Host '                git config --global user.name  "Your Name"' -ForegroundColor DarkGray
        Write-Host '                git config --global user.email "you@example.com"' -ForegroundColor DarkGray
    }
}

# ------------------------------------------------------------ 3. VS Code ---

function Get-CodeCommand {
    $c = Get-Command 'code' -ErrorAction SilentlyContinue
    if ($c) { return $c.Source }
    foreach ($p in @("$env:LOCALAPPDATA\Programs\Microsoft VS Code\bin\code.cmd",
                     "$env:ProgramFiles\Microsoft VS Code\bin\code.cmd")) {
        if (Test-Path $p) { return $p }
    }
    return $null
}

function Initialize-VSCode {
    $code = Get-CodeCommand
    if ($code) { Ok 'VS Code is installed'; return $code }

    Doing 'VS Code is missing - installing the user setup'
    if (Invoke-Winget @('install', '--id', 'Microsoft.VisualStudioCode', '-e', '--scope', 'user',
                        '--silent', '--accept-package-agreements', '--accept-source-agreements')) {
        Sync-Path
        $code = Get-CodeCommand
    }

    if (-not $code) {
        Doing 'falling back to the installer from code.visualstudio.com'
        $tmp = Join-Path $env:TEMP 'policydesk-vscode-setup.exe'
        if (Invoke-Download 'https://update.code.visualstudio.com/latest/win32-x64-user/stable' $tmp) {
            Start-Process -FilePath $tmp -Wait -ArgumentList @(
                '/VERYSILENT', '/SP-', '/NORESTART',
                '/MERGETASKS=!runcode,addcontextmenufiles,addcontextmenufolders,addtopath'
            ) | Out-Null
            Remove-Item $tmp -Force -ErrorAction SilentlyContinue
            Sync-Path
            $code = Get-CodeCommand
        }
    }

    if ($code) { Ok 'VS Code installed' }
    else { Warn 'VS Code could not be installed automatically - get it from https://code.visualstudio.com' }
    return $code
}

# ==========================================================================

Write-Host ''
Write-Host '  =========================================================' -ForegroundColor DarkCyan
Write-Host '   PolicyDesk - one-click setup' -ForegroundColor Cyan
Write-Host '   TalentPath Academy - AI-Powered SDLC Workshop' -ForegroundColor DarkGray
Write-Host '  =========================================================' -ForegroundColor DarkCyan
Write-Host "   Folder: $Root" -ForegroundColor DarkGray

if (-not (Test-Path (Join-Path $Root 'requirements.txt'))) {
    Write-Host ''
    Write-Host '  FAILED  This is the wrong folder - requirements.txt is not next to setup.bat.' -ForegroundColor Red
    Write-Host '          Open the folder you cloned (it has app\ and tests\ inside) and' -ForegroundColor Yellow
    Write-Host '          double-click setup.bat there.' -ForegroundColor Yellow
    exit 1
}

# 1 ------------------------------------------------------------------------
Step 1 'Python 3.12 or newer'
$py = Find-Python
if (-not $py) { $py = Install-Python }
if (-not $py) {
    Bad 'Python 3.12+ could not be found or installed.'
    Write-Host ''
    Write-Host '  Install it by hand from https://www.python.org/downloads/ and TICK' -ForegroundColor Yellow
    Write-Host '  "Add python.exe to PATH" on the first screen, then run setup.bat again.' -ForegroundColor Yellow
    exit 1
}
Ok "Python $($py.Version)"

# 2 ------------------------------------------------------------------------
Step 2 'Git (to clone and to push your work)'
Initialize-Git

# 3 ------------------------------------------------------------------------
Step 3 'VS Code'
$code = Initialize-VSCode

# 4 ------------------------------------------------------------------------
Step 4 'Virtual environment (.venv)'
$venvPy = Join-Path $Root '.venv\Scripts\python.exe'
if ((Test-Path (Join-Path $Root '.venv')) -and -not (Test-Path $venvPy)) {
    Doing 'the existing .venv is broken - deleting it'
    Remove-Item (Join-Path $Root '.venv') -Recurse -Force -ErrorAction SilentlyContinue
}
if (Test-Path $venvPy) {
    Ok '.venv already exists'
} else {
    Doing 'python -m venv .venv'
    & $py.Exe @(@($py.Prefix) + @('-m', 'venv', '.venv')) | Out-Host
    if (Test-Path $venvPy) { Ok '.venv created' } else { Bad 'could not create .venv' }
}
if (Test-Path $venvPy) {
    # Same effect as .venv\Scripts\activate, for the rest of this script.
    $env:VIRTUAL_ENV = Join-Path $Root '.venv'
    $env:Path = (Join-Path $Root '.venv\Scripts') + ';' + $env:Path
    Ok 'activated'
}

# 5 ------------------------------------------------------------------------
Step 5 'Project packages (pip install -r requirements.txt)'
if (Test-Path $venvPy) {
    & $venvPy -m pip install --upgrade pip --quiet --disable-pip-version-check | Out-Host
    & $venvPy -m pip install -r requirements.txt --disable-pip-version-check | Out-Host
    if ($LASTEXITCODE -eq 0) { Ok 'packages installed' }
    else { Bad 'pip could not install the packages - usually the Wi-Fi, or a college proxy blocking pypi.org' }
} else {
    Bad 'skipped - there is no virtual environment'
}

# --------------------------------------------------------------- summary ---

Write-Host ''
Write-Host '  =========================================================' -ForegroundColor DarkCyan
if ($script:Problems.Count -eq 0) {
    Write-Host '   SETUP COMPLETE' -ForegroundColor Green
} else {
    Write-Host "   SETUP FINISHED WITH $($script:Problems.Count) PROBLEM(S)" -ForegroundColor Red
    foreach ($p in $script:Problems) { Write-Host "     - $p" -ForegroundColor Red }
    Write-Host '   Show this window to the instructor.' -ForegroundColor Yellow
}
if ($script:Notes.Count -gt 0) {
    Write-Host '   Worth knowing:' -ForegroundColor Yellow
    foreach ($n in $script:Notes) { Write-Host "     - $n" -ForegroundColor Yellow }
}
Write-Host '  =========================================================' -ForegroundColor DarkCyan

if ($script:Problems.Count -gt 0) { exit 1 }

Write-Host ''
Write-Host '   To do this by hand next time:' -ForegroundColor DarkGray
Write-Host '     .venv\Scripts\activate' -ForegroundColor DarkGray
Write-Host '     uvicorn app.main:app --reload' -ForegroundColor DarkGray
Write-Host '     http://127.0.0.1:8000' -ForegroundColor DarkGray

if ($SkipApp) { exit 0 }

if (-not $Quiet) {
    Write-Host ''
    $answer = Read-Host '   Start PolicyDesk now? [Y/n]'
    if ($answer -ne '' -and $answer -notmatch '^[Yy]') { exit 0 }
}

# ----------------------------------------------------------- run the app ---

Write-Host ''
Doing 'starting PolicyDesk (a new window opens - close it to stop the app)'
if ($code) { Start-Process -FilePath $code -ArgumentList @('.') -WindowStyle Hidden }
Start-Process -FilePath 'powershell' -ArgumentList @(
    '-NoExit', '-NoProfile', '-Command',
    "Set-Location '$Root'; & '.venv\Scripts\Activate.ps1'; uvicorn app.main:app --reload"
)
Start-Sleep -Seconds 5
Start-Process 'http://127.0.0.1:8000'
Write-Host ''
Write-Host '   PolicyDesk is running at http://127.0.0.1:8000' -ForegroundColor Green

exit 0
