"""Inbound SMS command interface for feature-phone users with no app and no internet
(SRS Hardware Interfaces 3.2, FR 2.1, FR 3.1, and the "SMS Command Guide" deliverable).

Africa's Talking (and most SMS gateways) call a webhook with the sender's number and
message text whenever an SMS arrives on the shortcode/number this app is registered
under. This endpoint parses simple commands so a patient with only a basic GSM phone
can report symptoms or trigger an emergency alert without ever opening the app.
"""

from flask import Blueprint, request, jsonify, current_app
from app.models.patient import Patient
from app.routes.consultations import create_consultation_record
from app.routes.emergency_alerts import create_emergency_alert_record
from app.services.notifications import send_sms

sms_bp = Blueprint('sms', __name__)

HELP_TEXT = (
    "Umoja Health Connect commands: "
    "SYMPTOM <describe how you feel> to report symptoms, "
    "EMERGENCY <describe the emergency> to alert nearby providers, "
    "HELP for this message."
)
NO_ACCOUNT_TEXT = (
    "We could not find an Umoja Health Connect account for this number. "
    "Ask a community health volunteer to register you, then text again."
)


def _is_authorized(req):
    secret = current_app.config.get('SMS_INBOUND_SECRET')
    if not secret:
        # No secret configured (e.g. local dev) — accept any request.
        return True
    return req.values.get('secret') == secret or req.headers.get('X-Sms-Secret') == secret


@sms_bp.route('/inbound', methods=['POST'])
def inbound_sms():
    if not _is_authorized(request):
        return jsonify({'error': 'unauthorized'}), 403

    sender = (request.values.get('from') or '').strip()
    text = (request.values.get('text') or '').strip()
    if not sender or not text:
        return jsonify({'error': 'from and text are required'}), 400

    patient = Patient.query.filter_by(phone_number=sender).first()
    if not patient:
        send_sms(sender, NO_ACCOUNT_TEXT)
        return jsonify({'status': 'no_account'}), 200

    command, _, rest = text.strip().partition(' ')
    command = command.strip().upper()
    rest = rest.strip()

    if command == 'SYMPTOM' and rest:
        consultation, provider = create_consultation_record(patient, rest)
        if provider:
            send_sms(sender, 'Your symptoms were received. A provider has been notified and will respond soon.')
        else:
            send_sms(sender, 'Your symptoms were received. No provider is available right now — you will be notified.')
        return jsonify({'status': 'consultation_created', 'consultation_id': consultation.id}), 201

    if command == 'EMERGENCY' and rest:
        alert, providers = create_emergency_alert_record(patient, rest)
        send_sms(sender, f'Emergency alert sent to {len(providers)} nearby provider(s). Help is on the way.')
        return jsonify({'status': 'alert_created', 'alert_id': alert.id}), 201

    send_sms(sender, HELP_TEXT)
    return jsonify({'status': 'help_sent'}), 200
