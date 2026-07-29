# Umoja Health Connect

A mobile health (mHealth) web platform connecting patients in underserved, rural, and
conflict-affected African communities with verified healthcare providers.

Built to the project's Software Requirements Specification (SRS): patient registration,
teleconsultation, emergency alerts, appointment scheduling, patient records, a
multi-language health education library, and admin/provider/community-volunteer roles.

## Project structure

```
umoja-health-connect/
├── app/                # Flask backend (models, routes, services)
├── frontend/           # Web app (plain HTML/CSS/JS), served by Flask as static files
├── tests/              # pytest test suite for the backend
├── config.py           # Flask configuration
├── run.py              # Local dev server entry point
├── requirements.txt    # Python dependencies
└── Procfile            # Production entry point (gunicorn), for platforms like Render/Railway
```

## 1. Backend + web app setup (required)

The web frontend is served *by* the Flask backend, so this is the only setup needed to
run and use the full web app.

### Prerequisites
- Python 3.11+ and `pip`

### Steps
1. Clone the repo and enter it:
   ```bash
   git clone https://github.com/Bior-Majok/umoja-health-connect.git
   cd umoja-health-connect
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   python run.py
   ```
   This creates a local SQLite database (`instance/umoja_health.db`) automatically on
   first run — no separate migration step needed.
5. Open **http://127.0.0.1:5000** in your browser. That's the patient-facing web app.
   - Provider sign-in/register: `/provider-login.html`
   - Community volunteer sign-in/register: `/volunteer-login.html`
   - Administrator sign-in: `/admin-login.html`

### Creating an administrator account
Administrators are not self-registered (by design — see the SRS business rules). Create
one from the command line:
```bash
export FLASK_APP=run.py      # Windows: set FLASK_APP=run.py
flask seed-admin
```
Follow the prompts for name, phone number, and password, then log in at `/admin-login.html`.
From the admin dashboard you can verify newly-registered healthcare providers so they can
start receiving consultations and appointments.

### Running the test suite
```bash
pytest
```
66 tests covering auth (all four roles), consultations (including symptom-based routing
and SLA auto-escalation), emergency alerts, appointments, medical records (including
provider access), health education, inbound SMS commands, and account lockout.

## 2. Deployment

The Procfile (`web: gunicorn run:app`) is ready for any platform that runs a `Procfile`
(Render, Railway, Heroku-style hosts). Set the following environment variables in
production rather than relying on the development defaults in `config.py`:

| Variable | Required | Purpose |
|---|---|---|
| `SECRET_KEY` | Yes | Flask session/signing secret |
| `JWT_SECRET_KEY` | Yes | JWT signing secret |
| `DATABASE_URL` | No | Postgres connection string (per SRS Software Interfaces). Falls back to local SQLite if unset — fine for a demo/pilot, but set this for a real deployment. |
| `ENCRYPTION_KEY` | Recommended | Key used to derive the AES-256 key that encrypts personal health data at rest (symptoms, consultation notes, alert conditions, medical record details). Falls back to a fixed dev-only key if unset — **do not leave unset in production**. |
| `AFRICASTALKING_USERNAME` / `AFRICASTALKING_API_KEY` | No | Enables real outbound SMS delivery. Falls back to a mocked/logged sender if unset. |
| `SMS_INBOUND_SECRET` | Recommended if using inbound SMS | Shared secret Africa's Talking must echo back on the inbound webhook so it can't be spoofed by an arbitrary POST. |

### Wiring real SMS (outbound + inbound)
1. Create an Africa's Talking account and set `AFRICASTALKING_USERNAME`/`AFRICASTALKING_API_KEY` (and `AFRICASTALKING_SANDBOX=false` once out of sandbox) — this switches `app/services/notifications.py` from mocked to real delivery.
2. In the Africa's Talking dashboard, point your SMS number's inbound webhook at `https://<your-domain>/api/sms/inbound?secret=<SMS_INBOUND_SECRET>`. This is what lets patients with no smartphone and no internet text `SYMPTOM <how you feel>` or `EMERGENCY <what's happening>` and get routed through the same consultation/alert flow as the app — see `app/routes/sms.py`.

## Notes on scope

- Non-English health-education/UI content is a best-effort translation, not medically
  vetted — flagged via the `is_verified` field per the SRS's business rule that clinical
  content requires expert review before publishing.
- The background scheduler (`app/services/scheduler.py`) runs the consultation
  auto-escalation sweep every 5 minutes and a database backup every 24 hours. On the
  managed-Postgres path (`DATABASE_URL` set), the backup job just logs that the host's
  own automated backups apply, rather than reinventing `pg_dump` scheduling.
- 500,000-concurrent-user scale and multi-region African cloud hosting (both explicit
  SRS NFRs) are infrastructure claims that depend on the hosting tier chosen, not
  something the codebase itself can guarantee — the architecture (stateless JWT auth,
  indexed foreign keys, Postgres-ready config) doesn't block scaling, but this repo
  hasn't been load-tested at that scale.
