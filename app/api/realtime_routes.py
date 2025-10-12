# ==============================================================================
# app/api/realtime_routes.py
# Real-Time Collaboration API Routes - The Live Intelligence Gateway
# ==============================================================================
"""
This module provides API endpoints for real-time collaboration features.
Handles WebSocket connections, presence management, and live collaboration.
"""

from flask import Blueprint, request, jsonify, current_app, g
from flask_socketio import emit, join_room, leave_room
import logging
from datetime import datetime
from app.api.routes import api_key_required
from app.collaboration.realtime import RealtimeCollaborationManager, CollaborationEvents
from app.models import User, Workspace, WorkspaceMember, WorkspaceDocument
from app import db, socketio

# Configure logging
logger = logging.getLogger(__name__)

# Create realtime blueprint
realtime = Blueprint('realtime', __name__)

# Initialize real-time collaboration manager
realtime_manager = RealtimeCollaborationManager(socketio)

# ==============================================================================
# PRESENCE MANAGEMENT ENDPOINTS
# ==============================================================================

@realtime.route('/workspaces/<int:workspace_id>/presence', methods=['GET'])
@api_key_required
def get_workspace_presence(workspace_id):
    """
    Get current presence information for a workspace.
    
    Args:
        workspace_id: ID of the workspace
        
    Response:
        - active_users: List of active user IDs
        - total_active: Total number of active users
    """
    try:
        # Get current user
        user = g.current_user
        
        # Verify workspace access
        member = WorkspaceMember.query.filter_by(
            workspace_id=workspace_id,
            user_id=user.id
        ).first()
        
        if not member:
            return jsonify({'error': 'Access denied to workspace'}), 403
        
        # Get presence information
        active_users = realtime_manager.get_workspace_presence(workspace_id)
        
        # Get user details for active users
        user_details = []
        for user_id in active_users:
            user_obj = User.query.get(user_id)
            if user_obj:
                user_details.append({
                    'user_id': user_id,
                    'email': user_obj.email,
                    'last_seen': datetime.utcnow().isoformat()  # In real implementation, track actual last seen
                })
        
        return jsonify({
            'success': True,
            'workspace_id': workspace_id,
            'active_users': user_details,
            'total_active': len(active_users)
        }), 200
        
    except Exception as e:
        logger.error(f"Get workspace presence endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@realtime.route('/documents/<int:document_id>/editors', methods=['GET'])
@api_key_required
def get_document_editors(document_id):
    """
    Get current editors for a document.
    
    Args:
        document_id: ID of the document
        
    Response:
        - editors: List of editor user IDs
        - total_editors: Total number of editors
    """
    try:
        # Get current user
        user = g.current_user
        
        # Verify document access
        document = WorkspaceDocument.query.get(document_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        member = WorkspaceMember.query.filter_by(
            workspace_id=document.workspace_id,
            user_id=user.id
        ).first()
        
        if not member:
            return jsonify({'error': 'Access denied to document'}), 403
        
        # Get editor information
        editors = realtime_manager.get_document_editors(document_id)
        
        # Get user details for editors
        editor_details = []
        for user_id in editors:
            user_obj = User.query.get(user_id)
            if user_obj:
                editor_details.append({
                    'user_id': user_id,
                    'email': user_obj.email,
                    'started_editing': datetime.utcnow().isoformat()  # In real implementation, track actual start time
                })
        
        return jsonify({
            'success': True,
            'document_id': document_id,
            'editors': editor_details,
            'total_editors': len(editors)
        }), 200
        
    except Exception as e:
        logger.error(f"Get document editors endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==============================================================================
# COLLABORATION NOTIFICATION ENDPOINTS
# ==============================================================================

@realtime.route('/workspaces/<int:workspace_id>/notify', methods=['POST'])
@api_key_required
def send_workspace_notification(workspace_id):
    """
    Send a notification to all users in a workspace.
    
    Args:
        workspace_id: ID of the workspace
        
    Request:
        - message: Notification message
        - type: Notification type (info, warning, success, error)
        - data: Optional additional data
        
    Response:
        - message: Success message
    """
    try:
        # Get current user
        user = g.current_user
        
        # Verify workspace access and permissions
        member = WorkspaceMember.query.filter_by(
            workspace_id=workspace_id,
            user_id=user.id
        ).first()
        
        if not member:
            return jsonify({'error': 'Access denied to workspace'}), 403
        
        # Only admins and owners can send notifications
        if member.role not in ['admin', 'owner']:
            return jsonify({'error': 'Insufficient permissions to send notifications'}), 403
        
        # Get request data
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Notification message is required'}), 400
        
        message = data['message']
        notification_type = data.get('type', 'info')
        additional_data = data.get('data', {})
        
        # Create notification
        notification = {
            'workspace_id': workspace_id,
            'sender_id': user.id,
            'sender_email': user.email,
            'message': message,
            'type': notification_type,
            'data': additional_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Broadcast notification
        realtime_manager.broadcast_workspace_notification(workspace_id, notification)
        
        logger.info(f"User {user.id} sent notification to workspace {workspace_id}")
        
        return jsonify({
            'success': True,
            'message': 'Notification sent successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Send workspace notification endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@realtime.route('/documents/<int:document_id>/notify', methods=['POST'])
@api_key_required
def send_document_notification(document_id):
    """
    Send a notification to all users editing a document.
    
    Args:
        document_id: ID of the document
        
    Request:
        - message: Notification message
        - type: Notification type (info, warning, success, error)
        - data: Optional additional data
        
    Response:
        - message: Success message
    """
    try:
        # Get current user
        user = g.current_user
        
        # Verify document access
        document = WorkspaceDocument.query.get(document_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        member = WorkspaceMember.query.filter_by(
            workspace_id=document.workspace_id,
            user_id=user.id
        ).first()
        
        if not member:
            return jsonify({'error': 'Access denied to document'}), 403
        
        # Get request data
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Notification message is required'}), 400
        
        message = data['message']
        notification_type = data.get('type', 'info')
        additional_data = data.get('data', {})
        
        # Create notification
        notification = {
            'document_id': document_id,
            'sender_id': user.id,
            'sender_email': user.email,
            'message': message,
            'type': notification_type,
            'data': additional_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Broadcast notification
        realtime_manager.broadcast_document_notification(document_id, notification)
        
        logger.info(f"User {user.id} sent notification to document {document_id}")
        
        return jsonify({
            'success': True,
            'message': 'Notification sent successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Send document notification endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==============================================================================
# COLLABORATIVE ANALYSIS ENDPOINTS
# ==============================================================================

@realtime.route('/workspaces/<int:workspace_id>/analysis', methods=['POST'])
@api_key_required
def share_collaborative_analysis(workspace_id):
    """
    Share analysis results with workspace members.
    
    Args:
        workspace_id: ID of the workspace
        
    Request:
        - analysis_data: Analysis results to share
        - title: Analysis title
        - description: Analysis description
        
    Response:
        - message: Success message
    """
    try:
        # Get current user
        user = g.current_user
        
        # Verify workspace access
        member = WorkspaceMember.query.filter_by(
            workspace_id=workspace_id,
            user_id=user.id
        ).first()
        
        if not member:
            return jsonify({'error': 'Access denied to workspace'}), 403
        
        # Get request data
        data = request.get_json()
        if not data or 'analysis_data' not in data:
            return jsonify({'error': 'Analysis data is required'}), 400
        
        analysis_data = data['analysis_data']
        title = data.get('title', 'Shared Analysis')
        description = data.get('description', '')
        
        # Create analysis share
        analysis_share = {
            'workspace_id': workspace_id,
            'sharer_id': user.id,
            'sharer_email': user.email,
            'title': title,
            'description': description,
            'analysis_data': analysis_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Broadcast analysis to workspace
        room = f"workspace_{workspace_id}"
        socketio.emit(CollaborationEvents.ANALYSIS_SHARED, analysis_share, room=room)
        
        logger.info(f"User {user.id} shared analysis in workspace {workspace_id}")
        
        return jsonify({
            'success': True,
            'message': 'Analysis shared successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Share collaborative analysis endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==============================================================================
# WEBSOCKET CONNECTION MANAGEMENT
# ==============================================================================

@realtime.route('/connection/status', methods=['GET'])
@api_key_required
def get_connection_status():
    """
    Get WebSocket connection status and configuration.
    
    Response:
        - connected: Whether WebSocket is connected
        - server_url: WebSocket server URL
        - events: Available event types
    """
    try:
        # Get current user
        user = g.current_user
        
        return jsonify({
            'success': True,
            'connection': {
                'user_id': user.id,
                'connected': True,  # This would be determined by actual WebSocket state
                'server_url': f"ws://{request.host}/socket.io/",
                'events': {
                    'workspace_events': [
                        CollaborationEvents.JOIN_WORKSPACE,
                        CollaborationEvents.LEAVE_WORKSPACE,
                        CollaborationEvents.USER_JOINED_WORKSPACE,
                        CollaborationEvents.USER_LEFT_WORKSPACE,
                        CollaborationEvents.WORKSPACE_PRESENCE,
                        CollaborationEvents.WORKSPACE_NOTIFICATION
                    ],
                    'document_events': [
                        CollaborationEvents.START_EDITING_DOCUMENT,
                        CollaborationEvents.STOP_EDITING_DOCUMENT,
                        CollaborationEvents.USER_STARTED_EDITING,
                        CollaborationEvents.USER_STOPPED_EDITING,
                        CollaborationEvents.DOCUMENT_EDITORS,
                        CollaborationEvents.DOCUMENT_CHANGE,
                        CollaborationEvents.DOCUMENT_CHANGED,
                        CollaborationEvents.CURSOR_POSITION,
                        CollaborationEvents.CURSOR_MOVED,
                        CollaborationEvents.DOCUMENT_NOTIFICATION
                    ],
                    'analysis_events': [
                        CollaborationEvents.COLLABORATIVE_ANALYSIS,
                        CollaborationEvents.ANALYSIS_SHARED
                    ]
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get connection status endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==============================================================================
# ERROR HANDLERS
# ==============================================================================

@realtime.errorhandler(404)
def not_found(e):
    """Handle not found errors."""
    return jsonify({
        'error': 'Resource not found',
        'message': 'The requested resource could not be found'
    }), 404

@realtime.errorhandler(403)
def forbidden(e):
    """Handle forbidden errors."""
    return jsonify({
        'error': 'Access forbidden',
        'message': 'You do not have permission to access this resource'
    }), 403

# ==============================================================================
# WEBSOCKET EVENT HANDLERS (These are handled by the RealtimeCollaborationManager)
# ==============================================================================

# Note: The actual WebSocket event handlers are defined in the RealtimeCollaborationManager
# class in app/collaboration/realtime.py. This file provides the HTTP API endpoints
# for managing real-time collaboration features.
