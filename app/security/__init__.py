# ==============================================================================
# app/security/__init__.py
# Enterprise Security & Compliance Package - The Fortress of Intelligence
# ==============================================================================
"""
This package contains enterprise security and compliance features for CLARITY.
Includes audit logging, advanced rate limiting, encryption, and compliance frameworks.
"""

from .audit_logger import (
    AuditLogger,
    log_user_action,
    log_system_event,
    log_security_event,
    get_audit_trail
)

from .rate_limiter import (
    AdvancedRateLimiter,
    check_rate_limit,
    get_rate_limit_status,
    reset_rate_limit
)

from .encryption import (
    EncryptionManager,
    encrypt_data,
    decrypt_data,
    generate_encryption_key,
    rotate_encryption_key
)

from .compliance import (
    ComplianceManager,
    handle_gdpr_request,
    handle_hipaa_compliance,
    handle_soc2_audit,
    create_soc2_control,
    test_soc2_control,
    collect_soc2_evidence,
    report_soc2_incident,
    conduct_access_review,
    get_soc2_dashboard,
    get_compliance_status
)

__all__ = [
    # Audit Logging
    'AuditLogger',
    'log_user_action',
    'log_system_event',
    'log_security_event',
    'get_audit_trail',
    
    # Rate Limiting
    'AdvancedRateLimiter',
    'check_rate_limit',
    'get_rate_limit_status',
    'reset_rate_limit',
    
    # Encryption
    'EncryptionManager',
    'encrypt_data',
    'decrypt_data',
    'generate_encryption_key',
    'rotate_encryption_key',
    
    # Compliance
    'ComplianceManager',
    'handle_gdpr_request',
    'handle_hipaa_compliance',
    'handle_soc2_audit',
    'create_soc2_control',
    'test_soc2_control',
    'collect_soc2_evidence',
    'report_soc2_incident',
    'conduct_access_review',
    'get_soc2_dashboard',
    'get_compliance_status'
]

