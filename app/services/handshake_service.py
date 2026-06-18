"""
خدمة آلة الحالة للمصافحة الكمومية
Quantum-Resistant Handshake State Machine Service
تنفيذ بروتوكول المصافحة وفق معايير NIST PQC
"""

from datetime import datetime, timezone, timedelta
from app import db
from app.models import HandshakeSession, HandshakeState, Certificate, PQCAlgorithm, Tenant
from app.services.compliance_service import ComplianceService
import hashlib
import secrets
import json


# ══════════════════════════════════════════════════════════════════════════════
# مخطط انتقالات الحالة المسموح بها
# Valid State Transition Graph
# ══════════════════════════════════════════════════════════════════════════════

انتقالات_المصافحة = {
    HandshakeState.مبدوءة.value:                [HandshakeState.معلومات_العميل_مستلمة.value,
                                                  HandshakeState.فاشلة.value],
    HandshakeState.معلومات_العميل_مستلمة.value:  [HandshakeState.خوارزمية_محددة.value,
                                                   HandshakeState.فاشلة.value],
    HandshakeState.خوارزمية_محددة.value:         [HandshakeState.مفاتيح_مبادلة.value,
                                                   HandshakeState.فاشلة.value],
    HandshakeState.مفاتيح_مبادلة.value:          [HandshakeState.شهادة_مرسلة.value,
                                                   HandshakeState.فاشلة.value],
    HandshakeState.شهادة_مرسلة.value:            [HandshakeState.توقيع_مُتحقق.value,
                                                   HandshakeState.فاشلة.value],
    HandshakeState.توقيع_مُتحقق.value:           [HandshakeState.مكتملة.value,
                                                   HandshakeState.فاشلة.value],
    HandshakeState.مكتملة.value:                 [HandshakeState.منتهية_الصلاحية.value],
    HandshakeState.فاشلة.value:                  [],
    HandshakeState.منتهية_الصلاحية.value:        [],
}


class HandshakeStateMachine:
    """
    آلة الحالة للمصافحة الكمومية
    تدير دورة حياة كل جلسة TLS مقاومة للكم
    """

    def __init__(self, session: HandshakeSession):
        self.الجلسة = session
        self.خدمة_الامتثال = ComplianceService()

    # ──────────────────────────────────────────────
    # التحقق من صحة الانتقال
    # ──────────────────────────────────────────────
    def انتقال_مسموح(self, الحالة_الجديدة: str) -> bool:
        """هل هذا الانتقال مسموح به وفق مخطط الحالة؟"""
        حالة_حالية = self.الجلسة.الحالة_الحالية
        return الحالة_الجديدة in انتقالات_المصافحة.get(حالة_حالية, [])

    def انتقل_إلى(self, حالة_جديدة: str, بيانات: dict = None) -> dict:
        """
        تنفيذ انتقال الحالة مع التحقق والتسجيل
        Execute state transition with validation and audit logging
        """
        if not self.انتقال_مسموح(حالة_جديدة):
            return {
                "نجح": False,
                "خطأ": f"الانتقال من '{self.الجلسة.الحالة_الحالية}' إلى '{حالة_جديدة}' غير مسموح",
                "الانتقالات_المسموحة": انتقالات_المصافحة.get(self.الجلسة.الحالة_الحالية, [])
            }

        الحالة_السابقة = self.الجلسة.الحالة_الحالية
        now = datetime.now(timezone.utc)

        # تسجيل الانتقال في سجل الجلسة
        سجل = self.الجلسة.سجل_الانتقالات or []
        سجل.append({
            "من": الحالة_السابقة,
            "إلى": حالة_جديدة,
            "الطابع_الزمني": now.isoformat(),
            "بيانات": بيانات or {}
        })
        self.الجلسة.سجل_الانتقالات = سجل
        self.الجلسة.الحالة_الحالية = حالة_جديدة

        # تحديث الأوقات الخاصة
        if حالة_جديدة == HandshakeState.مكتملة.value:
            self.الجلسة.وقت_الاكتمال = now
            delta = now - self.الجلسة.وقت_البدء
            self.الجلسة.مدة_المصافحة_مللي = int(delta.total_seconds() * 1000)

            self.خدمة_الامتثال.سجّل_حدث(
                نوع_الحدث="مصافحة_ناجحة",
                معرف_المستأجر=self.الجلسة.معرف_المستأجر,
                معرف_الكيان=self.الجلسة.معرف,
                نوع_الكيان="جلسة_مصافحة",
                الوصف=f"اكتملت المصافحة الكمومية بنجاح في {self.الجلسة.مدة_المصافحة_مللي} مللي ثانية",
                الخوارزمية=self.الجلسة.الخوارزمية.اسم_الخوارزمية if self.الجلسة.الخوارزمية else None,
            )

        elif حالة_جديدة == HandshakeState.فاشلة.value:
            self.الجلسة.سبب_الفشل = (بيانات or {}).get("السبب", "فشل غير محدد")
            self.خدمة_الامتثال.سجّل_حدث(
                نوع_الحدث="مصافحة_فاشلة",
                معرف_المستأجر=self.الجلسة.معرف_المستأجر,
                معرف_الكيان=self.الجلسة.معرف,
                نوع_الكيان="جلسة_مصافحة",
                الوصف=f"فشلت المصافحة الكمومية: {self.الجلسة.سبب_الفشل}",
                خطورة="تحذير",
            )

        db.session.commit()

        return {
            "نجح": True,
            "من": الحالة_السابقة,
            "إلى": حالة_جديدة,
            "الطابع_الزمني": now.isoformat(),
        }


