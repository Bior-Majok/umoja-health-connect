"""SMS/push notification senders.

send_sms() sends a real SMS via Africa's Talking when AFRICASTALKING_USERNAME and
AFRICASTALKING_API_KEY are configured (see config.py / environment variables).
Without those credentials it falls back to a mocked sender that only logs and
records a NotificationLog row — so every notification the SRS requires (emergency
alerts, appointment reminders, family confirmations) is still verifiable end-to-end
in tests and the UI even with no SMS account set up.

send_push() (Firebase Cloud Messaging) remains mocked — wiring up real push
requires a Firebase project + device tokens, which is a separate piece of work.
"""
import requests
from flask import current_app
from app import db
from app.models.notification_log import NotificationLog


def _africastalking_configured():
    return bool(
        current_app.config.get('AFRICASTALKING_USERNAME')
        and current_app.config.get('AFRICASTALKING_API_KEY')
    )


def _send_via_africastalking(to, message):
    sandbox = current_app.config.get('AFRICASTALKING_SANDBOX', True)
    base_url = (
        'https://api.sandbox.africastalking.com'
        if sandbox
        else 'https://api.africastalking.com'
    )
    response = requests.post(
        f'{base_url}/version1/messaging',
        headers={
            'apiKey': current_app.config['AFRICASTALKING_API_KEY'],
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        data={
            'username': current_app.config['AFRICASTALKING_USERNAME'],
            'to': to,
            'message': message,
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def send_sms(to, message):
    if _africastalking_configured():
        try:
            result = _send_via_africastalking(to, message)
            current_app.logger.info('[SMS SENT] to=%s message=%s result=%s', to, message, result)
        except Exception as exc:
            current_app.logger.warning('[SMS FAILED] to=%s message=%s error=%s', to, message, exc)
    else:
        current_app.logger.info('[MOCK SMS] to=%s message=%s', to, message)

    log = NotificationLog(channel='sms', recipient=to, message=message)
    db.session.add(log)
    db.session.commit()
    return log


def send_push(to, title, body):
    message = f'{title}: {body}'
    current_app.logger.info('[MOCK PUSH] to=%s message=%s', to, message)
    log = NotificationLog(channel='push', recipient=to, message=message)
    db.session.add(log)
    db.session.commit()
    return log
