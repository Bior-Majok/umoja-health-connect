from app import db
from app.models.provider import HealthcareProvider

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patients.patient_id'), nullable=False)
    provider_id = db.Column(db.String(50), db.ForeignKey('healthcare_providers.provider_id'), nullable=False)
    clinic_name = db.Column(db.String(100), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.String(500))
    status = db.Column(db.String(20), nullable=False, default='upcoming')

    def to_dict(self):
        provider = HealthcareProvider.query.filter_by(provider_id=self.provider_id).first()
        return {
            'id': self.id,
            'provider_id': self.provider_id,
            'doctor_name': provider.full_name if provider else None,
            'clinic_name': self.clinic_name,
            'scheduled_at': self.scheduled_at.isoformat(),
            'notes': self.notes,
            'status': self.status,
        }
