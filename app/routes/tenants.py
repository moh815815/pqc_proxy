"""
مسارات إدارة المستأجرين - Tenant Management Routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Tenant

tenants_bp = Blueprint("tenants", __name__)


@tenants_bp.route("/", methods=["GET"])
@jwt_required()
def قائمة_المستأجرين():
    """جلب قائمة جميع المستأجرين"""
    صفحة   = request.args.get("صفحة", 1, type=int)
    عدد    = request.args.get("عدد", 20, type=int)
    نتائج  = Tenant.query.paginate(page=صفحة, per_page=عدد, error_out=False)
    return jsonify({
        "المستأجرون": [م.to_dict() for م in نتائج.items],
        "الإجمالي": نتائج.total,
        "الصفحة_الحالية": صفحة,
        "إجمالي_الصفحات": نتائج.pages,
    })


@tenants_bp.route("/", methods=["POST"])
@jwt_required()
def إنشاء_مستأجر():
    """إنشاء مستأجر جديد"""
    بيانات = request.get_json()
    required = ["اسم_المستأجر", "النطاق_الرئيسي"]
    if not all(ح in بيانات for ح in required):
        return jsonify({"خطأ": "حقول مطلوبة ناقصة"}), 400

    if Tenant.query.filter_by(النطاق_الرئيسي=بيانات["النطاق_الرئيسي"]).first():
        return jsonify({"خطأ": "النطاق مسجّل مسبقاً"}), 409

    مستأجر = Tenant(
        اسم_المستأجر=بيانات["اسم_المستأجر"],
        النطاق_الرئيسي=بيانات["النطاق_الرئيسي"],
        خطة_الاشتراك=بيانات.get("خطة_الاشتراك", "أساسي"),
        مستوى_أمان_NIST=بيانات.get("مستوى_أمان_NIST", 3),
    )
    db.session.add(مستأجر)
    db.session.commit()
    return jsonify({"رسالة": "تم إنشاء المستأجر بنجاح", "المستأجر": مستأجر.to_dict()}), 201


@tenants_bp.route("/<معرف>", methods=["GET"])
@jwt_required()
def جلب_مستأجر(معرف):
    مستأجر = Tenant.query.get_or_404(معرف)
    return jsonify(مستأجر.to_dict())


@tenants_bp.route("/<معرف>", methods=["PUT"])
@jwt_required()
def تحديث_مستأجر(معرف):
    مستأجر = Tenant.query.get_or_404(معرف)
    بيانات = request.get_json()
    for حقل in ["اسم_المستأجر", "خطة_الاشتراك", "مستوى_أمان_NIST", "حالة_الحساب"]:
        if حقل in بيانات:
            setattr(مستأجر, حقل, بيانات[حقل])
    db.session.commit()
    return jsonify({"رسالة": "تم التحديث", "المستأجر": مستأجر.to_dict()})
