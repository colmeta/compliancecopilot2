# ==============================================================================
# app/collaboration/realtime.py
# Real-Time Collaboration System - The Live Intelligence Hub
# ==============================================================================
"""
This module provides real-time collaboration features for CLARITY.
Handles live document editing, presence awareness, and collaborative analysis.
"""

import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from app.models import User, Workspace, WorkspaceMember, WorkspaceDocument
from app import db

logger = logging.getLogger(__name__)

# ==============================================================================
# REAL-TIME COLLABORATION MANAGER
# ==============================================================================

class RealtimeCollaborationManager:
    """
    Manages real-time collaboration features including live editing and presence.
    """
    
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.logger = logging.getLogger(__name__)
        
        # Track active users and their locations
        self.active_users: Dict[int, Dict[str, Any]] = {}
        self.document_editors: Dict[int, Set[int]] = {}  # document_id -> set of user_ids
        self.workspace_presence: Dict[int, Set[int]] = {}  # workspace_id -> set of user_ids
        
        # Setup event handlers
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Setup SocketIO event handlers."""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle user connection."""
            self.logger.info(f"User connected: {request.sid}")
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle user disconnection."""
            self.logger.info(f"User disconnected: {request.sid}")
            self._handle_user_disconnect(request.sid)
        
        @self.socketio.on('join_workspace')
        def handle_join_workspace(data):
            """Handle user joining a workspace."""
            try:
                workspace_id = data.get('workspace_id')
                user_id = data.get('user_id')
                
                if not workspace_id or not user_id:
                    emit('error', {'message': 'Missing workspace_id or user_id'})
                    return
                
                # Verify user has access to workspace
                if not self._verify_workspace_access(workspace_id, user_id):
                    emit('error', {'message': 'Access denied to workspace'})
                    return
                
                # Join workspace room
                room = f"workspace_{workspace_id}"
                join_room(room)
                
                # Update presence tracking
                self._update_workspace_presence(workspace_id, user_id, True)
                
                # Notify other users
                emit('user_joined_workspace', {
                    'user_id': user_id,
                    'workspace_id': workspace_id,
                    'timestamp': datetime.utcnow().isoformat()
                }, room=room, include_self=False)
                
                # Send current workspace presence
                current_users = self.workspace_presence.get(workspace_id, set())
                emit('workspace_presence', {
                    'workspace_id': workspace_id,
                    'active_users': list(current_users)
                })
                
                self.logger.info(f"User {user_id} joined workspace {workspace_id}")
                
            except Exception as e:
                self.logger.error(f"Error joining workspace: {e}")
                emit('error', {'message': 'Failed to join workspace'})
        
        @self.socketio.on('leave_workspace')
        def handle_leave_workspace(data):
            """Handle user leaving a workspace."""
            try:
                workspace_id = data.get('workspace_id')
                user_id = data.get('user_id')
                
                if not workspace_id or not user_id:
                    return
                
                # Leave workspace room
                room = f"workspace_{workspace_id}"
                leave_room(room)
                
                # Update presence tracking
                self._update_workspace_presence(workspace_id, user_id, False)
                
                # Notify other users
                emit('user_left_workspace', {
                    'user_id': user_id,
                    'workspace_id': workspace_id,
                    'timestamp': datetime.utcnow().isoformat()
                }, room=room, include_self=False)
                
                self.logger.info(f"User {user_id} left workspace {workspace_id}")
                
            except Exception as e:
                self.logger.error(f"Error leaving workspace: {e}")
        
        @self.socketio.on('start_editing_document')
        def handle_start_editing_document(data):
            """Handle user starting to edit a document."""
            try:
                document_id = data.get('document_id')
                user_id = data.get('user_id')
                
                if not document_id or not user_id:
                    emit('error', {'message': 'Missing document_id or user_id'})
                    return
                
                # Verify user has access to document
                if not self._verify_document_access(document_id, user_id):
                    emit('error', {'message': 'Access denied to document'})
                    return
                
                # Add user to document editors
                if document_id not in self.document_editors:
                    self.document_editors[document_id] = set()
                
                self.document_editors[document_id].add(user_id)
                
                # Join document room
                room = f"document_{document_id}"
                join_room(room)
                
                # Notify other editors
                emit('user_started_editing', {
                    'document_id': document_id,
                    'user_id': user_id,
                    'timestamp': datetime.utcnow().isoformat()
                }, room=room, include_self=False)
                
                # Send current editors
                current_editors = self.document_editors.get(document_id, set())
                emit('document_editors', {
                    'document_id': document_id,
                    'editors': list(current_editors)
                })
                
                self.logger.info(f"User {user_id} started editing document {document_id}")
                
            except Exception as e:
                self.logger.error(f"Error starting document edit: {e}")
                emit('error', {'message': 'Failed to start editing document'})
        
        @self.socketio.on('stop_editing_document')
        def handle_stop_editing_document(data):
            """Handle user stopping document editing."""
            try:
                document_id = data.get('document_id')
                user_id = data.get('user_id')
                
                if not document_id or not user_id:
                    return
                
                # Remove user from document editors
                if document_id in self.document_editors:
                    self.document_editors[document_id].discard(user_id)
                
                # Leave document room
                room = f"document_{document_id}"
                leave_room(room)
                
                # Notify other editors
                emit('user_stopped_editing', {
                    'document_id': document_id,
                    'user_id': user_id,
                    'timestamp': datetime.utcnow().isoformat()
                }, room=room, include_self=False)
                
                self.logger.info(f"User {user_id} stopped editing document {document_id}")
                
            except Exception as e:
                self.logger.error(f"Error stopping document edit: {e}")
        
        @self.socketio.on('document_change')
        def handle_document_change(data):
            """Handle document content changes."""
            try:
                document_id = data.get('document_id')
                user_id = data.get('user_id')
                change_data = data.get('change')
                
                if not document_id or not user_id or not change_data:
                    return
                
                # Verify user is editing the document
                if document_id not in self.document_editors or user_id not in self.document_editors[document_id]:
                    emit('error', {'message': 'Not authorized to edit this document'})
                    return
                
                # Broadcast change to other editors
                room = f"document_{document_id}"
                emit('document_changed', {
                    'document_id': document_id,
                    'user_id': user_id,
                    'change': change_data,
                    'timestamp': datetime.utcnow().isoformat()
                }, room=room, include_self=False)
                
            except Exception as e:
                self.logger.error(f"Error handling document change: {e}")
        
        @self.socketio.on('cursor_position')
        def handle_cursor_position(data):
            """Handle cursor position updates."""
            try:
                document_id = data.get('document_id')
                user_id = data.get('user_id')
                position = data.get('position')
                
                if not document_id or not user_id or position is None:
                    return
                
                # Verify user is editing the document
                if document_id not in self.document_editors or user_id not in self.document_editors[document_id]:
                    return
                
                # Broadcast cursor position to other editors
                room = f"document_{document_id}"
                emit('cursor_moved', {
                    'document_id': document_id,
                    'user_id': user_id,
                    'position': position,
                    'timestamp': datetime.utcnow().isoformat()
                }, room=room, include_self=False)
                
            except Exception as e:
                self.logger.error(f"Error handling cursor position: {e}")
        
        @self.socketio.on('collaborative_analysis')
        def handle_collaborative_analysis(data):
            """Handle collaborative analysis requests."""
            try:
                workspace_id = data.get('workspace_id')
                user_id = data.get('user_id')
                analysis_data = data.get('analysis')
                
                if not workspace_id or not user_id or not analysis_data:
                    emit('error', {'message': 'Missing required data'})
                    return
                
                # Verify user has access to workspace
                if not self._verify_workspace_access(workspace_id, user_id):
                    emit('error', {'message': 'Access denied to workspace'})
                    return
                
                # Broadcast analysis to workspace
                room = f"workspace_{workspace_id}"
                emit('analysis_shared', {
                    'workspace_id': workspace_id,
                    'user_id': user_id,
                    'analysis': analysis_data,
                    'timestamp': datetime.utcnow().isoformat()
                }, room=room, include_self=False)
                
                self.logger.info(f"User {user_id} shared analysis in workspace {workspace_id}")
                
            except Exception as e:
                self.logger.error(f"Error handling collaborative analysis: {e}")
                emit('error', {'message': 'Failed to share analysis'})
    
    def _handle_user_disconnect(self, sid: str):
        """Handle user disconnection cleanup."""
        try:
            # Find user by session ID and clean up
            for user_id, user_data in self.active_users.items():
                if user_data.get('session_id') == sid:
                    # Remove from all workspaces
                    for workspace_id in list(self.workspace_presence.keys()):
                        self._update_workspace_presence(workspace_id, user_id, False)
                    
                    # Remove from all documents
                    for document_id in list(self.document_editors.keys()):
                        self.document_editors[document_id].discard(user_id)
                    
                    # Remove from active users
                    del self.active_users[user_id]
                    break
                    
        except Exception as e:
            self.logger.error(f"Error handling user disconnect: {e}")
    
    def _update_workspace_presence(self, workspace_id: int, user_id: int, is_present: bool):
        """Update workspace presence tracking."""
        if workspace_id not in self.workspace_presence:
            self.workspace_presence[workspace_id] = set()
        
        if is_present:
            self.workspace_presence[workspace_id].add(user_id)
        else:
            self.workspace_presence[workspace_id].discard(user_id)
    
    def _verify_workspace_access(self, workspace_id: int, user_id: int) -> bool:
        """Verify user has access to workspace."""
        try:
            member = WorkspaceMember.query.filter_by(
                workspace_id=workspace_id,
                user_id=user_id
            ).first()
            return member is not None
        except Exception:
            return False
    
    def _verify_document_access(self, document_id: int, user_id: int) -> bool:
        """Verify user has access to document."""
        try:
            document = WorkspaceDocument.query.get(document_id)
            if not document:
                return False
            
            # Check workspace access
            return self._verify_workspace_access(document.workspace_id, user_id)
        except Exception:
            return False
    
    def get_workspace_presence(self, workspace_id: int) -> List[int]:
        """Get list of active users in workspace."""
        return list(self.workspace_presence.get(workspace_id, set()))
    
    def get_document_editors(self, document_id: int) -> List[int]:
        """Get list of users editing a document."""
        return list(self.document_editors.get(document_id, set()))
    
    def broadcast_workspace_notification(self, workspace_id: int, notification: Dict[str, Any]):
        """Broadcast notification to all users in workspace."""
        try:
            room = f"workspace_{workspace_id}"
            self.socketio.emit('workspace_notification', notification, room=room)
        except Exception as e:
            self.logger.error(f"Error broadcasting workspace notification: {e}")
    
    def broadcast_document_notification(self, document_id: int, notification: Dict[str, Any]):
        """Broadcast notification to all users editing a document."""
        try:
            room = f"document_{document_id}"
            self.socketio.emit('document_notification', notification, room=room)
        except Exception as e:
            self.logger.error(f"Error broadcasting document notification: {e}")

# ==============================================================================
# COLLABORATION EVENTS
# ==============================================================================

class CollaborationEvents:
    """Static class for collaboration event constants."""
    
    # Connection events
    CONNECT = 'connect'
    DISCONNECT = 'disconnect'
    
    # Workspace events
    JOIN_WORKSPACE = 'join_workspace'
    LEAVE_WORKSPACE = 'leave_workspace'
    USER_JOINED_WORKSPACE = 'user_joined_workspace'
    USER_LEFT_WORKSPACE = 'user_left_workspace'
    WORKSPACE_PRESENCE = 'workspace_presence'
    WORKSPACE_NOTIFICATION = 'workspace_notification'
    
    # Document events
    START_EDITING_DOCUMENT = 'start_editing_document'
    STOP_EDITING_DOCUMENT = 'stop_editing_document'
    USER_STARTED_EDITING = 'user_started_editing'
    USER_STOPPED_EDITING = 'user_stopped_editing'
    DOCUMENT_EDITORS = 'document_editors'
    DOCUMENT_CHANGE = 'document_change'
    DOCUMENT_CHANGED = 'document_changed'
    CURSOR_POSITION = 'cursor_position'
    CURSOR_MOVED = 'cursor_moved'
    DOCUMENT_NOTIFICATION = 'document_notification'
    
    # Analysis events
    COLLABORATIVE_ANALYSIS = 'collaborative_analysis'
    ANALYSIS_SHARED = 'analysis_shared'
    
    # Error events
    ERROR = 'error'

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def create_realtime_manager(socketio: SocketIO) -> RealtimeCollaborationManager:
    """Create and initialize a real-time collaboration manager."""
    return RealtimeCollaborationManager(socketio)

def get_workspace_room(workspace_id: int) -> str:
    """Get room name for workspace."""
    return f"workspace_{workspace_id}"

def get_document_room(document_id: int) -> str:
    """Get room name for document."""
    return f"document_{document_id}"
