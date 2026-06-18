"""
مسارات المصافحة الكمومية - Quantum Handshake Routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import HandshakeSession
from app.services.handshake_service import HandshakeService

handshake_bp = Blueprint("handshake", __name__)


@handshake_bp.route("/بدء", methods=["POST"])
@jwt_required()
def بدء_مصافحة():
    """بدء جلسة مصافحة كمومية جديدة"""
    بيانات = request.get_json()
    required = ["معرف_المستأجر", "معرف_الخوارزمية"]
    if not all(ح in بيانات for ح in required):
        return jsonify({"خطأ": "حقول مطلوبة ناقصة"}), 400

    نتيجة = HandshakeService.بدء_جلسة(
        معرف_المستأجر=بيانات["معرف_المستأجر"],
        معرف_الخوارزمية=بيانات["معرف_الخوارزمية"],
        عنوان_IP=request.remote_addr,
        منفذ=بيانات.get("المنفذ", 443),
    )
    return jsonify(نتيجة), 201 if نتيجة.get("نجح") else 400


@handshake_bp.route("/<معرف_الجلسة>/انتقال", methods=["POST"])
@jwt_required()
def انتقال_حالة(معرف_الجلسة):
    """تقدم آلة الحالة إلى الحالة التالية"""
    بيانات = request.get_json()
    if "الحالة_الجديدة" not in بيانات:
        return jsonify({"خطأ": "الحالة الجديدة مطلوبة"}), 400

    نتيجة = HandshakeService.تقدم_الجلسة(
        معرف_الجلسة=معرف_الجلسة,
        الحالة_الجديدة=بيانات["الحالة_الجديدة"],
        بيانات=بيانات.get("بيانات_إضافية"),
    )
    return jsonify(نتيجة), 200 if نتيجة.get("نجح") else 400


@handshake_bp.route("/مصافحة-كاملة", methods=["POST"])
@jwt_required()
def مصافحة_كاملة():
    """تنفيذ دورة مصافحة كمومية كاملة تلقائياً"""
    بيانات = request.get_json()
    required = ["معرف_المستأجر", "معرف_الخوارزمية"]
    if not all(ح in بيانات for ح in required):
        return jsonify({"خطأ": "حقول مطلوبة ناقصة"}), 400

    نتيجة = HandshakeService.تنفيذ_مصافحة_كاملة(
        معرف_المستأجر=بيانات["معرف_المستأجر"],
        معرف_الخوارزمية=بيانات["معرف_الخوارزمية"],
        معرف_الشهادة=بيانات.get("معرف_الشهادة"),
        عنوان_IP=request.remote_addr,
    )
    return jsonify(نتيجة), 200 if نتيجة.get("نجح") else 400


@handshake_bp.route("/<معرف_الجلسة>", methods=["GET"])
@jwt_required()
def جلب_جلسة(معرف_الجلسة):
    جلسة = HandshakeSession.query.get_or_404(معرف_الجلسة)
    return jsonify(جلسة.to_dict())


@handshake_bp.route("/إحصاءات/<معرف_المستأجر>", methods=["GET"])
@jwt_required()
def إحصاءات(معرف_المستأجر):
    return jsonify(HandshakeService.إحصاءات_المصافحة(معرف_المستأجر))
