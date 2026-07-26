from datetime import datetime
from app import db

class Consultation(db.Model):
    __tablename__ = 'consultations'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patients.patient_id'), nullable=False)
    provider_id = db.Column(db.String(50), db.ForeignKey('healthcare_providers.provider_id'), nullable=True)
    created_by_volunteer_id = db.Column(db.String(50), db.ForeignKey('community_health_volunteers.volunteer_id'), nullable=True)
    symptoms = db.Column(db.String(1000), nullable=False)
    language = db.Column(db.String(10), nullable=False, default='en')
    urgency = db.Column(db.String(10), nullable=False, default='normal')  # normal | critical
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending|assigned|responded|closed
    response_notes = db.Column(db.String(1000), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'provider_id': self.provider_id,
            'created_by_volunteer_id': self.created_by_volunteer_id,
            'symptoms': self.symptoms,
            'language': self.language,
            'urgency': self.urgency,
            'status': self.status,
            'response_notes': self.response_notes,
            'created_at': self.created_at.isoformat(),
        }
