# ==============================================================================
# app/api/routes.py -- COMPLETE VERSION (Strikes 2 & 3)
# The core service entrance. Protected by API keys.
# ==============================================================================

from flask import Blueprint, jsonify, request
from functools import wraps
from app import db, limiter
from app.models import APIKey, User, AnalysisFeedback, FinalizedBriefing
import base64
import json

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
@limiter.limit("10 per minute")  # Rate limit: 10 requests per minute per IP
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
    task = run_clarity_analysis.delay(user_directive, files_data, current_user.id)
    
    return jsonify({
        'message': 'Analysis initiated',
        'job_id': task.id,
        'status_url': f'/api/analyze/status/{task.id}'
    }), 202  # 202 = Accepted (processing in background)


@api.route('/analyze/status/<job_id>', methods=['GET'])
@limiter.limit("30 per minute")  # Rate limit: 30 status checks per minute per IP
@api_key_required
def check_analysis_status(job_id):
    """
    Check the status of a background analysis job.
    """
    from celery.result import AsyncResult
    celery = get_celery_app()
    task = AsyncResult(job_id, app=celery)
    
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


# ==============================================================================
# PHASE 3: HUMAN-AI SYMBIOSIS - FEEDBACK & COLLABORATION ENDPOINTS
# ==============================================================================

@api.route('/feedback', methods=['POST'])
@limiter.limit("20 per minute")  # Rate limit: 20 feedback submissions per minute per IP
@api_key_required
def submit_feedback():
    """
    Submit user feedback on CLARITY analysis results.
    
    This endpoint enables the accountability layer - users can tell us when
    CLARITY is right or wrong, building trust through transparency.
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        job_id = data.get('job_id')
        rating = data.get('rating')
        feedback_text = data.get('feedback_text', '')
        
        if not job_id:
            return jsonify({'error': 'job_id is required'}), 400
        
        if rating not in [1, -1]:
            return jsonify({'error': 'rating must be 1 (thumbs up) or -1 (thumbs down)'}), 400
        
        # Create feedback record
        feedback = AnalysisFeedback(
            job_id=job_id,
            user_id=request.current_user.id,
            rating=rating,
            feedback_text=feedback_text
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully',
            'feedback_id': feedback.id,
            'job_id': job_id,
            'rating': rating
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to submit feedback: {str(e)}'
        }), 500


@api.route('/briefings/finalize', methods=['POST'])
@limiter.limit("10 per minute")  # Rate limit: 10 finalizations per minute per IP
@api_key_required
def finalize_briefing():
    """
    Finalize and save a user-edited briefing.
    
    This endpoint enables the co-worker paradigm - users can edit CLARITY's
    draft and save their final, approved version.
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        job_id = data.get('job_id')
        final_content = data.get('final_content')
        
        if not job_id:
            return jsonify({'error': 'job_id is required'}), 400
        
        if not final_content:
            return jsonify({'error': 'final_content is required'}), 400
        
        # Validate final_content structure
        required_fields = ['executive_summary', 'key_findings', 'actionable_recommendations']
        for field in required_fields:
            if field not in final_content:
                return jsonify({'error': f'final_content must include {field}'}), 400
        
        # Convert final_content to JSON string for storage
        final_content_json = json.dumps(final_content)
        
        # Create finalized briefing record
        finalized_briefing = FinalizedBriefing(
            original_job_id=job_id,
            user_id=request.current_user.id,
            final_content=final_content_json
        )
        
        db.session.add(finalized_briefing)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Briefing finalized and saved successfully',
            'finalized_id': finalized_briefing.id,
            'job_id': job_id,
            'timestamp': finalized_briefing.timestamp.isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to finalize briefing: {str(e)}'
        }), 500
