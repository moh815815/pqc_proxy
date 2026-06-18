"""
إعدادات النظام - System Configuration
نظام وكيل التشفير ما بعد الكمومي
"""

import os
from datetime import timedelta


class ConfigBase:
    # ──────────────────────────────────────────────
    # إعدادات قاعدة البيانات PostgreSQL
    # ──────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://pqc_user:pqc_pass@localhost:5432/pqc_proxy_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # ──────────────────────────────────────────────
    # إعدادات JWT - رمز المصادقة
    # ──────────────────────────────────────────────
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "مفتاح-سري-يجب-تغييره-في-الإنتاج")
    JWT_ACCESS_TOKEN_EXPIRES  = timedelta(hours=2)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

    # ──────────────────────────────────────────────
    # إعدادات التشفير ما بعد الكمومي (NIST المعتمدة)
    # ──────────────────────────────────────────────
    PQC_ALGORITHMS = {
        # خوارزمية ML-KEM (كايبر سابقاً) - للتبادل الآمن للمفاتيح
        "ML-KEM-512":  {"level": 1, "type": "kem",        "nist_round": "final", "key_size": 800},
        "ML-KEM-768":  {"level": 3, "type": "kem",        "nist_round": "final", "key_size": 1184},
        "ML-KEM-1024": {"level": 5, "type": "kem",        "nist_round": "final", "key_size": 1568},
        # خوارزمية ML-DSA (ديليثيوم سابقاً) - للتوقيع الرقمي
        "ML-DSA-44":   {"level": 2, "type": "signature",  "nist_round": "final", "key_size": 1312},
        "ML-DSA-65":   {"level": 3, "type": "signature",  "nist_round": "final", "key_size": 1952},
        "ML-DSA-87":   {"level": 5, "type": "signature",  "nist_round": "final", "key_size": 2592},
        # خوارزمية SLH-DSA (سبينكس+ سابقاً) - توقيع رقمي قائم على الدوال الهاشية
        "SLH-DSA-128s":{"level": 1, "type": "signature",  "nist_round": "final", "key_size": 64},
        "SLH-DSA-192f":{"level": 3, "type": "signature",  "nist_round": "final", "key_size": 96},
        "SLH-DSA-256s":{"level": 5, "type": "signature",  "nist_round": "final", "key_size": 128},
        # خوارزمية FALCON - توقيع رقمي متشعب (قيد المراجعة)
        "FALCON-512":  {"level": 1, "type": "signature",  "nist_round": "round4", "key_size": 897},
        "FALCON-1024": {"level": 5, "type": "signature",  "nist_round": "round4", "key_size": 1793},
    }

    # مستويات أمان NIST
    NIST_SECURITY_LEVELS = {
        1: "مكافئ لـ AES-128",
        2: "مكافئ لـ SHA-256",
        3: "مكافئ لـ AES-192",
        4: "مكافئ لـ SHA-384",
        5: "مكافئ لـ AES-256",
    }

    # ──────────────────────────────────────────────
    # إعدادات الشهادات الرقمية
    # ──────────────────────────────────────────────
    CERT_EXPIRY_DAYS_DEFAULT = 365
    CERT_ROTATION_WARNING_DAYS = 30
    MAX_CERTS_PER_TENANT = 50

    # ──────────────────────────────────────────────
    # إعدادات المستأجرين المتعددين
    # ──────────────────────────────────────────────
    MAX_TENANTS = 1000
    DEFAULT_TENANT_PLAN = "أساسي"

    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "مفتاح-فلاسك-سري")
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"


class ConfigDevelopment(ConfigBase):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ConfigProduction(ConfigBase):
    DEBUG = False
    SQLALCHEMY_ECHO = False
