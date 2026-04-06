# Cross‑Platform Beginner Tutorial to Run Yu‑Gi‑Oh‑Card‑Tracker on Windows, macOS, and Ubuntu Using Conda

## Executive summary

This document is a beginner‑friendly, step‑by‑step, copy‑paste tutorial to run the GitHub project **Yu‑Gi‑Oh‑Card‑Tracker** (also branded in its README/UI as **OpenYuGi**) on **Windows**, **macOS**, and **Ubuntu Linux**, using a **Conda environment named `openyugi`** and **Python 3.10**. The repository’s entry point is the **root‑level `main.py`**, which launches a web UI using **NiceGUI** and defaults to opening the app at `http://localhost:8080`. citeturn34view0turn36view0

Key facts established from the repository and primary sources:

- The project expects **Python 3.10+** and provides a `requirements.txt` (no `environment.yml` is present in the root file list on GitHub at time of writing), so dependency installation primarily uses `pip install -r requirements.txt`. citeturn34view0turn33view0  
- `main.py` explicitly disables NiceGUI auto‑reload (`reload=False`) and starts the app via `ui.run(...)`. citeturn36view0  
- The app uses a local‑first data directory (`data/...`) and fetches Yu‑Gi‑Oh card data from the **YGOPRODeck** API endpoints (`db.ygoprodeck.com`), with no API key strings evident in the service code section shown. citeturn35view0turn36view0  
- **Miniconda** installers have stable “latest” filenames with direct downloads for each OS/architecture. citeturn16view0  
- Conda’s official docs provide canonical commands for creating an environment with a specific Python, initialising shells (`conda init`), and activating environments (`conda activate`). citeturn26view2turn26view3turn31view2  

Where the repository documentation contains placeholder clone commands (e.g., `yourusername/openyugi.git`), this tutorial uses the **actual repository URL** you provided. citeturn34view0  

## Project overview and what you will install

The application is a local collection manager with a browser‑based UI (NiceGUI). You run a local Python process (`python main.py`), then use a browser to access `http://localhost:8080`. The README states the server starts and your default browser should open that URL. citeturn34view0

The repository’s root contains (among other items) `main.py` (the launcher) and `requirements.txt` (Python dependencies). citeturn34view0turn33view0

The `requirements.txt` contains packages including `nicegui`, `pydantic`, `requests`, OCR/vision dependencies like `easyocr`, `ultralytics`, and `python-doctr[torch]`, and constraints like `numpy<2` and OpenCV `<4.10`. citeturn33view0

The app also uses the YGOPRODeck API endpoints in code (`https://db.ygoprodeck.com/api/v7/...`). citeturn35view0 YGOPRODeck’s API guide is public and warns to minimise API calls by storing pulled data locally (or risk IP blacklisting). citeturn12search9

Optional scanner functionality mentioned in the README requires **Tesseract OCR** (with OS‑specific install instructions). citeturn34view0turn13view0

## Windows setup

### Step zero: open a terminal

You will run commands from either **PowerShell** or **Command Prompt**.

- To open **Windows PowerShell**: use Start menu search (Microsoft’s official PowerShell docs describe launching it from Start). citeturn29search6  
- To open **Command Prompt**: one common method is **Win+R → `cmd` → Enter**. citeturn29search1  

### Step one: install Git (if not already installed)

Check first:

**PowerShell**
```powershell
git --version
```

**Command Prompt**
```bat
git --version
```

If you get “not recognised”, install Git for Windows from the official Git site (the Git project points Windows users to “Git for Windows”). citeturn19search0turn19search3

Optional: if you’re doing automated installs, Git for Windows documents silent install flags for its installer. citeturn19search1

### Step two: install Conda (recommended: Miniconda)

You asked for **exact download links and installer filenames**. The Miniconda repository listing provides stable “latest” file names for Windows and other platforms. citeturn16view0

#### Miniconda (GUI installer)

