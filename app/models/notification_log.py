from datetime import datetime
from app import db

class NotificationLog(db.Model):
    __tablename__ = 'notification_logs'

    id = db.Column(db.Integer, primary_key=True)
    channel = db.Column(db.String(10), nullable=False)  # sms | push
    recipient = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'channel': self.channel,
            'recipient': self.recipient,
            'message': self.message,
            'created_at': self.created_at.isoformat(),
        }
