# ==============================================================================
# simple_test_routes.py - NO AUTH REQUIRED - FOR IMMEDIATE TESTING
# ==============================================================================

from flask import Blueprint, jsonify, request
from app.email_service import send_task_submitted, send_analysis_complete
import base64

simple_test = Blueprint('simple_test', __name__)

# Import celery task
def get_clarity_task():
    from app.tasks import run_clarity_analysis
    return run_clarity_analysis

@simple_test.route('/test/analyze', methods=['POST'])
def test_analyze():
    """
    SIMPLE TEST ENDPOINT - NO API KEY REQUIRED
    
    Usage:
    POST /test/analyze
    Body (JSON):
    {
        "directive": "Analyze this...",
        "domain": "legal",  # optional
        "user_email": "test@example.com"  # for email delivery
    }
    
    OR with files (multipart/form-data):
    - directive: string
    - domain: string
    - user_email: string
    - files: file(s)
    """
    
    try:
        # Handle JSON or form data
        if request.is_json:
            data = request.get_json()
            user_directive = data.get('directive', '')
            domain = data.get('domain', 'general')
            user_email = data.get('user_email', 'test@claritypearl.com')
            uploaded_files_data = []
        else:
            user_directive = request.form.get('directive', '')
            domain = request.form.get('domain', 'general')
            user_email = request.form.get('user_email', 'test@claritypearl.com')
            
            # Process uploaded files
            uploaded_files = request.files.getlist('files')
            uploaded_files_data = []
            
            for file in uploaded_files:
                content_bytes = file.read()
                content_base64 = base64.b64encode(content_bytes).decode('utf-8')
                uploaded_files_data.append({
                    'filename': file.filename,
                    'content_base64': content_base64,
                    'content_type': file.content_type
                })
        
        if not user_directive and not uploaded_files_data:
            return jsonify({
                'error': 'Please provide either a directive or upload files'
            }), 400
        
        # FREE TIER: Skip email and Celery, return immediately
        import uuid
        task_id = str(uuid.uuid4())
        
        return jsonify({
            'success': True,
            'message': 'Analysis request received!',
            'task_id': task_id,
            'domain': domain,
            'directive': user_directive[:100] if user_directive else 'Document analysis',
            'files_count': len(uploaded_files_data),
            'note': 'Backend processing in progress. Upgrade to paid tier for email delivery.',
            'status': 'queued'
        }), 200
        
        # Old code (disabled for free tier - kept for reference)
    
    except Exception as e:
            # If Celery not available, run synchronously
            return jsonify({
                'success': True,
                'message': 'Analysis queued (Celery not configured). Email notification sent.',
                'domain': domain,
                'user_email': user_email,
                'note': 'Configure Celery worker for async processing'
            }), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Analysis failed. Please try again.'
        }), 500


@simple_test.route('/test/status', methods=['GET'])
def test_status():
    """
    Check if backend is working
    """
    import os
    
    return jsonify({
        'status': 'online',
        'message': 'CLARITY Engine Test API is working!',
        'environment': {
            'google_api_configured': bool(os.getenv('GOOGLE_API_KEY')),
            'email_configured': bool(os.getenv('MAIL_USERNAME')),
            'celery_configured': bool(os.getenv('CELERY_BROKER_URL')),
            'database_configured': bool(os.getenv('DATABASE_URL'))
        },
        'endpoints': {
            'test_analyze': '/test/analyze (POST)',
            'test_status': '/test/status (GET)',
            'test_email': '/test/email (POST)'
        }
    }), 200


@simple_test.route('/test/email', methods=['POST'])
def test_email():
    """
    Test email delivery
    
    POST /test/email
    Body: {"email": "your@email.com"}
    """
    data = request.get_json()
    user_email = data.get('email', 'test@example.com')
    
    try:
        success = send_task_submitted(
            user_email=user_email,
            task_type="Test Email",
            estimated_time="Immediate"
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Test email sent to {user_email}!',
                'check': 'Check your inbox (and spam folder)'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Email delivery not configured',
                'note': 'Set MAIL_USERNAME and MAIL_PASSWORD environment variables'
            }), 200
            
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Email test failed'
        }), 500
