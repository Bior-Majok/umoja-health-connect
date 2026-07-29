import re
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from app import db
from app.models.consultation import Consultation
from app.models.patient import Patient
from app.models.provider import HealthcareProvider
from app.models.emergency_alert import EmergencyAlert
from app.services.notifications import send_push, send_sms
from app.utils.auth import require_role

# Business rules: non-urgent consultations escalate to the next available provider after
# 24h with no response; critical ones escalate after 2h.
_ROUTINE_SLA = timedelta(hours=24)
_CRITICAL_SLA = timedelta(hours=2)

consultations_bp = Blueprint('consultations', __name__)

# FR 2.2: auto-assignment is based on location AND symptoms. Symptom text is matched
# against a specialization keyword so, say, a child's fever routes to a provider whose
# specialization mentions pediatrics before falling back to whoever is least loaded.
_SYMPTOM_SPECIALIZATION_RULES = [
    (r'\b(child|infant|baby|toddler|newborn)\b', r'child|pediatric|paediatric'),
    (r'\b(medication|prescription|drug|refill|dosage)\b', r'pharma'),
    (r'\b(wound|injury|bleeding|fracture|burn)\b', r'nurse'),
]


def _preferred_specialization_pattern(symptoms):
    text = (symptoms or '').lower()
    for symptom_pattern, specialization_pattern in _SYMPTOM_SPECIALIZATION_RULES:
        if re.search(symptom_pattern, text):
            return specialization_pattern
    return None


def _assign_provider(patient, symptoms=None, exclude_provider_id=None):
    """Least-loaded verified provider matching the patient's region and symptom category,
    falling back to region-only, then to any verified provider (FR 2.2)."""
    open_count = (
        db.session.query(Consultation.provider_id, db.func.count(Consultation.id))
        .filter(Consultation.status.in_(['assigned', 'pending']))
        .group_by(Consultation.provider_id)
    )
    load_by_provider = {pid: count for pid, count in open_count if pid}

    def pick(candidates):
        candidates = [p for p in candidates if p.provider_id != exclude_provider_id]
        if not candidates:
            return None
        return min(candidates, key=lambda p: load_by_provider.get(p.provider_id, 0))

    # Region is free text on both sides (registration forms), so match tolerant of
    # case/whitespace differences (e.g. "Nairobi" vs "nairobi " ) rather than an exact
    # string match, which would silently fail to find an otherwise-matching provider.
    patient_region = (patient.region or '').strip().lower()
    regional = HealthcareProvider.query.filter(
        HealthcareProvider.is_verified.is_(True),
        HealthcareProvider.is_available.is_(True),
        db.func.lower(db.func.trim(HealthcareProvider.region)) == patient_region,
    ).all()

    specialization_pattern = _preferred_specialization_pattern(symptoms)
    if specialization_pattern:
        regional_match = [p for p in regional if re.search(specialization_pattern, (p.specialization or '').lower())]
        chosen = pick(regional_match)
        if chosen:
            return chosen

    chosen = pick(regional)
    if chosen:
        return chosen

    any_verified = HealthcareProvider.query.filter_by(is_verified=True, is_available=True).all()
    if specialization_pattern:
        any_match = [p for p in any_verified if re.search(specialization_pattern, (p.specialization or '').lower())]
        chosen = pick(any_match)
        if chosen:
            return chosen

    return pick(any_verified)


def run_escalation_sweep():
    """Business rules NFR15: reassign consultations that have sat without a provider
    response past their SLA (2h critical / 24h routine) to the next available provider.
    Called periodically by the background scheduler in app/__init__.py."""
    now = datetime.utcnow()
    open_consultations = Consultation.query.filter(Consultation.status.in_(['assigned', 'pending'])).all()
    escalated = []

    for consultation in open_consultations:
        clock_start = consultation.assigned_at or consultation.created_at
        sla = _CRITICAL_SLA if consultation.urgency == 'critical' else _ROUTINE_SLA
        if now - clock_start < sla:
            continue

        patient = Patient.query.filter_by(patient_id=consultation.patient_id).first()
        if not patient:
            continue

        next_provider = _assign_provider(
            patient, symptoms=consultation.symptoms, exclude_provider_id=consultation.provider_id
        )
        if not next_provider:
            continue

        consultation.provider_id = next_provider.provider_id
        consultation.status = 'assigned'
        consultation.assigned_at = now
        consultation.escalation_count += 1
        db.session.add(consultation)
        send_push(
            next_provider.phone_number,
            'Escalated consultation assigned',
            f'Patient {consultation.patient_id} had no provider response in time — case escalated to you.',
        )
        escalated.append(consultation.id)

    if escalated:
        db.session.commit()
    return escalated


def create_consultation_record(patient, symptoms, language='en', created_by_volunteer_id=None):
    """Shared by the JSON API route and the inbound SMS command handler (FR 2.1) so
    feature-phone patients get the exact same auto-assignment and notification path."""
    provider = _assign_provider(patient, symptoms=symptoms)

    consultation = Consultation(
        patient_id=patient.patient_id,
        provider_id=provider.provider_id if provider else None,
        created_by_volunteer_id=created_by_volunteer_id,
        symptoms=symptoms,
        language=language,
        status='assigned' if provider else 'pending',
        assigned_at=datetime.utcnow() if provider else None,
    )
    db.session.add(consultation)
    db.session.commit()

    if provider:
        send_push(provider.phone_number, 'New consultation assigned', f'Patient {patient.patient_id} needs a response.')

    return consultation, provider


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

    consultation, _provider = create_consultation_record(
        patient, data['symptoms'], language=data.get('language', 'en'), created_by_volunteer_id=created_by_volunteer_id
    )

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

    patient = Patient.query.filter_by(patient_id=consultation.patient_id).first()

    urgency = data.get('urgency')
    escalated_alert = None
    if urgency == 'critical':
        consultation.urgency = 'critical'
        escalated_alert = EmergencyAlert(
            patient_id=patient.patient_id,
            location=f'{patient.region}, {patient.country}',
            condition=consultation.symptoms,
            severity='critical',
            status='open',
        )
        db.session.add(escalated_alert)
        send_sms(patient.phone_number, 'Your case has been escalated as urgent. A provider will contact you shortly.')
    else:
        # The critical path already notifies the patient above — for a routine
        # response, still let them know so they aren't left checking the app blindly.
        send_sms(patient.phone_number, 'A healthcare provider has responded to your consultation. Open the app to see their notes.')

    db.session.commit()

    response = {'consultation': consultation.to_dict()}
    if escalated_alert:
        response['emergency_alert'] = escalated_alert.to_dict()
    return jsonify(response), 200
