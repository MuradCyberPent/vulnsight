# Git workflow for VulnSight (3 members, 3 modules)

Every member pushes their own branch from their own computer and their own GitHub account. The branches are merged into `main` through Pull Requests, module by module. That gives many separate pushes from all three members instead of one big push.

## Before you start (one time)

1. **One member** creates an empty repository on GitHub and adds the other two as collaborators (Settings > Collaborators).
2. **Everyone** clones it and sets their own identity, so the commits show the right name:
   ```
   git clone https://github.com/YOURTEAM/vulnsight.git
   cd vulnsight
   git config user.name "Your Real Name"
   git config user.email "the-email-on-your-github-account"
   ```
3. **Everyone** unzips the full project **next to** the clone and names the folder `vulnsight-full`. It is only the place your files are copied from:
   ```
   some-folder/
   ├── vulnsight/        <- your Git clone (starts empty)
   └── vulnsight-full/   <- the unzipped project
   ```
4. In the empty clone, the first push needs a first commit on `main`. Member 1 does this once, before anything else:
   ```
   git commit --allow-empty -m "Start repository"
   git push -u origin main
   ```
   The other two then run `git pull`.

## The plan at a glance

| Phase | Week | Member 1 branch | Member 2 branch | Member 3 branch | Who merges |
|---|---|---|---|---|---|
| Setup (before the modules) | Week 0 | `setup/member1-project-structure` | `setup/member2-plugin-system` | `setup/member3-frontend-and-docs` | Member 1 |
| Module 1 | Week 1 | `module1/member1-authentication` | `module1/member2-security-rules` | `module1/member3-admin-and-privacy` | Member 1 |
| Module 2 | Week 2 | `module2/member1-scan-setup-and-progress` | `module2/member2-software-web-ssl-checks` | `module2/member3-files-dns-cloud-checks` | Member 2 |
| Module 3 | Week 3 | `module3/member1-dashboard-and-reports` | `module3/member2-risk-and-results` | `module3/member3-history-and-comparison` | Member 3 |

Each phase is **three pushes** (one per member), then the merges. Setup + 3 modules = **12 pushes** and 12 Pull Requests, from all three members.

## What every member does in a phase (always the same)

