# ==============================================================================
# app/collaboration/document_sharing.py
# Document Sharing System - The Knowledge Distribution Hub
# ==============================================================================
"""
This module manages document sharing within workspaces and between users.
Handles granular permissions, expiration, and access tracking.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.models import User, Workspace, WorkspaceDocument, DocumentShare, Subscription
from app import db
from app.tiers import can_use_feature

logger = logging.getLogger(__name__)

# ==============================================================================
# DOCUMENT SHARING MANAGER
# ==============================================================================

class DocumentSharingManager:
    """
    Manages document sharing with granular permissions and access control.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def share_document(self, document_id: int, sharer_id: int, recipient_id: int, 
                      permissions: str = 'view', expires_at: datetime = None) -> Dict[str, Any]:
        """
        Share a document with another user.
        
        Args:
            document_id: ID of the document to share
            sharer_id: ID of the user sharing the document
            recipient_id: ID of the user receiving the document
            permissions: Permissions to grant (view, edit, admin)
            expires_at: Optional expiration date
            
        Returns:
            Dict with sharing result
        """
        try:
            # Check if sharer has document sharing permissions
            if not self._can_share_document(document_id, sharer_id):
                return {'success': False, 'error': 'Insufficient permissions to share document'}
            
            # Check if user has document sharing feature
            user = User.query.get(sharer_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            subscription = Subscription.query.filter_by(user_id=sharer_id, status='active').first()
            user_tier = subscription.tier if subscription else 'free'
            
            if not can_use_feature(user_tier, 'document_sharing'):
                return {
                    'success': False,
                    'error': 'Document sharing not available in your tier',
                    'upgrade_prompt': 'Upgrade to Pro to share documents'
                }
            
            # Check if share already exists
            existing_share = DocumentShare.query.filter_by(
                document_id=document_id,
                shared_with=recipient_id
            ).first()
            
            if existing_share:
                # Update existing share
                existing_share.permissions = permissions
                existing_share.expires_at = expires_at
                existing_share.created_at = datetime.utcnow()
            else:
                # Create new share
                share = DocumentShare(
                    document_id=document_id,
                    shared_by=sharer_id,
                    shared_with=recipient_id,
                    permissions=permissions,
                    expires_at=expires_at
                )
                db.session.add(share)
            
            db.session.commit()
            
            self.logger.info(f"Shared document {document_id} with user {recipient_id}")
            
            return {
                'success': True,
                'share': {
                    'document_id': document_id,
                    'recipient_id': recipient_id,
                    'permissions': permissions,
                    'expires_at': expires_at.isoformat() if expires_at else None,
                    'created_at': datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to share document: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_shared_documents(self, user_id: int, include_expired: bool = False) -> Dict[str, Any]:
        """
        Get documents shared with a user.
        
        Args:
            user_id: ID of the user
            include_expired: Whether to include expired shares
            
        Returns:
            Dict with shared documents list
        """
        try:
            # Get shares for user
            query = DocumentShare.query.filter_by(shared_with=user_id)
            
            if not include_expired:
                # Filter out expired shares
                query = query.filter(
                    (DocumentShare.expires_at.is_(None)) | 
                    (DocumentShare.expires_at > datetime.utcnow())
                )
            
            shares = query.all()
            
            shared_documents = []
            for share in shares:
                # Get document info
                document = WorkspaceDocument.query.get(share.document_id)
                if document:
                    # Get workspace info
                    workspace = Workspace.query.get(document.workspace_id)
                    
                    # Get sharer info
                    sharer = User.query.get(share.shared_by)
                    
                    shared_documents.append({
                        'document_id': document.id,
                        'document_name': document.document_name,
                        'workspace_id': document.workspace_id,
                        'workspace_name': workspace.name if workspace else 'Unknown',
                        'sharer_id': share.shared_by,
                        'sharer_email': sharer.email if sharer else 'Unknown',
                        'permissions': share.permissions,
                        'shared_at': share.created_at.isoformat(),
                        'expires_at': share.expires_at.isoformat() if share.expires_at else None,
                        'access_count': share.access_count,
                        'last_accessed': share.last_accessed.isoformat() if share.last_accessed else None,
                        'is_valid': share.is_valid()
                    })
            
            return {
                'success': True,
                'shared_documents': shared_documents,
                'total_shared': len(shared_documents)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get shared documents: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_document_shares(self, document_id: int, requester_id: int) -> Dict[str, Any]:
        """
        Get all shares for a specific document.
        
        Args:
            document_id: ID of the document
            requester_id: ID of the user requesting the list
            
        Returns:
            Dict with shares list
        """
        try:
            # Check if user has permission to view shares
            if not self._can_manage_document_shares(document_id, requester_id):
                return {'success': False, 'error': 'Insufficient permissions to view document shares'}
            
            # Get shares
            shares = DocumentShare.query.filter_by(document_id=document_id).all()
            
            shares_list = []
            for share in shares:
                # Get recipient info
                recipient = User.query.get(share.shared_with)
                
                shares_list.append({
                    'share_id': share.id,
                    'recipient_id': share.shared_with,
                    'recipient_email': recipient.email if recipient else 'Unknown',
                    'permissions': share.permissions,
                    'shared_at': share.created_at.isoformat(),
                    'expires_at': share.expires_at.isoformat() if share.expires_at else None,
                    'access_count': share.access_count,
                    'last_accessed': share.last_accessed.isoformat() if share.last_accessed else None,
                    'is_valid': share.is_valid()
                })
            
            return {
                'success': True,
                'shares': shares_list,
                'total_shares': len(shares_list)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get document shares: {e}")
            return {'success': False, 'error': str(e)}
    
    def revoke_document_access(self, document_id: int, revoker_id: int, 
                             recipient_id: int = None) -> Dict[str, Any]:
        """
        Revoke document access for a user or all users.
        
        Args:
            document_id: ID of the document
            revoker_id: ID of the user revoking access
            recipient_id: ID of the user to revoke access from (None for all)
            
        Returns:
            Dict with revocation result
        """
        try:
            # Check if user has permission to revoke access
            if not self._can_manage_document_shares(document_id, revoker_id):
                return {'success': False, 'error': 'Insufficient permissions to revoke document access'}
            
            # Build query
            query = DocumentShare.query.filter_by(document_id=document_id)
            
            if recipient_id:
                query = query.filter_by(shared_with=recipient_id)
            
            shares = query.all()
            
            if not shares:
                return {'success': False, 'error': 'No shares found to revoke'}
            
            # Delete shares
            for share in shares:
                db.session.delete(share)
            
            db.session.commit()
            
            self.logger.info(f"Revoked document {document_id} access for user {recipient_id or 'all'}")
            
            return {
                'success': True,
                'message': f'Revoked access for {len(shares)} share(s)',
                'revoked_count': len(shares)
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to revoke document access: {e}")
            return {'success': False, 'error': str(e)}
    
    def update_share_permissions(self, share_id: int, updater_id: int, 
                               new_permissions: str) -> Dict[str, Any]:
        """
        Update permissions for a document share.
        
        Args:
            share_id: ID of the share
            updater_id: ID of the user updating permissions
            new_permissions: New permissions to set
            
        Returns:
            Dict with update result
        """
        try:
            # Get share
            share = DocumentShare.query.get(share_id)
            if not share:
                return {'success': False, 'error': 'Share not found'}
            
            # Check if user has permission to update
            if not self._can_manage_document_shares(share.document_id, updater_id):
                return {'success': False, 'error': 'Insufficient permissions to update share'}
            
            # Update permissions
            share.permissions = new_permissions
            db.session.commit()
            
            self.logger.info(f"Updated share {share_id} permissions to {new_permissions}")
            
            return {'success': True, 'message': 'Share permissions updated successfully'}
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to update share permissions: {e}")
            return {'success': False, 'error': str(e)}
    
    def track_document_access(self, document_id: int, user_id: int) -> Dict[str, Any]:
        """
        Track when a user accesses a shared document.
        
        Args:
            document_id: ID of the document
            user_id: ID of the user accessing the document
            
        Returns:
            Dict with tracking result
        """
        try:
            # Find share
            share = DocumentShare.query.filter_by(
                document_id=document_id,
                shared_with=user_id
            ).first()
            
            if not share:
                return {'success': False, 'error': 'Share not found'}
            
            # Check if share is still valid
            if not share.is_valid():
                return {'success': False, 'error': 'Share has expired'}
            
            # Update access tracking
            share.access_count += 1
            share.last_accessed = datetime.utcnow()
            
            db.session.commit()
            
            return {'success': True, 'message': 'Access tracked successfully'}
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to track document access: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_document_access_analytics(self, document_id: int, requester_id: int) -> Dict[str, Any]:
        """
        Get analytics for document access.
        
        Args:
            document_id: ID of the document
            requester_id: ID of the user requesting analytics
            
        Returns:
            Dict with analytics data
        """
        try:
            # Check if user has permission to view analytics
            if not self._can_manage_document_shares(document_id, requester_id):
                return {'success': False, 'error': 'Insufficient permissions to view analytics'}
            
            # Get all shares for document
            shares = DocumentShare.query.filter_by(document_id=document_id).all()
            
            # Calculate analytics
            total_shares = len(shares)
            active_shares = len([s for s in shares if s.is_valid()])
            expired_shares = total_shares - active_shares
            
            total_access_count = sum(share.access_count for share in shares)
            
            # Get most accessed share
            most_accessed = max(shares, key=lambda s: s.access_count) if shares else None
            
            # Get recent access (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_access = len([s for s in shares if s.last_accessed and s.last_accessed > thirty_days_ago])
            
            return {
                'success': True,
                'analytics': {
                    'total_shares': total_shares,
                    'active_shares': active_shares,
                    'expired_shares': expired_shares,
                    'total_access_count': total_access_count,
                    'recent_access_count': recent_access,
                    'most_accessed': {
                        'recipient_id': most_accessed.shared_with,
                        'access_count': most_accessed.access_count
                    } if most_accessed else None
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get document analytics: {e}")
            return {'success': False, 'error': str(e)}
    
    # ==============================================================================
    # HELPER METHODS
    # ==============================================================================
    
    def _can_share_document(self, document_id: int, user_id: int) -> bool:
        """Check if user can share a document."""
        # Get document
        document = WorkspaceDocument.query.get(document_id)
        if not document:
            return False
        
        # Check if user is in the workspace
        from app.collaboration.workspaces import check_workspace_permissions
        return check_workspace_permissions(document.workspace_id, user_id, 'edit_documents')
    
    def _can_manage_document_shares(self, document_id: int, user_id: int) -> bool:
        """Check if user can manage document shares."""
        # Get document
        document = WorkspaceDocument.query.get(document_id)
        if not document:
            return False
        
        # Check if user is the document owner or has admin permissions
        if document.uploaded_by == user_id:
            return True
        
        # Check workspace permissions
        from app.collaboration.workspaces import check_workspace_permissions
        return check_workspace_permissions(document.workspace_id, user_id, 'manage_members')

# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

def share_document(document_id: int, sharer_id: int, recipient_id: int, 
                  permissions: str = 'view', expires_at: datetime = None) -> Dict[str, Any]:
    """Share a document with another user."""
    manager = DocumentSharingManager()
    return manager.share_document(document_id, sharer_id, recipient_id, permissions, expires_at)

def get_shared_documents(user_id: int, include_expired: bool = False) -> Dict[str, Any]:
    """Get documents shared with a user."""
    manager = DocumentSharingManager()
    return manager.get_shared_documents(user_id, include_expired)

def revoke_document_access(document_id: int, revoker_id: int, 
                         recipient_id: int = None) -> Dict[str, Any]:
    """Revoke document access for a user or all users."""
    manager = DocumentSharingManager()
    return manager.revoke_document_access(document_id, revoker_id, recipient_id)

