from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt


def require_role(*roles):
    """Combines @jwt_required() with a check that the token's 'role' claim is allowed."""

    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get('role') not in roles:
                return jsonify({'error': 'Forbidden for this role'}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator
