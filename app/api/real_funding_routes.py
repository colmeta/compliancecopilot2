"""
REAL FUNDING ENGINE ROUTES - No More Simulations
Generates actual funding documents using AI
"""

from flask import Blueprint, jsonify, request
import uuid
from datetime import datetime
import logging
from app.funding.document_generator import get_document_generator

logger = logging.getLogger(__name__)

real_funding = Blueprint('real_funding', __name__)

@real_funding.route('/real/funding/generate', methods=['POST'])
def generate_real_funding_package():
    """
    Generate REAL funding documents (no simulations)
    
    POST /real/funding/generate
    Body: {
        "email": "user@example.com",
        "discovery_answers": {
            "project_name": "...",
            "vision": "...",
            ...
        },
        "config": {
            "fundingLevel": "seed",
            "selectedDocuments": ["vision", "pitch_deck", ...]
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip()
        discovery_answers = data.get('discovery_answers', {})
        config = data.get('config', {})
        
        # Validate
        if not email or '@' not in email:
            return jsonify({'error': 'Valid email required'}), 400
        
        if not discovery_answers:
            return jsonify({'error': 'Discovery answers required'}), 400
        
        selected_documents = config.get('selectedDocuments', [])
        if not selected_documents:
            return jsonify({'error': 'Select at least one document'}), 400
        
        funding_level = config.get('fundingLevel', 'seed')
        
        # Get generator
        generator = get_document_generator()
        
        if not generator.enabled:
            return jsonify({
                'success': False,
                'error': 'Document generator not configured',
                'message': 'GOOGLE_API_KEY not set',
                'instructions': {
                    'step1': 'Get API key: https://makersuite.google.com/app/apikey',
                    'step2': 'Add to .env: GOOGLE_API_KEY=your_key',
                    'step3': 'Restart backend',
                    'step4': 'Try again'
                },
                'status': 'not_configured'
            }), 503
        
        task_id = str(uuid.uuid4())
        
        logger.info(f"Starting REAL document generation: {len(selected_documents)} docs for {email}")
        
        # Generate documents (this takes 5-15 minutes)
        # In production, this would be a Celery task
        result = generator.generate_package(
            discovery_answers=discovery_answers,
            funding_level=funding_level,
            selected_documents=selected_documents
        )
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': result.get('error'),
                'message': 'Document generation failed',
                'task_id': task_id
            }), 500
        
        # In production: Package as ZIP, upload to S3, send email
        # For now: Return document metadata
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'email': email,
            'documents_generated': result['completed'],
            'documents_failed': result['failed'],
            'total_requested': result['total'],
            'documents': [
                {
                    'id': doc['id'],
                    'name': doc['name'],
                    'category': doc['category'],
                    'pages': doc.get('pages'),
                    'preview': doc['content'][:200] + '...' if len(doc['content']) > 200 else doc['content']
                }
                for doc in result['documents'] if doc['success']
            ],
            'metadata': result['metadata'],
            'note': '✅ REAL AI-GENERATED DOCUMENTS (not simulated)',
            'status': 'completed',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Funding generation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Document generation failed'
        }), 500


@real_funding.route('/real/funding/documents', methods=['GET'])
def list_available_funding_documents():
    """List all available document types"""
    documents = [
        {
            'id': 'vision',
            'name': 'Vision & Mission Statement',
            'category': 'core',
            'description': 'Inspiring vision and mission statements with core values',
            'pages': 2,
            'time_estimate': '3-5 minutes',
            'ai_powered': True
        },
        {
            'id': 'executive_summary',
            'name': 'Executive Summary',
            'category': 'core',
            'description': '2-page investor-grade executive summary',
            'pages': 2,
            'time_estimate': '3-5 minutes',
            'ai_powered': True
        },
        {
            'id': 'pitch_deck',
            'name': 'Investor Pitch Deck',
            'category': 'core',
            'description': '15-slide professional pitch deck (Y-Combinator format)',
            'pages': 15,
            'time_estimate': '10-15 minutes',
            'ai_powered': True
        },
        {
            'id': 'business_plan',
            'name': 'Comprehensive Business Plan',
            'category': 'core',
            'description': '40-page detailed business plan covering all aspects',
            'pages': 40,
            'time_estimate': '20-30 minutes',
            'ai_powered': True
        }
        # TODO: Add more document types as they're built
    ]
    
    generator = get_document_generator()
    
    return jsonify({
        'documents': documents,
        'total': len(documents),
        'ai_engine_status': 'ready' if generator.enabled else 'not_configured',
        'note': '✅ All documents use REAL AI generation' if generator.enabled else '❌ Configure GOOGLE_API_KEY to enable'
    }), 200


@real_funding.route('/real/funding/health', methods=['GET'])
def check_funding_generator_health():
    """Check if funding generator is configured"""
    generator = get_document_generator()
    
    return jsonify({
        'service': 'Real Funding Document Generator',
        'status': 'configured' if generator.enabled else 'not_configured',
        'api_key_set': bool(generator.api_key),
        'model': 'gemini-1.5-pro' if generator.enabled else None,
        'ready': generator.enabled,
        'message': '✅ Ready to generate real funding documents' if generator.enabled else '❌ GOOGLE_API_KEY not set'
    }), 200 if generator.enabled else 503
