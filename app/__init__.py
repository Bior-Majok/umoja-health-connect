from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_overrides=None):
    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)

    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    from app.routes.auth import auth_bp
    from app.routes.provider_auth import provider_auth_bp
    from app.routes.volunteer_auth import volunteer_auth_bp
    from app.routes.admin_auth import admin_auth_bp
    from app.routes.providers import providers_bp
    from app.routes.appointments import appointments_bp
    from app.routes.records import records_bp
    from app.routes.consultations import consultations_bp
    from app.routes.emergency_alerts import emergency_alerts_bp
    from app.routes.health_education import health_education_bp
    from app.routes.admin_reports import admin_reports_bp
    from app.routes.labels import labels_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(provider_auth_bp, url_prefix='/api/auth/provider')
    app.register_blueprint(volunteer_auth_bp, url_prefix='/api/auth/volunteer')
    app.register_blueprint(admin_auth_bp, url_prefix='/api/auth/admin')
    app.register_blueprint(providers_bp, url_prefix='/api/providers')
    app.register_blueprint(appointments_bp, url_prefix='/api/appointments')
    app.register_blueprint(records_bp, url_prefix='/api/records')
    app.register_blueprint(consultations_bp, url_prefix='/api/consultations')
    app.register_blueprint(emergency_alerts_bp, url_prefix='/api/emergency-alerts')
    app.register_blueprint(health_education_bp, url_prefix='/api/health-education')
    app.register_blueprint(admin_reports_bp, url_prefix='/api/admin/reports')
    app.register_blueprint(labels_bp, url_prefix='/api/labels')

    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    from app.cli import register_cli
    register_cli(app)

    with app.app_context():
        db.create_all()

    return app
