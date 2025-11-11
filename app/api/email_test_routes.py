"""
Email Delivery Test Routes - Verify email system works
"""

from flask import Blueprint, jsonify, request
from app.email_service import EmailService
import logging

logger = logging.getLogger(__name__)

email_test = Blueprint('email_test', __name__)

@email_test.route('/test/email/send', methods=['POST'])
def test_send_email():
    """
    TEST ENDPOINT - Send a test email
    
    POST /test/email/send
    Body: {
        "to_email": "test@example.com",
        "test_type": "analysis" | "funding" | "task"
    }
    """
    data = request.get_json() or {}
    
    to_email = data.get('to_email')
    test_type = data.get('test_type', 'analysis')
    
    if not to_email:
        return jsonify({
            'error': 'Please provide to_email'
        }), 400
    
    # Validate email format
    if '@' not in to_email or '.' not in to_email:
        return jsonify({
            'error': 'Invalid email format'
        }), 400
    
    email_service = EmailService()
    
    # Check if email is configured
    if not email_service.enabled:
        return jsonify({
            'success': False,
            'message': 'Email service not configured',
            'details': {
                'mail_username_set': bool(email_service.mail_username),
                'mail_password_set': bool(email_service.mail_password),
                'instructions': 'Set MAIL_USERNAME and MAIL_PASSWORD in your .env file'
            }
        }), 200
    
    # Send test email based on type
    try:
        if test_type == 'analysis':
            success = email_service.send_analysis_complete(
                user_email=to_email,
                analysis_id='TEST-123',
                domain='Legal Intelligence',
                result_summary='This is a test email from CLARITY Engine. If you receive this, email delivery is working!',
                confidence_score=0.95,
                download_url='https://clarity-engine-auto.vercel.app/work'
            )
        elif test_type == 'funding':
            success = email_service.send_funding_complete(
                user_email=to_email,
                project_name='Test Project',
                documents_count=14,
                download_url='https://clarity-engine-auto.vercel.app/funding'
            )
        elif test_type == 'task':
            success = email_service.send_task_submitted(
                user_email=to_email,
                task_type='test',
                task_id='TEST-456',
                estimated_time='5-15 minutes'
            )
        else:
            return jsonify({
                'error': 'Invalid test_type. Use: analysis, funding, or task'
            }), 400
        
        if success:
            return jsonify({
                'success': True,
                'message': f'✅ Test email sent successfully to {to_email}',
                'test_type': test_type,
                'check_inbox': 'Check your inbox (and spam folder) for the test email'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Email sending failed',
                'details': 'Check server logs for error details'
            }), 500
            
    except Exception as e:
        logger.error(f"Email test failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Email sending failed. Check credentials and server configuration.'
        }), 500


@email_test.route('/test/email/config', methods=['GET'])
def check_email_config():
    """
    Check email configuration status
    """
    email_service = EmailService()
    
    return jsonify({
        'email_delivery_enabled': email_service.enabled,
        'mail_server': email_service.mail_server,
        'mail_port': email_service.mail_port,
        'mail_username_set': bool(email_service.mail_username),
        'mail_password_set': bool(email_service.mail_password),
        'mail_sender': email_service.mail_sender,
        'status': 'configured' if email_service.enabled else 'not_configured',
        'instructions': {
            'step1': 'Get Gmail App Password: https://myaccount.google.com/apppasswords',
            'step2': 'Add to .env file: MAIL_USERNAME=your-email@gmail.com',
            'step3': 'Add to .env file: MAIL_PASSWORD=your-app-password',
            'step4': 'Restart the backend server',
            'step5': 'Test with: POST /test/email/send'
        }
    }), 200
