# ==============================================================================
# app/analytics/user_analytics.py
# User Analytics System - The Personal Intelligence Dashboard
# ==============================================================================
"""
This module provides user-specific analytics and insights for CLARITY.
Tracks usage patterns, document trends, and personal performance metrics.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_, or_
from app.models import (
    User, Workspace, WorkspaceMember, WorkspaceDocument, DocumentShare,
    AnalyticsSnapshot, DocumentAnalytics, UsageMetrics, Subscription
)
from app import db

logger = logging.getLogger(__name__)

# ==============================================================================
# USER ANALYTICS MANAGER
# ==============================================================================

class UserAnalyticsManager:
    """
    Manages user-specific analytics and insights.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_user_usage_stats(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive usage statistics for a user.
        
        Args:
            user_id: ID of the user
            days: Number of days to analyze (default: 30)
            
        Returns:
            Dict with usage statistics
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get user info
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Get subscription info
            subscription = Subscription.query.filter_by(user_id=user_id, status='active').first()
            user_tier = subscription.tier if subscription else 'free'
            
            # Calculate document statistics
            total_documents = WorkspaceDocument.query.filter_by(uploaded_by=user_id).count()
            recent_documents = WorkspaceDocument.query.filter(
                and_(
                    WorkspaceDocument.uploaded_by == user_id,
                    WorkspaceDocument.uploaded_at >= start_date
                )
            ).count()
            
            # Calculate workspace statistics
            owned_workspaces = Workspace.query.filter_by(owner_id=user_id, is_active=True).count()
            member_workspaces = WorkspaceMember.query.filter_by(user_id=user_id).count()
            
            # Calculate sharing statistics
            documents_shared = DocumentShare.query.filter_by(shared_by=user_id).count()
            documents_received = DocumentShare.query.filter_by(shared_with=user_id).count()
            
            # Get usage metrics
            usage_metrics = UsageMetrics.query.filter_by(user_id=user_id).all()
            
            # Calculate monthly usage
            current_month = datetime.utcnow().strftime('%Y-%m')
            monthly_usage = {}
            for metric in usage_metrics:
                if metric.period == current_month:
                    monthly_usage[metric.metric_type] = metric.count
            
            # Calculate trend data (last 7 days)
            trend_data = []
            for i in range(7):
                date = end_date - timedelta(days=i)
                date_str = date.strftime('%Y-%m-%d')
                
                # Count documents uploaded on this date
                doc_count = WorkspaceDocument.query.filter(
                    and_(
                        WorkspaceDocument.uploaded_by == user_id,
                        func.date(WorkspaceDocument.uploaded_at) == date.date()
                    )
                ).count()
                
                trend_data.append({
                    'date': date_str,
                    'documents': doc_count
                })
            
            trend_data.reverse()  # Show oldest to newest
            
            return {
                'success': True,
                'user_id': user_id,
                'user_tier': user_tier,
                'period_days': days,
                'statistics': {
                    'documents': {
                        'total': total_documents,
                        'recent': recent_documents,
                        'shared_by_me': documents_shared,
                        'shared_with_me': documents_received
                    },
                    'workspaces': {
                        'owned': owned_workspaces,
                        'member_of': member_workspaces
                    },
                    'monthly_usage': monthly_usage,
                    'trend_data': trend_data
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get user usage stats: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_user_document_analytics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Get detailed document analytics for a user.
        
        Args:
            user_id: ID of the user
            days: Number of days to analyze
            
        Returns:
            Dict with document analytics
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get user's documents
            documents = WorkspaceDocument.query.filter_by(uploaded_by=user_id).all()
            
            if not documents:
                return {
                    'success': True,
                    'user_id': user_id,
                    'analytics': {
                        'total_documents': 0,
                        'document_types': {},
                        'workspace_distribution': {},
                        'recent_activity': [],
                        'most_shared': [],
                        'file_size_stats': {
                            'total_size': 0,
                            'average_size': 0,
                            'largest_document': None
                        }
                    }
                }
            
            # Analyze document types
            document_types = {}
            workspace_distribution = {}
            file_sizes = []
            largest_document = None
            max_size = 0
            
            for doc in documents:
                # Document types
                file_type = doc.file_type or 'unknown'
                document_types[file_type] = document_types.get(file_type, 0) + 1
                
                # Workspace distribution
                workspace = Workspace.query.get(doc.workspace_id)
                workspace_name = workspace.name if workspace else 'Unknown'
                workspace_distribution[workspace_name] = workspace_distribution.get(workspace_name, 0) + 1
                
                # File sizes
                if doc.file_size:
                    file_sizes.append(doc.file_size)
                    if doc.file_size > max_size:
                        max_size = doc.file_size
                        largest_document = {
                            'id': doc.id,
                            'name': doc.document_name,
                            'size': doc.file_size,
                            'workspace': workspace_name
                        }
            
            # Calculate file size statistics
            total_size = sum(file_sizes)
            average_size = total_size / len(file_sizes) if file_sizes else 0
            
            # Get recent activity
            recent_documents = WorkspaceDocument.query.filter(
                and_(
                    WorkspaceDocument.uploaded_by == user_id,
                    WorkspaceDocument.uploaded_at >= start_date
                )
            ).order_by(desc(WorkspaceDocument.uploaded_at)).limit(10).all()
            
            recent_activity = []
            for doc in recent_documents:
                workspace = Workspace.query.get(doc.workspace_id)
                recent_activity.append({
                    'id': doc.id,
                    'name': doc.document_name,
                    'workspace': workspace.name if workspace else 'Unknown',
                    'uploaded_at': doc.uploaded_at.isoformat(),
                    'file_size': doc.file_size
                })
            
            # Get most shared documents
            shared_docs = db.session.query(
                DocumentShare.document_id,
                func.count(DocumentShare.id).label('share_count')
            ).filter_by(shared_by=user_id).group_by(DocumentShare.document_id).order_by(
                desc('share_count')
            ).limit(5).all()
            
            most_shared = []
            for doc_id, share_count in shared_docs:
                doc = WorkspaceDocument.query.get(doc_id)
                if doc:
                    workspace = Workspace.query.get(doc.workspace_id)
                    most_shared.append({
                        'id': doc.id,
                        'name': doc.document_name,
                        'workspace': workspace.name if workspace else 'Unknown',
                        'share_count': share_count
                    })
            
            return {
                'success': True,
                'user_id': user_id,
                'analytics': {
                    'total_documents': len(documents),
                    'document_types': document_types,
                    'workspace_distribution': workspace_distribution,
                    'recent_activity': recent_activity,
                    'most_shared': most_shared,
                    'file_size_stats': {
                        'total_size': total_size,
                        'average_size': average_size,
                        'largest_document': largest_document
                    }
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get user document analytics: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_user_workspace_analytics(self, user_id: int) -> Dict[str, Any]:
        """
        Get workspace analytics for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dict with workspace analytics
        """
        try:
            # Get user's workspaces
            memberships = WorkspaceMember.query.filter_by(user_id=user_id).all()
            
            if not memberships:
                return {
                    'success': True,
                    'user_id': user_id,
                    'analytics': {
                        'total_workspaces': 0,
                        'owned_workspaces': 0,
                        'workspace_roles': {},
                        'workspace_details': []
                    }
                }
            
            # Analyze workspace data
            owned_count = 0
            workspace_roles = {}
            workspace_details = []
            
            for membership in memberships:
                workspace = Workspace.query.get(membership.workspace_id)
                if not workspace or not workspace.is_active:
                    continue
                
                # Count owned workspaces
                if membership.role == 'owner':
                    owned_count += 1
                
                # Count roles
                role = membership.role
                workspace_roles[role] = workspace_roles.get(role, 0) + 1
                
                # Get workspace details
                member_count = WorkspaceMember.query.filter_by(workspace_id=workspace.id).count()
                document_count = WorkspaceDocument.query.filter_by(workspace_id=workspace.id).count()
                
                # Get recent activity (last 7 days)
                recent_docs = WorkspaceDocument.query.filter(
                    and_(
                        WorkspaceDocument.workspace_id == workspace.id,
                        WorkspaceDocument.uploaded_at >= datetime.utcnow() - timedelta(days=7)
                    )
                ).count()
                
                workspace_details.append({
                    'id': workspace.id,
                    'name': workspace.name,
                    'type': workspace.workspace_type,
                    'role': membership.role,
                    'member_count': member_count,
                    'document_count': document_count,
                    'recent_activity': recent_docs,
                    'created_at': workspace.created_at.isoformat()
                })
            
            return {
                'success': True,
                'user_id': user_id,
                'analytics': {
                    'total_workspaces': len(workspace_details),
                    'owned_workspaces': owned_count,
                    'workspace_roles': workspace_roles,
                    'workspace_details': workspace_details
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get user workspace analytics: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_user_performance_insights(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Get performance insights and recommendations for a user.
        
        Args:
            user_id: ID of the user
            days: Number of days to analyze
            
        Returns:
            Dict with performance insights
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get user info
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Get subscription info
            subscription = Subscription.query.filter_by(user_id=user_id, status='active').first()
            user_tier = subscription.tier if subscription else 'free'
            
            # Calculate productivity metrics
            total_documents = WorkspaceDocument.query.filter_by(uploaded_by=user_id).count()
            recent_documents = WorkspaceDocument.query.filter(
                and_(
                    WorkspaceDocument.uploaded_by == user_id,
                    WorkspaceDocument.uploaded_at >= start_date
                )
            ).count()
            
            # Calculate collaboration metrics
            documents_shared = DocumentShare.query.filter_by(shared_by=user_id).count()
            documents_received = DocumentShare.query.filter_by(shared_with=user_id).count()
            
            # Calculate workspace engagement
            workspace_count = WorkspaceMember.query.filter_by(user_id=user_id).count()
            
            # Generate insights
            insights = []
            recommendations = []
            
            # Document upload insights
            if recent_documents > 0:
                avg_docs_per_day = recent_documents / days
                insights.append({
                    'type': 'productivity',
                    'title': 'Document Upload Activity',
                    'description': f'You\'ve uploaded {recent_documents} documents in the last {days} days',
                    'value': f'{avg_docs_per_day:.1f} documents per day',
                    'trend': 'positive' if avg_docs_per_day > 0.5 else 'neutral'
                })
            else:
                recommendations.append({
                    'type': 'productivity',
                    'title': 'Start Documenting',
                    'description': 'Upload your first document to begin building your knowledge base',
                    'action': 'Upload a document'
                })
            
            # Collaboration insights
            if documents_shared > 0:
                insights.append({
                    'type': 'collaboration',
                    'title': 'Document Sharing',
                    'description': f'You\'ve shared {documents_shared} documents with others',
                    'value': f'{documents_shared} shared documents',
                    'trend': 'positive'
                })
            else:
                recommendations.append({
                    'type': 'collaboration',
                    'title': 'Share Knowledge',
                    'description': 'Share documents with team members to improve collaboration',
                    'action': 'Share a document'
                })
            
            # Workspace engagement insights
            if workspace_count > 0:
                insights.append({
                    'type': 'engagement',
                    'title': 'Workspace Participation',
                    'description': f'You\'re a member of {workspace_count} workspaces',
                    'value': f'{workspace_count} workspaces',
                    'trend': 'positive'
                })
            else:
                recommendations.append({
                    'type': 'engagement',
                    'title': 'Join Workspaces',
                    'description': 'Join or create workspaces to collaborate with others',
                    'action': 'Create or join a workspace'
                })
            
            # Tier-specific recommendations
            if user_tier == 'free':
                recommendations.append({
                    'type': 'upgrade',
                    'title': 'Unlock Advanced Features',
                    'description': 'Upgrade to Pro to access team workspaces, advanced analytics, and more',
                    'action': 'Upgrade to Pro'
                })
            
            # Calculate overall score
            score_components = []
            if recent_documents > 0:
                score_components.append(30)  # Document activity
            if documents_shared > 0:
                score_components.append(25)  # Collaboration
            if workspace_count > 0:
                score_components.append(25)  # Workspace engagement
            if user_tier != 'free':
                score_components.append(20)  # Tier bonus
            
            overall_score = sum(score_components) if score_components else 0
            
            return {
                'success': True,
                'user_id': user_id,
                'user_tier': user_tier,
                'period_days': days,
                'performance': {
                    'overall_score': overall_score,
                    'max_score': 100,
                    'insights': insights,
                    'recommendations': recommendations,
                    'metrics': {
                        'documents_uploaded': recent_documents,
                        'documents_shared': documents_shared,
                        'documents_received': documents_received,
                        'workspaces_joined': workspace_count
                    }
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get user performance insights: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_analytics_snapshot(self, user_id: int, date: datetime = None) -> Dict[str, Any]:
        """
        Create a daily analytics snapshot for a user.
        
        Args:
            user_id: ID of the user
            date: Date for snapshot (default: today)
            
        Returns:
            Dict with snapshot creation result
        """
        try:
            if date is None:
                date = datetime.utcnow().date()
            
            # Check if snapshot already exists
            existing = AnalyticsSnapshot.query.filter_by(
                user_id=user_id,
                date=date,
                metric_name='daily_summary'
            ).first()
            
            if existing:
                return {'success': False, 'error': 'Snapshot already exists for this date'}
            
            # Get usage stats for the day
            start_of_day = datetime.combine(date, datetime.min.time())
            end_of_day = datetime.combine(date, datetime.max.time())
            
            documents_uploaded = WorkspaceDocument.query.filter(
                and_(
                    WorkspaceDocument.uploaded_by == user_id,
                    WorkspaceDocument.uploaded_at >= start_of_day,
                    WorkspaceDocument.uploaded_at <= end_of_day
                )
            ).count()
            
            documents_shared = DocumentShare.query.filter(
                and_(
                    DocumentShare.shared_by == user_id,
                    DocumentShare.created_at >= start_of_day,
                    DocumentShare.created_at <= end_of_day
                )
            ).count()
            
            # Create snapshot
            snapshot = AnalyticsSnapshot(
                user_id=user_id,
                date=date,
                metric_name='daily_summary',
                value=documents_uploaded + documents_shared,
                metadata=f'{{"documents_uploaded": {documents_uploaded}, "documents_shared": {documents_shared}}}'
            )
            
            db.session.add(snapshot)
            db.session.commit()
            
            self.logger.info(f"Created analytics snapshot for user {user_id} on {date}")
            
            return {
                'success': True,
                'snapshot': {
                    'user_id': user_id,
                    'date': date.isoformat(),
                    'value': snapshot.value,
                    'metadata': snapshot.metadata
                }
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to create analytics snapshot: {e}")
            return {'success': False, 'error': str(e)}

# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

def get_user_usage_stats(user_id: int, days: int = 30) -> Dict[str, Any]:
    """Get user usage statistics."""
    manager = UserAnalyticsManager()
    return manager.get_user_usage_stats(user_id, days)

def get_user_document_analytics(user_id: int, days: int = 30) -> Dict[str, Any]:
    """Get user document analytics."""
    manager = UserAnalyticsManager()
    return manager.get_user_document_analytics(user_id, days)

def get_user_workspace_analytics(user_id: int) -> Dict[str, Any]:
    """Get user workspace analytics."""
    manager = UserAnalyticsManager()
    return manager.get_user_workspace_analytics(user_id)

def get_user_performance_insights(user_id: int, days: int = 30) -> Dict[str, Any]:
    """Get user performance insights."""
    manager = UserAnalyticsManager()
    return manager.get_user_performance_insights(user_id, days)