Download this file (Windows x86_64):

```text
Miniconda3-latest-Windows-x86_64.exe
https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe
```
citeturn16view0

Run it by double‑clicking the `.exe`.

Important note: conda documentation warns that “adding Anaconda to PATH” is generally **not recommended** because it bypasses activation scripts. citeturn26view1  
On Windows, conda’s installer documentation also notes that PATH behaviour changed due to a security issue (All Users PATH option disabled in some scenarios). citeturn14view1

#### Miniconda (command‑line / silent installer option)

Conda’s Windows installation docs describe silent installation using the `/S` argument for Miniconda (and note it should also work for Anaconda Distribution). citeturn14view1  
Anaconda’s silent‑mode guide also provides explicit “download with curl” and silent install patterns for Windows installers. citeturn18view0

A concrete Miniconda silent install example (Command Prompt):

```bat
curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe --output .\Miniconda3-latest-Windows-x86_64.exe
start /wait "" Miniconda3-latest-Windows-x86_64.exe /InstallationType=JustMe /RegisterPython=0 /S /D=%UserProfile%Miniconda3
```
citeturn18view0turn16view0

#### Alternative: full Anaconda Distribution (optional)

If you prefer Anaconda Distribution, the current archive lists Windows installers like:

```text
Anaconda3-2025.12-2-Windows-x86_64.exe
https://repo.anaconda.com/archive/Anaconda3-2025.12-2-Windows-x86_64.exe
```
citeturn30view0turn17view2

Licensing note: Anaconda’s system requirements page states that as of 2025‑11‑07, it is “Free for individuals and small organizations (`<200 employees`),” and a paid licence is required for larger organisations and some redistribution/embedding scenarios. citeturn17view1

### Step three: make Conda work in your shell

After installing Miniconda/Anaconda, open a new terminal window.

Verify conda works:

**PowerShell**
```powershell
conda --version
conda list
```

**Command Prompt**
```bat
conda --version
conda list
```

“Run `conda list`” is specifically recommended by conda’s Windows install guidance as a quick test. citeturn14view1

If `conda` is not found, see the troubleshooting section.

If `conda` exists but `conda activate` fails, initialise your shell:

**PowerShell**
```powershell
conda init powershell
```

**Command Prompt**
```bat
conda init cmd.exe
```

Conda’s `conda init` command explicitly supports shells including `powershell`, and defaults differ by OS; it also notes that you typically must restart the shell after running it. citeturn26view3

If PowerShell blocks activation scripts, you may need to set execution policy for the current user:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

This is consistent with PowerShell’s documented execution policy mechanisms and examples. citeturn32search5turn32search2

Close and reopen PowerShell after running `conda init` and/or changing the policy. citeturn26view3

### Step four: create and activate the Conda environment `openyugi` (Python 3.10)

The repository expects Python 3.10+. citeturn34view0  
Conda’s “Managing Python” guide shows the pattern: `conda create -n <env> python=<version>` and then verify with `python --version`. citeturn26view2

**PowerShell**
```powershell
conda create -n openyugi python=3.10 -y
conda activate openyugi
python --version
```

**Command Prompt**
```bat
conda create -n openyugi python=3.10 -y
conda activate openyugi
python --version
```

If you already created the env but need to force Python 3.10 inside it:

**PowerShell / Command Prompt**
```powershell
conda install -n openyugi python=3.10 -y
```
Conda documents that `conda install python=3.10` is the way to remain on a minor release (rather than upgrading across majors). citeturn26view2

### Step five: choose a target folder and clone the repository

You asked for explicit target paths like `C:\Users\<username>\Projects\...`, plus placeholders and how to find them.

Find your username:

**PowerShell**
```powershell
$env:USERNAME
whoami
```

**Command Prompt**
```bat
echo %USERNAME%
whoami
```

Find your current directory:

**PowerShell**
```powershell
Get-Location
pwd
```

