# Umoja Health Connect

A mobile health (mHealth) platform connecting patients in underserved, rural, and
conflict-affected African communities with verified healthcare providers — via a web
app, or plain SMS for patients with no smartphone or internet access.

**Live demo:** https://umoja-health-connect.onrender.com
**SRS document:** _add your SRS link here before submitting_

Built to satisfy the project's Software Requirements Specification (SRS): patient
registration, symptom-based teleconsultation, emergency alerts, appointment scheduling,
patient records, a multi-language health education library, and four distinct user
roles — Patient, Community Health Volunteer, Healthcare Provider, and Administrator.

---

## Table of contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Getting started](#getting-started)
- [Creating an administrator account](#creating-an-administrator-account)
- [Running the test suite](#running-the-test-suite)
- [API overview](#api-overview)
- [Environment variables](#environment-variables)
- [Deployment](#deployment)
- [Wiring real SMS](#wiring-real-sms-outbound--inbound)
- [Security notes](#security-notes)
- [Known limitations](#known-limitations)

---

## Features

**Patient**
- Registration and secure login (phone number + password, account lockout after 5 failed attempts)
- Symptom reporting via a visual checklist or free text, in the patient's own language
- Automatic teleconsultation assignment — matched by region *and* symptom category to the least-loaded verified provider
- One-tap emergency alerts (condition + location) notifying every verified provider in the region, plus the nearest facility
- Appointment booking against real verified providers, with SMS confirmation
- Personal medical record storage and retrieval
- Offline-downloadable health education library in English, French, Swahili, and Arabic (with right-to-left layout for Arabic)
- Full UI available in all four languages, patient-side and provider/admin/volunteer portals alike

**Community Health Volunteer**
- Submit a consultation or trigger an emergency alert on behalf of a patient who can't use the platform directly (by phone number)

**Healthcare Provider**
- Consultation queue, color-coded by urgency, with response/close/escalate workflow
- Direct access to the medical records of patients they're assigned to
- Appointment management and emergency alert resolution (with automatic SMS confirmation to the patient's family contact)

**Administrator**
- Verify or suspend healthcare providers — no provider can accept consultations until verified
- Manage a health facility directory (clinics, hospitals, pharmacies)
- Platform-wide reports: patients by country, providers by region, consultation and alert volumes

**Platform-wide**
- Inbound SMS command interface (`SYMPTOM ...`, `EMERGENCY ...`, `HELP`) so patients on a basic feature phone with zero internet can use the platform's core features by text message alone
- AES-256 encryption at rest for personal health data (symptoms, consultation notes, alert conditions, record details)
- Automatic consultation escalation if a provider doesn't respond in time (2h for critical cases, 24h for routine ones)
- Automated 24-hour database backups
- PostgreSQL-ready (falls back to SQLite for local development)

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-CORS |
| Database | SQLite (local dev) / PostgreSQL (production) |
| Frontend | Vanilla HTML, CSS, and JavaScript — served directly by Flask, no build step |
| Auth | JWT with role-based claims (patient / provider / volunteer / admin) |
| Background jobs | APScheduler (SLA escalation sweep, daily backups) |
| Encryption | `cryptography` (AES-256-GCM) for personal health data at rest |
| SMS | Africa's Talking (real delivery when configured, mocked/logged otherwise) |
| Testing | pytest |
| Deployment | gunicorn, via `Procfile` (Render, Railway, or any Heroku-style host) |

---

## Project structure

```
umoja-health-connect/
├── app/
│   ├── models/          # SQLAlchemy models (Patient, Provider, Volunteer, Admin, Consultation, ...)
│   ├── routes/          # Flask blueprints — one per feature area
│   ├── services/        # Notifications, encryption, backups, scheduler
│   ├── utils/            # Auth decorators, crypto helpers
│   └── labels.py         # All UI translation strings (en/fr/sw/ar)
├── frontend/             # Web app — plain HTML/CSS/JS, one HTML file per page
├── tests/                # pytest suite
├── config.py             # Flask configuration (env-var driven)
├── run.py                # Local dev server entry point
├── requirements.txt
└── Procfile               # Production entry point: gunicorn run:app
```

---

## Getting started

The web frontend is served *by* the Flask backend, so this is the only setup needed to
run the entire application locally.

### Prerequisites
- Python 3.11+ and `pip`

### Steps

1. **Clone the repo:**
   ```bash
   git clone https://github.com/Bior-Majok/umoja-health-connect.git
   cd umoja-health-connect
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv

   # Windows:
   venv\Scripts\activate

   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app:**
   ```bash
   python run.py
   ```
   This creates a local SQLite database (`instance/umoja_health.db`) automatically on
   first run — no separate migration step needed.

5. **Open the app** at **http://127.0.0.1:5000**
   - Patient: login / register at the root URL
   - Healthcare provider: `/provider-login.html` / `/provider-register.html`
   - Community volunteer: `/volunteer-login.html` / `/volunteer-register.html`
   - Administrator: `/admin-login.html` (see below — admins are not self-registered)

---

## Creating an administrator account

Administrators are provisioned, not self-registered — this is an explicit SRS business
rule (no provider can be verified without an admin, so admin accounts can't be open
signups). Create one from the command line:

```bash
export FLASK_APP=run.py      # Windows: set FLASK_APP=run.py
flask seed-admin
```

Follow the prompts for name, phone number, and password, then log in at
`/admin-login.html`. From the admin dashboard you can verify newly-registered
healthcare providers so they can start receiving consultations and appointments.

> **Deploying to Render or another host?** Run the same command from the host's shell
> (e.g. Render's "Shell" tab) — each environment has its own separate database.

---

## Running the test suite

```bash
pytest
```

66 tests covering:
- Authentication for all four roles, including account lockout
- Consultations — auto-assignment, symptom-based routing, SLA auto-escalation, critical escalation to emergency alerts
- Emergency alerts — trigger, provider/facility notification fan-out, resolution
- Appointments, medical records (including provider access), health education
- Inbound SMS commands
- Health facility directory, admin reports, i18n labels

---

## API overview

All endpoints are prefixed `/api`. JSON in, JSON out, JWT bearer auth except where noted.

| Prefix | Purpose |
|---|---|
| `/api/auth` | Patient registration, login, profile |
| `/api/auth/provider` | Provider registration (unverified until admin approval), login |
| `/api/auth/volunteer` | Volunteer registration, login |
| `/api/auth/admin` | Admin login only — no self-registration |
| `/api/providers` | Public provider listing; admin-only verify/suspend |
| `/api/consultations` | Create/list/respond — role-scoped by JWT claim |
| `/api/emergency-alerts` | Trigger/list/resolve |
| `/api/appointments` | Booking and management |
| `/api/records` | Patient's own records; `/records/patient/<id>` for assigned providers |
| `/api/health-education` | Public reads; admin-only writes |
| `/api/facilities` | Public reads; admin-only writes |
| `/api/admin/reports` | Admin-only aggregate reporting |
| `/api/labels` | UI translations, `?lang=en\|fr\|sw\|ar` |
| `/api/sms/inbound` | Webhook for inbound SMS commands (no JWT — see [Wiring real SMS](#wiring-real-sms-outbound--inbound)) |

---

## Environment variables

None are required for local development — sensible defaults are used. Set these in
production:

| Variable | Required | Purpose |
|---|---|---|
| `SECRET_KEY` | Yes | Flask session/signing secret |
| `JWT_SECRET_KEY` | Yes | JWT signing secret |
| `ENCRYPTION_KEY` | Recommended | Derives the AES-256 key that encrypts personal health data at rest. Falls back to a fixed dev-only key if unset — **do not leave unset in production** |
| `DATABASE_URL` | No | PostgreSQL connection string. Falls back to local SQLite if unset |
| `AFRICASTALKING_USERNAME` / `AFRICASTALKING_API_KEY` | No | Enables real outbound SMS delivery. Falls back to a mocked/logged sender if unset |
| `AFRICASTALKING_SANDBOX` | No | Defaults to `true`; set to `false` once out of Africa's Talking sandbox |
| `SMS_INBOUND_SECRET` | Recommended if using inbound SMS | Shared secret the SMS gateway must echo back so `/api/sms/inbound` can't be spoofed by an arbitrary POST |

---

## Deployment

The included `Procfile` (`web: gunicorn run:app`) works on any platform that runs a
`Procfile` — Render, Railway, or other Heroku-style hosts.

1. Connect the GitHub repo as a new Web Service.
2. Build command: `pip install -r requirements.txt`
3. **Start command: `gunicorn run:app`** — some platforms auto-detect and guess wrong (e.g. `gunicorn app:app`, which will fail since the Flask instance lives in `run.py`, not inside the `app` package). Set it explicitly.
4. Set the environment variables listed above (`SECRET_KEY`, `JWT_SECRET_KEY`, `ENCRYPTION_KEY` at minimum).
5. Deploy, then seed an admin account via the host's shell (see [Creating an administrator account](#creating-an-administrator-account)).

## Wiring real SMS (outbound + inbound)

1. Create an Africa's Talking account and set `AFRICASTALKING_USERNAME` /
   `AFRICASTALKING_API_KEY` (and `AFRICASTALKING_SANDBOX=false` once out of sandbox) —
   this switches `app/services/notifications.py` from mocked to real delivery.
2. In the Africa's Talking dashboard, point your SMS number's inbound webhook at
   `https://<your-domain>/api/sms/inbound?secret=<SMS_INBOUND_SECRET>`. This lets
   patients with no smartphone and no internet text `SYMPTOM <how you feel>` or
   `EMERGENCY <what's happening>` and get routed through the same consultation/alert
   pipeline as the web app — see `app/routes/sms.py`.

---

## Security notes

- Passwords are hashed (never stored in plaintext); accounts lock after 5 failed login attempts
- JWTs carry a role claim and every endpoint is role-gated via `require_role()`
- Personal health data (symptoms, consultation notes, alert conditions, record details) is encrypted at rest with AES-256-GCM
- Providers must be verified by an administrator before they can receive any consultation

## Known limitations

- Non-English health-education/UI content is a best-effort translation, not medically
  vetted — flagged via the `is_verified` field per the SRS's business rule that clinical
  content requires expert review before publishing
- The background scheduler (`app/services/scheduler.py`) runs the consultation
  auto-escalation sweep every 5 minutes and a database backup every 24 hours. On the
  managed-Postgres path (`DATABASE_URL` set), the backup job logs that the host's own
  automated backups apply, rather than reinventing `pg_dump` scheduling
- 500,000-concurrent-user scale and multi-region African cloud hosting (both explicit
  SRS NFRs) are infrastructure claims that depend on the hosting tier chosen, not
  something the codebase alone can guarantee — the architecture (stateless JWT auth,
  indexed foreign keys, Postgres-ready config) doesn't block scaling, but this repo
  hasn't been load-tested at that scale
