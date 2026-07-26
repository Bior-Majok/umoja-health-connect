import re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.patient import Patient
import uuid

auth_bp = Blueprint('auth', __name__)

PHONE_RE = re.compile(r'^\+?[0-9]{7,15}$')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    required_fields = ['full_name', 'phone_number', 'age', 'gender', 'country', 'region', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    if not PHONE_RE.match(str(data['phone_number'])):
        return jsonify({'error': 'phone_number must be 7-15 digits, optionally prefixed with +'}), 400

    try:
        age = int(data['age'])
        if age <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({'error': 'age must be a positive integer'}), 400
    data['age'] = age

    if Patient.query.filter_by(phone_number=data['phone_number']).first():
        return jsonify({'error': 'Phone number already registered'}), 409

    patient = Patient(
        patient_id=str(uuid.uuid4())[:8].upper(),
        full_name=data['full_name'],
        phone_number=data['phone_number'],
        age=data['age'],
        gender=data['gender'],
        country=data['country'],
        region=data['region'],
        family_contact_phone=data.get('family_contact_phone'),
    )
    patient.set_password(data['password'])

    db.session.add(patient)
    db.session.commit()

    return jsonify({'message': 'Patient registered successfully', 'patient': patient.to_dict()}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if 'phone_number' not in data or 'password' not in data:
        return jsonify({'error': 'Phone number and password are required'}), 400

    patient = Patient.query.filter_by(phone_number=data['phone_number']).first()

    if not patient:
        return jsonify({'error': 'Invalid phone number or password'}), 401

    if patient.is_locked():
        return jsonify({'error': 'Account locked due to too many failed attempts. Try again later.'}), 423

    if not patient.check_password(data['password']):
        patient.register_failed_attempt()
        return jsonify({'error': 'Invalid phone number or password'}), 401

    patient.reset_failed_attempts()

    access_token = create_access_token(identity=patient.patient_id, additional_claims={'role': 'patient'})

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'patient': patient.to_dict()
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    patient = Patient.query.filter_by(patient_id=get_jwt_identity()).first()
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    return jsonify({'patient': patient.to_dict()}), 200


@auth_bp.route('/me', methods=['PATCH'])
@jwt_required()
def update_me():
    patient = Patient.query.filter_by(patient_id=get_jwt_identity()).first()
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    data = request.get_json()
    editable_fields = ['full_name', 'age', 'gender', 'country', 'region', 'family_contact_phone']
    for field in editable_fields:
        if field in data:
            setattr(patient, field, data[field])

    if 'phone_number' in data and data['phone_number'] != patient.phone_number:
        existing = Patient.query.filter_by(phone_number=data['phone_number']).first()
        if existing:
            return jsonify({'error': 'Phone number already registered'}), 409
        patient.phone_number = data['phone_number']

    db.session.commit()

    return jsonify({'message': 'Profile updated successfully', 'patient': patient.to_dict()}), 200
