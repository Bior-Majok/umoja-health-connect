import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'umoja-health-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///umoja_health.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'umoja-jwt-secret-key'

    # Real SMS delivery via Africa's Talking (https://africastalking.com). Leave unset to
    # keep using the mocked/logged sender in app/services/notifications.py.
    AFRICASTALKING_USERNAME = os.environ.get('AFRICASTALKING_USERNAME')
    AFRICASTALKING_API_KEY = os.environ.get('AFRICASTALKING_API_KEY')
    AFRICASTALKING_SANDBOX = os.environ.get('AFRICASTALKING_SANDBOX', 'true').lower() != 'false'
