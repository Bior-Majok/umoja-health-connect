from app import db
from app.utils.crypto import EncryptedText

class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patients.patient_id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    details = db.Column(EncryptedText)
    recorded_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='normal')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'details': self.details,
            'recorded_at': self.recorded_at.isoformat(),
            'status': self.status,
        }
