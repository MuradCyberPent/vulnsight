# VulnSight Scanner

A cloud-style vulnerability assessment platform. Log in, scan a domain or IP that you own, read plain-English
explanations of every finding, download reports, and compare scans over time.

**Tech stack**

| Part | Choice |
|---|---|
| Language | Python (scanners + backend), JavaScript (frontend) |
| Frontend framework | React, built with Vite |
| Backend framework | FastAPI |
| Styling | Tailwind CSS |
| ORM | SQLAlchemy (SQLite locally, PostgreSQL in production) |
| Deployment | Render (API + database), Vercel (frontend) |

> **Only scan systems you own or have written permission to test.** Safe practice targets:
> your own machine, a local lab such as DVWA, or `scanme.nmap.org` (light scans only).

---

## 1. Run it on your computer (VS Code)

You need **Python 3.10+** and **Node.js 18+**. Open the `vulnsight` folder in VS Code, then open **two terminals**
(Terminal > New Terminal).

### Terminal 1: backend

```bash
cd backend

# create a virtual environment (a private box for this project's Python packages)
python -m venv .venv

# activate it
#   Windows (PowerShell):   .venv\Scripts\Activate.ps1
#   Windows (cmd):          .venv\Scripts\activate.bat
#   Mac / Linux:            source .venv/bin/activate

pip install -r requirements.txt

# create your settings file
#   Windows:  copy .env.example .env
#   Mac/Linux: cp .env.example .env
# then open .env and set SECRET_KEY. Generate one with:
python -c "import secrets; print(secrets.token_urlsafe(48))"

uvicorn app.main:app --reload
```

The API is now at <http://localhost:8000>. Open <http://localhost:8000/docs> to see and test every endpoint
(click **Authorize** after logging in).

### Terminal 2: frontend

```bash
cd frontend
npm install
cp .env.example .env     # Windows: copy .env.example .env
npm run dev
```

Open <http://localhost:5173>, click **Create an account**, and run your first scan.

> On Windows PowerShell, if activating the virtual environment is blocked, run
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.

### Making someone an admin

Register the account in the website first, then:

```bash
cd backend
python create_admin.py yourusername
```

### Run the tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

---

## 2. How the project is split

The code is split into the three modules of the proposal. Each module has its own folder in the backend and in the frontend, and every feature is its own file, so three people can work in the same module without touching the same file.

| Module | Member | Functionality | Files (under `backend/app/modules/`, and `ui/` = `frontend/src/modules/`) |
|---|---|---|---|
| Module 1 | Member 1 | Secure Authentication: registration, login and bcrypt password hashing | `users/schemas.py`<br>`users/security.py`<br>`users/routes/auth.py` |
| Module 1 | Member 1 | Login and Register pages with session handling | `ui/users/components/AuthShell.jsx`<br>`ui/users/pages/Login.jsx`<br>`ui/users/pages/Register.jsx` |
| Module 1 | Member 2 | Account Lockout after 5 failed logins | `users/lockout.py` |
| Module 1 | Member 2 | Scan Permission Check: scope guard and scan limit | `users/scan_permission.py` |
| Module 1 | Member 3 | Private Workspace: users only reach their own scans | `users/workspace.py` |
| Module 1 | Member 3 | Admin role check and admin API for users and scans | `users/admin_access.py`<br>`users/routes/admin.py`<br>`backend/create_admin.py` |
| Module 1 | Member 3 | Admin page | `ui/users/pages/Admin.jsx` |
| Module 2 | Member 1 | Port Scanning and Service Detection | `scanning/checks/ports.py` |
| Module 2 | Member 1 | Scan Profiles and background scan runner | `scanning/profiles.py`<br>`scanning/runner.py` |
| Module 2 | Member 1 | New Scan Setup: start a scan with a target, profile and ports | `scanning/schemas.py`<br>`scanning/routes/scans.py` |
| Module 2 | Member 1 | Live Scan Progress API | `scanning/routes/progress.py` |
| Module 2 | Member 1 | New scan page and live progress panel | `ui/scanning/pages/NewScan.jsx`<br>`ui/scanning/pages/ScanProgress.jsx`<br>`ui/scanning/components/ProgressPanel.jsx` |
| Module 2 | Member 2 | Outdated Software Detection against the local CVE database | `scanning/checks/cve.py`<br>`backend/data/cve.json` |
| Module 2 | Member 2 | Web Security Headers Check | `scanning/checks/headers.py` |
| Module 2 | Member 2 | SSL/TLS Certificate Check | `scanning/checks/ssl_check.py` |
| Module 2 | Member 3 | Exposed File Detection | `scanning/checks/exposed.py` |
| Module 2 | Member 3 | DNS Analysis | `scanning/checks/dns_check.py` |
| Module 2 | Member 3 | Subdomain Discovery | `scanning/checks/subdomains.py` |
| Module 2 | Member 3 | Cloud Storage Check | `scanning/checks/cloud.py` |
| Module 3 | Member 1 | User Dashboard | `analysis/routes/dashboard.py`<br>`ui/analysis/pages/Dashboard.jsx` |
| Module 3 | Member 1 | Report Export in HTML, JSON and TXT | `analysis/reports.py`<br>`analysis/templates/report.html`<br>`analysis/routes/reports.py`<br>`ui/analysis/components/ReportButtons.jsx` |
| Module 3 | Member 2 | Risk Scoring | `analysis/scoring.py` |
| Module 3 | Member 2 | risk dial and finding cards for Beginner Mode | `ui/analysis/components/RiskDial.jsx`<br>`ui/analysis/components/FindingCard.jsx` |
| Module 3 | Member 2 | Scan Results View with severity filters | `ui/analysis/pages/ScanDetail.jsx` |
| Module 3 | Member 3 | Scan History with delete | `analysis/routes/history.py`<br>`ui/analysis/pages/History.jsx` |
| Module 3 | Member 3 | Scan Comparison | `analysis/routes/compare.py`<br>`ui/analysis/pages/Compare.jsx` |
| Module 3 | Member 3 | automated tests | `backend/tests/test_core.py`<br>`backend/tests/test_api.py` |