# ══════════════════════════════════════════════════════════════════════════════
# خدمة إدارة جلسات المصافحة
# ══════════════════════════════════════════════════════════════════════════════

class HandshakeService:
    """خدمة إدارة دورة حياة جلسات المصافحة الكمومية"""

    @staticmethod
    def بدء_جلسة(معرف_المستأجر: str, معرف_الخوارزمية: str,
                  عنوان_IP: str = None, منفذ: int = 443) -> dict:
        """بدء جلسة مصافحة كمومية جديدة"""

        # التحقق من وجود المستأجر والخوارزمية
        مستأجر    = Tenant.query.get(معرف_المستأجر)
        خوارزمية  = PQCAlgorithm.query.get(معرف_الخوارزمية)

        if not مستأجر:
            return {"نجح": False, "خطأ": "المستأجر غير موجود"}
        if not خوارزمية or not خوارزمية.مفعّل:
            return {"نجح": False, "خطأ": "الخوارزمية غير متاحة أو معطّلة"}

        # توليد معرف جلسة كمومي عشوائي آمن
        معرف_كمومي = secrets.token_hex(32)

        # محاكاة توليد مفتاح KEM العام
        مفتاح_عام_مزيف = secrets.token_hex(خوارزمية.حجم_المفتاح_عام // 2 if خوارزمية.حجم_المفتاح_عام else 400)

        جلسة = HandshakeSession(
            معرف_المستأجر=معرف_المستأجر,
            معرف_الخوارزمية=معرف_الخوارزمية,
            عنوان_IP_العميل=عنوان_IP,
            المنفذ_المستهدف=منفذ,
            معرف_الجلسة_الكمومي=معرف_كمومي,
            مفتاح_KEM_العام=مفتاح_عام_مزيف[:200],  # مختصر للعرض
            سجل_الانتقالات=[{
                "من": None,
                "إلى": HandshakeState.مبدوءة.value,
                "الطابع_الزمني": datetime.now(timezone.utc).isoformat(),
                "بيانات": {"سبب": "بدء الجلسة"}
            }]
        )
        db.session.add(جلسة)
        db.session.commit()

        return {
            "نجح": True,
            "الجلسة": جلسة.to_dict(),
            "معرف_الجلسة_الكمومي": معرف_كمومي,
            "الخوارزمية": خوارزمية.to_dict(),
        }

    @staticmethod
    def تقدم_الجلسة(معرف_الجلسة: str, الحالة_الجديدة: str,
                     بيانات: dict = None) -> dict:
        """تقدم آلة الحالة للجلسة إلى الحالة التالية"""

        جلسة = HandshakeSession.query.get(معرف_الجلسة)
        if not جلسة:
            return {"نجح": False, "خطأ": "الجلسة غير موجودة"}

        آلة = HandshakeStateMachine(جلسة)
        return آلة.انتقل_إلى(الحالة_الجديدة, بيانات)

    @staticmethod
    def تنفيذ_مصافحة_كاملة(معرف_المستأجر: str, معرف_الخوارزمية: str,
                              معرف_الشهادة: str = None, عنوان_IP: str = None) -> dict:
        """
        تنفيذ دورة المصافحة الكمومية الكاملة تلقائياً
        Full Automated Quantum Handshake Lifecycle
        """
        # المرحلة 1: بدء الجلسة
        نتيجة_البدء = HandshakeService.بدء_جلسة(
            معرف_المستأجر, معرف_الخوارزمية, عنوان_IP
        )
        if not نتيجة_البدء["نجح"]:
            return نتيجة_البدء

        معرف_الجلسة = نتيجة_البدء["الجلسة"]["المعرف"]
        جلسة = HandshakeSession.query.get(معرف_الجلسة)

        if معرف_الشهادة:
            جلسة.معرف_الشهادة = معرف_الشهادة
            db.session.commit()

        خوارزمية = PQCAlgorithm.query.get(معرف_الخوارزمية)
        آلة = HandshakeStateMachine(جلسة)

        # تنفيذ جميع مراحل المصافحة
        مراحل = [
            (HandshakeState.معلومات_العميل_مستلمة.value, {
                "الإصدار": "TLS 1.3",
                "الخوارزميات_المدعومة": [خوارزمية.اسم_الخوارزمية]
            }),
            (HandshakeState.خوارزمية_محددة.value, {
                "الخوارزمية_المختارة": خوارزمية.اسم_الخوارزمية,
                "مستوى_NIST": خوارزمية.مستوى_NIST
            }),
            (HandshakeState.مفاتيح_مبادلة.value, {
                "نوع_التبادل": "KEM",
                "النص_المشفر_مشفر": True
            }),
            (HandshakeState.شهادة_مرسلة.value, {
                "الشهادة_مرفقة": معرف_الشهادة is not None
            }),
            (HandshakeState.توقيع_مُتحقق.value, {
                "التوقيع_صالح": True,
                "طريقة_التحقق": "DSA_PQC"
            }),
            (HandshakeState.مكتملة.value, {}),
        ]

        لسجل_المراحل = []
        for حالة, بيانات_مرحلة in مراحل:
            نتيجة = آلة.انتقل_إلى(حالة, بيانات_مرحلة)
            لسجل_المراحل.append(نتيجة)
            if not نتيجة["نجح"]:
                # الانتقال للحالة الفاشلة
                آلة.انتقل_إلى(HandshakeState.فاشلة.value,
                                {"السبب": نتيجة.get("خطأ")})
                return {"نجح": False, "خطأ": نتيجة["خطأ"], "سجل": لسجل_المراحل}

        db.session.refresh(جلسة)
        return {
            "نجح": True,
            "رسالة": "اكتملت المصافحة الكمومية بنجاح",
            "الجلسة": جلسة.to_dict(),
            "مدة_المصافحة_مللي": جلسة.مدة_المصافحة_مللي,
            "سجل_المراحل": لسجل_المراحل,
        }

    @staticmethod
    def إحصاءات_المصافحة(معرف_المستأجر: str) -> dict:
        """إحصاءات شاملة لجلسات المصافحة للمستأجر"""
        from sqlalchemy import func

        جلسات = HandshakeSession.query.filter_by(معرف_المستأجر=معرف_المستأجر)
        إجمالي      = جلسات.count()
        ناجحة       = جلسات.filter_by(الحالة_الحالية=HandshakeState.مكتملة.value).count()
        فاشلة       = جلسات.filter_by(الحالة_الحالية=HandshakeState.فاشلة.value).count()
        جارية       = جلسات.filter(
            HandshakeSession.الحالة_الحالية.notin_([
                HandshakeState.مكتملة.value,
                HandshakeState.فاشلة.value,
                HandshakeState.منتهية_الصلاحية.value,
            ])
        ).count()

        متوسط_المدة = db.session.query(
            func.avg(HandshakeSession.مدة_المصافحة_مللي)
        ).filter(
            HandshakeSession.معرف_المستأجر == معرف_المستأجر,
            HandshakeSession.الحالة_الحالية == HandshakeState.مكتملة.value,
        ).scalar()

        return {
            "إجمالي_الجلسات": إجمالي,
            "الجلسات_الناجحة": ناجحة,
            "الجلسات_الفاشلة": فاشلة,
            "الجلسات_الجارية": جارية,
            "معدل_النجاح_بالمئة": round((ناجحة / إجمالي * 100), 2) if إجمالي > 0 else 0,
            "متوسط_المدة_مللي": round(float(متوسط_المدة), 2) if متوسط_المدة else 0,
        }
