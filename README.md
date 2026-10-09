# DealRoom Security

**Enterprise security questionnaire autopilot** — connect GitHub / AWS / Google Workspace, scan controls, upload buyer CSV/XLSX, auto-draft evidence-backed answers, export for the deal.

## Stack

- **Backend:** FastAPI, SQLAlchemy, SQLite (dev)
- **Frontend:** React + Vite + TypeScript

## Run locally (Windows)

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --app-dir .
```

API: http://127.0.0.1:8000 — docs at http://127.0.0.1:8000/docs

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

### Tests

```powershell
# backend
cd backend
pip install -r requirements-dev.txt
pytest

# frontend
cd frontend
npm test
```

Backend: auth (register/login/me), controls catalog, integrations + scan wiring (GitHub API mocked),
questionnaire upload / matching / approve / CSV export, org isolation, public trust page.
Frontend: API error formatting, auth form validation + token storage, questionnaire upload regression.

## Docker

Builds the API and serves the UI through nginx (which proxies `/api` to the backend):

```powershell
docker compose up --build
```

- App: http://localhost:8080
- API: http://localhost:8000
- SQLite data is kept in the `dealroom-data` volume.

## Demo flow

1. **Sign up** with company name (creates org + trust slug).
2. **Integrations** → connect GitHub (PAT with `repo` read) → branch protection & repo checks run.
3. **Controls** → review pass/fail/unknown.
4. **Questionnaires** → upload `sample-data/buyer-questionnaire.csv`.
5. **Review** → approve drafts → **Export CSV**.
6. Open **Trust page** `/trust/your-slug` (public).

### Integrations

- **GitHub:** personal access token (read). Scans branch protection, repo activity, code scanning.
- **AWS:** access key + secret (read-only). Live checks when `boto3` is installed, guided otherwise.
- **Google Workspace:** paste an `admin_email` for guided checks, or a **service-account JSON**
  (with domain-wide delegation) plus the impersonated admin to run a live Admin SDK scan of
  admin 2-Step Verification enforcement and shared-mailbox usage.

## Security note (MVP)

Integration secrets are stored in local SQLite as JSON. For production: encrypt at rest, use a secrets manager, OAuth instead of long-lived tokens, and PostgreSQL.

## Product roadmap

- Stripe billing, team RBAC
- Questionnaire column mapping (multi-column Excel)
- PDF export + auditor pack
- Custom control library per framework (SIG Lite, CAIQ)
