# ==============================================================================
# app/vault/routes.py
# Intelligence Vault API Routes - Document Ingestion & Management
# ==============================================================================
"""
This module handles all Intelligence Vault operations:
- Document upload and ingestion
- Vault statistics and management
- Document search and retrieval
- Vault cleanup and maintenance

All endpoints require authentication and API key validation.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
import base64
import io
from app.vector_store import get_vector_store
from app.tasks import index_document_task
from app.api.routes import api_key_required
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create vault blueprint
vault = Blueprint('vault', __name__)


def vault_api_key_required(f):
    """
    Decorator that requires both login and API key for vault operations.
    This ensures maximum security for the Intelligence Vault.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check API key
        provided_key = request.headers.get('X-API-KEY')
        if not provided_key:
            return jsonify({'error': 'API key required for vault operations'}), 401
        
        # Import here to avoid circular imports
        from app.models import APIKey
        
        # Verify API key belongs to current user
        user_keys = APIKey.query.filter_by(user_id=current_user.id, is_active=True).all()
        valid_key = False
        
        for key_record in user_keys:
            if key_record.check_key(provided_key):
                valid_key = True
                break
        
        if not valid_key:
            return jsonify({'error': 'Invalid or inactive API key'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


@vault.route('/add', methods=['POST'])
@vault_api_key_required
def add_document():
    """
    Upload and index a document into the user's Intelligence Vault.
    
    This endpoint accepts file uploads and triggers background indexing.
    The document will be chunked, embedded, and stored in the user's private vault.
    
    Request:
        - files: One or more files (PDF, DOCX, TXT, etc.)
        - metadata: Optional JSON metadata for the document
        - source: Optional source identifier
    
    Response:
        - job_id: Celery task ID for tracking indexing progress
        - message: Status message
        - document_count: Number of files queued for indexing
    """
    try:
        # Get uploaded files
        uploaded_files = request.files.getlist('files')
        if not uploaded_files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        # Get optional metadata
        metadata = request.form.get('metadata', '{}')
        source = request.form.get('source', 'unknown')
        
        # Process files
        files_data = []
        for file in uploaded_files:
            if file.filename == '':
                continue
                
            # Read file content
            content_bytes = file.read()
            content_base64 = base64.b64encode(content_bytes).decode('utf-8')
            
            files_data.append({
                'filename': file.filename,
                'content_base64': content_base64,
                'content_type': file.content_type,
                'source': source,
                'metadata': metadata
            })
        
        if not files_data:
            return jsonify({'error': 'No valid files to process'}), 400
        
        # Dispatch indexing task
        task = index_document_task.delay(
            user_id=current_user.id,
            files_data=files_data
        )
        
        logger.info(f"Queued {len(files_data)} files for indexing for user {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': f'Queued {len(files_data)} files for indexing',
            'job_id': task.id,
            'document_count': len(files_data),
            'status_url': f'/vault/status/{task.id}'
        }), 202
        
    except Exception as e:
        logger.error(f"Error in add_document for user {current_user.id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vault.route('/status/<job_id>', methods=['GET'])
@vault_api_key_required
def check_indexing_status(job_id):
    """
    Check the status of a document indexing job.
    
    Args:
        job_id: Celery task ID
        
    Returns:
        Job status and result information
    """
    try:
        from celery.result import AsyncResult
        # Lazy import to avoid circular dependency
        from celery_worker import celery as celery_app
        
        task = AsyncResult(job_id, app=celery_app)
        
        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'status': 'Document indexing queued...',
                'progress': 0
            }
        elif task.state == 'PROCESSING':
            response = {
                'state': task.state,
                'status': 'Indexing documents...',
                'progress': 50
            }
        elif task.state == 'SUCCESS':
            result = task.result
            response = {
                'state': task.state,
                'status': 'Indexing completed successfully',
                'progress': 100,
                'result': result
            }
        elif task.state == 'FAILURE':
            response = {
                'state': task.state,
                'status': 'Indexing failed',
                'progress': 0,
                'error': str(task.info)
            }
        else:
            response = {
                'state': task.state,
                'status': 'Unknown state',
                'progress': 0
            }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error checking indexing status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vault.route('/search', methods=['POST'])
@vault_api_key_required
def search_vault():
    """
    Search the user's Intelligence Vault for similar documents.
    
    This is the core RAG retrieval function that will be used
    to augment AI prompts with relevant context.
    
    Request:
        - query: Search query text
        - n_results: Number of results to return (default: 5)
        - filter: Optional metadata filter
    
    Response:
        - documents: List of similar document chunks
        - metadatas: List of metadata for each document
        - distances: Similarity scores
    """
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query text required'}), 400
        
        query = data['query']
        n_results = data.get('n_results', 5)
        filter_metadata = data.get('filter', None)
        
        # Search the vault
        store = get_vector_store()
        results = store.query_similar_documents(
            user_id=current_user.id,
            query_text=query,
            n_results=n_results,
            filter_metadata=filter_metadata
        )
        
        if not results['success']:
            return jsonify({
                'success': False,
                'error': results['error']
            }), 500
        
        return jsonify({
            'success': True,
            'query': query,
            'documents': results['documents'],
            'metadatas': results['metadatas'],
            'distances': results['distances'],
            'ids': results['ids'],
            'count': len(results['documents'])
        })
        
    except Exception as e:
        logger.error(f"Error searching vault for user {current_user.id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vault.route('/stats', methods=['GET'])
@vault_api_key_required
def get_vault_stats():
    """
    Get statistics about the user's Intelligence Vault.
    
    Returns:
        - collection_name: User's collection name
        - document_count: Number of documents in vault
        - user_id: User ID
        - last_updated: Last modification time
    """
    try:
        store = get_vector_store()
        stats = store.get_collection_stats(current_user.id)
        
        if not stats['success']:
            return jsonify({
                'success': False,
                'error': stats['error']
            }), 500
        
        return jsonify({
            'success': True,
            'vault_stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting vault stats for user {current_user.id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vault.route('/clear', methods=['POST'])
@vault_api_key_required
def clear_vault():
    """
    Clear the user's entire Intelligence Vault.
    
    WARNING: This action is irreversible!
    All documents and embeddings will be permanently deleted.
    
    Request:
        - confirm: Must be "DELETE_ALL_DATA" to confirm
    
    Response:
        - success: Operation status
        - message: Confirmation message
    """
    try:
        data = request.get_json()
        if not data or data.get('confirm') != 'DELETE_ALL_DATA':
            return jsonify({
                'error': 'Confirmation required. Send {"confirm": "DELETE_ALL_DATA"}'
            }), 400
        
        store = get_vector_store()
        result = store.delete_user_collection(current_user.id)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
        logger.warning(f"User {current_user.id} cleared their Intelligence Vault")
        
        return jsonify({
            'success': True,
            'message': 'Intelligence Vault cleared successfully',
            'user_id': current_user.id
        })
        
    except Exception as e:
        logger.error(f"Error clearing vault for user {current_user.id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vault.route('/health', methods=['GET'])
def vault_health():
    """
    Check the health of the Intelligence Vault system.
    
    This endpoint is public and can be used for monitoring.
    
    Returns:
        - status: System status
        - vector_store: ChromaDB connection status
        - embedding_model: Model status
    """
    try:
        store = get_vector_store()
        
        # Test vector store connection
        test_stats = store.get_collection_stats(0)  # Test with user 0
        
        return jsonify({
            'status': 'healthy',
            'vector_store': 'connected',
            'embedding_model': 'loaded',
            'chroma_host': current_app.config.get('CHROMA_HOST', 'localhost'),
            'chroma_port': current_app.config.get('CHROMA_PORT', 8000)
        })
        
    except Exception as e:
        logger.error(f"Vault health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
