"""
REAL ANALYSIS ROUTES - No More Simulations
Uses actual Google Gemini AI for all analysis
"""

from flask import Blueprint, jsonify, request
import uuid
from datetime import datetime
import base64
import logging
from app.ai.real_analysis_engine import get_analysis_engine

logger = logging.getLogger(__name__)

real_analysis = Blueprint('real_analysis', __name__)

@real_analysis.route('/real/analyze', methods=['POST'])
def analyze_with_real_ai():
    """
    REAL AI ANALYSIS - Uses Google Gemini (no simulations)
    
    POST /real/analyze
    Body: {
        "directive": "Your analysis request",
        "domain": "legal|financial|security|...",
        "files": [] (optional)
    }
    
    Returns: REAL AI analysis results
    """
    data = request.get_json() or {}
    
    directive = data.get('directive', '').strip()
    domain = data.get('domain', 'general')
    files = data.get('files', [])
    
    if not directive:
        return jsonify({
            'error': 'Directive is required',
            'message': 'Please provide an analysis directive (e.g., "Find liability clauses")'
        }), 400
    
    # Validate domain
    valid_domains = [
        'legal', 'financial', 'security', 'healthcare', 'data-science',
        'education', 'proposals', 'ngo', 'data-entry', 'expenses'
    ]
    
    if domain not in valid_domains:
        return jsonify({
            'error': 'Invalid domain',
            'message': f'Domain must be one of: {", ".join(valid_domains)}',
            'provided': domain
        }), 400
    
    task_id = str(uuid.uuid4())
    
    # Get AI engine
    engine = get_analysis_engine()
    
    if not engine.enabled:
        return jsonify({
            'success': False,
            'error': 'AI Engine not configured',
            'message': 'GOOGLE_API_KEY not set in environment variables',
            'instructions': {
                'step1': 'Get API key from: https://makersuite.google.com/app/apikey',
                'step2': 'Add to .env file: GOOGLE_API_KEY=your_key_here',
                'step3': 'Restart backend server',
                'step4': 'Try again'
            },
            'status': 'not_configured'
        }), 503
    
    try:
        # Call REAL AI analysis
        result = engine.analyze(
            directive=directive,
            domain=domain,
            document_content=None,  # TODO: Extract from files
            files_data=files
        )
        
        if not result.get('success'):
            return jsonify(result), 500
        
        # Return real AI results
        return jsonify({
            'success': True,
            'task_id': task_id,
            'domain': domain,
            'directive': directive,
            'timestamp': datetime.utcnow().isoformat(),
            'analysis': result['analysis'],
            'model': result.get('model', 'gemini-1.5-flash'),
            'status': 'completed',
            'note': '✅ REAL AI ANALYSIS (not simulated)',
            'processing_time': 'Real-time'
        }), 200
        
    except Exception as e:
        logger.error(f"Real analysis failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'AI analysis failed. Check server logs.',
            'task_id': task_id,
            'status': 'failed'
        }), 500


@real_analysis.route('/real/health', methods=['GET'])
def check_real_ai_health():
    """Check if real AI engine is configured and working"""
    engine = get_analysis_engine()
    
    return jsonify({
        'service': 'Real AI Analysis Engine',
        'status': 'configured' if engine.enabled else 'not_configured',
        'api_key_set': bool(engine.api_key),
        'model': 'gemini-1.5-flash' if engine.enabled else None,
        'ready': engine.enabled,
        'message': '✅ Ready for real AI analysis' if engine.enabled else '❌ GOOGLE_API_KEY not set',
        'instructions': {
            'get_key': 'https://makersuite.google.com/app/apikey',
            'add_to_env': 'GOOGLE_API_KEY=your_key_here',
            'restart': 'Restart backend after adding key'
        } if not engine.enabled else None
    }), 200 if engine.enabled else 503


@real_analysis.route('/real/domains', methods=['GET'])
def list_real_domains():
    """List all domains with real AI support"""
    domains = [
        {
            'id': 'legal',
            'name': 'Legal Intelligence',
            'description': 'Contract review, compliance, risk analysis',
            'ai_powered': True,
            'example': 'Find liability clauses in this contract'
        },
        {
            'id': 'financial',
            'name': 'Financial Intelligence',
            'description': 'Financial analysis, anomaly detection, audits',
            'ai_powered': True,
            'example': 'Analyze financial statements for red flags'
        },
        {
            'id': 'security',
            'name': 'Security Intelligence',
            'description': 'Security audits, SOC2 compliance, vulnerability assessment',
            'ai_powered': True,
            'example': 'Audit our security policies for SOC2 compliance'
        },
        {
            'id': 'healthcare',
            'name': 'Healthcare Intelligence',
            'description': 'HIPAA compliance, patient data analysis, clinical protocols',
            'ai_powered': True,
            'example': 'Review patient records for HIPAA compliance'
        },
        {
            'id': 'data-science',
            'name': 'Data Science Engine',
            'description': 'Statistical analysis, predictive modeling, data insights',
            'ai_powered': True,
            'example': 'Analyze this dataset for trends and predictions'
        },
        {
            'id': 'education',
            'name': 'Education Intelligence',
            'description': 'Curriculum analysis, accreditation, student performance',
            'ai_powered': True,
            'example': 'Review our curriculum against accreditation standards'
        },
        {
            'id': 'proposals',
            'name': 'Proposal Intelligence',
            'description': 'RFP response, bid optimization, compliance checking',
            'ai_powered': True,
            'example': 'Analyze this RFP and suggest a winning strategy'
        },
        {
            'id': 'ngo',
            'name': 'NGO & Impact',
            'description': 'Grant writing, impact assessment, donor reporting',
            'ai_powered': True,
            'example': 'Write a grant proposal for our education program'
        },
        {
            'id': 'data-entry',
            'name': 'Data Entry Automation',
            'description': 'OCR, data extraction, validation',
            'ai_powered': True,
            'example': 'Extract data from these invoices'
        },
        {
            'id': 'expenses',
            'name': 'Expense Management',
            'description': 'Receipt scanning, expense categorization, anomaly detection',
            'ai_powered': True,
            'example': 'Analyze our expenses and find savings opportunities'
        }
    ]
    
    engine = get_analysis_engine()
    
    return jsonify({
        'domains': domains,
        'total': len(domains),
        'ai_engine_status': 'ready' if engine.enabled else 'not_configured',
        'note': '✅ All domains use REAL AI (Google Gemini)' if engine.enabled else '❌ Configure GOOGLE_API_KEY to enable'
    }), 200
