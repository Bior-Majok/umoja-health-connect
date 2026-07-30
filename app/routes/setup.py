"""One-time admin provisioning over HTTP, for hosts where a shell isn't available
(e.g. Render's free tier). Mirrors `flask seed-admin` (see app/cli.py) but reachable
without shell access. Locked behind SETUP_SECRET — if that env var isn't set, this
endpoint always refuses, so it's inert on any deployment that hasn't opted in.
"""

import uuid
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.admin import Administrator

setup_bp = Blueprint('setup', __name__)


@setup_bp.route('/seed-admin', methods=['POST'])
def seed_admin():
    secret = current_app.config.get('SETUP_SECRET')
    if not secret or request.headers.get('X-Setup-Secret') != secret:
        return jsonify({'error': 'unauthorized'}), 403

    data = request.get_json() or {}
    full_name = data.get('full_name')
    phone_number = data.get('phone_number')
    password = data.get('password')
    if not full_name or not phone_number or not password:
        return jsonify({'error': 'full_name, phone_number, and password are required'}), 400

    if Administrator.query.filter_by(phone_number=phone_number).first():
        return jsonify({'error': 'An administrator with that phone number already exists'}), 409

    admin = Administrator(
        admin_id=str(uuid.uuid4())[:8].upper(),
        full_name=full_name,
        phone_number=phone_number,
        scope_level=data.get('scope_level', 'national'),
        region=data.get('region'),
    )
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()

    return jsonify({'admin_id': admin.admin_id}), 201
