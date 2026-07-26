from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app import db
from app.models.record import MedicalRecord
from app.utils.auth import require_role

records_bp = Blueprint('records', __name__)


@records_bp.route('', methods=['GET'])
@require_role('patient')
def list_records():
    patient_id = get_jwt_identity()
    records = (
        MedicalRecord.query.filter_by(patient_id=patient_id)
        .order_by(MedicalRecord.recorded_at.desc())
        .all()
    )
    return jsonify({'records': [r.to_dict() for r in records]}), 200


@records_bp.route('', methods=['POST'])
@require_role('patient')
def create_record():
    patient_id = get_jwt_identity()
    data = request.get_json()

    if not data.get('title'):
        return jsonify({'error': 'title is required'}), 400

    if data.get('recorded_at'):
        try:
            recorded_at = datetime.fromisoformat(data['recorded_at'])
        except (TypeError, ValueError):
            return jsonify({'error': 'recorded_at must be a valid ISO datetime'}), 400
    else:
        recorded_at = datetime.now(timezone.utc).replace(tzinfo=None)

    status = data.get('status', 'normal')
    if status not in ('normal', 'flagged'):
        return jsonify({'error': 'status must be one of normal, flagged'}), 400

    record = MedicalRecord(
        patient_id=patient_id,
        title=data['title'],
        details=data.get('details'),
        recorded_at=recorded_at,
        status=status,
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({'record': record.to_dict()}), 201
