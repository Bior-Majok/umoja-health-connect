from flask import Blueprint, request, jsonify
from app.labels import labels_for, LANGUAGES

labels_bp = Blueprint('labels', __name__)


@labels_bp.route('', methods=['GET'])
def get_labels():
    lang = request.args.get('lang', 'en')
    return jsonify(labels_for(lang)), 200


@labels_bp.route('/languages', methods=['GET'])
def get_languages():
    return jsonify({'languages': LANGUAGES}), 200
