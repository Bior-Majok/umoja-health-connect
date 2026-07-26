import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity
from app import db
from app.models.provider import HealthcareProvider
from app.utils.validators import is_valid_phone
from app.utils.auth import require_role

provider_auth_bp = Blueprint('provider_auth', __name__)


@provider_auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    required_fields = ['full_name', 'phone_number', 'specialization', 'country', 'region', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    if not is_valid_phone(data['phone_number']):
        return jsonify({'error': 'phone_number must be 7-15 digits, optionally prefixed with +'}), 400

    if HealthcareProvider.query.filter_by(phone_number=data['phone_number']).first():
        return jsonify({'error': 'Phone number already registered'}), 409

    provider = HealthcareProvider(
        provider_id=str(uuid.uuid4())[:8].upper(),
        full_name=data['full_name'],
        phone_number=data['phone_number'],
        specialization=data['specialization'],
        country=data['country'],
        region=data['region'],
    )
    provider.set_password(data['password'])

    db.session.add(provider)
    db.session.commit()

    return jsonify({
        'message': 'Provider registered. Awaiting administrator verification before you can log in.',
        'provider': provider.to_dict(),
    }), 201


@provider_auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if 'phone_number' not in data or 'password' not in data:
        return jsonify({'error': 'Phone number and password are required'}), 400

    provider = HealthcareProvider.query.filter_by(phone_number=data['phone_number']).first()

    if not provider:
        return jsonify({'error': 'Invalid phone number or password'}), 401

    if provider.is_locked():
        return jsonify({'error': 'Account locked due to too many failed attempts. Try again later.'}), 423

    if not provider.check_password(data['password']):
        provider.register_failed_attempt()
        return jsonify({'error': 'Invalid phone number or password'}), 401

    provider.reset_failed_attempts()

    if not provider.is_verified:
        return jsonify({'error': 'Your account has not yet been verified by an administrator'}), 403

    access_token = create_access_token(identity=provider.provider_id, additional_claims={'role': 'provider'})

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'provider': provider.to_dict(),
    }), 200


@provider_auth_bp.route('/me', methods=['GET'])
@require_role('provider')
def get_me():
    provider = HealthcareProvider.query.filter_by(provider_id=get_jwt_identity()).first()
    if not provider:
        return jsonify({'error': 'Provider not found'}), 404
    return jsonify({'provider': provider.to_dict()}), 200
