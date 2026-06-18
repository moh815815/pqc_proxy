"""
نقطة دخول التطبيق - Application Entry Point
نظام وكيل التشفير ما بعد الكمومي | PQC Proxy Controller
"""

from app import create_app, db
from app.models import (
    Tenant, User, PQCAlgorithm, Certificate,
    HandshakeSession, ComplianceLedger, MigrationPolicy
)

app = create_app()


@app.shell_context_processor
def make_shell_context():
    """سياق الـ Shell للتطوير والاختبار"""
    return {
        "db": db,
        "Tenant": Tenant,
        "User": User,
        "PQCAlgorithm": PQCAlgorithm,
        "Certificate": Certificate,
        "HandshakeSession": HandshakeSession,
        "ComplianceLedger": ComplianceLedger,
        "MigrationPolicy": MigrationPolicy,
    }


@app.route("/")
def الصفحة_الرئيسية():
    from flask import jsonify
    return jsonify({
        "النظام": "وكيل التشفير ما بعد الكمومي",
        "الإصدار": "1.0.0",
        "الحالة": "يعمل",
        "المعايير_المدعومة": ["FIPS 203 (ML-KEM)", "FIPS 204 (ML-DSA)", "FIPS 205 (SLH-DSA)"],
        "توثيق_API": "/api/v1/",
    })


@app.route("/صحة")
def فحص_الصحة():
    from flask import jsonify
    try:
        db.session.execute(db.text("SELECT 1"))
        return jsonify({"الحالة": "سليم", "قاعدة_البيانات": "متصلة"})
    except Exception as خطأ:
        return jsonify({"الحالة": "خطأ", "التفاصيل": str(خطأ)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