**Command Prompt**
```bat
cd
echo %CD%
```

Create the Projects folder and clone:

**PowerShell**
```powershell
mkdir "$env:USERPROFILE\Projects"
cd "$env:USERPROFILE\Projects"
git clone https://github.com/DJ-Cat-N-Cheese/Yu-Gi-Oh-Card-Tracker.git
cd ".\Yu-Gi-Oh-Card-Tracker"
```

**Command Prompt**
```bat
mkdir "%USERPROFILE%\Projects"
cd /d "%USERPROFILE%\Projects"
git clone https://github.com/DJ-Cat-N-Cheese/Yu-Gi-Oh-Card-Tracker.git
cd "Yu-Gi-Oh-Card-Tracker"
```

Expected final paths (examples you can mirror):

- `C:\Users\<username>\Projects\Yu-Gi-Oh-Card-Tracker`
- `C:\Users\Alice\Projects\Yu-Gi-Oh-Card-Tracker`

The README shows the general pattern of cloning and then running `python main.py`, though its clone URL example is a placeholder; the actual entry point is still `main.py`. citeturn34view0turn36view0

### Step six: check for dependency files and install dependencies

The root file list shows a `requirements.txt`, and its contents list the required Python packages. citeturn34view0turn33view0

First, check whether an `environment.yml` exists (for Conda YAML installs). Even though it is not shown in the GitHub root file list, you asked for a precise workflow that checks. citeturn34view0

**PowerShell**
```powershell
Test-Path .\environment.yml
Test-Path .\requirements.txt
```

**Command Prompt**
```bat
if exist environment.yml (echo Found environment.yml) else (echo No environment.yml found)
if exist requirements.txt (echo Found requirements.txt) else (echo requirements.txt missing)
```

If `environment.yml` exists, create from it:

```powershell
conda env create -n openyugi -f environment.yml
```
The `conda env create` docs confirm `-f/--file` is used to specify an environment definition file, and `-n/--name` sets (and can override) the environment name. citeturn26view0

Otherwise (expected for this repo), install via `requirements.txt` (recommended):

1) Ensure you are inside the repo root (you should see `main.py` and `requirements.txt`). citeturn34view0turn33view0  
2) Ensure you are in the `openyugi` environment. Conda docs state activation is essential so PATH and activation scripts apply. citeturn26view1turn31view2  

**PowerShell / Command Prompt**
```powershell
conda activate openyugi
python --version
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The Python Packaging User Guide recommends invoking pip via `python -m pip ...` (and shows upgrading pip/setuptools/wheel patterns). citeturn24search12turn24search15

### Step seven: start OpenYuGi and verify it works

The README’s launch step is:

```text
python main.py
```

and it says the browser should open `http://localhost:8080`. citeturn34view0

Also, the repository’s `main.py` ends with `ui.run(title='OpenYuGi', ... reload=False)` guarded by an `if __name__ in {"__main__", "__mp_main__"}` block. citeturn36view0

Run it:

**PowerShell / Command Prompt**
```powershell
python main.py
```

If your browser does not open automatically, open it yourself (Windows command):

**PowerShell**
```powershell
Start-Process "http://localhost:8080"
```

**Command Prompt**
```bat
start http://localhost:8080
```

What you should see:

