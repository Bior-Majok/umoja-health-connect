from flask import Blueprint, request, jsonify
from app import db
from app.models.health_facility import HealthFacility
from app.utils.auth import require_role

health_facilities_bp = Blueprint('health_facilities', __name__)


@health_facilities_bp.route('', methods=['GET'])
def list_facilities():
    query = HealthFacility.query
    if request.args.get('country'):
        query = query.filter_by(country=request.args['country'])
    if request.args.get('region'):
        query = query.filter_by(region=request.args['region'])
    facilities = query.order_by(HealthFacility.name).all()
    return jsonify({'facilities': [f.to_dict() for f in facilities]}), 200


@health_facilities_bp.route('', methods=['POST'])
@require_role('admin')
def create_facility():
    data = request.get_json()
    required_fields = ['name', 'country', 'region']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    facility_type = data.get('facility_type', 'clinic')
    if facility_type not in ('clinic', 'hospital', 'pharmacy'):
        return jsonify({'error': 'facility_type must be one of clinic, hospital, pharmacy'}), 400

    facility = HealthFacility(
        name=data['name'],
        facility_type=facility_type,
        country=data['country'],
        region=data['region'],
        phone_number=data.get('phone_number'),
    )
    db.session.add(facility)
    db.session.commit()
    return jsonify({'facility': facility.to_dict()}), 201


@health_facilities_bp.route('/<int:facility_id>', methods=['DELETE'])
@require_role('admin')
def delete_facility(facility_id):
    facility = HealthFacility.query.get(facility_id)
    if not facility:
        return jsonify({'error': 'Facility not found'}), 404
    db.session.delete(facility)
    db.session.commit()
    return jsonify({'message': 'Facility removed'}), 200
