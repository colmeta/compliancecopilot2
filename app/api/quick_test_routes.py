# ==============================================================================
# quick_test_routes.py - INSTANT RESPONSE TEST (NO EMAIL, NO CELERY)
# ==============================================================================

from flask import Blueprint, jsonify, request

quick_test = Blueprint('quick_test', __name__)

@quick_test.route('/quick/status', methods=['GET'])
def quick_status():
    """Instant status check"""
    return jsonify({
        'status': 'online',
        'message': 'CLARITY Quick Test API',
        'note': 'This endpoint returns immediately for testing'
    }), 200

@quick_test.route('/quick/test', methods=['POST'])
def quick_analyze():
    """
    INSTANT TEST - Returns immediately, no email, no processing
    
    POST /quick/test
    Body: {"directive": "your task", "domain": "legal"}
    """
    data = request.get_json() or {}
    
    directive = data.get('directive', '')
    domain = data.get('domain', 'general')
    
    if not directive:
        return jsonify({
            'error': 'Please provide a directive'
        }), 400
    
    # Return immediately (no email, no Celery)
    return jsonify({
        'success': True,
        'message': 'Request received!',
        'your_directive': directive,
        'domain': domain,
        'note': 'This is a quick test. Real processing would happen in background.'
    }), 200

@quick_test.route('/quick/domains', methods=['GET'])
def list_domains():
    """List all available domains"""
    domains = [
        {'id': 'legal', 'name': 'Legal Intelligence'},
        {'id': 'financial', 'name': 'Financial Intelligence'},
        {'id': 'security', 'name': 'Security Intelligence'},
        {'id': 'healthcare', 'name': 'Healthcare Intelligence'},
        {'id': 'data-science', 'name': 'Data Science Engine'},
        {'id': 'education', 'name': 'Education Intelligence'},
        {'id': 'proposals', 'name': 'Proposal Writing'},
        {'id': 'ngo', 'name': 'NGO & Impact'},
        {'id': 'data-entry', 'name': 'Data Entry Automation'},
        {'id': 'expenses', 'name': 'Expense Management'},
    ]
    
    return jsonify({
        'domains': domains,
        'total': len(domains)
    }), 200
