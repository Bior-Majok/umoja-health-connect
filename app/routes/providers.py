from flask import Blueprint, request, jsonify
from app import db
from app.models.provider import HealthcareProvider
from app.utils.auth import require_role

providers_bp = Blueprint('providers', __name__)


@providers_bp.route('', methods=['GET'])
def list_providers():
    """Public listing (used for appointment booking) — verified providers only by default."""
    query = HealthcareProvider.query
    if request.args.get('all') != '1':
        query = query.filter_by(is_verified=True)
    if request.args.get('country'):
        query = query.filter_by(country=request.args['country'])
    if request.args.get('region'):
        query = query.filter_by(region=request.args['region'])
    providers = query.order_by(HealthcareProvider.full_name).all()
    return jsonify({'providers': [p.to_dict() for p in providers]}), 200


@providers_bp.route('/<provider_id>/verify', methods=['PATCH'])
@require_role('admin')
def verify_provider(provider_id):
    provider = HealthcareProvider.query.filter_by(provider_id=provider_id).first()
    if not provider:
        return jsonify({'error': 'Provider not found'}), 404
    provider.is_verified = True
    db.session.commit()
    return jsonify({'provider': provider.to_dict()}), 200


@providers_bp.route('/<provider_id>/suspend', methods=['PATCH'])
@require_role('admin')
def suspend_provider(provider_id):
    provider = HealthcareProvider.query.filter_by(provider_id=provider_id).first()
    if not provider:
        return jsonify({'error': 'Provider not found'}), 404
    provider.is_verified = False
    provider.is_available = False
    db.session.commit()
    return jsonify({'provider': provider.to_dict()}), 200
