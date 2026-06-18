"""
مسارات سجل الامتثال - Compliance Ledger Routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime, timezone
from app.models import ComplianceLedger
from app.services.compliance_service import ComplianceService

compliance_bp = Blueprint("compliance", __name__)
خدمة = ComplianceService()


@compliance_bp.route("/سجل", methods=["GET"])
@jwt_required()
def سجل_الامتثال():
    """جلب سجل أحداث الامتثال"""
    معرف_مستأجر = request.args.get("معرف_المستأجر")
    خطورة        = request.args.get("خطورة")
    نوع          = request.args.get("نوع_الحدث")
    صفحة         = request.args.get("صفحة", 1, type=int)
    عدد          = request.args.get("عدد", 50, type=int)

    query = ComplianceLedger.query
    if معرف_مستأجر: query = query.filter_by(معرف_المستأجر=معرف_مستأجر)
    if خطورة:        query = query.filter_by(خطورة_الحدث=خطورة)
    if نوع:          query = query.filter_by(نوع_الحدث=نوع)

    نتائج = query.order_by(ComplianceLedger.طابع_زمني.desc()).paginate(
        page=صفحة, per_page=عدد, error_out=False
    )
    return jsonify({
        "السجلات": [س.to_dict() for س in نتائج.items],
        "الإجمالي": نتائج.total,
        "الصفحة": صفحة,
        "إجمالي_الصفحات": نتائج.pages,
    })


@compliance_bp.route("/تقرير/<معرف_المستأجر>", methods=["GET"])
@jwt_required()
def تقرير_الامتثال(معرف_المستأجر):
    """توليد تقرير امتثال شامل بالمصطلحات التقنية العربية"""
    من_تاريخ_str  = request.args.get("من_تاريخ")
    إلى_تاريخ_str = request.args.get("إلى_تاريخ")

    من_تاريخ  = datetime.fromisoformat(من_تاريخ_str).replace(tzinfo=timezone.utc)  if من_تاريخ_str  else None
    إلى_تاريخ = datetime.fromisoformat(إلى_تاريخ_str).replace(tzinfo=timezone.utc) if إلى_تاريخ_str else None

    تقرير = خدمة.توليد_تقرير_الامتثال(معرف_المستأجر, من_تاريخ, إلى_تاريخ)
    return jsonify(تقرير)


@compliance_bp.route("/إحصاءات/<معرف_المستأجر>", methods=["GET"])
@jwt_required()
def إحصاءات_الامتثال(معرف_المستأجر):
    """ملخص إحصائي سريع للامتثال"""
    from sqlalchemy import func
    from app import db

    إجمالي    = ComplianceLedger.query.filter_by(معرف_المستأجر=معرف_المستأجر).count()
    معلومات   = ComplianceLedger.query.filter_by(معرف_المستأجر=معرف_المستأجر, خطورة_الحدث="معلومات").count()
    تحذيرات   = ComplianceLedger.query.filter_by(معرف_المستأجر=معرف_المستأجر, خطورة_الحدث="تحذير").count()
    حرجة      = ComplianceLedger.query.filter_by(معرف_المستأجر=معرف_المستأجر, خطورة_الحدث="حرج").count()

    # توزيع حسب نوع الحدث
    توزيع = db.session.query(
        ComplianceLedger.نوع_الحدث,
        func.count(ComplianceLedger.معرف).label("عدد")
    ).filter_by(معرف_المستأجر=معرف_المستأجر).group_by(ComplianceLedger.نوع_الحدث).all()

    return jsonify({
        "إجمالي_الأحداث": إجمالي,
        "توزيع_الخطورة": {
            "معلومات": معلومات,
            "تحذير":   تحذيرات,
            "حرج":     حرجة,
        },
        "توزيع_أنواع_الأحداث": {نوع: عدد for نوع, عدد in توزيع},
    })
