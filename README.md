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
47 tests covering auth (all four roles), consultations, emergency alerts, appointments,
medical records, health education, and account lockout.

## 2. Deployment

The Procfile (`web: gunicorn run:app`) is ready for any platform that runs a `Procfile`
(Render, Railway, Heroku-style hosts). Set the following environment variables in
production rather than relying on the development defaults in `config.py`:
- `SECRET_KEY`
- `JWT_SECRET_KEY`

## Notes on scope

- **SMS and push notifications are simulated**, not sent through a real carrier — there's
  no paid Africa's Talking/Firebase account configured. Every notification the SRS
  requires (emergency alerts, appointment confirmations, consultation escalations) still
  fires through `app/services/notifications.py` and is logged/recorded (`NotificationLog`
  table), so the feature is fully demonstrable end-to-end; swapping in real credentials
  is a small, isolated change in that one file.
- Non-English health-education/UI content is a best-effort translation, not medically
  vetted — flagged via the `is_verified` field per the SRS's business rule that clinical
  content requires expert review before publishing.
