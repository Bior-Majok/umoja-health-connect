from datetime import datetime
from app import db

class HealthEducationArticle(db.Model):
    __tablename__ = 'health_education_articles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    language = db.Column(db.String(10), nullable=False, default='en')
    is_verified = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'body': self.body,
            'category': self.category,
            'language': self.language,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
        }
