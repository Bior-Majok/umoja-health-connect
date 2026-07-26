from app import db
from app.models.mixins import AuthMixin

class Administrator(db.Model, AuthMixin):
    __tablename__ = 'administrators'

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    scope_level = db.Column(db.String(20), nullable=False, default='national')  # national | regional
    region = db.Column(db.String(50), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            'admin_id': self.admin_id,
            'full_name': self.full_name,
            'phone_number': self.phone_number,
            'scope_level': self.scope_level,
            'region': self.region,
        }
