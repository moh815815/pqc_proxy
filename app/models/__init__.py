"""
نماذج قاعدة البيانات - Database Models
نظام وكيل التشفير ما بعد الكمومي
جميع الجداول مصممة لدعم التشغيل متعدد المستأجرين
"""

from datetime import datetime, timezone
from app import db
import uuid
import enum


def utcnow():
    return datetime.now(timezone.utc)

# ══════════════════════════════════════════════════════════════════════════════
# جدول المستأجرين - Multi-Tenant Registry
# ══════════════════════════════════════════════════════════════════════════════

class Tenant(db.Model):
    """جدول المستأجرين - يُمثل كل مؤسسة مشتركة في النظام"""
    __tablename__ = "المستأجرون"

    معرف               = db.Column("id",             db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    اسم_المستأجر       = db.Column("اسم_المستأجر",   db.String(200), nullable=False)
    النطاق_الرئيسي     = db.Column("النطاق_الرئيسي", db.String(255), unique=True, nullable=False)
    خطة_الاشتراك       = db.Column("خطة_الاشتراك",  db.String(50),  default="أساسي")
    حالة_الحساب        = db.Column("حالة_الحساب",   db.String(20),  default="نشط")
    مستوى_أمان_NIST    = db.Column("مستوى_امان_nist",db.Integer,     default=3)
    تاريخ_التسجيل      = db.Column("تاريخ_التسجيل", db.DateTime(timezone=True), default=utcnow)
    آخر_تحديث          = db.Column("آخر_تحديث",     db.DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    الحد_الأقصى_للشهادات = db.Column("الحد_الاقصى_للشهادات", db.Integer, default=50)
    بيانات_تعريف       = db.Column("بيانات_تعريف",  db.JSON, default=dict)

    # العلاقات
    الشهادات   = db.relationship("Certificate",       back_populates="المستأجر",  cascade="all, delete-orphan")
    المصافحات  = db.relationship("HandshakeSession",  back_populates="المستأجر",  cascade="all, delete-orphan")
    المستخدمون = db.relationship("User",              back_populates="المستأجر",  cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "المعرف": self.معرف,
            "اسم_المستأجر": self.اسم_المستأجر,
            "النطاق_الرئيسي": self.النطاق_الرئيسي,
            "خطة_الاشتراك": self.خطة_الاشتراك,
            "حالة_الحساب": self.حالة_الحساب,
            "مستوى_أمان_NIST": self.مستوى_أمان_NIST,
            "تاريخ_التسجيل": self.تاريخ_التسجيل.isoformat() if self.تاريخ_التسجيل else None,
            "عدد_الشهادات_الحالية": len(self.الشهادات) if self.الشهادات else 0,
        }


# ══════════════════════════════════════════════════════════════════════════════
# جدول المستخدمين - Users
# ══════════════════════════════════════════════════════════════════════════════

class User(db.Model):
    """جدول المستخدمين - مسؤولو كل مستأجر"""
    __tablename__ = "المستخدمون"

    معرف              = db.Column("id",             db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    معرف_المستأجر     = db.Column("معرف_المستأجر", db.String(36), db.ForeignKey("المستأجرون.id"), nullable=False)
    البريد_الإلكتروني = db.Column("البريد_الالكتروني", db.String(255), unique=True, nullable=False)
    كلمة_المرور_مشفرة = db.Column("كلمة_المرور_مشفرة", db.String(255), nullable=False)
    الاسم_الكامل      = db.Column("الاسم_الكامل",  db.String(200))
    الدور             = db.Column("الدور",          db.String(50), default="مدير")  # مدير / مشغل / مراقب
    نشط               = db.Column("نشط",           db.Boolean, default=True)
    تاريخ_الإنشاء     = db.Column("تاريخ_الانشاء", db.DateTime(timezone=True), default=utcnow)
    آخر_دخول          = db.Column("آخر_دخول",      db.DateTime(timezone=True))

    المستأجر = db.relationship("Tenant", back_populates="المستخدمون")

    def to_dict(self):
        return {
            "المعرف": self.معرف,
            "البريد_الإلكتروني": self.البريد_الإلكتروني,
            "الاسم_الكامل": self.الاسم_الكامل,
            "الدور": self.الدور,
            "نشط": self.نشط,
            "آخر_دخول": self.آخر_دخول.isoformat() if self.آخر_دخول else None,
        }


# ══════════════════════════════════════════════════════════════════════════════
# جدول الخوارزميات المدعومة - PQC Algorithm Registry
# ══════════════════════════════════════════════════════════════════════════════

class PQCAlgorithm(db.Model):
    """سجل خوارزميات التشفير ما بعد الكمومي المعتمدة من NIST"""
    __tablename__ = "خوارزميات_التشفير_الكمي"

    معرف                = db.Column("id",             db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    اسم_الخوارزمية     = db.Column("اسم_الخوارزمية", db.String(100), unique=True, nullable=False)
    نوع_الخوارزمية     = db.Column("نوع_الخوارزمية", db.String(50))   # تبادل_مفاتيح / توقيع_رقمي
    مستوى_NIST         = db.Column("مستوى_nist",     db.Integer)      # 1-5
    وصف_مستوى_NIST     = db.Column("وصف_مستوى_nist", db.String(200))
    دورة_NIST          = db.Column("دورة_nist",      db.String(20))   # final / round4
    حجم_المفتاح_عام    = db.Column("حجم_المفتاح_عام",  db.Integer)   # بالبايت
    حجم_التوقيع         = db.Column("حجم_التوقيع",    db.Integer)
    حجم_النص_المشفر    = db.Column("حجم_النص_المشفر", db.Integer)
    مفعّل              = db.Column("مفعل",            db.Boolean, default=True)
    تاريخ_الإضافة      = db.Column("تاريخ_الاضافة",  db.DateTime(timezone=True), default=utcnow)
    ملاحظات_أمنية      = db.Column("ملاحظات_امنية",  db.Text)

    الشهادات  = db.relationship("Certificate",       back_populates="الخوارزمية")
    المصافحات = db.relationship("HandshakeSession",  back_populates="الخوارزمية")

    def to_dict(self):
        return {
            "المعرف": self.معرف,
            "اسم_الخوارزمية": self.اسم_الخوارزمية,
            "نوع_الخوارزمية": self.نوع_الخوارزمية,
            "مستوى_NIST": self.مستوى_NIST,
            "وصف_مستوى_NIST": self.وصف_مستوى_NIST,
            "دورة_NIST": self.دورة_NIST,
            "حجم_المفتاح_العام_بايت": self.حجم_المفتاح_عام,
            "مفعّل": self.مفعّل,
            "ملاحظات_أمنية": self.ملاحظات_أمنية,
        }


# ══════════════════════════════════════════════════════════════════════════════
# جدول الشهادات الرقمية - Quantum-Resistant Digital Certificates
# ══════════════════════════════════════════════════════════════════════════════

class CertificateStatus(str, enum.Enum):
    نشطة         = "نشطة"
    منتهية       = "منتهية"
    ملغاة        = "ملغاة"
    قيد_الترحيل  = "قيد_الترحيل"
    مرحّلة       = "مرحّلة"
    محجوزة       = "محجوزة"


class Certificate(db.Model):
    """جدول الشهادات الرقمية المقاومة للحواسيب الكمومية"""
    __tablename__ = "الشهادات_الرقمية"

    معرف               = db.Column("id",              db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    معرف_المستأجر      = db.Column("معرف_المستأجر",  db.String(36), db.ForeignKey("المستأجرون.id"), nullable=False)
    معرف_الخوارزمية    = db.Column("معرف_الخوارزمية",db.String(36), db.ForeignKey("خوارزميات_التشفير_الكمي.id"), nullable=False)
    الاسم_الشائع       = db.Column("الاسم_الشائع",  db.String(255), nullable=False)
    المنظمة            = db.Column("المنظمة",        db.String(255))
    الدولة             = db.Column("الدولة",         db.String(10))
    بصمة_الشهادة       = db.Column("بصمة_الشهادة",  db.String(128), unique=True)
    المفتاح_العام      = db.Column("المفتاح_العام",  db.Text)
    تاريخ_الإصدار      = db.Column("تاريخ_الاصدار", db.DateTime(timezone=True), default=utcnow)
    تاريخ_الانتهاء     = db.Column("تاريخ_الانتهاء",db.DateTime(timezone=True), nullable=False)
    الحالة             = db.Column("الحالة",         db.String(30), default=CertificateStatus.نشطة.value)
    شهادة_الجذر        = db.Column("شهادة_الجذر",   db.Boolean, default=False)
    معرف_الشهادة_السابقة = db.Column("معرف_الشهادة_السابقة", db.String(36), db.ForeignKey("الشهادات_الرقمية.id"), nullable=True)
    سبب_الترحيل        = db.Column("سبب_الترحيل",   db.String(500))
    بيانات_X509        = db.Column("بيانات_x509",   db.Text)
    تاريخ_الإلغاء      = db.Column("تاريخ_الالغاء", db.DateTime(timezone=True))
    سبب_الإلغاء        = db.Column("سبب_الالغاء",   db.String(500))
    آخر_تحديث          = db.Column("آخر_تحديث",    db.DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    المستأجر     = db.relationship("Tenant",      back_populates="الشهادات")
    الخوارزمية   = db.relationship("PQCAlgorithm",back_populates="الشهادات")
    الشهادة_السابقة = db.relationship("Certificate", remote_side=[معرف], backref="الشهادات_البديلة")

    def to_dict(self):
        return {
            "المعرف": self.معرف,
            "الاسم_الشائع": self.الاسم_الشائع,
            "المنظمة": self.المنظمة,
            "الدولة": self.الدولة,
            "بصمة_الشهادة": self.بصمة_الشهادة,
            "تاريخ_الإصدار": self.تاريخ_الإصدار.isoformat() if self.تاريخ_الإصدار else None,
            "تاريخ_الانتهاء": self.تاريخ_الانتهاء.isoformat() if self.تاريخ_الانتهاء else None,
            "الحالة": self.الحالة,
            "الخوارزمية": self.الخوارزمية.اسم_الخوارزمية if self.الخوارزمية else None,
            "شهادة_الجذر": self.شهادة_الجذر,
        }


# ══════════════════════════════════════════════════════════════════════════════
# جدول جلسات المصافحة - Quantum Handshake State Machine
# ══════════════════════════════════════════════════════════════════════════════

class HandshakeState(str, enum.Enum):
    """حالات آلة الحالة للمصافحة الكمومية"""
    مبدوءة                = "مبدوءة"               # CLIENT_HELLO تم إرسال
    معلومات_العميل_مستلمة = "معلومات_العميل_مستلمة" # استقبال قدرات العميل
    خوارزمية_محددة        = "خوارزمية_محددة"        # اتفاق على الخوارزمية
    مفاتيح_مبادلة         = "مفاتيح_مبادلة"         # تبادل المفاتيح KEM
    شهادة_مرسلة           = "شهادة_مرسلة"           # إرسال الشهادة
    توقيع_مُتحقق          = "توقيع_مُتحقق"           # التحقق من التوقيع
    مكتملة               = "مكتملة"                 # المصافحة ناجحة
    فاشلة                = "فاشلة"                  # فشل المصافحة
    منتهية_الصلاحية       = "منتهية_الصلاحية"        # انتهت صلاحية الجلسة


class HandshakeSession(db.Model):
    """جلسات المصافحة الكمومية - آلة الحالة الكاملة"""
    __tablename__ = "جلسات_المصافحة_الكمومية"

    معرف                = db.Column("id",              db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    معرف_المستأجر       = db.Column("معرف_المستأجر",  db.String(36), db.ForeignKey("المستأجرون.id"), nullable=False)
    معرف_الخوارزمية     = db.Column("معرف_الخوارزمية",db.String(36), db.ForeignKey("خوارزميات_التشفير_الكمي.id"), nullable=False)
    معرف_الشهادة        = db.Column("معرف_الشهادة",   db.String(36), db.ForeignKey("الشهادات_الرقمية.id"), nullable=True)
    الحالة_الحالية      = db.Column("الحالة_الحالية", db.String(50),  default=HandshakeState.مبدوءة.value)
    عنوان_IP_العميل     = db.Column("عنوان_ip_العميل",db.String(45))
    المنفذ_المستهدف     = db.Column("المنفذ_المستهدف",db.Integer)
    بروتوكول_TLS        = db.Column("بروتوكول_tls",  db.String(20), default="TLS 1.3")
    معرف_الجلسة_الكمومي = db.Column("معرف_الجلسة_الكمومي", db.String(128))
    مفتاح_KEM_العام     = db.Column("مفتاح_kem_العام", db.Text)
    النص_المشفر_KEM     = db.Column("النص_المشفر_kem", db.Text)
    بصمة_التوقيع        = db.Column("بصمة_التوقيع",  db.String(256))
    وقت_البدء           = db.Column("وقت_البدء",     db.DateTime(timezone=True), default=utcnow)
    وقت_الاكتمال        = db.Column("وقت_الاكتمال",  db.DateTime(timezone=True))
    وقت_الانتهاء        = db.Column("وقت_الانتهاء",  db.DateTime(timezone=True))
    سبب_الفشل           = db.Column("سبب_الفشل",    db.Text)
    مدة_المصافحة_مللي   = db.Column("مدة_المصافحة_مللي", db.Integer)  # بالميلي ثانية
    سجل_الانتقالات      = db.Column("سجل_الانتقالات", db.JSON, default=list)
    بيانات_إضافية       = db.Column("بيانات_اضافية",  db.JSON, default=dict)

    المستأجر   = db.relationship("Tenant",       back_populates="المصافحات")
    الخوارزمية = db.relationship("PQCAlgorithm", back_populates="المصافحات")
    الشهادة    = db.relationship("Certificate")

    def to_dict(self):
        return {
            "المعرف": self.معرف,
            "الحالة_الحالية": self.الحالة_الحالية,
            "الخوارزمية": self.الخوارزمية.اسم_الخوارزمية if self.الخوارزمية else None,
            "عنوان_IP_العميل": self.عنوان_IP_العميل,
            "بروتوكول_TLS": self.بروتوكول_TLS,
            "وقت_البدء": self.وقت_البدء.isoformat() if self.وقت_البدء else None,
            "وقت_الاكتمال": self.وقت_الاكتمال.isoformat() if self.وقت_الاكتمال else None,
            "مدة_المصافحة_مللي": self.مدة_المصافحة_مللي,
            "سجل_الانتقالات": self.سجل_الانتقالات,
        }


# ══════════════════════════════════════════════════════════════════════════════
# جدول سجلات الامتثال - Compliance Ledger
# ══════════════════════════════════════════════════════════════════════════════

class ComplianceEventType(str, enum.Enum):
    """أنواع أحداث الامتثال"""
    إصدار_شهادة      = "إصدار_شهادة"
    ترحيل_شهادة      = "ترحيل_شهادة"
    إلغاء_شهادة      = "إلغاء_شهادة"
    مصافحة_ناجحة     = "مصافحة_ناجحة"
    مصافحة_فاشلة     = "مصافحة_فاشلة"
    تسجيل_مستأجر     = "تسجيل_مستأجر"
    تحديث_خوارزمية   = "تحديث_خوارزمية"
    انتهاك_أمني      = "انتهاك_أمني"
    تدقيق_دوري       = "تدقيق_دوري"
    تحديث_سياسة      = "تحديث_سياسة"


class ComplianceLedger(db.Model):
    """سجل الامتثال غير القابل للتعديل - Immutable Compliance Ledger"""
    __tablename__ = "سجل_الامتثال"

    معرف                = db.Column("id",              db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    معرف_المستأجر       = db.Column("معرف_المستأجر",  db.String(36), db.ForeignKey("المستأجرون.id"), nullable=True)
    نوع_الحدث           = db.Column("نوع_الحدث",     db.String(50), nullable=False)
    الكيان_المرجعي      = db.Column("الكيان_المرجعي", db.String(36))  # معرف الشهادة أو الجلسة المرتبطة
    نوع_الكيان          = db.Column("نوع_الكيان",    db.String(50))   # شهادة / جلسة / مستأجر
    خطورة_الحدث        = db.Column("خطورة_الحدث",   db.String(20), default="معلومات")  # معلومات / تحذير / حرج
    وصف_الحدث          = db.Column("وصف_الحدث",     db.Text, nullable=False)
    تفاصيل_تقنية        = db.Column("تفاصيل_تقنية",  db.JSON, default=dict)
    الخوارزمية_المستخدمة = db.Column("الخوارزمية_المستخدمة", db.String(100))
    عنوان_IP_المصدر     = db.Column("عنوان_ip_المصدر", db.String(45))
    معرف_المستخدم       = db.Column("معرف_المستخدم",  db.String(36), db.ForeignKey("المستخدمون.id"), nullable=True)
    بصمة_السجل          = db.Column("بصمة_السجل",   db.String(256))  # hash للتحقق من التكامل
    طابع_زمني          = db.Column("طابع_زمني",     db.DateTime(timezone=True), default=utcnow, nullable=False)
    معيار_الامتثال      = db.Column("معيار_الامتثال", db.String(100))  # NIST SP 800-208 / ISO 27001

    def to_dict(self):
        return {
            "المعرف": self.معرف,
            "نوع_الحدث": self.نوع_الحدث,
            "خطورة_الحدث": self.خطورة_الحدث,
            "وصف_الحدث": self.وصف_الحدث,
            "الخوارزمية_المستخدمة": self.الخوارزمية_المستخدمة,
            "طابع_زمني": self.طابع_زمني.isoformat() if self.طابع_زمني else None,
            "معيار_الامتثال": self.معيار_الامتثال,
            "بصمة_السجل": self.بصمة_السجل,
        }


# ══════════════════════════════════════════════════════════════════════════════
# جدول سياسات الترحيل - Certificate Migration Policies
# ══════════════════════════════════════════════════════════════════════════════

class MigrationPolicy(db.Model):
    """سياسات الترحيل الديناميكية للشهادات"""
    __tablename__ = "سياسات_الترحيل"

    معرف                    = db.Column("id",                     db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    معرف_المستأجر           = db.Column("معرف_المستأجر",         db.String(36), db.ForeignKey("المستأجرون.id"), nullable=False)
    اسم_السياسة             = db.Column("اسم_السياسة",           db.String(200), nullable=False)
    الخوارزمية_المصدر        = db.Column("الخوارزمية_المصدر",     db.String(100))
    الخوارزمية_الهدف         = db.Column("الخوارزمية_الهدف",     db.String(100), nullable=False)
    الترحيل_التلقائي        = db.Column("الترحيل_التلقائي",      db.Boolean, default=True)
    أيام_التحذير_قبل_الانتهاء = db.Column("ايام_التحذير",        db.Integer, default=30)
    الأولوية                = db.Column("الاولوية",              db.Integer, default=1)
    نشطة                    = db.Column("نشطة",                  db.Boolean, default=True)
    تاريخ_الإنشاء           = db.Column("تاريخ_الانشاء",         db.DateTime(timezone=True), default=utcnow)
    شروط_الترحيل            = db.Column("شروط_الترحيل",          db.JSON, default=dict)

    المستأجر = db.relationship("Tenant", backref="سياسات_الترحيل")

    def to_dict(self):
        return {
            "المعرف": self.معرف,
            "اسم_السياسة": self.اسم_السياسة,
            "الخوارزمية_المصدر": self.الخوارزمية_المصدر,
            "الخوارزمية_الهدف": self.الخوارزمية_الهدف,
            "الترحيل_التلقائي": self.الترحيل_التلقائي,
            "أيام_التحذير": self.أيام_التحذير_قبل_الانتهاء,
            "نشطة": self.نشطة,
        }
