import os


def _database_uri():
    # SRS Software Interfaces (3.3) specifies PostgreSQL. Render (and most hosts) inject
    # a DATABASE_URL env var when a Postgres instance is attached; SQLAlchemy 1.4+ requires
    # the "postgresql://" scheme, but most providers still hand out the older "postgres://"
    # form, so normalize it. Falls back to local SQLite when no DATABASE_URL is set (local
    # dev / tests), since there's no Postgres server to talk to in that case.
    url = os.environ.get('DATABASE_URL')
    if not url:
        return 'sqlite:///umoja_health.db'
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    return url


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'umoja-health-secret-key'
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'umoja-jwt-secret-key'

    # Real SMS delivery via Africa's Talking (https://africastalking.com). Leave unset to
    # keep using the mocked/logged sender in app/services/notifications.py.
    AFRICASTALKING_USERNAME = os.environ.get('AFRICASTALKING_USERNAME')
    AFRICASTALKING_API_KEY = os.environ.get('AFRICASTALKING_API_KEY')
    AFRICASTALKING_SANDBOX = os.environ.get('AFRICASTALKING_SANDBOX', 'true').lower() != 'false'
    # Shared secret Africa's Talking must send back so /api/sms/inbound can't be spoofed
    # by an arbitrary POST from the internet (NFR01/NFR14 data integrity).
    SMS_INBOUND_SECRET = os.environ.get('SMS_INBOUND_SECRET')

    # NFR01: personal health information encrypted at rest (AES-256-GCM), applied to the
    # free-text medical fields via app/utils/crypto.py. Falls back to a fixed dev key so
    # local/test runs work out of the box; production deployments should set a real key.
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')

    # Unlocks POST /api/setup/seed-admin — an HTTP alternative to `flask seed-admin` for
    # hosts without shell access (e.g. Render's free tier). Unset by default, which
    # keeps the endpoint refusing all requests.
    SETUP_SECRET = os.environ.get('SETUP_SECRET')
