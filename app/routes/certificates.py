"""
مسارات إدارة الشهادات الرقمية - Certificate Management Routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import Certificate
from app.services.certificate_service import CertificateService

certificates_bp = Blueprint("certificates", __name__)


@certificates_bp.route("/", methods=["GET"])
@jwt_required()
def قائمة_الشهادات():
    """جلب شهادات مستأجر معين"""
    معرف_مستأجر = request.args.get("معرف_المستأجر")
    حالة         = request.args.get("حالة")
    query = Certificate.query
    if معرف_مستأجر:
        query = query.filter_by(معرف_المستأجر=معرف_مستأجر)
    if حالة:
        query = query.filter_by(الحالة=حالة)
    شهادات = query.order_by(Certificate.تاريخ_الإصدار.desc()).limit(100).all()
    return jsonify({"الشهادات": [ش.to_dict() for ش in شهادات], "العدد": len(شهادات)})


@certificates_bp.route("/إصدار", methods=["POST"])
@jwt_required()
def إصدار_شهادة():
    """إصدار شهادة رقمية جديدة مقاومة للكم"""
    بيانات = request.get_json()
    required = ["معرف_المستأجر", "معرف_الخوارزمية", "الاسم_الشائع"]
    if not all(ح in بيانات for ح in required):
        return jsonify({"خطأ": "حقول مطلوبة ناقصة", "الحقول": required}), 400

    نتيجة = CertificateService.إصدار_شهادة(
        معرف_المستأجر=بيانات["معرف_المستأجر"],
        معرف_الخوارزمية=بيانات["معرف_الخوارزمية"],
        الاسم_الشائع=بيانات["الاسم_الشائع"],
        المنظمة=بيانات.get("المنظمة"),
        الدولة=بيانات.get("الدولة", "SA"),
        أيام_الصلاحية=بيانات.get("أيام_الصلاحية", 365),
        شهادة_جذر=بيانات.get("شهادة_جذر", False),
    )
    return jsonify(نتيجة), 201 if نتيجة.get("نجح") else 400


@certificates_bp.route("/<معرف_الشهادة>/ترحيل", methods=["POST"])
@jwt_required()
def ترحيل_شهادة(معرف_الشهادة):
    """ترحيل شهادة إلى خوارزمية جديدة"""
    بيانات = request.get_json()
    if "معرف_الخوارزمية_الجديدة" not in بيانات:
        return jsonify({"خطأ": "معرف الخوارزمية الجديدة مطلوب"}), 400

    نتيجة = CertificateService.ترحيل_شهادة(
        معرف_الشهادة=معرف_الشهادة,
        معرف_الخوارزمية_الجديدة=بيانات["معرف_الخوارزمية_الجديدة"],
        سبب=بيانات.get("سبب", "ترقية أمنية"),
    )
    return jsonify(نتيجة), 200 if نتيجة.get("نجح") else 400


@certificates_bp.route("/<معرف_الشهادة>/إلغاء", methods=["POST"])
@jwt_required()
def إلغاء_شهادة(معرف_الشهادة):
    بيانات = request.get_json() or {}
    نتيجة = CertificateService.إلغاء_شهادة(
        معرف_الشهادة=معرف_الشهادة,
        سبب=بيانات.get("سبب", "إلغاء يدوي"),
    )
    return jsonify(نتيجة), 200 if نتيجة.get("نجح") else 400


@certificates_bp.route("/قرب-الانتهاء", methods=["GET"])
@jwt_required()
def الشهادات_قرب_الانتهاء():
    """قائمة الشهادات التي ستنتهي قريباً"""
    معرف_مستأجر = request.args.get("معرف_المستأجر", "")
    أيام         = request.args.get("أيام", 30, type=int)
    شهادات = CertificateService.الشهادات_قرب_الانتهاء(معرف_مستأجر, أيام)
    return jsonify({"شهادات_قرب_الانتهاء": شهادات, "العدد": len(شهادات)})
