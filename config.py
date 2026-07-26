import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'umoja-health-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///umoja_health.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'umoja-jwt-secret-key'
