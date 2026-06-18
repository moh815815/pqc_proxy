"""الترحيل الأولي - Initial Migration
يُنشئ جميع جداول قاعدة البيانات بالمصطلحات العربية
"""
from alembic import op
import sqlalchemy as sa


revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # جدول المستأجرين
    op.create_table(
        'المستأجرون',
        sa.Column('id',               sa.String(36),  primary_key=True),
        sa.Column('اسم_المستأجر',    sa.String(200), nullable=False),
        sa.Column('النطاق_الرئيسي',  sa.String(255), nullable=False, unique=True),
        sa.Column('خطة_الاشتراك',   sa.String(50),  server_default='أساسي'),
        sa.Column('حالة_الحساب',    sa.String(20),  server_default='نشط'),
        sa.Column('مستوى_امان_nist', sa.Integer,     server_default='3'),
        sa.Column('تاريخ_التسجيل',  sa.DateTime(timezone=True)),
        sa.Column('آخر_تحديث',      sa.DateTime(timezone=True)),
        sa.Column('الحد_الاقصى_للشهادات', sa.Integer, server_default='50'),
        sa.Column('بيانات_تعريف',   sa.JSON),
    )

    # جدول خوارزميات التشفير
    op.create_table(
        'خوارزميات_التشفير_الكمي',
        sa.Column('id',                sa.String(36),  primary_key=True),
        sa.Column('اسم_الخوارزمية',   sa.String(100), nullable=False, unique=True),
        sa.Column('نوع_الخوارزمية',   sa.String(50)),
        sa.Column('مستوى_nist',       sa.Integer),
        sa.Column('وصف_مستوى_nist',   sa.String(200)),
        sa.Column('دورة_nist',        sa.String(20)),
        sa.Column('حجم_المفتاح_عام',  sa.Integer),
        sa.Column('حجم_التوقيع',      sa.Integer),
        sa.Column('حجم_النص_المشفر',  sa.Integer),
        sa.Column('مفعل',             sa.Boolean,     server_default='true'),
        sa.Column('تاريخ_الاضافة',    sa.DateTime(timezone=True)),
        sa.Column('ملاحظات_امنية',    sa.Text),
    )

    # جدول المستخدمين
    op.create_table(
        'المستخدمون',
        sa.Column('id',                   sa.String(36),  primary_key=True),
        sa.Column('معرف_المستأجر',       sa.String(36),  sa.ForeignKey('المستأجرون.id'), nullable=False),
        sa.Column('البريد_الالكتروني',   sa.String(255), nullable=False, unique=True),
        sa.Column('كلمة_المرور_مشفرة',  sa.String(255), nullable=False),
        sa.Column('الاسم_الكامل',        sa.String(200)),
        sa.Column('الدور',               sa.String(50),  server_default='مدير'),
        sa.Column('نشط',                 sa.Boolean,     server_default='true'),
        sa.Column('تاريخ_الانشاء',       sa.DateTime(timezone=True)),
        sa.Column('آخر_دخول',           sa.DateTime(timezone=True)),
    )

    # جدول الشهادات
    op.create_table(
        'الشهادات_الرقمية',
        sa.Column('id',                       sa.String(36), primary_key=True),
        sa.Column('معرف_المستأجر',           sa.String(36), sa.ForeignKey('المستأجرون.id'),                nullable=False),
        sa.Column('معرف_الخوارزمية',         sa.String(36), sa.ForeignKey('خوارزميات_التشفير_الكمي.id'), nullable=False),
        sa.Column('الاسم_الشائع',            sa.String(255), nullable=False),
        sa.Column('المنظمة',                  sa.String(255)),
        sa.Column('الدولة',                   sa.String(10)),
        sa.Column('بصمة_الشهادة',            sa.String(128), unique=True),
        sa.Column('المفتاح_العام',            sa.Text),
        sa.Column('تاريخ_الاصدار',           sa.DateTime(timezone=True)),
        sa.Column('تاريخ_الانتهاء',          sa.DateTime(timezone=True), nullable=False),
        sa.Column('الحالة',                   sa.String(30), server_default='نشطة'),
        sa.Column('شهادة_الجذر',             sa.Boolean,    server_default='false'),
        sa.Column('معرف_الشهادة_السابقة',    sa.String(36), sa.ForeignKey('الشهادات_الرقمية.id'), nullable=True),
        sa.Column('سبب_الترحيل',             sa.String(500)),
        sa.Column('بيانات_x509',             sa.Text),
        sa.Column('تاريخ_الالغاء',           sa.DateTime(timezone=True)),
        sa.Column('سبب_الالغاء',             sa.String(500)),
        sa.Column('آخر_تحديث',              sa.DateTime(timezone=True)),
    )

    # جدول جلسات المصافحة
    op.create_table(
        'جلسات_المصافحة_الكمومية',
        sa.Column('id',                       sa.String(36), primary_key=True),
        sa.Column('معرف_المستأجر',           sa.String(36), sa.ForeignKey('المستأجرون.id'),                nullable=False),
        sa.Column('معرف_الخوارزمية',         sa.String(36), sa.ForeignKey('خوارزميات_التشفير_الكمي.id'), nullable=False),
        sa.Column('معرف_الشهادة',            sa.String(36), sa.ForeignKey('الشهادات_الرقمية.id'),         nullable=True),
        sa.Column('الحالة_الحالية',          sa.String(50), server_default='مبدوءة'),
        sa.Column('عنوان_ip_العميل',         sa.String(45)),
        sa.Column('المنفذ_المستهدف',         sa.Integer),
        sa.Column('بروتوكول_tls',            sa.String(20), server_default='TLS 1.3'),
        sa.Column('معرف_الجلسة_الكمومي',    sa.String(128)),
        sa.Column('مفتاح_kem_العام',         sa.Text),
        sa.Column('النص_المشفر_kem',         sa.Text),
        sa.Column('بصمة_التوقيع',            sa.String(256)),
        sa.Column('وقت_البدء',              sa.DateTime(timezone=True)),
        sa.Column('وقت_الاكتمال',           sa.DateTime(timezone=True)),
        sa.Column('وقت_الانتهاء',           sa.DateTime(timezone=True)),
        sa.Column('سبب_الفشل',              sa.Text),
        sa.Column('مدة_المصافحة_مللي',      sa.Integer),
        sa.Column('سجل_الانتقالات',         sa.JSON),
        sa.Column('بيانات_اضافية',          sa.JSON),
    )

    # جدول سجل الامتثال
    op.create_table(
        'سجل_الامتثال',
        sa.Column('id',                       sa.String(36), primary_key=True),
        sa.Column('معرف_المستأجر',           sa.String(36), sa.ForeignKey('المستأجرون.id'),  nullable=True),
        sa.Column('نوع_الحدث',              sa.String(50),  nullable=False),
        sa.Column('الكيان_المرجعي',          sa.String(36)),
        sa.Column('نوع_الكيان',             sa.String(50)),
        sa.Column('خطورة_الحدث',            sa.String(20),  server_default='معلومات'),
        sa.Column('وصف_الحدث',              sa.Text,        nullable=False),
        sa.Column('تفاصيل_تقنية',           sa.JSON),
        sa.Column('الخوارزمية_المستخدمة',   sa.String(100)),
        sa.Column('عنوان_ip_المصدر',         sa.String(45)),
        sa.Column('معرف_المستخدم',          sa.String(36),  sa.ForeignKey('المستخدمون.id'), nullable=True),
        sa.Column('بصمة_السجل',             sa.String(256)),
        sa.Column('طابع_زمني',              sa.DateTime(timezone=True), nullable=False),
        sa.Column('معيار_الامتثال',          sa.String(100)),
    )

    # جدول سياسات الترحيل
    op.create_table(
        'سياسات_الترحيل',
        sa.Column('id',                       sa.String(36), primary_key=True),
        sa.Column('معرف_المستأجر',           sa.String(36), sa.ForeignKey('المستأجرون.id'), nullable=False),
        sa.Column('اسم_السياسة',             sa.String(200), nullable=False),
        sa.Column('الخوارزمية_المصدر',       sa.String(100)),
        sa.Column('الخوارزمية_الهدف',       sa.String(100), nullable=False),
        sa.Column('الترحيل_التلقائي',        sa.Boolean,    server_default='true'),
        sa.Column('ايام_التحذير',            sa.Integer,    server_default='30'),
        sa.Column('الاولوية',                sa.Integer,    server_default='1'),
        sa.Column('نشطة',                    sa.Boolean,    server_default='true'),
        sa.Column('تاريخ_الانشاء',          sa.DateTime(timezone=True)),
        sa.Column('شروط_الترحيل',           sa.JSON),
    )


def downgrade():
    op.drop_table('سياسات_الترحيل')
    op.drop_table('سجل_الامتثال')
    op.drop_table('جلسات_المصافحة_الكمومية')
    op.drop_table('الشهادات_الرقمية')
    op.drop_table('المستخدمون')
    op.drop_table('خوارزميات_التشفير_الكمي')
    op.drop_table('المستأجرون')
