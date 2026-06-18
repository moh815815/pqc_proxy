"""
مسارات إدارة الخوارزميات - PQC Algorithm Routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import PQCAlgorithm

algorithms_bp = Blueprint("algorithms", __name__)


@algorithms_bp.route("/", methods=["GET"])
def قائمة_الخوارزميات():
    """قائمة خوارزميات التشفير ما بعد الكمومي المدعومة"""
    نوع     = request.args.get("نوع")
    مفعّلة  = request.args.get("مفعّلة", "true").lower() == "true"

    query = PQCAlgorithm.query
    if نوع:    query = query.filter_by(نوع_الخوارزمية=نوع)
    if مفعّلة: query = query.filter_by(مفعّل=True)

    خوارزميات = query.order_by(PQCAlgorithm.مستوى_NIST).all()
    return jsonify({
        "الخوارزميات": [خ.to_dict() for خ in خوارزميات],
        "العدد": len(خوارزميات),
    })


@algorithms_bp.route("/<معرف>", methods=["GET"])
def جلب_خوارزمية(معرف):
    خوارزمية = PQCAlgorithm.query.get_or_404(معرف)
    return jsonify(خوارزمية.to_dict())


@algorithms_bp.route("/", methods=["POST"])
@jwt_required()
def إضافة_خوارزمية():
    """إضافة خوارزمية PQC جديدة للسجل"""
    بيانات = request.get_json()
    required = ["اسم_الخوارزمية", "نوع_الخوارزمية", "مستوى_NIST"]
    if not all(ح in بيانات for ح in required):
        return jsonify({"خطأ": "حقول مطلوبة ناقصة", "الحقول": required}), 400

    if PQCAlgorithm.query.filter_by(اسم_الخوارزمية=بيانات["اسم_الخوارزمية"]).first():
        return jsonify({"خطأ": "الخوارزمية مسجّلة مسبقاً"}), 409

    from config.settings import ConfigBase
    وصف_المستوى = ConfigBase.NIST_SECURITY_LEVELS.get(بيانات["مستوى_NIST"], "")

    خوارزمية = PQCAlgorithm(
        اسم_الخوارزمية=بيانات["اسم_الخوارزمية"],
        نوع_الخوارزمية=بيانات["نوع_الخوارزمية"],
        مستوى_NIST=بيانات["مستوى_NIST"],
        وصف_مستوى_NIST=وصف_المستوى,
        دورة_NIST=بيانات.get("دورة_NIST", "final"),
        حجم_المفتاح_عام=بيانات.get("حجم_المفتاح_عام"),
        حجم_التوقيع=بيانات.get("حجم_التوقيع"),
        ملاحظات_أمنية=بيانات.get("ملاحظات_أمنية"),
    )
    db.session.add(خوارزمية)
    db.session.commit()
    return jsonify({"رسالة": "تمت الإضافة بنجاح", "الخوارزمية": خوارزمية.to_dict()}), 201


@algorithms_bp.route("/<معرف>/تفعيل", methods=["PATCH"])
@jwt_required()
def تفعيل_خوارزمية(معرف):
    خوارزمية = PQCAlgorithm.query.get_or_404(معرف)
    خوارزمية.مفعّل = True
    db.session.commit()
    return jsonify({"رسالة": f"تم تفعيل {خوارزمية.اسم_الخوارزمية}"})


@algorithms_bp.route("/<معرف>/تعطيل", methods=["PATCH"])
@jwt_required()
def تعطيل_خوارزمية(معرف):
    خوارزمية = PQCAlgorithm.query.get_or_404(معرف)
    خوارزمية.مفعّل = False
    db.session.commit()
    return jsonify({"رسالة": f"تم تعطيل {خوارزمية.اسم_الخوارزمية}"})
