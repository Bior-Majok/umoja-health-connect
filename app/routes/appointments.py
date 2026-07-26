from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app import db
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.provider import HealthcareProvider
from app.services.notifications import send_sms
from app.utils.auth import require_role

appointments_bp = Blueprint('appointments', __name__)


@appointments_bp.route('', methods=['GET'])
@require_role('patient')
def list_appointments():
    patient_id = get_jwt_identity()
    appointments = (
        Appointment.query.filter_by(patient_id=patient_id)
        .order_by(Appointment.scheduled_at)
        .all()
    )
    return jsonify({'appointments': [a.to_dict() for a in appointments]}), 200


@appointments_bp.route('', methods=['POST'])
@require_role('patient')
def create_appointment():
    patient_id = get_jwt_identity()
    data = request.get_json()

    required_fields = ['provider_id', 'clinic_name', 'scheduled_at']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    provider = HealthcareProvider.query.filter_by(provider_id=data['provider_id'], is_verified=True).first()
    if not provider:
        return jsonify({'error': 'No verified provider found with that provider_id'}), 400

    try:
        scheduled_at = datetime.fromisoformat(data['scheduled_at'])
    except (TypeError, ValueError):
        return jsonify({'error': 'scheduled_at must be a valid ISO datetime'}), 400

    appointment = Appointment(
        patient_id=patient_id,
        provider_id=provider.provider_id,
        clinic_name=data['clinic_name'],
        scheduled_at=scheduled_at,
        notes=data.get('notes'),
    )
    db.session.add(appointment)
    db.session.commit()

    patient = Patient.query.filter_by(patient_id=patient_id).first()
    send_sms(patient.phone_number, f'Appointment confirmed with {provider.full_name} at {appointment.scheduled_at}.')

    return jsonify({'appointment': appointment.to_dict()}), 201


@appointments_bp.route('/provider', methods=['GET'])
@require_role('provider')
def list_provider_appointments():
    provider_id = get_jwt_identity()
    appointments = (
        Appointment.query.filter_by(provider_id=provider_id)
        .order_by(Appointment.scheduled_at)
        .all()
    )
    return jsonify({'appointments': [a.to_dict() for a in appointments]}), 200


@appointments_bp.route('/<int:appointment_id>/complete', methods=['PATCH'])
@require_role('provider')
def complete_appointment(appointment_id):
    provider_id = get_jwt_identity()
    appointment = Appointment.query.filter_by(id=appointment_id, provider_id=provider_id).first()
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    appointment.status = 'completed'
    db.session.commit()
    return jsonify({'appointment': appointment.to_dict()}), 200


@appointments_bp.route('/<int:appointment_id>', methods=['PATCH'])
@require_role('patient')
def update_appointment(appointment_id):
    patient_id = get_jwt_identity()
    appointment = Appointment.query.filter_by(id=appointment_id, patient_id=patient_id).first()
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404

    data = request.get_json()
    status = data.get('status')
    if status not in ('upcoming', 'completed', 'cancelled'):
        return jsonify({'error': 'status must be one of upcoming, completed, cancelled'}), 400

    appointment.status = status
    db.session.commit()

    return jsonify({'appointment': appointment.to_dict()}), 200
