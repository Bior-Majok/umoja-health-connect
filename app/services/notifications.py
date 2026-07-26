"""Mocked SMS/push notification senders.

This app has no paid Africa's Talking (SMS) or Firebase Cloud Messaging (push)
credentials configured, so real messages are never sent. Instead each call logs
via the app logger and records a NotificationLog row, so every notification the
SRS requires (emergency alerts, appointment reminders, family confirmations) can
still be verified end-to-end in tests and the UI.

To go live: swap the body of send_sms()/send_push() for real Africa's Talking /
FCM SDK calls, gated behind app.config values (e.g. AFRICAS_TALKING_API_KEY).
"""
from flask import current_app
from app import db
from app.models.notification_log import NotificationLog


def send_sms(to, message):
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
