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
        # Core Documents (Essential)
        {
            'id': 'one_pager',
            'name': 'One-Page Investment Summary',
            'category': 'core',
            'description': 'Punchy 30-second read for busy investors',
            'pages': 1,
            'time_estimate': '2-3 minutes',
            'quality': 'Demo Day / Y-Combinator Standard',
            'ai_powered': True
        },
        {
            'id': 'vision',
            'name': 'Vision & Mission Statement',
            'category': 'core',
            'description': 'Inspiring vision and mission with core values',
            'pages': 2,
            'time_estimate': '3-5 minutes',
            'quality': 'Fortune 500 Strategic Communications',
            'ai_powered': True
        },
        {
            'id': 'executive_summary',
            'name': 'Executive Summary',
            'category': 'core',
            'description': '2-page investor-grade summary (opportunity, solution, traction, ask)',
            'pages': 2,
            'time_estimate': '3-5 minutes',
            'quality': 'VC Partner Grade',
            'ai_powered': True
        },
        {
            'id': 'pitch_deck',
            'name': 'Investor Pitch Deck',
            'category': 'core',
            'description': '15-slide professional deck (Sequoia/a16z format)',
            'pages': 15,
            'time_estimate': '10-15 minutes',
            'quality': 'Y-Combinator / Series A Standard',
            'ai_powered': True
        },
        {
            'id': 'business_plan',
            'name': 'Comprehensive Business Plan',
            'category': 'core',
            'description': '40-page detailed plan (market, product, operations, financials)',
            'pages': 40,
            'time_estimate': '20-30 minutes',
            'quality': 'Harvard MBA / PE Firm Standard',
            'ai_powered': True
        },
        
        # Financial Documents
        {
            'id': 'financial_projections',
            'name': '5-Year Financial Projections',
            'category': 'financial',
            'description': 'Complete P&L, cash flow, balance sheet with scenarios',
            'pages': 12,
            'time_estimate': '10-15 minutes',
            'quality': 'CFO / Financial Diligence Grade',
            'ai_powered': True
        },
        
        # Market Documents
        {
            'id': 'market_research',
            'name': 'Market Research & Validation',
            'category': 'market',
            'description': 'TAM/SAM/SOM, customer analysis, market dynamics',
            'pages': 10,
            'time_estimate': '10-15 minutes',
            'quality': 'McKinsey / Market Research Standard',
            'ai_powered': True
        },
        {
            'id': 'competitive_analysis',
            'name': 'Competitive Analysis',
            'category': 'market',
            'description': 'Competitor landscape, positioning, differentiation strategy',
            'pages': 6,
            'time_estimate': '5-10 minutes',
            'quality': 'Competitive Intelligence Professional',
            'ai_powered': True
        },
        {
            'id': 'go_to_market',
            'name': 'Go-to-Market Strategy',
            'category': 'market',
            'description': 'Customer acquisition channels, sales strategy, success metrics',
            'pages': 8,
            'time_estimate': '8-12 minutes',
            'quality': 'Growth Strategist / Series A Standard',
            'ai_powered': True
        },
        
        # Operations Documents
        {
            'id': 'product_roadmap',
            'name': 'Product Roadmap',
            'category': 'operations',
            'description': '18-month roadmap with features, milestones, tech stack',
            'pages': 6,
            'time_estimate': '5-10 minutes',
            'quality': 'Head of Product / Tech Company Standard',
            'ai_powered': True
        },
        {
            'id': 'team_bios',
            'name': 'Team Bios & Org Chart',
            'category': 'operations',
            'description': 'Founder profiles, key hires, advisory board',
            'pages': 4,
            'time_estimate': '5-8 minutes',
            'quality': 'Executive Search / Sequoia Team Assessment',
            'ai_powered': True
        },
        {
            'id': 'risk_analysis',
            'name': 'Risk Analysis & Mitigation',
            'category': 'operations',
            'description': 'Market, operational, financial risks with mitigation plans',
            'pages': 5,
            'time_estimate': '5-8 minutes',
            'quality': 'Risk Management / Board Governance Standard',
            'ai_powered': True
        },
        
        # Impact & Specialized
        {
            'id': 'impact_assessment',
            'name': 'Impact Assessment',
            'category': 'impact',
            'description': 'Social impact metrics, theory of change, SROI',
            'pages': 6,
            'time_estimate': '5-10 minutes',
            'quality': 'Gates Foundation / Impact Investor Standard',
            'ai_powered': True
        },
        {
            'id': 'investor_faq',
            'name': 'Investor FAQ',
            'category': 'specialized',
            'description': '65+ common investor questions with answers',
            'pages': 8,
            'time_estimate': '8-12 minutes',
            'quality': 'Startup Attorney / Partner Meeting Prep',
            'ai_powered': True
        },
        
        # Legal & Financial
        {
            'id': 'term_sheet',
            'name': 'Sample Term Sheet',
            'category': 'legal',
            'description': 'NVCA-standard term sheet with founder-friendly terms',
            'pages': 4,
            'time_estimate': '5-8 minutes',
            'quality': 'Wilson Sonsini / Startup Attorney',
            'ai_powered': True
        },
        {
            'id': 'cap_table',
            'name': 'Cap Table & Ownership',
            'category': 'legal',
            'description': 'Fully-diluted ownership with round-by-round projections',
            'pages': 3,
            'time_estimate': '5-8 minutes',
            'quality': 'Startup CFO / Exit Scenario Analysis',
            'ai_powered': True
        },
        {
            'id': 'regulatory_compliance',
            'name': 'Regulatory Strategy',
            'category': 'legal',
            'description': 'Compliance roadmap (FDA, HIPAA, GDPR, SOC2)',
            'pages': 4,
            'time_estimate': '5-8 minutes',
            'quality': 'Compliance Officer / Regulatory Strategy',
            'ai_powered': True
        },
        {
            'id': 'financial_model',
            'name': 'Financial Model Structure',
            'category': 'financial',
            'description': 'Excel/Sheets model template (assumptions, P&L, cash flow)',
            'pages': 1,
            'time_estimate': '3-5 minutes',
            'quality': 'Financial Modeler / Series B Standard',
            'ai_powered': True
        },
        
        # Additional Operations
        {
            'id': 'operating_plan',
            'name': 'Operating Plan',
            'category': 'operations',
            'description': '18-month milestone map with OKRs and resource allocation',
            'pages': 5,
            'time_estimate': '5-10 minutes',
            'quality': 'COO / Board Presentation Standard',
            'ai_powered': True
        },
        {
            'id': 'hiring_plan',
            'name': 'Hiring & Talent Plan',
            'category': 'operations',
            'description': 'Headcount roadmap, job descriptions, compensation',
            'pages': 5,
            'time_estimate': '5-10 minutes',
            'quality': 'Head of People / Executive Recruiting',
            'ai_powered': True
        },
        
        # Advanced Specialized
        {
            'id': 'customer_case_studies',
            'name': 'Customer Case Studies',
            'category': 'specialized',
            'description': '3-5 customer stories with quantified ROI',
            'pages': 6,
            'time_estimate': '8-12 minutes',
            'quality': 'Enterprise Marketing / Sales Enablement',
            'ai_powered': True
        },
        {
            'id': 'technology_ip',
            'name': 'Technology & IP',
            'category': 'specialized',
            'description': 'Tech stack, architecture, patents, defensibility',
            'pages': 5,
            'time_estimate': '5-10 minutes',
            'quality': 'CTO / Google Ventures Due Diligence',
            'ai_powered': True
        },
        {
            'id': 'sales_playbook',
            'name': 'Sales Playbook',
            'category': 'specialized',
            'description': 'Sales process, objection handling, ICP, metrics',
            'pages': 7,
            'time_estimate': '8-12 minutes',
            'quality': 'VP Sales / $100M ARR Standard',
            'ai_powered': True
        },
        {
            'id': 'customer_acquisition',
            'name': 'Customer Acquisition',
            'category': 'market',
            'description': 'Channel playbooks, CAC/LTV, budget optimization',
            'pages': 8,
            'time_estimate': '10-15 minutes',
            'quality': 'VP Growth / Performance Marketing',
            'ai_powered': True
        },
        {
            'id': 'partnership_strategy',
            'name': 'Partnership Strategy',
            'category': 'specialized',
            'description': 'Target partners, deal structure, BD execution plan',
            'pages': 5,
            'time_estimate': '5-10 minutes',
            'quality': 'VP Business Development / Strategic Alliances',
            'ai_powered': True
        },
        {
            'id': 'board_deck',
            'name': 'Board Meeting Deck',
            'category': 'specialized',
            'description': 'Quarterly board presentation template with KPIs',
            'pages': 12,
            'time_estimate': '10-15 minutes',
            'quality': 'CEO / Benchmark/a16z Board Standard',
            'ai_powered': True
        }
    ]
    
    generator = get_document_generator()
    
    return jsonify({
        'documents': documents,
        'total': len(documents),
        'ai_engine_status': 'ready' if generator.enabled else 'not_configured',
        'note': '✅ All documents use REAL AI generation' if generator.enabled else '❌ Configure GOOGLE_API_KEY to enable'
    }), 200


@real_funding.route('/funding/health', methods=['GET'])
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
