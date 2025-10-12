# ==============================================================================
# app/collaboration/__init__.py
# Collaborative Intelligence Package - The Team Intelligence Hub
# ==============================================================================
"""
This package contains collaborative features for CLARITY.
Includes workspace management, document sharing, and real-time collaboration.
"""

from .workspaces import (
    WorkspaceManager,
    create_workspace,
    invite_user_to_workspace,
    get_user_workspaces,
    check_workspace_permissions
)

from .document_sharing import (
    DocumentSharingManager,
    share_document,
    get_shared_documents,
    revoke_document_access
)

__all__ = [
    # Workspace Management
    'WorkspaceManager',
    'create_workspace',
    'invite_user_to_workspace', 
    'get_user_workspaces',
    'check_workspace_permissions',
    
    # Document Sharing
    'DocumentSharingManager',
    'share_document',
    'get_shared_documents',
    'revoke_document_access'
]

