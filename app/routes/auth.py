"""
مسارات المصادقة - Authentication Routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from app import db
from app.models import User, Tenant

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/تسجيل-دخول", methods=["POST"])
def تسجيل_دخول():
    """تسجيل دخول المستخدم وإصدار رمز JWT"""
    بيانات = request.get_json()
    if not بيانات:
        return jsonify({"خطأ": "البيانات مفقودة"}), 400

    مستخدم = User.query.filter_by(
        البريد_الإلكتروني=بيانات.get("البريد_الإلكتروني")
    ).first()

    if not مستخدم or not check_password_hash(
        مستخدم.كلمة_المرور_مشفرة, بيانات.get("كلمة_المرور", "")
    ):
        return jsonify({"خطأ": "بيانات الدخول غير صحيحة"}), 401

    if not مستخدم.نشط:
        return jsonify({"خطأ": "الحساب معطّل"}), 403

    مستخدم.آخر_دخول = datetime.now(timezone.utc)
    db.session.commit()

    هوية = {"معرف": مستخدم.معرف, "دور": مستخدم.الدور, "مستأجر": مستخدم.معرف_المستأجر}

    return jsonify({
        "رسالة": "تم تسجيل الدخول بنجاح",
        "رمز_الوصول":  create_access_token(identity=str(هوية)),
        "رمز_التجديد": create_refresh_token(identity=str(هوية)),
        "المستخدم": مستخدم.to_dict(),
    }), 200


@auth_bp.route("/تسجيل", methods=["POST"])
def تسجيل():
    """تسجيل مستخدم جديد"""
    بيانات = request.get_json()
    required = ["البريد_الإلكتروني", "كلمة_المرور", "الاسم_الكامل", "معرف_المستأجر"]
    if not all(ح in بيانات for ح in required):
        return jsonify({"خطأ": "حقول مطلوبة ناقصة", "الحقول_المطلوبة": required}), 400

    if User.query.filter_by(البريد_الإلكتروني=بيانات["البريد_الإلكتروني"]).first():
        return jsonify({"خطأ": "البريد الإلكتروني مسجّل مسبقاً"}), 409

    مستخدم = User(
        معرف_المستأجر=بيانات["معرف_المستأجر"],
        البريد_الإلكتروني=بيانات["البريد_الإلكتروني"],
        كلمة_المرور_مشفرة=generate_password_hash(بيانات["كلمة_المرور"]),
        الاسم_الكامل=بيانات["الاسم_الكامل"],
        الدور=بيانات.get("الدور", "مشغل"),
    )
    db.session.add(مستخدم)
    db.session.commit()

    return jsonify({"رسالة": "تم إنشاء الحساب بنجاح", "المستخدم": مستخدم.to_dict()}), 201
