from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity
from app.models.admin import Administrator
from app.utils.auth import require_role

admin_auth_bp = Blueprint('admin_auth', __name__)

# No public self-registration route: per the SRS business rules, administrators are
# provisioned out-of-band (see the `flask seed-admin` CLI command in app/cli.py).


@admin_auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if 'phone_number' not in data or 'password' not in data:
        return jsonify({'error': 'Phone number and password are required'}), 400

    admin = Administrator.query.filter_by(phone_number=data['phone_number']).first()

    if not admin:
        return jsonify({'error': 'Invalid phone number or password'}), 401

    if admin.is_locked():
        return jsonify({'error': 'Account locked due to too many failed attempts. Try again later.'}), 423

    if not admin.check_password(data['password']):
        admin.register_failed_attempt()
        return jsonify({'error': 'Invalid phone number or password'}), 401

    admin.reset_failed_attempts()

    access_token = create_access_token(identity=admin.admin_id, additional_claims={'role': 'admin'})

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'admin': admin.to_dict(),
    }), 200


@admin_auth_bp.route('/me', methods=['GET'])
@require_role('admin')
def get_me():
    admin = Administrator.query.filter_by(admin_id=get_jwt_identity()).first()
    if not admin:
        return jsonify({'error': 'Administrator not found'}), 404
    return jsonify({'admin': admin.to_dict()}), 200
