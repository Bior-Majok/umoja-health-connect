from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from app import db
from app.models.emergency_alert import EmergencyAlert
from app.models.patient import Patient
from app.models.provider import HealthcareProvider
from app.services.notifications import send_sms, send_push
from app.utils.auth import require_role

emergency_alerts_bp = Blueprint('emergency_alerts', __name__)

NEAREST_FACILITY_CONTACT = '+000000000'  # placeholder for a real facility directory lookup


@emergency_alerts_bp.route('', methods=['POST'])
@require_role('patient', 'volunteer')
def trigger_alert():
    data = request.get_json()
    claims = get_jwt()
    role = claims.get('role')

    if not data.get('location') or not data.get('condition'):
        return jsonify({'error': 'location and condition are required'}), 400

    if role == 'patient':
        patient = Patient.query.filter_by(patient_id=get_jwt_identity()).first()
        triggered_by_volunteer_id = None
    else:
        patient_phone = data.get('patient_phone_number')
        if not patient_phone:
            return jsonify({'error': 'patient_phone_number is required when triggered by a volunteer'}), 400
        patient = Patient.query.filter_by(phone_number=patient_phone).first()
        if not patient:
            return jsonify({'error': 'No patient found with that phone number'}), 404
        triggered_by_volunteer_id = get_jwt_identity()

    alert = EmergencyAlert(
        patient_id=patient.patient_id,
        triggered_by_volunteer_id=triggered_by_volunteer_id,
        location=data['location'],
        condition=data['condition'],
        severity=data.get('severity', 'critical'),
    )
    db.session.add(alert)
    db.session.commit()

    providers = HealthcareProvider.query.filter_by(is_verified=True, region=patient.region).all()
    for provider in providers:
        send_push(provider.phone_number, 'EMERGENCY ALERT', f'{patient.full_name} at {alert.location}: {alert.condition}')
    send_sms(NEAREST_FACILITY_CONTACT, f'Emergency: {patient.full_name} at {alert.location}: {alert.condition}')

    alert.status = 'notified'
    db.session.commit()

    return jsonify({'emergency_alert': alert.to_dict(), 'providers_notified': len(providers)}), 201


@emergency_alerts_bp.route('', methods=['GET'])
@require_role('patient', 'provider', 'volunteer', 'admin')
def list_alerts():
    claims = get_jwt()
    role = claims.get('role')
    identity = get_jwt_identity()

    query = EmergencyAlert.query
    if role == 'patient':
        query = query.filter_by(patient_id=identity)
    elif role == 'volunteer':
        query = query.filter_by(triggered_by_volunteer_id=identity)
    elif role == 'provider':
        provider = HealthcareProvider.query.filter_by(provider_id=identity).first()
        patient_ids = [p.patient_id for p in Patient.query.filter_by(region=provider.region).all()]
        query = query.filter(EmergencyAlert.patient_id.in_(patient_ids))
    # admin: no filter

    alerts = query.order_by(EmergencyAlert.created_at.desc()).all()
    return jsonify({'emergency_alerts': [a.to_dict() for a in alerts]}), 200


@emergency_alerts_bp.route('/<int:alert_id>/resolve', methods=['PATCH'])
@require_role('provider')
def resolve_alert(alert_id):
    alert = EmergencyAlert.query.filter_by(id=alert_id).first()
    if not alert:
        return jsonify({'error': 'Emergency alert not found'}), 404

    alert.status = 'resolved'
    alert.resolved_at = datetime.utcnow()
    db.session.commit()

    patient = Patient.query.filter_by(patient_id=alert.patient_id).first()
    if patient and patient.family_contact_phone:
        send_sms(
            patient.family_contact_phone,
            f'{patient.full_name}\'s emergency case has been treated and resolved.',
        )

    return jsonify({'emergency_alert': alert.to_dict()}), 200
