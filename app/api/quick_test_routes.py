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
    import uuid
    
    # Simulate a quick analysis response
    analysis_preview = {
        'legal': 'Contract review initiated. Scanning for liability clauses, payment terms, and compliance issues.',
        'financial': 'Financial analysis started. Examining revenue trends, expense patterns, and anomaly detection.',
        'security': 'Security audit in progress. Checking for vulnerabilities, access controls, and compliance gaps.',
        'healthcare': 'Healthcare data review. Analyzing patient records, treatment protocols, and HIPAA compliance.',
        'data-science': 'Data science pipeline initiated. Running statistical analysis and predictive models.',
        'education': 'Education intelligence engaged. Analyzing curriculum alignment and student performance patterns.',
        'proposals': 'Proposal drafting started. Structuring sections, compliance checks, and competitive positioning.',
        'ngo': 'NGO impact assessment. Analyzing program effectiveness and grant alignment.',
        'data-entry': 'Data entry automation active. Extracting structured data from documents.',
        'expenses': 'Expense analysis running. Categorizing transactions and identifying cost-saving opportunities.'
    }
    
    return jsonify({
        'success': True,
        'message': 'CLARITY Analysis Initiated',
        'task_id': str(uuid.uuid4()),
        'domain': domain,
        'directive': directive,
        'preview': analysis_preview.get(domain, 'Analysis in progress...'),
        'estimated_completion': '5-15 minutes',
        'status': 'processing',
        'note': 'Upgrade to paid tier for email delivery and full AI processing.'
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
