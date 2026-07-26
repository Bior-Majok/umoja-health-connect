from datetime import datetime
from app import db

class EmergencyAlert(db.Model):
    __tablename__ = 'emergency_alerts'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patients.patient_id'), nullable=False)
    triggered_by_volunteer_id = db.Column(db.String(50), db.ForeignKey('community_health_volunteers.volunteer_id'), nullable=True)
    location = db.Column(db.String(200), nullable=False)
    condition = db.Column(db.String(500), nullable=False)
    severity = db.Column(db.String(10), nullable=False, default='critical')  # normal | critical
    status = db.Column(db.String(10), nullable=False, default='open')  # open | notified | resolved
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'triggered_by_volunteer_id': self.triggered_by_volunteer_id,
            'location': self.location,
            'condition': self.condition,
            'severity': self.severity,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
        }