Who pushes what, branch names and the exact commands are in **GIT_WORKFLOW.md**. `ownership.json` is the same plan in a form the helper script reads.

---

## 3. Non-functional requirements

**Usability**
- Beginner mode on by default: every finding has "What this means" and "How to fix it".
- One-screen scan form with three profiles, live progress, severity filters.
- Responsive layout (works on phones), keyboard focus outlines, labelled form fields, reduced-motion support.
- Plain error messages that say what to do next.

**Security**
- Passwords hashed with bcrypt; never stored or logged in plain text.
- Login tokens are signed JWTs that expire (default 8 hours).
- Account lockout after 5 wrong passwords; login errors never reveal whether a username exists.
- SQL injection protected by the ORM (parameterized queries).
- Users can only read, download or delete their own scans (other people's IDs return "not found").
- Scope guard: permission confirmation is required and stored; one host per scan; private, loopback, link-local
  (cloud metadata) and multicast addresses are blocked on public servers.
- Scanner HTTP requests do not follow redirects (stops a target from redirecting the scanner to internal addresses).
- Reports escape all scanned content (a hostile banner cannot inject code into the HTML report).
- CORS only allows your own frontend URL.
- Limits: at most 2 concurrent scans per user, at most 2000 custom ports.

**Known limitations (be honest about these in your report)**
- The CVE file is small and version matching uses banners, which can be hidden or wrong.
- TLS 1.0/1.1 detection depends on your local OpenSSL; some builds refuse to test old protocols.
- Background scans run inside the API process, so a server restart marks running scans as failed. For heavy
  production use, move scans to a job queue (Celery / RQ).
- Tables are created automatically on start-up. For schema changes in production, add Alembic migrations.
- JWT is kept in `localStorage` for simplicity. For stronger protection use HttpOnly cookies.

---

## 4. Deploy

### Important before you deploy

Hosting providers often forbid port scanning from their servers in their acceptable-use policy. Read the
current policy of the provider you choose before running scans from it. A safe pattern is: deploy the website
and keep **web-only** scans for public use, and run **port scans** from your own computer.
Also check Render's current free-tier limits (free databases are time-limited).

### Step A: put the code on GitHub

```bash
git init
git add .
git commit -m "VulnSight"
# create an empty repo on github.com, then:
git remote add origin https://github.com/YOURNAME/vulnsight.git
git push -u origin main
```

(`.gitignore` already keeps `.env` files and databases out of GitHub.)

### Step B: backend + database on Render

1. Sign in at render.com > **New > Blueprint** > select your repo. Render reads `render.yaml`.
2. When asked for `FRONTEND_URLS`, type a temporary value (for example `http://localhost:5173`). You will update it in Step D.
3. Wait for the deploy. Your API URL looks like `https://vulnsight-api.onrender.com`. Check `/api/health`.

### Step C: frontend on Vercel

1. vercel.com > **Add New > Project** > pick the same repo.
2. Set **Root Directory** to `frontend`. Framework preset: Vite.
3. Add an Environment Variable: `VITE_API_URL` = your Render URL (no trailing slash).
4. Deploy. `vercel.json` makes page refreshes work.

### Step D: connect them

In Render > your service > **Environment**, set `FRONTEND_URLS` to your Vercel URL
(for example `https://vulnsight.vercel.app`) and redeploy. Register an account on the live site, then make
yourself admin from your own computer (Render's Shell tab is a paid feature): copy the database's **External
Database URL** from the Render dashboard, then run

```bash
cd backend
# Mac/Linux:
DATABASE_URL="<external url>" python create_admin.py yourusername
# Windows PowerShell:
$env:DATABASE_URL="<external url>"; python create_admin.py yourusername
```

(For this you also need `pip install psycopg2-binary` locally.)

---

## 5. Folder map and how the modules plug together

```
vulnsight/
├── backend/
│   ├── app/
│   │   ├── main.py            start-up only: creates the app and finds the modules
│   │   ├── core/              shared foundation: settings, database, tables, plug-in system
│   │   └── modules/
│   │       ├── users/         Module 1: accounts, lockout, scan permission, admin, private workspace
│   │       ├── scanning/      Module 2: scan setup, runner, progress, and the 8 checks in checks/
│   │       └── analysis/      Module 3: risk scoring, dashboard, reports, history, comparison
│   ├── data/cve.json
│   ├── tests/
│   └── create_admin.py
├── frontend/src/
│   ├── shared/                api calls, login state, layout, page finder
│   └── modules/{users,scanning,analysis}/{pages,components}/
├── ownership.json  GIT_WORKFLOW.md  tools/git_plan.py
├── render.yaml
└── README.md
```

How the pieces find each other (so nobody edits a shared list):

- **Backend routes:** `core/discovery.py` imports every file under `modules/` at start-up. A file that defines `router` becomes API routes.
- **Scan checks:** each file in `scanning/checks/` registers itself with `@register_check`. A profile only lists check names.
- **Login and scoring:** `users/lockout.py` and `analysis/scoring.py` plug into the login and the scan runner through `core/hooks.py`.
- **Frontend pages:** every file in `modules/*/pages/` that exports `route` becomes a page, and `nav` adds its menu entry (`shared/pageRegistry.js`).
- **Adding a feature** means adding a file in a module. No shared file changes.
