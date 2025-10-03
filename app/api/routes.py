# ==============================================================================
# app/api/routes.py -- COMPLETE VERSION (Strikes 2 & 3)
# The core service entrance. Protected by API keys.
# ==============================================================================

from flask import Blueprint, jsonify, request
from functools import wraps
from app import db
from app.models import APIKey, User
import base64

api = Blueprint('api', __name__)

# We'll import celery lazily inside functions to avoid circular import
def get_celery_app():
    """Lazy import of celery to avoid circular dependency."""
    from celery_worker import celery
    return celery

# ==============================================================================
# STRIKE 2: The Guard - Bulletproof API Key Protection
# ==============================================================================
def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Look for the key in the 'X-API-KEY' header
        provided_key = request.headers.get('X-API-KEY')
        if not provided_key:
            return jsonify({'error': 'Missing API key. Include X-API-KEY in request headers.'}), 401

        # Search for a matching key in the database
        active_keys = APIKey.query.filter_by(is_active=True).all()
        
        valid_key_record = None
        for key_record in active_keys:
            if key_record.check_key(provided_key):
                valid_key_record = key_record
                break
        
        if valid_key_record:
            # Store the authenticated user in the request context
            request.current_user = valid_key_record.owner
            return f(*args, **kwargs)
        
        return jsonify({'error': 'Invalid or inactive API key.'}), 401
    
    return decorated_function

# ==============================================================================
# The Armory: Key Generation Route (FOR TESTING/ADMIN USE)
# ==============================================================================
@api.route('/generate-key/<int:user_id>', methods=['POST'])
def generate_key(user_id):
    """Generates a new API key for a given user. FOR TESTING ONLY."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    new_key_str, hashed_key = APIKey.generate_key()
    
    new_api_key = APIKey(user_id=user.id)
    new_api_key.key_hash = hashed_key
    
    db.session.add(new_api_key)
    db.session.commit()
    
    # IMPORTANT: Show the user the key ONCE. It cannot be recovered.
    return jsonify({
        'message': 'API key generated successfully. Store it securely!',
        'api_key': new_key_str,
        'user_email': user.email
    }), 201

# ==============================================================================
# STRIKE 3: The Core Analysis Endpoints
# ==============================================================================

@api.route('/analyze/start', methods=['POST'])
@api_key_required
def start_analysis():
    """
    The main entrance to the CLARITY Engine.
    Accepts files and a directive, dispatches the analysis task.
    """
    # Extract the user's directive
    user_directive = request.form.get('directive', '')
    
    # Extract uploaded files
    uploaded_files = request.files.getlist('files')
    if not uploaded_files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    # Process files into the format our Celery task expects
    files_data = []
    for file in uploaded_files:
        content_bytes = file.read()
        content_base64 = base64.b64encode(content_bytes).decode('utf-8')
        
        files_data.append({
            'filename': file.filename,
            'content_base64': content_base64,
            'content_type': file.content_type
        })
    
    # Dispatch the background task
    from app.tasks import run_clarity_analysis
    task = run_clarity_analysis.delay(user_directive, files_data)
    
    return jsonify({
        'message': 'Analysis initiated',
        'job_id': task.id,
        'status_url': f'/api/analyze/status/{task.id}'
    }), 202  # 202 = Accepted (processing in background)


@api.route('/analyze/status/<job_id>', methods=['GET'])
@api_key_required
def check_analysis_status(job_id):
    """
    Check the status of a background analysis job.
    """
    from celery.result import AsyncResult
    task = AsyncResult(job_id, app=celery_app)
    
    if task.state == 'PENDING':
        response = {'state': task.state, 'status': 'Task is queued...'}
    elif task.state == 'PROCESSING':
        response = {'state': task.state, 'status': 'Analysis in progress...'}
    elif task.state == 'SUCCESS':
        response = {'state': task.state, 'result': task.result}
    elif task.state == 'FAILURE':
        response = {'state': task.state, 'error': str(task.info)}
    else:
        response = {'state': task.state, 'status': 'Unknown state'}
    
    return jsonify(response)


# ==============================================================================
# Protected Endpoint Example (Keep for testing)
# ==============================================================================
@api.route('/test-protected')
@api_key_required
def test_protected_route():
    """An example of an endpoint protected by our decorator."""
    return jsonify({
        'message': 'Success! You have accessed a protected route.',
        'authenticated_user': request.current_user.email
    })
