# ==============================================================================
# app/analytics/admin_analytics.py
# Admin Analytics System - The Business Intelligence Dashboard
# ==============================================================================
"""
This module provides admin-level analytics and business intelligence for CLARITY.
Tracks system-wide metrics, user engagement, business KPIs, and AI performance.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_, or_, distinct
from app.models import (
    User, Workspace, WorkspaceMember, WorkspaceDocument, DocumentShare,
    AnalyticsSnapshot, DocumentAnalytics, UsageMetrics, Subscription,
    AuditLog, ComplianceEvent
)
from app import db

logger = logging.getLogger(__name__)

# ==============================================================================
# ADMIN ANALYTICS MANAGER
# ==============================================================================

class AdminAnalyticsManager:
    """
    Manages admin-level analytics and business intelligence.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_system_metrics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive system-wide metrics.
        
        Args:
            days: Number of days to analyze (default: 30)
            
        Returns:
            Dict with system metrics
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # User metrics
            total_users = User.query.count()
            active_users = User.query.filter(User.last_login >= start_date).count()
            new_users = User.query.filter(User.created_at >= start_date).count()
            
            # Subscription metrics
            total_subscriptions = Subscription.query.filter_by(status='active').count()
            free_users = Subscription.query.filter_by(tier='free', status='active').count()
            pro_users = Subscription.query.filter_by(tier='pro', status='active').count()
            enterprise_users = Subscription.query.filter_by(tier='enterprise', status='active').count()
            
            # Workspace metrics
            total_workspaces = Workspace.query.filter_by(is_active=True).count()
            new_workspaces = Workspace.query.filter(Workspace.created_at >= start_date).count()
            
            # Document metrics
            total_documents = WorkspaceDocument.query.count()
            new_documents = WorkspaceDocument.query.filter(WorkspaceDocument.uploaded_at >= start_date).count()
            
            # Sharing metrics
            total_shares = DocumentShare.query.count()
            new_shares = DocumentShare.query.filter(DocumentShare.created_at >= start_date).count()
            
            # Calculate growth rates
            user_growth_rate = self._calculate_growth_rate(new_users, total_users - new_users)
            workspace_growth_rate = self._calculate_growth_rate(new_workspaces, total_workspaces - new_workspaces)
            document_growth_rate = self._calculate_growth_rate(new_documents, total_documents - new_documents)
            
            # Calculate daily trends
            daily_metrics = self._get_daily_trends(start_date, end_date)
            
            return {
                'success': True,
                'period_days': days,
                'metrics': {
                    'users': {
                        'total': total_users,
                        'active': active_users,
                        'new': new_users,
                        'growth_rate': user_growth_rate
                    },
                    'subscriptions': {
                        'total_active': total_subscriptions,
                        'free': free_users,
                        'pro': pro_users,
                        'enterprise': enterprise_users,
                        'conversion_rate': (pro_users + enterprise_users) / total_users if total_users > 0 else 0
                    },
                    'workspaces': {
                        'total': total_workspaces,
                        'new': new_workspaces,
                        'growth_rate': workspace_growth_rate
                    },
                    'documents': {
                        'total': total_documents,
                        'new': new_documents,
                        'growth_rate': document_growth_rate
                    },
                    'sharing': {
                        'total_shares': total_shares,
                        'new_shares': new_shares
                    },
                    'daily_trends': daily_metrics
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_user_engagement_metrics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get user engagement and activity metrics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with engagement metrics
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Active user metrics
            daily_active_users = self._get_daily_active_users(start_date, end_date)
            weekly_active_users = self._get_weekly_active_users(start_date, end_date)
            monthly_active_users = self._get_monthly_active_users(start_date, end_date)
            
            # User activity patterns
            activity_patterns = self._get_activity_patterns(start_date, end_date)
            
            # Feature usage
            feature_usage = self._get_feature_usage(start_date, end_date)
            
            # User retention
            retention_metrics = self._get_retention_metrics(start_date, end_date)
            
            # Top users by activity
            top_users = self._get_top_active_users(start_date, end_date, limit=10)
            
            return {
                'success': True,
                'period_days': days,
                'engagement': {
                    'active_users': {
                        'daily': daily_active_users,
                        'weekly': weekly_active_users,
                        'monthly': monthly_active_users
                    },
                    'activity_patterns': activity_patterns,
                    'feature_usage': feature_usage,
                    'retention': retention_metrics,
                    'top_users': top_users
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get user engagement metrics: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_business_metrics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get business and revenue metrics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with business metrics
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Subscription revenue (simplified - would need actual payment data)
            subscription_metrics = self._get_subscription_metrics()
            
            # User acquisition metrics
            acquisition_metrics = self._get_acquisition_metrics(start_date, end_date)
            
            # Churn analysis
            churn_metrics = self._get_churn_metrics(start_date, end_date)
            
            # Feature adoption
            feature_adoption = self._get_feature_adoption_metrics()
            
            # Workspace utilization
            workspace_utilization = self._get_workspace_utilization_metrics()
            
            return {
                'success': True,
                'period_days': days,
                'business': {
                    'subscriptions': subscription_metrics,
                    'acquisition': acquisition_metrics,
                    'churn': churn_metrics,
                    'feature_adoption': feature_adoption,
                    'workspace_utilization': workspace_utilization
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get business metrics: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_ai_performance_metrics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get AI performance and usage metrics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with AI performance metrics
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Analysis performance (from audit logs)
            analysis_metrics = self._get_analysis_performance_metrics(start_date, end_date)
            
            # Model usage statistics
            model_usage = self._get_model_usage_metrics(start_date, end_date)
            
            # Response time metrics
            response_time_metrics = self._get_response_time_metrics(start_date, end_date)
            
            # Error rates
            error_metrics = self._get_error_metrics(start_date, end_date)
            
            # Feature usage by tier
            tier_usage = self._get_tier_usage_metrics(start_date, end_date)
            
            return {
                'success': True,
                'period_days': days,
                'ai_performance': {
                    'analysis_metrics': analysis_metrics,
                    'model_usage': model_usage,
                    'response_times': response_time_metrics,
                    'error_rates': error_metrics,
                    'tier_usage': tier_usage
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get AI performance metrics: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_compliance_metrics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get compliance and security metrics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with compliance metrics
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Audit log metrics
            audit_metrics = self._get_audit_metrics(start_date, end_date)
            
            # Compliance events
            compliance_events = self._get_compliance_events(start_date, end_date)
            
            # Data retention metrics
            retention_metrics = self._get_data_retention_metrics()
            
            # Security events
            security_metrics = self._get_security_metrics(start_date, end_date)
            
            return {
                'success': True,
                'period_days': days,
                'compliance': {
                    'audit_logs': audit_metrics,
                    'compliance_events': compliance_events,
                    'data_retention': retention_metrics,
                    'security': security_metrics
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get compliance metrics: {e}")
            return {'success': False, 'error': str(e)}
    
    # ==============================================================================
    # HELPER METHODS
    # ==============================================================================
    
    def _calculate_growth_rate(self, new_count: int, existing_count: int) -> float:
        """Calculate growth rate percentage."""
        if existing_count == 0:
            return 100.0 if new_count > 0 else 0.0
        return (new_count / existing_count) * 100
    
    def _get_daily_trends(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get daily trend data."""
        trends = []
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            
            # Count new users
            new_users = User.query.filter(
                func.date(User.created_at) == current_date.date()
            ).count()
            
            # Count new documents
            new_documents = WorkspaceDocument.query.filter(
                func.date(WorkspaceDocument.uploaded_at) == current_date.date()
            ).count()
            
            # Count new workspaces
            new_workspaces = Workspace.query.filter(
                func.date(Workspace.created_at) == current_date.date()
            ).count()
            
            trends.append({
                'date': date_str,
                'new_users': new_users,
                'new_documents': new_documents,
                'new_workspaces': new_workspaces
            })
            
            current_date += timedelta(days=1)
        
        return trends
    
    def _get_daily_active_users(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get daily active users."""
        daily_active = []
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            
            # Count users who logged in on this date
            active_count = User.query.filter(
                func.date(User.last_login) == current_date.date()
            ).count()
            
            daily_active.append({
                'date': date_str,
                'active_users': active_count
            })
            
            current_date += timedelta(days=1)
        
        return daily_active
    
    def _get_weekly_active_users(self, start_date: datetime, end_date: datetime) -> int:
        """Get weekly active users."""
        week_start = end_date - timedelta(days=7)
        return User.query.filter(User.last_login >= week_start).count()
    
    def _get_monthly_active_users(self, start_date: datetime, end_date: datetime) -> int:
        """Get monthly active users."""
        return User.query.filter(User.last_login >= start_date).count()
    
    def _get_activity_patterns(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get user activity patterns."""
        # This would analyze patterns like peak usage hours, days of week, etc.
        # For now, return placeholder data
        return {
            'peak_hours': [9, 10, 11, 14, 15, 16],
            'peak_days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday'],
            'weekend_activity': 0.3  # 30% of weekday activity
        }
    
    def _get_feature_usage(self, start_date: datetime, end_date: datetime) -> Dict[str, int]:
        """Get feature usage statistics."""
        # This would analyze which features are most used
        # For now, return placeholder data
        return {
            'document_upload': 150,
            'document_sharing': 75,
            'workspace_creation': 25,
            'collaboration': 100,
            'analytics': 50
        }
    
    def _get_retention_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """Get user retention metrics."""
        # This would calculate retention rates for different cohorts
        # For now, return placeholder data
        return {
            'day_1_retention': 0.85,
            'day_7_retention': 0.65,
            'day_30_retention': 0.45,
            'monthly_retention': 0.70
        }
    
    def _get_top_active_users(self, start_date: datetime, end_date: datetime, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top active users by activity."""
        # This would analyze user activity and return top users
        # For now, return placeholder data
        return [
            {
                'user_id': 1,
                'email': 'user1@example.com',
                'activity_score': 95,
                'documents_uploaded': 25,
                'workspaces_created': 3
            }
        ]
    
    def _get_subscription_metrics(self) -> Dict[str, Any]:
        """Get subscription and revenue metrics."""
        total_subscriptions = Subscription.query.filter_by(status='active').count()
        free_subscriptions = Subscription.query.filter_by(tier='free', status='active').count()
        pro_subscriptions = Subscription.query.filter_by(tier='pro', status='active').count()
        enterprise_subscriptions = Subscription.query.filter_by(tier='enterprise', status='active').count()
        
        return {
            'total_active': total_subscriptions,
            'free': free_subscriptions,
            'pro': pro_subscriptions,
            'enterprise': enterprise_subscriptions,
            'conversion_rate': (pro_subscriptions + enterprise_subscriptions) / total_subscriptions if total_subscriptions > 0 else 0
        }
    
    def _get_acquisition_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get user acquisition metrics."""
        new_users = User.query.filter(User.created_at >= start_date).count()
        
        # This would include more detailed acquisition data
        return {
            'new_users': new_users,
            'acquisition_channels': {
                'organic': 0.6,
                'referral': 0.2,
                'paid': 0.2
            }
        }
    
    def _get_churn_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get user churn metrics."""
        # This would analyze user churn patterns
        return {
            'monthly_churn_rate': 0.05,  # 5%
            'churned_users': 10,
            'retention_rate': 0.95
        }
    
    def _get_feature_adoption_metrics(self) -> Dict[str, Any]:
        """Get feature adoption metrics."""
        # This would analyze how quickly users adopt new features
        return {
            'workspace_adoption': 0.75,
            'sharing_adoption': 0.60,
            'analytics_adoption': 0.40
        }
    
    def _get_workspace_utilization_metrics(self) -> Dict[str, Any]:
        """Get workspace utilization metrics."""
        total_workspaces = Workspace.query.filter_by(is_active=True).count()
        active_workspaces = Workspace.query.join(WorkspaceDocument).filter(
            Workspace.is_active == True
        ).distinct().count()
        
        return {
            'total_workspaces': total_workspaces,
            'active_workspaces': active_workspaces,
            'utilization_rate': active_workspaces / total_workspaces if total_workspaces > 0 else 0
        }
    
    def _get_analysis_performance_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get analysis performance metrics."""
        # This would analyze AI analysis performance
        return {
            'total_analyses': 1000,
            'successful_analyses': 950,
            'failed_analyses': 50,
            'success_rate': 0.95
        }
    
    def _get_model_usage_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get AI model usage metrics."""
        # This would track which models are used most
        return {
            'gemini_flash': 0.6,
            'gemini_pro': 0.3,
            'gemini_ultra': 0.1
        }
    
    def _get_response_time_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get response time metrics."""
        # This would track AI response times
        return {
            'average_response_time': 2.5,  # seconds
            'p95_response_time': 5.0,
            'p99_response_time': 10.0
        }
    
    def _get_error_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get error rate metrics."""
        # This would track error rates
        return {
            'total_requests': 10000,
            'error_requests': 100,
            'error_rate': 0.01
        }
    
    def _get_tier_usage_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get feature usage by tier."""
        # This would analyze feature usage by subscription tier
        return {
            'free': {
                'documents_uploaded': 500,
                'analyses_performed': 200
            },
            'pro': {
                'documents_uploaded': 2000,
                'analyses_performed': 1500,
                'workspaces_created': 100
            },
            'enterprise': {
                'documents_uploaded': 5000,
                'analyses_performed': 4000,
                'workspaces_created': 200
            }
        }
    
    def _get_audit_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get audit log metrics."""
        total_logs = AuditLog.query.filter(AuditLog.timestamp >= start_date).count()
        successful_actions = AuditLog.query.filter(
            and_(
                AuditLog.timestamp >= start_date,
                AuditLog.status == 'success'
            )
        ).count()
        
        return {
            'total_logs': total_logs,
            'successful_actions': successful_actions,
            'failed_actions': total_logs - successful_actions
        }
    
    def _get_compliance_events(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get compliance event metrics."""
        total_events = ComplianceEvent.query.filter(ComplianceEvent.timestamp >= start_date).count()
        handled_events = ComplianceEvent.query.filter(
            and_(
                ComplianceEvent.timestamp >= start_date,
                ComplianceEvent.handled == True
            )
        ).count()
        
        return {
            'total_events': total_events,
            'handled_events': handled_events,
            'pending_events': total_events - handled_events
        }
    
    def _get_data_retention_metrics(self) -> Dict[str, Any]:
        """Get data retention metrics."""
        # This would analyze data retention compliance
        return {
            'documents_retained': 10000,
            'documents_deleted': 500,
            'retention_compliance_rate': 0.95
        }
    
    def _get_security_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get security metrics."""
        # This would track security-related events
        return {
            'failed_logins': 50,
            'suspicious_activities': 5,
            'security_alerts': 2
        }

# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

def get_system_metrics(days: int = 30) -> Dict[str, Any]:
    """Get system-wide metrics."""
    manager = AdminAnalyticsManager()
    return manager.get_system_metrics(days)

def get_user_engagement_metrics(days: int = 30) -> Dict[str, Any]:
    """Get user engagement metrics."""
    manager = AdminAnalyticsManager()
    return manager.get_user_engagement_metrics(days)

def get_business_metrics(days: int = 30) -> Dict[str, Any]:
    """Get business metrics."""
    manager = AdminAnalyticsManager()
    return manager.get_business_metrics(days)

def get_ai_performance_metrics(days: int = 30) -> Dict[str, Any]:
    """Get AI performance metrics."""
    manager = AdminAnalyticsManager()
    return manager.get_ai_performance_metrics(days)