- A terminal line indicating the server is ready (NiceGUI commonly prints “NiceGUI ready to go on http://localhost:8080/”). citeturn22search5  
- Your browser shows the OpenYuGi UI at `http://localhost:8080`. citeturn34view0  

To stop the server: press `Ctrl+C` in the terminal window that is running it.

Background option (Windows):

**Command Prompt**
```bat
start "" /B python main.py
```

**PowerShell (starts a separate process window)**
```powershell
Start-Process -FilePath python -ArgumentList "main.py" -WorkingDirectory (Get-Location)
```

### Step eight: take screenshots for your tutorial (Windows)

You requested screenshots for each major step. Use Snipping Tool shortcut:

- **Win + Shift + S** opens the snipping overlay. citeturn27search0  

Suggested screenshot checklist and filenames (example):

- `win-01-git-version.png` (after `git --version`)
- `win-02-miniconda-installer.png` (installer screen)
- `win-03-conda-version.png` (after `conda --version`)
- `win-04-openyugi-env.png` (after `conda activate openyugi` and `python --version`)
- `win-05-pip-install.png` (after `pip install -r requirements.txt`)
- `win-06-openyugi-running.png` (terminal + browser showing `http://localhost:8080`)

image_group{"layout":"carousel","aspect_ratio":"16:9","query":["Miniconda Windows installer screenshot","Git for Windows installer screenshot","Windows PowerShell conda activate screenshot","NiceGUI localhost 8080 screenshot"],"num_per_query":1}

## macOS setup

### Step zero: open Terminal and check your CPU architecture

Open Terminal (Apple’s official Terminal guide shows it in `/Applications/Utilities/Terminal.app` and via Launchpad search). citeturn29search4

Check whether you have Apple Silicon or Intel:

```bash
uname -m
```

- `arm64` = Apple Silicon  
- `x86_64` = Intel

### Step one: install Git (if needed)

Check first:

```bash
git --version
```

Git’s official macOS install page notes you can install Git via **Xcode Command Line Tools**:

```bash
xcode-select --install
```
citeturn19search2

### Step two: install Conda (Miniconda recommended)

The Miniconda download index provides exact “latest” filenames for macOS arm64 and x86_64 in both `.pkg` (GUI) and `.sh` (terminal installer) forms. citeturn16view0

#### Miniconda (GUI `.pkg` installer)

Apple Silicon (arm64):

```text
Miniconda3-latest-MacOSX-arm64.pkg
https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.pkg
```

Intel (x86_64):

```text
Miniconda3-latest-MacOSX-x86_64.pkg
https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.pkg
```
citeturn16view0

Double‑click the `.pkg` you downloaded and follow prompts.

#### Miniconda (terminal `.sh` installer)

Apple Silicon (arm64):

```text
Miniconda3-latest-MacOSX-arm64.sh
https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
```

Intel (x86_64):

```text
Miniconda3-latest-MacOSX-x86_64.sh
https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
```
citeturn16view0

Example download + install (adjust filename for your architecture):

```bash
cd ~/Downloads
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
bash Miniconda3-latest-MacOSX-arm64.sh
```

### Step three: initialise Conda for your shell (zsh or bash)

Most modern macOS systems default to **zsh**. You can check:

```bash
echo $SHELL
```

Initialise conda:

```bash
conda init zsh
# or, if you use bash:
conda init bash
```

Conda documents that `conda init` supports `zsh` and `bash`, and you generally must restart the shell for it to take effect. citeturn26view3

Close and reopen Terminal.

Test:

```bash
conda --version
conda list
```

### Step four: create and activate `openyugi` (Python 3.10)

Conda’s Managing Python guide provides the canonical workflow (`conda create -n ... python=...` then `python --version`). citeturn26view2

```bash
conda create -n openyugi python=3.10 -y
conda activate openyugi
python --version
```

### Step five: clone the repo into a clear folder path

Find your username:

```bash
whoami
echo "$USER"
```

Find current directory:

```bash
pwd
```

Create a Projects directory and clone:

```bash
mkdir -p /Users/<username>/Projects
cd /Users/<username>/Projects
git clone https://github.com/DJ-Cat-N-Cheese/Yu-Gi-Oh-Card-Tracker.git
cd Yu-Gi-Oh-Card-Tracker
```

Example path:
- `/Users/alice/Projects/Yu-Gi-Oh-Card-Tracker`

### Step six: install dependencies

Confirm you’re in the repo root (you should see `main.py` and `requirements.txt`). citeturn34view0turn33view0

Check for `environment.yml`:

```bash
ls -la
test -f environment.yml && echo "Found environment.yml" || echo "No environment.yml found"
```

If `environment.yml` exists:

```bash
conda env create -n openyugi -f environment.yml
```
Conda’s `conda env create` docs confirm `-f/--file` and `-n/--name`. citeturn26view0

Otherwise (expected):

```bash
conda activate openyugi
python -m pip install --upgrade pip
pip install -r requirements.txt
```
citeturn33view0turn24search15

### Step seven: run the app and verify

Run:

```bash
python main.py
```

This is the repository’s stated launch command, and it should open `http://localhost:8080`. citeturn34view0turn36view0

If your browser does not open automatically:

```bash
open http://localhost:8080
```

Expected behaviour:

- Terminal logs indicate the server is running; NiceGUI commonly reports it is available at `http://localhost:8080/`. citeturn22search5

Background option (macOS):

```bash
nohup python main.py > openyugi.log 2>&1 &
```

### Step eight: take screenshots for your tutorial (macOS)

Apple documents screenshot shortcuts including:

- **Shift + Command + 4** (select an area). citeturn27search1  

Suggested screenshot checklist:

- `mac-01-terminal-git-version.png`
- `mac-02-miniconda-installer.png`
- `mac-03-conda-version.png`
- `mac-04-openyugi-env.png`
- `mac-05-pip-install.png`
- `mac-06-openyugi-running.png`

image_group{"layout":"carousel","aspect_ratio":"16:9","query":["Miniconda macOS pkg installer screenshot","macOS Terminal conda init zsh screenshot","NiceGUI app localhost 8080 mac screenshot","Xcode-select install git screenshot"],"num_per_query":1}

## Ubuntu setup

### Step zero: open Terminal

Ubuntu’s official “Using the Terminal” documentation describes opening Terminal and lists **Ctrl + Alt + T** as a keyboard shortcut in GNOME‑based Ubuntu. citeturn29search3

To confirm where you are:

```bash
pwd
```

### Step one: install Git (if needed)

Git’s official Linux install page recommends using your distribution’s package manager; for Debian/Ubuntu it shows `apt-get install git`. citeturn19search7

```bash
sudo apt-get update
sudo apt-get install -y git
git --version
```

### Step two: install Conda (Miniconda recommended)

The Miniconda download index provides the exact Linux installer filenames, including x86_64 and aarch64. citeturn16view0

Ubuntu on most PCs is **x86_64**:

```bash
uname -m
```

- If `x86_64`, use:
  ```text
  Miniconda3-latest-Linux-x86_64.sh
  https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
  ```
- If `aarch64`, use:
  ```text
  Miniconda3-latest-Linux-aarch64.sh
  https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh
  ```

citeturn16view0

Install example (x86_64 shown):

```bash
cd ~/Downloads
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

### Step three: initialise Conda for bash and verify

Initialise bash:

```bash
conda init bash
```

`conda init` supports bash and requires restarting your shell for changes to apply. citeturn26view3

Close and reopen Terminal, then verify:

```bash
conda --version
conda list
```

### Step four: create and activate `openyugi` (Python 3.10)

Conda’s docs show the exact create‑and‑verify pattern. citeturn26view2

```bash
conda create -n openyugi python=3.10 -y
conda activate openyugi
python --version
```

### Step five: clone the repository into a clear path

Find your username:

```bash
whoami
echo "$USER"
```

Create target folder and clone:

```bash
mkdir -p /home/<username>/Projects
cd /home/<username>/Projects
git clone https://github.com/DJ-Cat-N-Cheese/Yu-Gi-Oh-Card-Tracker.git
cd Yu-Gi-Oh-Card-Tracker
```

Example:
- `/home/alice/Projects/Yu-Gi-Oh-Card-Tracker`

### Step six: install dependencies

Check for dependency files:

```bash
ls -la
test -f environment.yml && echo "Found environment.yml" || echo "No environment.yml found"
test -f requirements.txt && echo "Found requirements.txt" || echo "requirements.txt missing"
```

If `environment.yml` exists:

```bash
conda env create -n openyugi -f environment.yml
```
citeturn26view0

Otherwise:

```bash
conda activate openyugi
python -m pip install --upgrade pip
pip install -r requirements.txt
```
citeturn33view0turn24search15

### Step seven: start the app and verify

Run:

```bash
python main.py
```

Entry point and run call are in `main.py` (`ui.run(...)`). citeturn36view0

Open browser manually if needed (Ubuntu):

```bash
xdg-open http://localhost:8080
```

Expected:

- Browser loads the UI at `http://localhost:8080`. citeturn34view0  
- Terminal shows the server is ready; NiceGUI commonly prints a “ready to go” URL including port 8080. citeturn22search5

Background option (Ubuntu):

```bash
nohup python main.py > openyugi.log 2>&1 &
```

### Step eight: take screenshots for your tutorial (Ubuntu)

Ubuntu’s official help docs for the built‑in screenshot tool state:

- Press **Print Screen** to open the screenshot overlay and capture images; screenshots are typically saved under `~/Pictures/Screenshots`. citeturn27search2  

Suggested screenshot checklist:

- `ubuntu-01-git-install.png`
- `ubuntu-02-miniconda-install.png`
- `ubuntu-03-conda-version.png`
- `ubuntu-04-openyugi-env.png`
- `ubuntu-05-pip-install.png`
- `ubuntu-06-openyugi-running.png`

## Troubleshooting and maintenance

### Conda problems

**Problem: `conda` command not found**

- If you installed Conda but it isn’t on PATH in your current shell, run `conda init <your shell>` and restart the shell; conda’s docs emphasise that each shell must be configured and that restarting is usually required. citeturn26view3  

**Problem: `conda activate` fails / “shell not configured”**

- `conda init` exists specifically because activation requires shell integration. citeturn26view3turn31view0  
- Run (pick your shell):
  ```bash
  conda init bash
  conda init zsh
  ```
  ```powershell
  conda init powershell
  ```
  Then restart the terminal. citeturn26view3

**Problem: PowerShell says scripts are disabled / activation doesn’t work**

- PowerShell execution policy may block profile scripts; setting `RemoteSigned` at `CurrentUser` scope is a standard documented approach. citeturn32search5turn32search2  
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
  Then close and reopen PowerShell.

**Maintenance commands**

Update conda itself (official docs show `conda update conda`). citeturn23search12

```bash
conda update conda -y
```

Update all packages in the active environment (commonly used pattern; conda explains how `conda update` works). citeturn23search2

```bash
conda update --all -y
```

### Python/pip problems

**Problem: wrong Python is used**

Always verify inside your activated environment:

```bash
conda activate openyugi
python --version
```

Conda’s docs explicitly recommend verifying with `python --version` after creating/activating an environment. citeturn26view2turn31view2

**Problem: pip installs into the wrong environment**

Use:

```bash
python -m pip install -r requirements.txt
```

The pip user guide explains `python -m pip ...` runs pip for the specific interpreter you invoked. citeturn24search15

Upgrade pip:

```bash
python -m pip install --upgrade pip
```
citeturn24search12turn24search7

### Project‑specific problems

**Problem: `ModuleNotFoundError: No module named 'src'`**

This project’s `main.py` manipulates `sys.path` based on its own file location and expects to be run from the repository context. citeturn36view0  
Fix: make sure you `cd` into the repo root (where `main.py` is), then run:

```bash
python main.py
```
citeturn34view0turn36view0

**Problem: browser opens but page doesn’t load**

- Ensure you’re using `http://localhost:8080` as the README states. citeturn34view0  
- If port 8080 is already in use, you can identify what’s listening:

Windows (PowerShell):
```powershell
netstat -ano | findstr :8080
```

macOS / Ubuntu:
```bash
lsof -i :8080
```

Then stop the conflicting process or reboot.

**Problem: scanner features don’t work**

The README says OCR scanning needs **Tesseract OCR**, with OS‑specific install notes (Windows installer; Linux apt; macOS brew). citeturn34view0  
For Windows, the linked installer source lists a current Windows setup executable (example shown on that page). citeturn13view0

### Credentials / API keys check

The code defines YGOPRODeck API endpoints directly and (in the sampled section) does not show any API key constants. citeturn35view0  
If you want to *verify whether any credentials are required anywhere*, search the repo for common secret strings:

Windows (PowerShell):
```powershell
Get-ChildItem -Recurse -File | Select-String -Pattern "API_KEY|SECRET|TOKEN|PASSWORD|KEY=" -CaseSensitive:$false
```

Windows (Command Prompt):
```bat
findstr /S /I "API_KEY SECRET TOKEN PASSWORD KEY=" *.py *.env *.yml *.yaml *.toml *.json
```

macOS / Ubuntu:
```bash
grep -RInE "API_KEY|SECRET|TOKEN|PASSWORD|KEY=" .
```

If nothing is found, treat credentials as **not required or not implemented**; if something is found (e.g., `.env` instructions), follow the repository’s documentation or code comments.

## Visual aids and command comparison

### Setup flowchart

```mermaid
flowchart TD
  A[Open terminal] --> B[Install Git]
  B --> C[Install Conda (Miniconda recommended)]
  C --> D[conda init for your shell]
  D --> E[Create env: conda create -n openyugi python=3.10]
  E --> F[Activate env: conda activate openyugi]
  F --> G[Clone repo into Projects folder]
  G --> H[Install deps: pip install -r requirements.txt]
  H --> I[Run: python main.py]
  I --> J[Open http://localhost:8080]
  J --> K[Capture screenshots + verify]
```

### Command comparison table

| Task | Windows (PowerShell) | Windows (Command Prompt) | macOS (Terminal zsh/bash) | Ubuntu (bash) |
|---|---|---|---|---|
| Show username | `$env:USERNAME` | `echo %USERNAME%` | `whoami` | `whoami` |
| Show current folder | `Get-Location` / `pwd` | `cd` / `echo %CD%` | `pwd` | `pwd` |
| Create env | `conda create -n openyugi python=3.10 -y` | `conda create -n openyugi python=3.10 -y` | `conda create -n openyugi python=3.10 -y` | `conda create -n openyugi python=3.10 -y` |
| Activate env | `conda activate openyugi` | `conda activate openyugi` | `conda activate openyugi` | `conda activate openyugi` |
| Verify Python | `python --version` | `python --version` | `python --version` | `python --version` |
| Clone repo | `git clone https://github.com/DJ-Cat-N-Cheese/Yu-Gi-Oh-Card-Tracker.git` | `git clone https://github.com/DJ-Cat-N-Cheese/Yu-Gi-Oh-Card-Tracker.git` | same | same |
| Install deps | `pip install -r requirements.txt` | `pip install -r requirements.txt` | same | same |
| Run app | `python main.py` | `python main.py` | `python main.py` | `python main.py` |
| Open browser | `Start-Process "http://localhost:8080"` | `start http://localhost:8080` | `open http://localhost:8080` | `xdg-open http://localhost:8080` |

Conda activation (`conda activate myenv`) is the documented standard, and `conda init` exists to enable that behaviour across shells. citeturn31view2turn26view3

### Screenshot capture shortcuts recap

- Windows: **Win + Shift + S** (Snipping Tool overlay). citeturn27search0  
- macOS: **Shift + Command + 4** (capture selected area). citeturn27search1  
- Ubuntu: **Print Screen** (opens screenshot overlay; saves under `~/Pictures/Screenshots`). citeturn27search2