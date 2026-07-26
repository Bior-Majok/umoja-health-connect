from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


class AuthMixin:
    """Shared password hashing + failed-login lockout (NFR02) for all role models.

    Concrete models must inherit as `class Foo(db.Model, AuthMixin)` and define a
    `password_hash` column themselves (the primary key/id columns differ per role).
    """

    failed_attempts = db.Column(db.Integer, nullable=False, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_locked(self):
        return bool(self.locked_until and self.locked_until > datetime.utcnow())

    def register_failed_attempt(self):
        self.failed_attempts = (self.failed_attempts or 0) + 1
        if self.failed_attempts >= MAX_FAILED_ATTEMPTS:
            self.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)
        db.session.commit()

    def reset_failed_attempts(self):
        self.failed_attempts = 0
        self.locked_until = None
        db.session.commit()
