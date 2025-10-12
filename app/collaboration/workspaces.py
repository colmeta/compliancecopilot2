# ==============================================================================
# app/collaboration/workspaces.py
# Workspace Management System - The Team Intelligence Hub
# ==============================================================================
"""
This module manages collaborative workspaces for CLARITY.
Handles workspace creation, member management, and permission control.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from app.models import User, Workspace, WorkspaceMember, WorkspaceDocument, Subscription
from app import db
from app.tiers import can_use_feature, get_feature_limit

logger = logging.getLogger(__name__)

# ==============================================================================
# WORKSPACE MANAGER
# ==============================================================================

class WorkspaceManager:
    """
    Manages collaborative workspaces with role-based access control.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_workspace(self, owner_id: int, name: str, description: str = None, 
                        workspace_type: str = 'team') -> Dict[str, Any]:
        """
        Create a new collaborative workspace.
        
        Args:
            owner_id: ID of the user creating the workspace
            name: Workspace name
            description: Optional workspace description
            workspace_type: Type of workspace (personal, team, organization)
            
        Returns:
            Dict with workspace creation result
        """
        try:
            # Check if user can create workspaces
            user = User.query.get(owner_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Check subscription tier
            subscription = Subscription.query.filter_by(user_id=owner_id, status='active').first()
            user_tier = subscription.tier if subscription else 'free'
            
            if not can_use_feature(user_tier, 'team_vaults'):
                return {
                    'success': False, 
                    'error': 'Team workspaces not available in your tier',
                    'upgrade_prompt': 'Upgrade to Pro to create collaborative workspaces'
                }
            
            # Check workspace limit
            if not self._can_create_workspace(owner_id, user_tier):
                return {
                    'success': False,
                    'error': 'Workspace limit exceeded',
                    'upgrade_prompt': 'Upgrade to create more workspaces'
                }
            
            # Create workspace
            workspace = Workspace(
                name=name,
                owner_id=owner_id,
                workspace_type=workspace_type,
                description=description
            )
            
            db.session.add(workspace)
            db.session.flush()  # Get the ID
            
            # Add owner as admin member
            owner_member = WorkspaceMember(
                workspace_id=workspace.id,
                user_id=owner_id,
                role='owner',
                permissions='{"all": true}'
            )
            
            db.session.add(owner_member)
            db.session.commit()
            
            self.logger.info(f"Created workspace '{name}' for user {owner_id}")
            
            return {
                'success': True,
                'workspace': {
                    'id': workspace.id,
                    'name': workspace.name,
                    'type': workspace.workspace_type,
                    'description': workspace.description,
                    'created_at': workspace.created_at.isoformat(),
                    'owner_id': workspace.owner_id
                }
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to create workspace: {e}")
            return {'success': False, 'error': str(e)}
    
    def invite_user(self, workspace_id: int, inviter_id: int, user_email: str, 
                   role: str = 'viewer') -> Dict[str, Any]:
        """
        Invite a user to a workspace.
        
        Args:
            workspace_id: ID of the workspace
            inviter_id: ID of the user sending the invitation
            user_email: Email of the user to invite
            role: Role to assign (owner, admin, editor, viewer)
            
        Returns:
            Dict with invitation result
        """
        try:
            # Check if inviter has permission
            if not self._has_permission(workspace_id, inviter_id, 'invite_members'):
                return {'success': False, 'error': 'Insufficient permissions to invite users'}
            
            # Find user by email
            user = User.query.filter_by(email=user_email).first()
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Check if user is already a member
            existing_member = WorkspaceMember.query.filter_by(
                workspace_id=workspace_id,
                user_id=user.id
            ).first()
            
            if existing_member:
                return {'success': False, 'error': 'User is already a member of this workspace'}
            
            # Check workspace member limit
            workspace = Workspace.query.get(workspace_id)
            if not workspace:
                return {'success': False, 'error': 'Workspace not found'}
            
            if not self._can_add_member(workspace, user.id):
                return {'success': False, 'error': 'Workspace member limit exceeded'}
            
            # Create membership
            member = WorkspaceMember(
                workspace_id=workspace_id,
                user_id=user.id,
                role=role,
                invited_by=inviter_id
            )
            
            db.session.add(member)
            db.session.commit()
            
            self.logger.info(f"Added user {user.id} to workspace {workspace_id} with role {role}")
            
            return {
                'success': True,
                'member': {
                    'user_id': user.id,
                    'email': user.email,
                    'role': role,
                    'joined_at': member.joined_at.isoformat()
                }
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to invite user: {e}")
            return {'success': False, 'error': str(e)}
    
    def remove_member(self, workspace_id: int, remover_id: int, user_id: int) -> Dict[str, Any]:
        """
        Remove a user from a workspace.
        
        Args:
            workspace_id: ID of the workspace
            remover_id: ID of the user removing the member
            user_id: ID of the user to remove
            
        Returns:
            Dict with removal result
        """
        try:
            # Check if remover has permission
            if not self._has_permission(workspace_id, remover_id, 'manage_members'):
                return {'success': False, 'error': 'Insufficient permissions to remove members'}
            
            # Find membership
            member = WorkspaceMember.query.filter_by(
                workspace_id=workspace_id,
                user_id=user_id
            ).first()
            
            if not member:
                return {'success': False, 'error': 'User is not a member of this workspace'}
            
            # Don't allow removing the owner
            if member.role == 'owner':
                return {'success': False, 'error': 'Cannot remove workspace owner'}
            
            # Remove membership
            db.session.delete(member)
            db.session.commit()
            
            self.logger.info(f"Removed user {user_id} from workspace {workspace_id}")
            
            return {'success': True, 'message': 'User removed from workspace'}
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to remove member: {e}")
            return {'success': False, 'error': str(e)}
    
    def update_member_role(self, workspace_id: int, updater_id: int, user_id: int, 
                          new_role: str) -> Dict[str, Any]:
        """
        Update a member's role in a workspace.
        
        Args:
            workspace_id: ID of the workspace
            updater_id: ID of the user updating the role
            user_id: ID of the user whose role is being updated
            new_role: New role to assign
            
        Returns:
            Dict with update result
        """
        try:
            # Check if updater has permission
            if not self._has_permission(workspace_id, updater_id, 'manage_members'):
                return {'success': False, 'error': 'Insufficient permissions to update roles'}
            
            # Find membership
            member = WorkspaceMember.query.filter_by(
                workspace_id=workspace_id,
                user_id=user_id
            ).first()
            
            if not member:
                return {'success': False, 'error': 'User is not a member of this workspace'}
            
            # Don't allow changing owner role
            if member.role == 'owner':
                return {'success': False, 'error': 'Cannot change owner role'}
            
            # Update role
            member.role = new_role
            db.session.commit()
            
            self.logger.info(f"Updated user {user_id} role to {new_role} in workspace {workspace_id}")
            
            return {'success': True, 'message': 'Role updated successfully'}
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to update member role: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_workspace_members(self, workspace_id: int, requester_id: int) -> Dict[str, Any]:
        """
        Get list of workspace members.
        
        Args:
            workspace_id: ID of the workspace
            requester_id: ID of the user requesting the list
            
        Returns:
            Dict with member list
        """
        try:
            # Check if user has access to workspace
            if not self._has_workspace_access(workspace_id, requester_id):
                return {'success': False, 'error': 'Access denied to workspace'}
            
            # Get members
            members = WorkspaceMember.query.filter_by(workspace_id=workspace_id).all()
            
            member_list = []
            for member in members:
                user = User.query.get(member.user_id)
                if user:
                    member_list.append({
                        'user_id': user.id,
                        'email': user.email,
                        'role': member.role,
                        'joined_at': member.joined_at.isoformat(),
                        'invited_by': member.invited_by
                    })
            
            return {
                'success': True,
                'members': member_list,
                'total_members': len(member_list)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get workspace members: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_user_workspaces(self, user_id: int) -> Dict[str, Any]:
        """
        Get all workspaces a user has access to.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dict with workspace list
        """
        try:
            # Get workspaces where user is a member
            memberships = WorkspaceMember.query.filter_by(user_id=user_id).all()
            
            workspaces = []
            for membership in memberships:
                workspace = Workspace.query.get(membership.workspace_id)
                if workspace and workspace.is_active:
                    workspaces.append({
                        'id': workspace.id,
                        'name': workspace.name,
                        'type': workspace.workspace_type,
                        'description': workspace.description,
                        'role': membership.role,
                        'created_at': workspace.created_at.isoformat(),
                        'owner_id': workspace.owner_id,
                        'member_count': WorkspaceMember.query.filter_by(workspace_id=workspace.id).count()
                    })
            
            return {
                'success': True,
                'workspaces': workspaces,
                'total_workspaces': len(workspaces)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get user workspaces: {e}")
            return {'success': False, 'error': str(e)}
    
    def delete_workspace(self, workspace_id: int, requester_id: int) -> Dict[str, Any]:
        """
        Delete a workspace (only owner can delete).
        
        Args:
            workspace_id: ID of the workspace
            requester_id: ID of the user requesting deletion
            
        Returns:
            Dict with deletion result
        """
        try:
            # Check if user is the owner
            workspace = Workspace.query.get(workspace_id)
            if not workspace:
                return {'success': False, 'error': 'Workspace not found'}
            
            if workspace.owner_id != requester_id:
                return {'success': False, 'error': 'Only workspace owner can delete workspace'}
            
            # Delete workspace (cascade will handle members and documents)
            db.session.delete(workspace)
            db.session.commit()
            
            self.logger.info(f"Deleted workspace {workspace_id} by user {requester_id}")
            
            return {'success': True, 'message': 'Workspace deleted successfully'}
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to delete workspace: {e}")
            return {'success': False, 'error': str(e)}
    
    # ==============================================================================
    # HELPER METHODS
    # ==============================================================================
    
    def _can_create_workspace(self, user_id: int, user_tier: str) -> bool:
        """Check if user can create a new workspace."""
        # Get current workspace count
        current_count = Workspace.query.filter_by(owner_id=user_id, is_active=True).count()
        
        # Get tier limit
        limit = get_feature_limit(user_tier, 'team_vaults')
        
        if limit == -1:  # Unlimited
            return True
        
        return current_count < limit
    
    def _can_add_member(self, workspace: Workspace, user_id: int) -> bool:
        """Check if a member can be added to workspace."""
        # Get current member count
        current_count = WorkspaceMember.query.filter_by(workspace_id=workspace.id).count()
        
        # Get workspace owner's tier
        subscription = Subscription.query.filter_by(user_id=workspace.owner_id, status='active').first()
        user_tier = subscription.tier if subscription else 'free'
        
        # Get tier limit
        limit = get_feature_limit(user_tier, 'workspace_members')
        
        if limit == -1:  # Unlimited
            return True
        
        return current_count < limit
    
    def _has_workspace_access(self, workspace_id: int, user_id: int) -> bool:
        """Check if user has access to workspace."""
        member = WorkspaceMember.query.filter_by(
            workspace_id=workspace_id,
            user_id=user_id
        ).first()
        
        return member is not None
    
    def _has_permission(self, workspace_id: int, user_id: int, permission: str) -> bool:
        """Check if user has specific permission in workspace."""
        member = WorkspaceMember.query.filter_by(
            workspace_id=workspace_id,
            user_id=user_id
        ).first()
        
        if not member:
            return False
        
        # Role-based permissions
        role_permissions = {
            'owner': ['all'],
            'admin': ['manage_members', 'invite_members', 'edit_documents', 'view_documents'],
            'editor': ['edit_documents', 'view_documents'],
            'viewer': ['view_documents']
        }
        
        user_permissions = role_permissions.get(member.role, [])
        
        return 'all' in user_permissions or permission in user_permissions

# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

def create_workspace(owner_id: int, name: str, description: str = None, 
                    workspace_type: str = 'team') -> Dict[str, Any]:
    """Create a new workspace."""
    manager = WorkspaceManager()
    return manager.create_workspace(owner_id, name, description, workspace_type)

def invite_user_to_workspace(workspace_id: int, inviter_id: int, user_email: str, 
                           role: str = 'viewer') -> Dict[str, Any]:
    """Invite a user to a workspace."""
    manager = WorkspaceManager()
    return manager.invite_user(workspace_id, inviter_id, user_email, role)

def get_user_workspaces(user_id: int) -> Dict[str, Any]:
    """Get all workspaces for a user."""
    manager = WorkspaceManager()
    return manager.get_user_workspaces(user_id)

def check_workspace_permissions(workspace_id: int, user_id: int, permission: str) -> bool:
    """Check if user has permission in workspace."""
    manager = WorkspaceManager()
    return manager._has_permission(workspace_id, user_id, permission)

