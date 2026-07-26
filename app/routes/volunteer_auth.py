import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity
from app import db
from app.models.volunteer import CommunityHealthVolunteer
from app.utils.validators import is_valid_phone
from app.utils.auth import require_role

volunteer_auth_bp = Blueprint('volunteer_auth', __name__)


@volunteer_auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    required_fields = ['full_name', 'phone_number', 'assigned_region', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    if not is_valid_phone(data['phone_number']):
        return jsonify({'error': 'phone_number must be 7-15 digits, optionally prefixed with +'}), 400

    if CommunityHealthVolunteer.query.filter_by(phone_number=data['phone_number']).first():
        return jsonify({'error': 'Phone number already registered'}), 409

    volunteer = CommunityHealthVolunteer(
        volunteer_id=str(uuid.uuid4())[:8].upper(),
        full_name=data['full_name'],
        phone_number=data['phone_number'],
        assigned_region=data['assigned_region'],
    )
    volunteer.set_password(data['password'])

    db.session.add(volunteer)
    db.session.commit()

    return jsonify({'message': 'Volunteer registered successfully', 'volunteer': volunteer.to_dict()}), 201


@volunteer_auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if 'phone_number' not in data or 'password' not in data:
        return jsonify({'error': 'Phone number and password are required'}), 400

    volunteer = CommunityHealthVolunteer.query.filter_by(phone_number=data['phone_number']).first()

    if not volunteer:
        return jsonify({'error': 'Invalid phone number or password'}), 401

    if volunteer.is_locked():
        return jsonify({'error': 'Account locked due to too many failed attempts. Try again later.'}), 423

    if not volunteer.check_password(data['password']):
        volunteer.register_failed_attempt()
        return jsonify({'error': 'Invalid phone number or password'}), 401

    volunteer.reset_failed_attempts()

    access_token = create_access_token(identity=volunteer.volunteer_id, additional_claims={'role': 'volunteer'})

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'volunteer': volunteer.to_dict(),
    }), 200


@volunteer_auth_bp.route('/me', methods=['GET'])
@require_role('volunteer')
def get_me():
    volunteer = CommunityHealthVolunteer.query.filter_by(volunteer_id=get_jwt_identity()).first()
    if not volunteer:
        return jsonify({'error': 'Volunteer not found'}), 404
    return jsonify({'volunteer': volunteer.to_dict()}), 200
