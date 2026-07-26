from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from app import db
from app.models.consultation import Consultation
from app.models.patient import Patient
from app.models.provider import HealthcareProvider
from app.models.emergency_alert import EmergencyAlert
from app.services.notifications import send_push, send_sms
from app.utils.auth import require_role

consultations_bp = Blueprint('consultations', __name__)


def _assign_provider(patient):
    """Least-loaded verified provider in the patient's region, else any verified provider."""
    open_count = (
        db.session.query(Consultation.provider_id, db.func.count(Consultation.id))
        .filter(Consultation.status.in_(['assigned', 'pending']))
        .group_by(Consultation.provider_id)
    )
    load_by_provider = {pid: count for pid, count in open_count if pid}

    def pick(candidates):
        if not candidates:
            return None
        return min(candidates, key=lambda p: load_by_provider.get(p.provider_id, 0))

    regional = HealthcareProvider.query.filter_by(
        is_verified=True, is_available=True, region=patient.region
    ).all()
    chosen = pick(regional)
    if chosen:
        return chosen

    any_verified = HealthcareProvider.query.filter_by(is_verified=True, is_available=True).all()
    return pick(any_verified)


@consultations_bp.route('', methods=['POST'])
@require_role('patient', 'volunteer')
def create_consultation():
    data = request.get_json()
    claims = get_jwt()
    role = claims.get('role')

    if not data.get('symptoms'):
        return jsonify({'error': 'symptoms is required'}), 400

    if role == 'patient':
        patient = Patient.query.filter_by(patient_id=get_jwt_identity()).first()
        created_by_volunteer_id = None
    else:
        patient_phone = data.get('patient_phone_number')
        if not patient_phone:
            return jsonify({'error': 'patient_phone_number is required when submitted by a volunteer'}), 400
        patient = Patient.query.filter_by(phone_number=patient_phone).first()
        if not patient:
            return jsonify({'error': 'No patient found with that phone number'}), 404
        created_by_volunteer_id = get_jwt_identity()

    provider = _assign_provider(patient)

    consultation = Consultation(
        patient_id=patient.patient_id,
        provider_id=provider.provider_id if provider else None,
        created_by_volunteer_id=created_by_volunteer_id,
        symptoms=data['symptoms'],
        language=data.get('language', 'en'),
        status='assigned' if provider else 'pending',
    )
    db.session.add(consultation)
    db.session.commit()

    if provider:
        send_push(provider.phone_number, 'New consultation assigned', f'Patient {patient.patient_id} needs a response.')

    return jsonify({'consultation': consultation.to_dict()}), 201


@consultations_bp.route('', methods=['GET'])
@require_role('patient', 'provider', 'volunteer', 'admin')
def list_consultations():
    claims = get_jwt()
    role = claims.get('role')
    identity = get_jwt_identity()

    query = Consultation.query
    if role == 'patient':
        query = query.filter_by(patient_id=identity)
    elif role == 'provider':
        query = query.filter_by(provider_id=identity)
    elif role == 'volunteer':
        query = query.filter_by(created_by_volunteer_id=identity)
    # admin: no filter, sees all

    consultations = query.order_by(Consultation.created_at.desc()).all()
    return jsonify({'consultations': [c.to_dict() for c in consultations]}), 200


@consultations_bp.route('/<int:consultation_id>/respond', methods=['PATCH'])
@require_role('provider')
def respond_consultation(consultation_id):
    provider_id = get_jwt_identity()
    consultation = Consultation.query.filter_by(id=consultation_id, provider_id=provider_id).first()
    if not consultation:
        return jsonify({'error': 'Consultation not found'}), 404

    data = request.get_json()
    status = data.get('status', 'responded')
    if status not in ('responded', 'closed'):
        return jsonify({'error': 'status must be responded or closed'}), 400

    consultation.response_notes = data.get('response_notes', consultation.response_notes)
    consultation.status = status

    urgency = data.get('urgency')
    escalated_alert = None
    if urgency == 'critical':
        consultation.urgency = 'critical'
        patient = Patient.query.filter_by(patient_id=consultation.patient_id).first()
        escalated_alert = EmergencyAlert(
            patient_id=patient.patient_id,
            location=f'{patient.region}, {patient.country}',
            condition=consultation.symptoms,
            severity='critical',
            status='open',
        )
        db.session.add(escalated_alert)
        send_sms(patient.phone_number, 'Your case has been escalated as urgent. A provider will contact you shortly.')

    db.session.commit()

    response = {'consultation': consultation.to_dict()}
    if escalated_alert:
        response['emergency_alert'] = escalated_alert.to_dict()
    return jsonify(response), 200
