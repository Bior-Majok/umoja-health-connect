from app import db
from app.models.mixins import AuthMixin

class HealthcareProvider(db.Model, AuthMixin):
    __tablename__ = 'healthcare_providers'

    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    region = db.Column(db.String(50), nullable=False)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    is_available = db.Column(db.Boolean, nullable=False, default=True)
    password_hash = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            'provider_id': self.provider_id,
            'full_name': self.full_name,
            'phone_number': self.phone_number,
            'specialization': self.specialization,
            'country': self.country,
            'region': self.region,
            'is_verified': self.is_verified,
            'is_available': self.is_available,
        }
