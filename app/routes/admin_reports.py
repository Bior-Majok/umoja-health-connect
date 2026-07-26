from flask import Blueprint, jsonify
from app import db
from app.models.provider import HealthcareProvider
from app.models.consultation import Consultation
from app.models.emergency_alert import EmergencyAlert
from app.models.patient import Patient
from app.utils.auth import require_role

admin_reports_bp = Blueprint('admin_reports', __name__)


def _group_count(model, group_col):
    rows = db.session.query(group_col, db.func.count(model.id)).group_by(group_col).all()
    return {key or 'unknown': count for key, count in rows}


@admin_reports_bp.route('', methods=['GET'])
@require_role('admin')
def get_reports():
    return jsonify({
        'patients_by_country': _group_count(Patient, Patient.country),
        'providers_by_region': _group_count(HealthcareProvider, HealthcareProvider.region),
        'verified_providers': HealthcareProvider.query.filter_by(is_verified=True).count(),
        'pending_providers': HealthcareProvider.query.filter_by(is_verified=False).count(),
        'consultations_by_status': _group_count(Consultation, Consultation.status),
        'emergency_alerts_by_status': _group_count(EmergencyAlert, EmergencyAlert.status),
    }), 200
