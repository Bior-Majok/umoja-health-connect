from app import db
from app.models.mixins import AuthMixin

class Patient(db.Model, AuthMixin):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    region = db.Column(db.String(50), nullable=False)
    family_contact_phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            'patient_id': self.patient_id,
            'full_name': self.full_name,
            'phone_number': self.phone_number,
            'age': self.age,
            'gender': self.gender,
            'country': self.country,
            'region': self.region,
            'family_contact_phone': self.family_contact_phone,
        }
