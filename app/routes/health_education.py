from flask import Blueprint, request, jsonify
from app import db
from app.models.health_article import HealthEducationArticle
from app.utils.auth import require_role

health_education_bp = Blueprint('health_education', __name__)


@health_education_bp.route('', methods=['GET'])
def list_articles():
    query = HealthEducationArticle.query
    if request.args.get('lang'):
        query = query.filter_by(language=request.args['lang'])
    if request.args.get('category'):
        query = query.filter_by(category=request.args['category'])
    articles = query.order_by(HealthEducationArticle.title).all()
    return jsonify({'articles': [a.to_dict() for a in articles]}), 200


@health_education_bp.route('', methods=['POST'])
@require_role('admin')
def create_article():
    data = request.get_json()
    required_fields = ['title', 'body', 'category']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    article = HealthEducationArticle(
        title=data['title'],
        body=data['body'],
        category=data['category'],
        language=data.get('language', 'en'),
        is_verified=bool(data.get('is_verified', False)),
    )
    db.session.add(article)
    db.session.commit()
    return jsonify({'article': article.to_dict()}), 201


@health_education_bp.route('/<int:article_id>', methods=['PATCH'])
@require_role('admin')
def update_article(article_id):
    article = HealthEducationArticle.query.get(article_id)
    if not article:
        return jsonify({'error': 'Article not found'}), 404

    data = request.get_json()
    for field in ('title', 'body', 'category', 'language', 'is_verified'):
        if field in data:
            setattr(article, field, data[field])
    db.session.commit()
    return jsonify({'article': article.to_dict()}), 200
