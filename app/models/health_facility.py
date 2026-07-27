from datetime import datetime
from app import db

class HealthFacility(db.Model):
    __tablename__ = 'health_facilities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    facility_type = db.Column(db.String(50), nullable=False, default='clinic')  # clinic | hospital | pharmacy
    country = db.Column(db.String(50), nullable=False)
    region = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'facility_type': self.facility_type,
            'country': self.country,
            'region': self.region,
            'phone_number': self.phone_number,
        }
