# ==============================================================================
# app/security/audit_logger.py
# Advanced Audit Logging System - The Compliance Trail
# ==============================================================================
"""
This module provides comprehensive audit logging for CLARITY.
Tracks all user actions, system events, and security events for compliance.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from flask import request, current_app
from sqlalchemy import desc, and_, or_
from app.models import AuditLog, User, ComplianceEvent
from app import db

logger = logging.getLogger(__name__)

# ==============================================================================
# AUDIT LOGGER
# ==============================================================================

class AuditLogger:
    """
    Comprehensive audit logging system for compliance and security.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def log_user_action(self, user_id: int, action: str, resource_type: str = None, 
                       resource_id: str = None, details: Dict[str, Any] = None,
                       status: str = 'success', ip_address: str = None,
                       user_agent: str = None) -> Dict[str, Any]:
        """
        Log a user action for audit purposes.
        
        Args:
            user_id: ID of the user performing the action
            action: Action being performed (e.g., 'login', 'upload', 'download')
            resource_type: Type of resource being accessed (e.g., 'document', 'workspace')
            resource_id: ID of the resource being accessed
            details: Additional details about the action
            status: Status of the action ('success', 'failure', 'warning')
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Dict with logging result
        """
        try:
            # Get request context if available
            if not ip_address and hasattr(request, 'remote_addr'):
                ip_address = request.remote_addr
            
            if not user_agent and hasattr(request, 'user_agent'):
                user_agent = str(request.user_agent)
            
            # Create audit log entry
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=json.dumps(details) if details else None,
                ip_address=ip_address,
                user_agent=user_agent,
                status=status
            )
            
            db.session.add(audit_log)
            db.session.commit()
            
            self.logger.info(f"Audit log created: User {user_id} performed {action} on {resource_type} {resource_id}")
            
            return {
                'success': True,
                'audit_id': audit_log.id,
                'timestamp': audit_log.timestamp.isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to log user action: {e}")
            return {'success': False, 'error': str(e)}
    
    def log_system_event(self, event_type: str, details: Dict[str, Any] = None,
                        severity: str = 'info', component: str = None) -> Dict[str, Any]:
        """
        Log a system event for monitoring and debugging.
        
        Args:
            event_type: Type of system event
            details: Additional details about the event
            severity: Severity level ('info', 'warning', 'error', 'critical')
            component: System component generating the event
            
        Returns:
            Dict with logging result
        """
        try:
            # Create audit log entry (system events have no user_id)
            audit_log = AuditLog(
                user_id=None,  # System event
                action=f'system_{event_type}',
                resource_type='system',
                resource_id=component,
                details=json.dumps(details) if details else None,
                ip_address=None,
                user_agent=None,
                status=severity
            )
            
            db.session.add(audit_log)
            db.session.commit()
            
            self.logger.info(f"System event logged: {event_type} in {component}")
            
            return {
                'success': True,
                'audit_id': audit_log.id,
                'timestamp': audit_log.timestamp.isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to log system event: {e}")
            return {'success': False, 'error': str(e)}
    
    def log_security_event(self, event_type: str, user_id: int = None,
                          details: Dict[str, Any] = None, severity: str = 'warning',
                          ip_address: str = None) -> Dict[str, Any]:
        """
        Log a security-related event.
        
        Args:
            event_type: Type of security event
            user_id: ID of the user involved (if any)
            details: Additional details about the event
            severity: Severity level ('low', 'medium', 'high', 'critical')
            ip_address: IP address involved
            
        Returns:
            Dict with logging result
        """
        try:
            # Get request context if available
            if not ip_address and hasattr(request, 'remote_addr'):
                ip_address = request.remote_addr
            
            # Create audit log entry
            audit_log = AuditLog(
                user_id=user_id,
                action=f'security_{event_type}',
                resource_type='security',
                resource_id=None,
                details=json.dumps(details) if details else None,
                ip_address=ip_address,
                user_agent=str(request.user_agent) if hasattr(request, 'user_agent') else None,
                status=severity
            )
            
            db.session.add(audit_log)
            
            # Also create compliance event for security incidents
            if severity in ['high', 'critical']:
                compliance_event = ComplianceEvent(
                    event_type=f'security_{event_type}',
                    user_id=user_id,
                    data_classification='security_incident',
                    details=json.dumps(details) if details else None,
                    handled=False
                )
                db.session.add(compliance_event)
            
            db.session.commit()
            
            self.logger.warning(f"Security event logged: {event_type} for user {user_id} with severity {severity}")
            
            return {
                'success': True,
                'audit_id': audit_log.id,
                'timestamp': audit_log.timestamp.isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to log security event: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_audit_trail(self, user_id: int = None, action: str = None,
                       resource_type: str = None, start_date: datetime = None,
                       end_date: datetime = None, limit: int = 100) -> Dict[str, Any]:
        """
        Retrieve audit trail based on filters.
        
        Args:
            user_id: Filter by user ID
            action: Filter by action type
            resource_type: Filter by resource type
            start_date: Start date for filtering
            end_date: End date for filtering
            limit: Maximum number of records to return
            
        Returns:
            Dict with audit trail data
        """
        try:
            # Build query
            query = AuditLog.query
            
            if user_id:
                query = query.filter(AuditLog.user_id == user_id)
            
            if action:
                query = query.filter(AuditLog.action == action)
            
            if resource_type:
                query = query.filter(AuditLog.resource_type == resource_type)
            
            if start_date:
                query = query.filter(AuditLog.timestamp >= start_date)
            
            if end_date:
                query = query.filter(AuditLog.timestamp <= end_date)
            
            # Order by timestamp (newest first) and limit
            query = query.order_by(desc(AuditLog.timestamp)).limit(limit)
            
            # Execute query
            audit_logs = query.all()
            
            # Format results
            trail = []
            for log in audit_logs:
                trail.append({
                    'id': log.id,
                    'user_id': log.user_id,
                    'action': log.action,
                    'resource_type': log.resource_type,
                    'resource_id': log.resource_id,
                    'details': json.loads(log.details) if log.details else None,
                    'ip_address': log.ip_address,
                    'user_agent': log.user_agent,
                    'timestamp': log.timestamp.isoformat(),
                    'status': log.status
                })
            
            return {
                'success': True,
                'audit_trail': trail,
                'total_records': len(trail),
                'filters': {
                    'user_id': user_id,
                    'action': action,
                    'resource_type': resource_type,
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get audit trail: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_user_activity_summary(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Get activity summary for a user.
        
        Args:
            user_id: ID of the user
            days: Number of days to analyze
            
        Returns:
            Dict with activity summary
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get user's audit logs
            logs = AuditLog.query.filter(
                and_(
                    AuditLog.user_id == user_id,
                    AuditLog.timestamp >= start_date
                )
            ).all()
            
            # Analyze activity
            action_counts = {}
            resource_counts = {}
            status_counts = {}
            daily_activity = {}
            
            for log in logs:
                # Count actions
                action_counts[log.action] = action_counts.get(log.action, 0) + 1
                
                # Count resources
                if log.resource_type:
                    resource_counts[log.resource_type] = resource_counts.get(log.resource_type, 0) + 1
                
                # Count statuses
                status_counts[log.status] = status_counts.get(log.status, 0) + 1
                
                # Daily activity
                date_str = log.timestamp.date().isoformat()
                daily_activity[date_str] = daily_activity.get(date_str, 0) + 1
            
            # Get most active day
            most_active_day = max(daily_activity.items(), key=lambda x: x[1]) if daily_activity else None
            
            return {
                'success': True,
                'user_id': user_id,
                'period_days': days,
                'summary': {
                    'total_actions': len(logs),
                    'action_breakdown': action_counts,
                    'resource_breakdown': resource_counts,
                    'status_breakdown': status_counts,
                    'daily_activity': daily_activity,
                    'most_active_day': most_active_day,
                    'average_actions_per_day': len(logs) / days if days > 0 else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get user activity summary: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_security_events(self, days: int = 30, severity: str = None) -> Dict[str, Any]:
        """
        Get security events for monitoring.
        
        Args:
            days: Number of days to analyze
            severity: Filter by severity level
            
        Returns:
            Dict with security events
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Build query for security events
            query = AuditLog.query.filter(
                and_(
                    AuditLog.action.like('security_%'),
                    AuditLog.timestamp >= start_date
                )
            )
            
            if severity:
                query = query.filter(AuditLog.status == severity)
            
            query = query.order_by(desc(AuditLog.timestamp))
            
            security_logs = query.all()
            
            # Format results
            events = []
            for log in security_logs:
                events.append({
                    'id': log.id,
                    'event_type': log.action.replace('security_', ''),
                    'user_id': log.user_id,
                    'severity': log.status,
                    'details': json.loads(log.details) if log.details else None,
                    'ip_address': log.ip_address,
                    'timestamp': log.timestamp.isoformat()
                })
            
            # Calculate statistics
            severity_counts = {}
            for log in security_logs:
                severity_counts[log.status] = severity_counts.get(log.status, 0) + 1
            
            return {
                'success': True,
                'period_days': days,
                'events': events,
                'statistics': {
                    'total_events': len(events),
                    'severity_breakdown': severity_counts,
                    'events_per_day': len(events) / days if days > 0 else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get security events: {e}")
            return {'success': False, 'error': str(e)}
    
    def cleanup_old_logs(self, retention_days: int = 2555) -> Dict[str, Any]:
        """
        Clean up old audit logs based on retention policy.
        
        Args:
            retention_days: Number of days to retain logs
            
        Returns:
            Dict with cleanup result
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            # Count logs to be deleted
            old_logs_count = AuditLog.query.filter(AuditLog.timestamp < cutoff_date).count()
            
            # Delete old logs
            deleted_count = AuditLog.query.filter(AuditLog.timestamp < cutoff_date).delete()
            
            db.session.commit()
            
            self.logger.info(f"Cleaned up {deleted_count} old audit logs (older than {retention_days} days)")
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'retention_days': retention_days,
                'cutoff_date': cutoff_date.isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to cleanup old logs: {e}")
            return {'success': False, 'error': str(e)}

# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

def log_user_action(user_id: int, action: str, resource_type: str = None, 
                   resource_id: str = None, details: Dict[str, Any] = None,
                   status: str = 'success') -> Dict[str, Any]:
    """Log a user action."""
    logger = AuditLogger()
    return logger.log_user_action(user_id, action, resource_type, resource_id, details, status)

def log_system_event(event_type: str, details: Dict[str, Any] = None,
                    severity: str = 'info', component: str = None) -> Dict[str, Any]:
    """Log a system event."""
    logger = AuditLogger()
    return logger.log_system_event(event_type, details, severity, component)

def log_security_event(event_type: str, user_id: int = None,
                      details: Dict[str, Any] = None, severity: str = 'warning') -> Dict[str, Any]:
    """Log a security event."""
    logger = AuditLogger()
    return logger.log_security_event(event_type, user_id, details, severity)

def get_audit_trail(user_id: int = None, action: str = None,
                   resource_type: str = None, start_date: datetime = None,
                   end_date: datetime = None, limit: int = 100) -> Dict[str, Any]:
    """Get audit trail."""
    logger = AuditLogger()
    return logger.get_audit_trail(user_id, action, resource_type, start_date, end_date, limit)

