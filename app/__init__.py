"""
نظام التحكم في الوكيل الكمي المقاوم للحساب الكمومي
Post-Quantum Cryptography Web Proxy Controller
المطور: نظام مفتوح المصدر - Arabic PQC Controller
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config.settings import ConfigBase

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_class=ConfigBase):
    """مصنع تطبيق فلاسك - Flask Application Factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # تهيئة الإضافات
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # تسجيل المسارات
    from app.routes.auth import auth_bp
    from app.routes.tenants import tenants_bp
    from app.routes.certificates import certificates_bp
    from app.routes.handshake import handshake_bp
    from app.routes.compliance import compliance_bp
    from app.routes.algorithms import algorithms_bp

    app.register_blueprint(auth_bp,          url_prefix="/api/v1/auth")
    app.register_blueprint(tenants_bp,       url_prefix="/api/v1/tenants")
    app.register_blueprint(certificates_bp,  url_prefix="/api/v1/certificates")
    app.register_blueprint(handshake_bp,     url_prefix="/api/v1/handshake")
    app.register_blueprint(compliance_bp,    url_prefix="/api/v1/compliance")
    app.register_blueprint(algorithms_bp,    url_prefix="/api/v1/algorithms")

    return app
