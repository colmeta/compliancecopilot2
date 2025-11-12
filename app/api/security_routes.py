# ==============================================================================
# app/api/security_routes.py
# Security & Compliance API Routes - The Fortress Gateway
# ==============================================================================
"""
This module provides API endpoints for security and compliance features.
Includes audit logging, rate limiting, encryption, and compliance management.
"""

from flask import Blueprint, request, jsonify, current_app, g
from functools import wraps
import logging
from datetime import datetime, timedelta
from app.api.routes import api_key_required
from app.middleware.tier_check import check_tier_limit, require_tier
from app.security.audit_logger import AuditLogger
from app.security.rate_limiter import AdvancedRateLimiter
from app.security.encryption import EncryptionManager
from app.security.compliance import ComplianceManager
from app.models import User, Subscription

# Configure logging
logger = logging.getLogger(__name__)

# Create security blueprint
security = Blueprint('security', __name__)

# ==============================================================================
# AUDIT LOGGING ENDPOINTS
# ==============================================================================

@security.route('/audit/trail', methods=['GET'])
@api_key_required
@check_tier_limit('audit_logging', 1)
def get_audit_trail():
    """
    Get audit trail for the current user or system.
    
    Available for Pro and Enterprise tiers.
    
    Query Parameters:
        - action: Filter by action type
        - resource_type: Filter by resource type
        - start_date: Start date (ISO format)
        - end_date: End date (ISO format)
        - limit: Maximum number of records (default: 100)
    
    Response:
        - audit_trail: List of audit log entries
        - total_records: Total number of records returned
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get query parameters
        action = request.args.get('action')
        resource_type = request.args.get('resource_type')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        limit = int(request.args.get('limit', 100))
        
        # Parse dates
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid start_date format'}), 400
        
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid end_date format'}), 400
        
        # Get user's subscription tier
        subscription = Subscription.query.filter_by(user_id=user.id, status='active').first()
        user_tier = subscription.tier if subscription else 'free'
        
        # Check if user can access system-wide audit logs
        if user_tier != 'enterprise':
            # Regular users can only see their own audit logs
            user_id = user.id
        else:
            # Enterprise users can see system-wide logs
            user_id = request.args.get('user_id', user.id)
            if user_id != user.id and user_tier != 'enterprise':
                return jsonify({'error': 'Access denied to other users\' audit logs'}), 403
        
        # Get audit trail
        logger = AuditLogger()
        result = logger.get_audit_trail(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'audit_trail': result['audit_trail'],
                'total_records': result['total_records'],
                'filters': result['filters']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get audit trail endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@security.route('/audit/activity', methods=['GET'])
@api_key_required
@check_tier_limit('audit_logging', 1)
def get_user_activity_summary():
    """
    Get activity summary for the current user.
    
    Available for Pro and Enterprise tiers.
    
    Query Parameters:
        - days: Number of days to analyze (default: 30)
    
    Response:
        - summary: User activity summary
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get query parameters
        days = int(request.args.get('days', 30))
        
        # Get activity summary
        logger = AuditLogger()
        result = logger.get_user_activity_summary(user.id, days)
        
        if result['success']:
            return jsonify({
                'success': True,
                'user_id': user.id,
                'period_days': days,
                'summary': result['summary']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get user activity summary endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@security.route('/audit/security-events', methods=['GET'])
@api_key_required
@require_tier('enterprise')  # Only enterprise users can access security events
def get_security_events():
    """
    Get security events for monitoring.
    
    Available for Enterprise tier only.
    
    Query Parameters:
        - days: Number of days to analyze (default: 30)
        - severity: Filter by severity level
    
    Response:
        - events: List of security events
        - statistics: Security event statistics
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get query parameters
        days = int(request.args.get('days', 30))
        severity = request.args.get('severity')
        
        # Get security events
        logger = AuditLogger()
        result = logger.get_security_events(days, severity)
        
        if result['success']:
            return jsonify({
                'success': True,
                'period_days': days,
                'events': result['events'],
                'statistics': result['statistics']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get security events endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==============================================================================
# RATE LIMITING ENDPOINTS
# ==============================================================================

@security.route('/rate-limit/status', methods=['GET'])
@api_key_required
def get_rate_limit_status():
    """
    Get current rate limit status for the user.
    
    Available for all tiers.
    
    Query Parameters:
        - endpoint: Specific endpoint to check
        - feature: Specific feature to check
    
    Response:
        - status: Rate limit status information
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get query parameters
        endpoint = request.args.get('endpoint')
        feature = request.args.get('feature')
        
        # Get rate limit status
        limiter = AdvancedRateLimiter()
        result = limiter.get_rate_limit_status(user.id, endpoint, feature)
        
        if result['success']:
            return jsonify({
                'success': True,
                'user_id': user.id,
                'tier': result['tier'],
                'limits': result['limits'],
                'usage': result['usage'],
                'remaining': result['remaining']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get rate limit status endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@security.route('/rate-limit/reset', methods=['POST'])
@api_key_required
@require_tier('enterprise')  # Only enterprise users can reset rate limits
def reset_rate_limit():
    """
    Reset rate limits for the user.
    
    Available for Enterprise tier only.
    
    Request:
        - limit_type: Type of limit to reset (optional, resets all if not provided)
    
    Response:
        - result: Rate limit reset result
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get request data
        data = request.get_json() or {}
        limit_type = data.get('limit_type')
        
        # Reset rate limit
        limiter = AdvancedRateLimiter()
        result = limiter.reset_rate_limit(user.id, limit_type)
        
        if result['success']:
            return jsonify({
                'success': True,
                'user_id': user.id,
                'deleted_keys': result['deleted_keys'],
                'limit_type': result['limit_type']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Reset rate limit endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==============================================================================
# ENCRYPTION ENDPOINTS
# ==============================================================================

@security.route('/encryption/status', methods=['GET'])
@api_key_required
@check_tier_limit('encryption', 1)
def get_encryption_status():
    """
    Get encryption system status.
    
    Available for Pro and Enterprise tiers.
    
    Response:
        - status: Encryption system status
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get encryption status
        manager = EncryptionManager()
        result = manager.get_encryption_status()
        
        if result['success']:
            return jsonify({
                'success': True,
                'encryption_enabled': result['encryption_enabled'],
                'available_keys': result['available_keys'],
                'key_info': result['key_info'],
                'status': result['status']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get encryption status endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@security.route('/encryption/validate', methods=['POST'])
@api_key_required
@require_tier('enterprise')  # Only enterprise users can validate encryption
def validate_encryption_integrity():
    """
    Validate encryption system integrity.
    
    Available for Enterprise tier only.
    
    Response:
        - validation: Encryption integrity validation result
    """
    try:
        # Get current user
        user = g.current_user
        
        # Validate encryption integrity
        manager = EncryptionManager()
        result = manager.validate_encryption_integrity()
        
        if result['success']:
            return jsonify({
                'success': True,
                'overall_status': result['overall_status'],
                'validation_results': result['validation_results'],
                'tested_at': result['tested_at']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Validate encryption integrity endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@security.route('/encryption/rotate-key', methods=['POST'])
@api_key_required
@require_tier('enterprise')  # Only enterprise users can rotate keys
def rotate_encryption_key():
    """
    Rotate an encryption key.
    
    Available for Enterprise tier only.
    
    Request:
        - key_type: Type of key to rotate
    
    Response:
        - result: Key rotation result
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get request data
        data = request.get_json()
        if not data or 'key_type' not in data:
            return jsonify({'error': 'key_type is required'}), 400
        
        key_type = data['key_type']
        
        # Rotate encryption key
        manager = EncryptionManager()
        result = manager.rotate_encryption_key(key_type, user.id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'key_type': result['key_type'],
                'old_key_id': result['old_key_id'],
                'rotated_at': result['rotated_at']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Rotate encryption key endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==============================================================================
# COMPLIANCE ENDPOINTS
# ==============================================================================

@security.route('/compliance/status', methods=['GET'])
@api_key_required
@check_tier_limit('compliance_frameworks', 1)
def get_compliance_status():
    """
    Get compliance status for the user or system.
    
    Available for Pro and Enterprise tiers.
    
    Query Parameters:
        - framework: Specific framework ('gdpr', 'hipaa', 'soc2')
    
    Response:
        - compliance: Compliance status information
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get query parameters
        framework = request.args.get('framework')
        
        # Get user's subscription tier
        subscription = Subscription.query.filter_by(user_id=user.id, status='active').first()
        user_tier = subscription.tier if subscription else 'free'
        
        # Check if user can access system-wide compliance
        if user_tier != 'enterprise':
            # Regular users can only see their own compliance status
            user_id = user.id
        else:
            # Enterprise users can see system-wide compliance
            user_id = request.args.get('user_id', user.id)
            if user_id != user.id and user_tier != 'enterprise':
                return jsonify({'error': 'Access denied to other users\' compliance data'}), 403
        
        # Get compliance status
        manager = ComplianceManager()
        result = manager.get_compliance_status(user_id, framework)
        
        if result['success']:
            return jsonify({
                'success': True,
                'user_id': user_id,
                'framework': framework,
                'compliance_status': result['compliance_status'],
                'consent_status': result['consent_status'],
                'retention_status': result['retention_status'],
                'last_updated': result['last_updated']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get compliance status endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@security.route('/compliance/gdpr', methods=['POST'])
@api_key_required
def handle_gdpr_request():
    """
    Handle GDPR compliance request.
    
    Available for all tiers.
    
    Request:
        - request_type: Type of GDPR request ('access', 'deletion', 'portability', 'rectification')
        - requester_email: Email of the requester (for verification)
    
    Response:
        - result: GDPR request handling result
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get request data
        data = request.get_json()
        if not data or 'request_type' not in data:
            return jsonify({'error': 'request_type is required'}), 400
        
        request_type = data['request_type']
        requester_email = data.get('requester_email')
        
        # Handle GDPR request
        manager = ComplianceManager()
        result = manager.handle_gdpr_request(request_type, user.id, requester_email)
        
        if result['success']:
            return jsonify({
                'success': True,
                'request_type': result['request_type'],
                'user_id': result['user_id'],
                'compliance_event_id': result['compliance_event_id'],
                'result': result['result']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Handle GDPR request endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@security.route('/compliance/consent', methods=['POST'])
@api_key_required
def record_consent():
    """
    Record user consent for compliance tracking.
    
    Available for all tiers.
    
    Request:
        - consent_type: Type of consent ('terms', 'privacy', 'marketing', 'data_processing')
        - granted: Whether consent was granted
        - consent_text: Text of the consent (optional)
    
    Response:
        - result: Consent recording result
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get request data
        data = request.get_json()
        if not data or 'consent_type' not in data or 'granted' not in data:
            return jsonify({'error': 'consent_type and granted are required'}), 400
        
        consent_type = data['consent_type']
        granted = data['granted']
        consent_text = data.get('consent_text')
        
        # Get IP address
        ip_address = request.remote_addr if hasattr(request, 'remote_addr') else None
        
        # Record consent
        manager = ComplianceManager()
        result = manager.record_consent(user.id, consent_type, granted, consent_text, ip_address)
        
        if result['success']:
            return jsonify({
                'success': True,
                'user_id': result['user_id'],
                'consent_type': result['consent_type'],
                'granted': result['granted'],
                'recorded_at': result['recorded_at']
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Record consent endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@security.route('/compliance/hipaa', methods=['POST'])
@api_key_required
@check_tier_limit('compliance_frameworks', 1)
def handle_hipaa_compliance():
    """
    Handle HIPAA compliance requirements.
    
    Available for Pro and Enterprise tiers.
    
    Request:
        - action: Action being performed
        - phi_data: Whether PHI (Protected Health Information) is involved
    
    Response:
        - result: HIPAA compliance result
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get request data
        data = request.get_json()
        if not data or 'action' not in data:
            return jsonify({'error': 'action is required'}), 400
        
        action = data['action']
        phi_data = data.get('phi_data', False)
        
        # Handle HIPAA compliance
        manager = ComplianceManager()
        result = manager.handle_hipaa_compliance(user.id, action, phi_data)
        
        if result['success']:
            return jsonify({
                'success': True,
                'action': result['action'],
                'user_id': result['user_id'],
                'phi_data': result['phi_data'],
                'compliance_event_id': result['compliance_event_id'],
                'controls_applied': result['controls_applied']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Handle HIPAA compliance endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@security.route('/compliance/soc2/audit', methods=['POST'])
@api_key_required
@require_tier('enterprise')  # Only enterprise users can handle SOC2 audits
def handle_soc2_audit():
    """
    Handle SOC2 audit requirements.
    
    Available for Enterprise tier only.
    
    Request:
        - audit_type: Type of SOC2 audit ('type1', 'type2', 'continuous')
        - period_start: Start date of audit period (ISO format, optional)
        - period_end: End date of audit period (ISO format, optional)
        - auditor_name: Name of the auditor (optional)
    
    Response:
        - result: SOC2 audit result with comprehensive report
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get request data
        data = request.get_json()
        if not data or 'audit_type' not in data:
            return jsonify({'error': 'audit_type is required'}), 400
        
        audit_type = data['audit_type']
        period_start = None
        period_end = None
        auditor_name = data.get('auditor_name')
        
        if 'period_start' in data:
            period_start = datetime.fromisoformat(data['period_start'].replace('Z', '+00:00'))
        if 'period_end' in data:
            period_end = datetime.fromisoformat(data['period_end'].replace('Z', '+00:00'))
        
        # Handle SOC2 audit
        manager = ComplianceManager()
        result = manager.handle_soc2_audit(
            audit_type=audit_type,
            auditor_id=user.id,
            period_start=period_start,
            period_end=period_end,
            auditor_name=auditor_name
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Handle SOC2 audit endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@security.route('/compliance/soc2/controls', methods=['POST'])
@api_key_required
@require_tier('enterprise')
def create_soc2_control():
    """Create a new SOC2 control."""
    try:
        user = g.current_user
        data = request.get_json()
        
        required_fields = ['control_id', 'control_name', 'trust_service_criteria']
        if not all(field in data for field in required_fields):
            return jsonify({'error': f'Missing required fields: {required_fields}'}), 400
        
        manager = ComplianceManager()
        result = manager.create_soc2_control(
            control_id=data['control_id'],
            control_name=data['control_name'],
            trust_service_criteria=data['trust_service_criteria'],
            description=data.get('description'),
            control_type=data.get('control_type', 'preventive'),
            frequency=data.get('frequency', 'continuous')
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Create SOC2 control error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@security.route('/compliance/soc2/controls/<int:control_id>/test', methods=['POST'])
@api_key_required
@require_tier('enterprise')
def test_soc2_control(control_id):
    """Test a SOC2 control."""
    try:
        user = g.current_user
        data = request.get_json() or {}
        
        manager = ComplianceManager()
        result = manager.test_soc2_control(
            control_id=control_id,
            tested_by=user.id,
            test_type=data.get('test_type', 'operating_effectiveness'),
            test_method=data.get('test_method', 'inquiry'),
            test_procedures=data.get('test_procedures'),
            findings=data.get('findings')
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Test SOC2 control error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@security.route('/compliance/soc2/controls/<int:control_id>/evidence', methods=['POST'])
@api_key_required
@require_tier('enterprise')
def collect_soc2_evidence(control_id):
    """Collect evidence for a SOC2 control."""
    try:
        user = g.current_user
        data = request.get_json()
        
        required_fields = ['evidence_type', 'evidence_name']
        if not all(field in data for field in required_fields):
            return jsonify({'error': f'Missing required fields: {required_fields}'}), 400
        
        manager = ComplianceManager()
        result = manager.collect_soc2_evidence(
            control_id=control_id,
            evidence_type=data['evidence_type'],
            evidence_name=data['evidence_name'],
            collected_by=user.id,
            evidence_path=data.get('evidence_path'),
            evidence_data=data.get('evidence_data'),
            description=data.get('description')
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Collect SOC2 evidence error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@security.route('/compliance/soc2/incidents', methods=['POST'])
@api_key_required
@require_tier('enterprise')
def report_soc2_incident():
    """Report a SOC2 security incident."""
    try:
        user = g.current_user
        data = request.get_json()
        
        required_fields = ['incident_type', 'title', 'description']
        if not all(field in data for field in required_fields):
            return jsonify({'error': f'Missing required fields: {required_fields}'}), 400
        
        manager = ComplianceManager()
        result = manager.report_soc2_incident(
            incident_type=data['incident_type'],
            title=data['title'],
            description=data['description'],
            reported_by=user.id,
            severity=data.get('severity', 'medium')
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Report SOC2 incident error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@security.route('/compliance/soc2/access-reviews', methods=['POST'])
@api_key_required
@require_tier('enterprise')
def conduct_access_review():
    """Conduct a SOC2 access review."""
    try:
        user = g.current_user
        data = request.get_json() or {}
        
        period_start = None
        period_end = None
        if 'period_start' in data:
            period_start = datetime.fromisoformat(data['period_start'].replace('Z', '+00:00'))
        if 'period_end' in data:
            period_end = datetime.fromisoformat(data['period_end'].replace('Z', '+00:00'))
        
        manager = ComplianceManager()
        result = manager.conduct_access_review(
            reviewed_by=user.id,
            review_type=data.get('review_type', 'quarterly'),
            period_start=period_start,
            period_end=period_end
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Conduct access review error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@security.route('/compliance/soc2/dashboard', methods=['GET'])
@api_key_required
@require_tier('enterprise')
def get_soc2_dashboard():
    """Get comprehensive SOC2 compliance dashboard."""
    try:
        manager = ComplianceManager()
        result = manager.get_soc2_dashboard()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Get SOC2 dashboard error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==============================================================================
# ERROR HANDLERS
# ==============================================================================

@security.errorhandler(404)
def not_found(e):
    """Handle not found errors."""
    return jsonify({
        'error': 'Resource not found',
        'message': 'The requested security resource could not be found'
    }), 404

@security.errorhandler(403)
def forbidden(e):
    """Handle forbidden errors."""
    return jsonify({
        'error': 'Access forbidden',
        'message': 'You do not have permission to access this security resource'
    }), 403

