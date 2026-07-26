from app import db
from app.models.mixins import AuthMixin

class CommunityHealthVolunteer(db.Model, AuthMixin):
    __tablename__ = 'community_health_volunteers'

    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    assigned_region = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            'volunteer_id': self.volunteer_id,
            'full_name': self.full_name,
            'phone_number': self.phone_number,
            'assigned_region': self.assigned_region,
        }
