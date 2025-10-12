# ==============================================================================
# app/api/collaboration_routes.py
# Collaboration API Routes - The Team Intelligence Gateway
# ==============================================================================
"""
This module provides API endpoints for collaborative features including:
- Workspace management
- Document sharing
- Team collaboration
- Permission management

All endpoints require authentication and respect tier limits.
"""

from flask import Blueprint, request, jsonify, current_app, g
from functools import wraps
import logging
from app.api.routes import api_key_required
from app.middleware.tier_check import check_tier_limit, require_tier
from app.collaboration.workspaces import WorkspaceManager
from app.collaboration.document_sharing import DocumentSharingManager
from app.models import User, Subscription
from app import db

# Configure logging
logger = logging.getLogger(__name__)

# Create collaboration blueprint
collaboration = Blueprint('collaboration', __name__)

# ==============================================================================
# WORKSPACE MANAGEMENT ENDPOINTS
# ==============================================================================

@collaboration.route('/workspaces', methods=['POST'])
@api_key_required
@check_tier_limit('team_vaults', 1)
def create_workspace():
    """
    Create a new collaborative workspace.
    
    Available for Pro and Enterprise tiers.
    
    Request:
        - name: Workspace name
        - description: Optional workspace description
        - type: Workspace type (personal, team, organization)
    
    Response:
        - workspace: Created workspace information
        - message: Success message
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get request data
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Workspace name is required'}), 400
        
        name = data['name']
        description = data.get('description', '')
        workspace_type = data.get('type', 'team')
        
        # Create workspace
        manager = WorkspaceManager()
        result = manager.create_workspace(
            owner_id=user.id,
            name=name,
            description=description,
            workspace_type=workspace_type
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'workspace': result['workspace'],
                'message': 'Workspace created successfully'
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': result['error'],
                'upgrade_prompt': result.get('upgrade_prompt')
            }), 400
        
    except Exception as e:
        logger.error(f"Create workspace endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@collaboration.route('/workspaces', methods=['GET'])
@api_key_required
def get_user_workspaces():
    """
    Get all workspaces for the current user.
    
    Response:
        - workspaces: List of user's workspaces
        - total: Total number of workspaces
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get workspaces
        manager = WorkspaceManager()
        result = manager.get_user_workspaces(user.id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'workspaces': result['workspaces'],
                'total': result['total_workspaces']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get workspaces endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@collaboration.route('/workspaces/<int:workspace_id>', methods=['GET'])
@api_key_required
def get_workspace_details(workspace_id):
    """
    Get detailed information about a specific workspace.
    
    Args:
        workspace_id: ID of the workspace
        
    Response:
        - workspace: Workspace details
        - members: List of workspace members
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get workspace details
        manager = WorkspaceManager()
        
        # Get workspace info
        from app.models import Workspace
        workspace = Workspace.query.get(workspace_id)
        if not workspace:
            return jsonify({'error': 'Workspace not found'}), 404
        
        # Check access
        if not manager._has_workspace_access(workspace_id, user.id):
            return jsonify({'error': 'Access denied to workspace'}), 403
        
        # Get members
        members_result = manager.get_workspace_members(workspace_id, user.id)
        
        return jsonify({
            'success': True,
            'workspace': {
                'id': workspace.id,
                'name': workspace.name,
                'type': workspace.workspace_type,
                'description': workspace.description,
                'created_at': workspace.created_at.isoformat(),
                'owner_id': workspace.owner_id,
                'is_active': workspace.is_active
            },
            'members': members_result.get('members', []) if members_result['success'] else []
        }), 200
        
    except Exception as e:
        logger.error(f"Get workspace details endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@collaboration.route('/workspaces/<int:workspace_id>/invite', methods=['POST'])
@api_key_required
def invite_to_workspace(workspace_id):
    """
    Invite a user to a workspace.
    
    Args:
        workspace_id: ID of the workspace
        
    Request:
        - email: Email of the user to invite
        - role: Role to assign (owner, admin, editor, viewer)
    
    Response:
        - member: Invited member information
        - message: Success message
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get request data
        data = request.get_json()
        if not data or 'email' not in data:
            return jsonify({'error': 'User email is required'}), 400
        
        email = data['email']
        role = data.get('role', 'viewer')
        
        # Invite user
        manager = WorkspaceManager()
        result = manager.invite_user(workspace_id, user.id, email, role)
        
        if result['success']:
            return jsonify({
                'success': True,
                'member': result['member'],
                'message': 'User invited successfully'
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
    except Exception as e:
        logger.error(f"Invite to workspace endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@collaboration.route('/workspaces/<int:workspace_id>/members/<int:user_id>', methods=['DELETE'])
@api_key_required
def remove_workspace_member(workspace_id, user_id):
    """
    Remove a user from a workspace.
    
    Args:
        workspace_id: ID of the workspace
        user_id: ID of the user to remove
        
    Response:
        - message: Success message
    """
    try:
        # Get current user
        user = g.current_user
        
        # Remove member
        manager = WorkspaceManager()
        result = manager.remove_member(workspace_id, user.id, user_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
    except Exception as e:
        logger.error(f"Remove workspace member endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@collaboration.route('/workspaces/<int:workspace_id>/members/<int:user_id>/role', methods=['PUT'])
@api_key_required
def update_member_role(workspace_id, user_id):
    """
    Update a member's role in a workspace.
    
    Args:
        workspace_id: ID of the workspace
        user_id: ID of the user whose role is being updated
        
    Request:
        - role: New role to assign
        
    Response:
        - message: Success message
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get request data
        data = request.get_json()
        if not data or 'role' not in data:
            return jsonify({'error': 'Role is required'}), 400
        
        new_role = data['role']
        
        # Update role
        manager = WorkspaceManager()
        result = manager.update_member_role(workspace_id, user.id, user_id, new_role)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
    except Exception as e:
        logger.error(f"Update member role endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==============================================================================
# DOCUMENT SHARING ENDPOINTS
# ==============================================================================

@collaboration.route('/documents/<int:document_id>/share', methods=['POST'])
@api_key_required
@check_tier_limit('document_sharing', 1)
def share_document_endpoint(document_id):
    """
    Share a document with another user.
    
    Available for Pro and Enterprise tiers.
    
    Args:
        document_id: ID of the document to share
        
    Request:
        - user_id: ID of the user to share with
        - permissions: Permissions to grant (view, edit, admin)
        - expires_at: Optional expiration date (ISO format)
    
    Response:
        - share: Share information
        - message: Success message
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get request data
        data = request.get_json()
        if not data or 'user_id' not in data:
            return jsonify({'error': 'User ID is required'}), 400
        
        recipient_id = data['user_id']
        permissions = data.get('permissions', 'view')
        expires_at = data.get('expires_at')
        
        # Parse expiration date if provided
        if expires_at:
            from datetime import datetime
            try:
                expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid expiration date format'}), 400
        
        # Share document
        manager = DocumentSharingManager()
        result = manager.share_document(
            document_id=document_id,
            sharer_id=user.id,
            recipient_id=recipient_id,
            permissions=permissions,
            expires_at=expires_at
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'share': result['share'],
                'message': 'Document shared successfully'
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': result['error'],
                'upgrade_prompt': result.get('upgrade_prompt')
            }), 400
        
    except Exception as e:
        logger.error(f"Share document endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@collaboration.route('/documents/shared', methods=['GET'])
@api_key_required
def get_shared_documents_endpoint():
    """
    Get documents shared with the current user.
    
    Response:
        - shared_documents: List of shared documents
        - total: Total number of shared documents
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get shared documents
        manager = DocumentSharingManager()
        result = manager.get_shared_documents(user.id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'shared_documents': result['shared_documents'],
                'total': result['total_shared']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get shared documents endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@collaboration.route('/documents/<int:document_id>/shares', methods=['GET'])
@api_key_required
def get_document_shares_endpoint(document_id):
    """
    Get all shares for a specific document.
    
    Args:
        document_id: ID of the document
        
    Response:
        - shares: List of document shares
        - total: Total number of shares
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get document shares
        manager = DocumentSharingManager()
        result = manager.get_document_shares(document_id, user.id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'shares': result['shares'],
                'total': result['total_shares']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get document shares endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@collaboration.route('/documents/<int:document_id>/shares/<int:user_id>', methods=['DELETE'])
@api_key_required
def revoke_document_access_endpoint(document_id, user_id):
    """
    Revoke document access for a specific user.
    
    Args:
        document_id: ID of the document
        user_id: ID of the user to revoke access from
        
    Response:
        - message: Success message
    """
    try:
        # Get current user
        user = g.current_user
        
        # Revoke access
        manager = DocumentSharingManager()
        result = manager.revoke_document_access(document_id, user.id, user_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
    except Exception as e:
        logger.error(f"Revoke document access endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@collaboration.route('/documents/<int:document_id>/access', methods=['POST'])
@api_key_required
def track_document_access_endpoint(document_id):
    """
    Track when a user accesses a shared document.
    
    Args:
        document_id: ID of the document
        
    Response:
        - message: Success message
    """
    try:
        # Get current user
        user = g.current_user
        
        # Track access
        manager = DocumentSharingManager()
        result = manager.track_document_access(document_id, user.id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
    except Exception as e:
        logger.error(f"Track document access endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==============================================================================
# COLLABORATION ANALYTICS ENDPOINTS
# ==============================================================================

@collaboration.route('/workspaces/<int:workspace_id>/analytics', methods=['GET'])
@api_key_required
def get_workspace_analytics(workspace_id):
    """
    Get analytics for a workspace.
    
    Args:
        workspace_id: ID of the workspace
        
    Response:
        - analytics: Workspace analytics data
    """
    try:
        # Get current user
        user = g.current_user
        
        # Check workspace access
        manager = WorkspaceManager()
        if not manager._has_workspace_access(workspace_id, user.id):
            return jsonify({'error': 'Access denied to workspace'}), 403
        
        # Get workspace info
        from app.models import Workspace, WorkspaceMember, WorkspaceDocument
        workspace = Workspace.query.get(workspace_id)
        
        # Calculate analytics
        member_count = WorkspaceMember.query.filter_by(workspace_id=workspace_id).count()
        document_count = WorkspaceDocument.query.filter_by(workspace_id=workspace_id).count()
        
        # Get recent activity (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        recent_documents = WorkspaceDocument.query.filter(
            WorkspaceDocument.workspace_id == workspace_id,
            WorkspaceDocument.uploaded_at > thirty_days_ago
        ).count()
        
        return jsonify({
            'success': True,
            'analytics': {
                'workspace_id': workspace_id,
                'workspace_name': workspace.name,
                'member_count': member_count,
                'document_count': document_count,
                'recent_documents': recent_documents,
                'created_at': workspace.created_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get workspace analytics endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@collaboration.route('/documents/<int:document_id>/analytics', methods=['GET'])
@api_key_required
def get_document_analytics_endpoint(document_id):
    """
    Get analytics for a document.
    
    Args:
        document_id: ID of the document
        
    Response:
        - analytics: Document analytics data
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get document analytics
        manager = DocumentSharingManager()
        result = manager.get_document_access_analytics(document_id, user.id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'analytics': result['analytics']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get document analytics endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==============================================================================
# ERROR HANDLERS
# ==============================================================================

@collaboration.errorhandler(404)
def not_found(e):
    """Handle not found errors."""
    return jsonify({
        'error': 'Resource not found',
        'message': 'The requested resource could not be found'
    }), 404

@collaboration.errorhandler(403)
def forbidden(e):
    """Handle forbidden errors."""
    return jsonify({
        'error': 'Access forbidden',
        'message': 'You do not have permission to access this resource'
    }), 403