1. `git checkout main` then `git pull` (get everyone's merged work first).
2. `git checkout -b <your branch>` (names are in the plan below).
3. For each commit in your list: copy its files, then `git add` and `git commit`.
   The helper copies the right files for you: `python ../vulnsight-full/tools/git_plan.py --module 1 --member 2 --copy 1`
4. `git push -u origin <your branch>`
5. On GitHub, open a **Pull Request** from your branch into `main` and tell the member who merges.

Run `python ../vulnsight-full/tools/git_plan.py --module 1 --member 2` (change the numbers) to print your whole plan. It only prints and copies files. It never runs Git for you and never changes who you are.

## Who merges, and in what order

On GitHub, open each Pull Request, check the changed files, and choose **Create a merge commit** (this keeps every member's separate commits visible). Or on the command line:
```
git checkout main
git pull
git merge --no-ff origin/<branch>
git push
```

---

## Setup (before the modules) (Week 0)

**Merged by:** Member 1.  **Order:** Merge in this order: Member 1, then Member 2, then Member 3 (the database tables must exist before the entry point, and the frontend comes last).

### Member 1: `setup/member1-project-structure`

| # | Commit message | Files |
|---|---|---|
| 1 | Add project structure, settings and database connection | `.gitignore`<br>`backend/requirements.txt`<br>`backend/requirements-dev.txt`<br>`backend/.env.example`<br>`backend/app/__init__.py`<br>`backend/app/core/__init__.py`<br>`backend/app/core/config.py`<br>`backend/app/core/database.py` |
| 2 | Add database tables from the ER diagram: User, Scan and Finding | `backend/app/core/models/__init__.py`<br>`backend/app/core/models/user.py`<br>`backend/app/core/models/scan.py`<br>`backend/app/core/models/finding.py` |

```
git checkout main
git pull
git checkout -b setup/member1-project-structure
python ../vulnsight-full/tools/git_plan.py --module setup --member 1 --copy 1
git add .gitignore backend/requirements.txt backend/requirements-dev.txt backend/.env.example backend/app/__init__.py backend/app/core/__init__.py
git add backend/app/core/config.py backend/app/core/database.py
git commit -m "Add project structure, settings and database connection"
python ../vulnsight-full/tools/git_plan.py --module setup --member 1 --copy 2
git add backend/app/core/models/__init__.py backend/app/core/models/user.py backend/app/core/models/scan.py backend/app/core/models/finding.py
git commit -m "Add database tables from the ER diagram: User, Scan and Finding"
git push -u origin setup/member1-project-structure
```

### Member 2: `setup/member2-plugin-system`

| # | Commit message | Files |
|---|---|---|
| 1 | Add plug-in system: hooks, check registry and module discovery | `backend/app/core/hooks.py`<br>`backend/app/core/checks.py`<br>`backend/app/core/discovery.py`<br>`backend/app/core/finding_utils.py`<br>`backend/app/core/scan_views.py`<br>`backend/app/modules/__init__.py`<br>`backend/app/modules/users/__init__.py`<br>`backend/app/modules/users/routes/__init__.py`<br>`backend/app/modules/scanning/__init__.py`<br>`backend/app/modules/scanning/routes/__init__.py`<br>`backend/app/modules/scanning/checks/__init__.py`<br>`backend/app/modules/analysis/__init__.py`<br>`backend/app/modules/analysis/routes/__init__.py` |
| 2 | Add API entry point and test setup | `backend/app/main.py`<br>`backend/tests/__init__.py`<br>`backend/tests/conftest.py` |

```
git checkout main
git pull
git checkout -b setup/member2-plugin-system
python ../vulnsight-full/tools/git_plan.py --module setup --member 2 --copy 1
git add backend/app/core/hooks.py backend/app/core/checks.py backend/app/core/discovery.py backend/app/core/finding_utils.py backend/app/core/scan_views.py backend/app/modules/__init__.py
git add backend/app/modules/users/__init__.py backend/app/modules/users/routes/__init__.py backend/app/modules/scanning/__init__.py backend/app/modules/scanning/routes/__init__.py backend/app/modules/scanning/checks/__init__.py backend/app/modules/analysis/__init__.py
git add backend/app/modules/analysis/routes/__init__.py
git commit -m "Add plug-in system: hooks, check registry and module discovery"
python ../vulnsight-full/tools/git_plan.py --module setup --member 2 --copy 2
git add backend/app/main.py backend/tests/__init__.py backend/tests/conftest.py
git commit -m "Add API entry point and test setup"
git push -u origin setup/member2-plugin-system
```

### Member 3: `setup/member3-frontend-and-docs`

| # | Commit message | Files |
|---|---|---|
| 1 | Add frontend foundation: Vite, React, Tailwind and shared files | `frontend/package.json`<br>`frontend/package-lock.json`<br>`frontend/vite.config.js`<br>`frontend/postcss.config.js`<br>`frontend/tailwind.config.js`<br>`frontend/index.html`<br>`frontend/.env.example`<br>`frontend/vercel.json`<br>`frontend/src/index.css`<br>`frontend/src/main.jsx`<br>`frontend/src/App.jsx`<br>`frontend/src/shared/api.js`<br>`frontend/src/shared/auth.jsx`<br>`frontend/src/shared/util.js`<br>`frontend/src/shared/pageRegistry.js`<br>`frontend/src/shared/components/CountChips.jsx`<br>`frontend/src/shared/components/Layout.jsx`<br>`frontend/src/shared/components/Logo.jsx`<br>`frontend/src/shared/components/SeverityBadge.jsx`<br>`frontend/src/shared/components/Welcome.jsx` |
| 2 | Add README, deployment file and Git workflow guide | `README.md`<br>`render.yaml`<br>`GIT_WORKFLOW.md`<br>`ownership.json`<br>`tools/git_plan.py` |

```
git checkout main
git pull
git checkout -b setup/member3-frontend-and-docs
python ../vulnsight-full/tools/git_plan.py --module setup --member 3 --copy 1
git add frontend/package.json frontend/package-lock.json frontend/vite.config.js frontend/postcss.config.js frontend/tailwind.config.js frontend/index.html
git add frontend/.env.example frontend/vercel.json frontend/src/index.css frontend/src/main.jsx frontend/src/App.jsx frontend/src/shared/api.js
git add frontend/src/shared/auth.jsx frontend/src/shared/util.js frontend/src/shared/pageRegistry.js frontend/src/shared/components/CountChips.jsx frontend/src/shared/components/Layout.jsx frontend/src/shared/components/Logo.jsx
git add frontend/src/shared/components/SeverityBadge.jsx frontend/src/shared/components/Welcome.jsx
git commit -m "Add frontend foundation: Vite, React, Tailwind and shared files"
python ../vulnsight-full/tools/git_plan.py --module setup --member 3 --copy 2
git add README.md render.yaml GIT_WORKFLOW.md ownership.json tools/git_plan.py
git commit -m "Add README, deployment file and Git workflow guide"
git push -u origin setup/member3-frontend-and-docs
```

---

## Module 1: User Management and Security (Week 1)

**Merged by:** Member 1.  **Order:** Merge Member 1 first. Member 3's admin files import Member 1's `security.py`. Member 2's files can be merged at any time.

### Member 1: `module1/member1-authentication`

| # | Commit message | Files |
|---|---|---|
| 1 | Add Secure Authentication: registration, login and bcrypt password hashing | `backend/app/modules/users/schemas.py`<br>`backend/app/modules/users/security.py`<br>`backend/app/modules/users/routes/auth.py` |
| 2 | Add Login and Register pages with session handling | `frontend/src/modules/users/components/AuthShell.jsx`<br>`frontend/src/modules/users/pages/Login.jsx`<br>`frontend/src/modules/users/pages/Register.jsx` |

```
git checkout main
git pull
git checkout -b module1/member1-authentication
python ../vulnsight-full/tools/git_plan.py --module 1 --member 1 --copy 1
git add backend/app/modules/users/schemas.py backend/app/modules/users/security.py backend/app/modules/users/routes/auth.py
git commit -m "Add Secure Authentication: registration, login and bcrypt password hashing"
python ../vulnsight-full/tools/git_plan.py --module 1 --member 1 --copy 2
git add frontend/src/modules/users/components/AuthShell.jsx frontend/src/modules/users/pages/Login.jsx frontend/src/modules/users/pages/Register.jsx
git commit -m "Add Login and Register pages with session handling"
git push -u origin module1/member1-authentication
```

### Member 2: `module1/member2-security-rules`

| # | Commit message | Files |
|---|---|---|
| 1 | Add Account Lockout after 5 failed logins | `backend/app/modules/users/lockout.py` |
| 2 | Add Scan Permission Check: scope guard and scan limit | `backend/app/modules/users/scan_permission.py` |

```
git checkout main
git pull
git checkout -b module1/member2-security-rules
python ../vulnsight-full/tools/git_plan.py --module 1 --member 2 --copy 1
git add backend/app/modules/users/lockout.py
git commit -m "Add Account Lockout after 5 failed logins"
python ../vulnsight-full/tools/git_plan.py --module 1 --member 2 --copy 2
git add backend/app/modules/users/scan_permission.py
git commit -m "Add Scan Permission Check: scope guard and scan limit"
git push -u origin module1/member2-security-rules
```

### Member 3: `module1/member3-admin-and-privacy`

| # | Commit message | Files |
|---|---|---|
| 1 | Add Private Workspace: users only reach their own scans | `backend/app/modules/users/workspace.py` |
| 2 | Add Admin role check and admin API for users and scans | `backend/app/modules/users/admin_access.py`<br>`backend/app/modules/users/routes/admin.py`<br>`backend/create_admin.py` |
| 3 | Add Admin page | `frontend/src/modules/users/pages/Admin.jsx` |

```
git checkout main
git pull
git checkout -b module1/member3-admin-and-privacy
python ../vulnsight-full/tools/git_plan.py --module 1 --member 3 --copy 1
git add backend/app/modules/users/workspace.py
git commit -m "Add Private Workspace: users only reach their own scans"
python ../vulnsight-full/tools/git_plan.py --module 1 --member 3 --copy 2
git add backend/app/modules/users/admin_access.py backend/app/modules/users/routes/admin.py backend/create_admin.py
git commit -m "Add Admin role check and admin API for users and scans"
python ../vulnsight-full/tools/git_plan.py --module 1 --member 3 --copy 3
git add frontend/src/modules/users/pages/Admin.jsx
git commit -m "Add Admin page"
git push -u origin module1/member3-admin-and-privacy
```

---

## Module 2: Vulnerability Scanning Engine (Week 2)

**Merged by:** Member 2.  **Order:** Any order works. The three members' files do not depend on each other.

### Member 1: `module2/member1-scan-setup-and-progress`

| # | Commit message | Files |
|---|---|---|
| 1 | Add Port Scanning and Service Detection | `backend/app/modules/scanning/checks/ports.py` |
| 2 | Add Scan Profiles and background scan runner | `backend/app/modules/scanning/profiles.py`<br>`backend/app/modules/scanning/runner.py` |
| 3 | Add New Scan Setup: start a scan with a target, profile and ports | `backend/app/modules/scanning/schemas.py`<br>`backend/app/modules/scanning/routes/scans.py` |
| 4 | Add Live Scan Progress API | `backend/app/modules/scanning/routes/progress.py` |
| 5 | Add New scan page and live progress panel | `frontend/src/modules/scanning/pages/NewScan.jsx`<br>`frontend/src/modules/scanning/pages/ScanProgress.jsx`<br>`frontend/src/modules/scanning/components/ProgressPanel.jsx` |

```
git checkout main
git pull
git checkout -b module2/member1-scan-setup-and-progress
python ../vulnsight-full/tools/git_plan.py --module 2 --member 1 --copy 1
git add backend/app/modules/scanning/checks/ports.py
git commit -m "Add Port Scanning and Service Detection"
python ../vulnsight-full/tools/git_plan.py --module 2 --member 1 --copy 2
git add backend/app/modules/scanning/profiles.py backend/app/modules/scanning/runner.py
git commit -m "Add Scan Profiles and background scan runner"
python ../vulnsight-full/tools/git_plan.py --module 2 --member 1 --copy 3
git add backend/app/modules/scanning/schemas.py backend/app/modules/scanning/routes/scans.py
git commit -m "Add New Scan Setup: start a scan with a target, profile and ports"
python ../vulnsight-full/tools/git_plan.py --module 2 --member 1 --copy 4
git add backend/app/modules/scanning/routes/progress.py
git commit -m "Add Live Scan Progress API"
python ../vulnsight-full/tools/git_plan.py --module 2 --member 1 --copy 5
git add frontend/src/modules/scanning/pages/NewScan.jsx frontend/src/modules/scanning/pages/ScanProgress.jsx frontend/src/modules/scanning/components/ProgressPanel.jsx
git commit -m "Add New scan page and live progress panel"
git push -u origin module2/member1-scan-setup-and-progress
```

### Member 2: `module2/member2-software-web-ssl-checks`

| # | Commit message | Files |
|---|---|---|
| 1 | Add Outdated Software Detection against the local CVE database | `backend/app/modules/scanning/checks/cve.py`<br>`backend/data/cve.json` |
| 2 | Add Web Security Headers Check | `backend/app/modules/scanning/checks/headers.py` |
| 3 | Add SSL/TLS Certificate Check | `backend/app/modules/scanning/checks/ssl_check.py` |

```
git checkout main
git pull
git checkout -b module2/member2-software-web-ssl-checks
python ../vulnsight-full/tools/git_plan.py --module 2 --member 2 --copy 1
git add backend/app/modules/scanning/checks/cve.py backend/data/cve.json
git commit -m "Add Outdated Software Detection against the local CVE database"
python ../vulnsight-full/tools/git_plan.py --module 2 --member 2 --copy 2
git add backend/app/modules/scanning/checks/headers.py
git commit -m "Add Web Security Headers Check"
python ../vulnsight-full/tools/git_plan.py --module 2 --member 2 --copy 3
git add backend/app/modules/scanning/checks/ssl_check.py
git commit -m "Add SSL/TLS Certificate Check"
git push -u origin module2/member2-software-web-ssl-checks
```

### Member 3: `module2/member3-files-dns-cloud-checks`

| # | Commit message | Files |
|---|---|---|
| 1 | Add Exposed File Detection | `backend/app/modules/scanning/checks/exposed.py` |
| 2 | Add DNS Analysis | `backend/app/modules/scanning/checks/dns_check.py` |
| 3 | Add Subdomain Discovery | `backend/app/modules/scanning/checks/subdomains.py` |
| 4 | Add Cloud Storage Check | `backend/app/modules/scanning/checks/cloud.py` |

```
git checkout main
git pull
git checkout -b module2/member3-files-dns-cloud-checks
python ../vulnsight-full/tools/git_plan.py --module 2 --member 3 --copy 1
git add backend/app/modules/scanning/checks/exposed.py
git commit -m "Add Exposed File Detection"
python ../vulnsight-full/tools/git_plan.py --module 2 --member 3 --copy 2
git add backend/app/modules/scanning/checks/dns_check.py
git commit -m "Add DNS Analysis"
python ../vulnsight-full/tools/git_plan.py --module 2 --member 3 --copy 3
git add backend/app/modules/scanning/checks/subdomains.py
git commit -m "Add Subdomain Discovery"
python ../vulnsight-full/tools/git_plan.py --module 2 --member 3 --copy 4
git add backend/app/modules/scanning/checks/cloud.py
git commit -m "Add Cloud Storage Check"
git push -u origin module2/member3-files-dns-cloud-checks
```

---

## Module 3: Analysis, Reporting and Dashboard (Week 3)

**Merged by:** Member 3.  **Order:** Merge Member 1 first. Member 2's results page uses Member 1's report buttons. Member 3's files can be merged at any time.

### Member 1: `module3/member1-dashboard-and-reports`

| # | Commit message | Files |
|---|---|---|
| 1 | Add User Dashboard | `backend/app/modules/analysis/routes/dashboard.py`<br>`frontend/src/modules/analysis/pages/Dashboard.jsx` |
| 2 | Add Report Export in HTML, JSON and TXT | `backend/app/modules/analysis/reports.py`<br>`backend/app/modules/analysis/templates/report.html`<br>`backend/app/modules/analysis/routes/reports.py`<br>`frontend/src/modules/analysis/components/ReportButtons.jsx` |

```
git checkout main
git pull
git checkout -b module3/member1-dashboard-and-reports
python ../vulnsight-full/tools/git_plan.py --module 3 --member 1 --copy 1
git add backend/app/modules/analysis/routes/dashboard.py frontend/src/modules/analysis/pages/Dashboard.jsx
git commit -m "Add User Dashboard"
python ../vulnsight-full/tools/git_plan.py --module 3 --member 1 --copy 2
git add backend/app/modules/analysis/reports.py backend/app/modules/analysis/templates/report.html backend/app/modules/analysis/routes/reports.py frontend/src/modules/analysis/components/ReportButtons.jsx
git commit -m "Add Report Export in HTML, JSON and TXT"
git push -u origin module3/member1-dashboard-and-reports
```

### Member 2: `module3/member2-risk-and-results`

| # | Commit message | Files |
|---|---|---|
| 1 | Add Risk Scoring | `backend/app/modules/analysis/scoring.py` |
| 2 | Add risk dial and finding cards for Beginner Mode | `frontend/src/modules/analysis/components/RiskDial.jsx`<br>`frontend/src/modules/analysis/components/FindingCard.jsx` |
| 3 | Add Scan Results View with severity filters | `frontend/src/modules/analysis/pages/ScanDetail.jsx` |

```
git checkout main
git pull
git checkout -b module3/member2-risk-and-results
python ../vulnsight-full/tools/git_plan.py --module 3 --member 2 --copy 1
git add backend/app/modules/analysis/scoring.py
git commit -m "Add Risk Scoring"
python ../vulnsight-full/tools/git_plan.py --module 3 --member 2 --copy 2
git add frontend/src/modules/analysis/components/RiskDial.jsx frontend/src/modules/analysis/components/FindingCard.jsx
git commit -m "Add risk dial and finding cards for Beginner Mode"
python ../vulnsight-full/tools/git_plan.py --module 3 --member 2 --copy 3
git add frontend/src/modules/analysis/pages/ScanDetail.jsx
git commit -m "Add Scan Results View with severity filters"
git push -u origin module3/member2-risk-and-results
```

### Member 3: `module3/member3-history-and-comparison`

| # | Commit message | Files |
|---|---|---|
| 1 | Add Scan History with delete | `backend/app/modules/analysis/routes/history.py`<br>`frontend/src/modules/analysis/pages/History.jsx` |
| 2 | Add Scan Comparison | `backend/app/modules/analysis/routes/compare.py`<br>`frontend/src/modules/analysis/pages/Compare.jsx` |
| 3 | Add automated tests | `backend/tests/test_core.py`<br>`backend/tests/test_api.py` |

```
git checkout main
git pull
git checkout -b module3/member3-history-and-comparison
python ../vulnsight-full/tools/git_plan.py --module 3 --member 3 --copy 1
git add backend/app/modules/analysis/routes/history.py frontend/src/modules/analysis/pages/History.jsx
git commit -m "Add Scan History with delete"
python ../vulnsight-full/tools/git_plan.py --module 3 --member 3 --copy 2
git add backend/app/modules/analysis/routes/compare.py frontend/src/modules/analysis/pages/Compare.jsx
git commit -m "Add Scan Comparison"
python ../vulnsight-full/tools/git_plan.py --module 3 --member 3 --copy 3
git add backend/tests/test_core.py backend/tests/test_api.py
git commit -m "Add automated tests"
git push -u origin module3/member3-history-and-comparison
```

---

## After every merge: check that the app still runs

```
cd backend
.venv\Scripts\Activate.ps1          (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
uvicorn app.main:app --reload
```
and in a second terminal:
```
cd frontend
npm install
npm run dev
```
After Module 1 you can register, log in and see the Admin page. After Module 2 you can also start scans and watch their progress. After Module 3 everything works (dashboard, results, reports, history, comparison). After the last merge, run `pytest` in `backend`.

## Showing proof to your teacher

```
git log --graph --all --date=short --format="%h  %an  %ad  %s"
git shortlog -sn --all
```
On GitHub: **Pull requests > Closed** (each member's merged requests), **Insights > Contributors**, and **Insights > Network** (the branches joining `main`).

## Keep it honest and smooth

- Commit and push **only your own files**, with your **own** Git identity. Never use someone else's account or change dates.
- Do the phases in order and push when you really do each one. The dates in Git are real.
- Everyone should be able to open their files and explain them. Your teacher can ask about any commit.
- Check your course rules about using AI help, and follow them.
- Never use `git push --force` on `main`.
