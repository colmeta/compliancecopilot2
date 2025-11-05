# ==============================================================================
# app/api/funding_routes.py
# Funding Readiness Engine API Routes
# ==============================================================================
"""
API endpoints for the Funding Readiness Engine.

Helps transform brilliant ideas into fundable ventures with complete documentation.
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.funding import FundingEngine, FundingLevel
from app import db
from datetime import datetime

funding_api = Blueprint('funding', __name__, url_prefix='/api/funding')


@funding_api.route('/assess', methods=['POST'])
@login_required
def assess_readiness():
    """
    Assess funding readiness of an idea/project.
    
    Request Body:
    {
        "idea_description": "Description of the project/idea",
        "current_documents": {
            "exec_summary": "...",
            "business_plan": "..."
        }
    }
    
    Returns assessment with missing documents and recommendations.
    """
    try:
        data = request.get_json()
        
        idea = data.get('idea_description')
        if not idea:
            return jsonify({'error': 'idea_description is required'}), 400
        
        current_docs = data.get('current_documents', {})
        
        # Create funding engine
        engine = FundingEngine()
        
        # Assess readiness
        assessment = engine.assess_readiness(idea, current_docs)
        
        return jsonify({
            'success': True,
            'assessment': assessment
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@funding_api.route('/generate-package', methods=['POST'])
@login_required
def generate_document_package():
    """
    Generate complete documentation package for funding readiness.
    
    Request Body:
    {
        "idea_description": "Full description of project/idea",
        "funding_level": "seed|series_a|accelerator|enterprise|government|presidential",
        "context": {
            "team": [{"name": "...", "bio": "..."}],
            "traction": "...",
            "market_validation": "...",
            "revenue": 0
        }
    }
    
    Returns complete documentation package.
    """
    try:
        data = request.get_json()
        
        idea = data.get('idea_description')
        if not idea:
            return jsonify({'error': 'idea_description is required'}), 400
        
        level_str = data.get('funding_level', 'seed')
        try:
            funding_level = FundingLevel(level_str.lower())
        except ValueError:
            return jsonify({'error': f'Invalid funding_level: {level_str}'}), 400
        
        context = data.get('context', {})
        
        # Create funding engine
        engine = FundingEngine()
        
        # Generate complete package
        package = engine.generate_document_package(
            idea_description=idea,
            funding_level=funding_level,
            additional_context=context
        )
        
        # Convert to dictionary
        package_dict = {
            'executive_summary': package.executive_summary,
            'vision_statement': package.vision_statement,
            'mission_statement': package.mission_statement,
            'business_plan': package.business_plan,
            'pitch_deck': package.pitch_deck,
            'one_pager': package.one_pager,
            'organizational_structure': package.organizational_structure,
            'team_bios': package.team_bios,
            'governance_model': package.governance_model,
            'financial_projections': package.financial_projections,
            'revenue_model': package.revenue_model,
            'budget_breakdown': package.budget_breakdown,
            'funding_ask': package.funding_ask,
            'operational_plan': package.operational_plan,
            'policies_procedures': package.policies_procedures,
            'risk_assessment': package.risk_assessment,
            'impact_assessment': package.impact_assessment,
            'market_analysis': package.market_analysis,
            'competitive_landscape': package.competitive_landscape,
            'legal_structure': package.legal_structure,
            'intellectual_property': package.intellectual_property,
            'regulatory_compliance': package.regulatory_compliance,
            'case_studies': package.case_studies,
            'testimonials': package.testimonials,
            'roadmap': package.roadmap,
            'created_at': package.created_at.isoformat(),
            'funding_level': package.funding_level.value,
            'readiness_score': package.readiness_score
        }
        
        return jsonify({
            'success': True,
            'package': package_dict,
            'summary': {
                'total_documents': 25,
                'readiness_score': package.readiness_score,
                'funding_level': funding_level.value,
                'estimated_completion_time': '15-30 minutes'
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@funding_api.route('/generate-single-document', methods=['POST'])
@login_required
def generate_single_document():
    """
    Generate a single document (faster than full package).
    
    Request Body:
    {
        "idea_description": "...",
        "document_type": "executive_summary|business_plan|pitch_deck|financial_projections|...",
        "funding_level": "seed|series_a|...",
        "context": {}
    }
    """
    try:
        data = request.get_json()
        
        idea = data.get('idea_description')
        doc_type = data.get('document_type')
        
        if not idea or not doc_type:
            return jsonify({'error': 'idea_description and document_type required'}), 400
        
        level_str = data.get('funding_level', 'seed')
        funding_level = FundingLevel(level_str.lower())
        context = data.get('context', {})
        
        # Create engine
        engine = FundingEngine()
        
        import google.generativeai as genai
        genai.configure(api_key=engine.google_api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Generate specific document
        document_generators = {
            'executive_summary': engine._generate_executive_summary,
            'vision_statement': engine._generate_vision_statement,
            'mission_statement': engine._generate_mission_statement,
            'business_plan': engine._generate_business_plan,
            'pitch_deck': engine._generate_pitch_deck,
            'financial_projections': engine._generate_financial_projections,
            'market_analysis': engine._generate_market_analysis,
            'impact_assessment': engine._generate_impact_assessment
        }
        
        if doc_type not in document_generators:
            return jsonify({'error': f'Unknown document_type: {doc_type}'}), 400
        
        generator = document_generators[doc_type]
        
        # Call appropriate generator
        if doc_type in ['executive_summary', 'business_plan', 'pitch_deck']:
            content = generator(model, idea, funding_level, context)
        elif doc_type in ['impact_assessment']:
            content = generator(model, idea, funding_level, context)
        else:
            content = generator(model, idea, context)
        
        return jsonify({
            'success': True,
            'document_type': doc_type,
            'content': content
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@funding_api.route('/levels', methods=['GET'])
def get_funding_levels():
    """Get available funding levels and their descriptions."""
    levels = {
        'seed': {
            'name': 'Seed / Angel',
            'amount': '$50K - $2M',
            'focus': 'Team, Vision, Market Opportunity',
            'investors': 'Angel investors, seed funds'
        },
        'series_a': {
            'name': 'Series A',
            'amount': '$2M - $15M',
            'focus': 'Traction, Unit Economics, Scale Plan',
            'investors': 'VC firms'
        },
        'accelerator': {
            'name': 'Accelerator (Y-Combinator)',
            'amount': '$125K - $500K',
            'focus': 'Scalability, Team, Market Size',
            'investors': 'Y-Combinator, Techstars, etc.'
        },
        'enterprise': {
            'name': 'Fortune 500 Partnership',
            'amount': 'Varies',
            'focus': 'ROI, Integration, Enterprise Value',
            'investors': 'Strategic partnerships'
        },
        'government': {
            'name': 'Government Grants/Contracts',
            'amount': '$100K - $50M+',
            'focus': 'Public Benefit, Compliance, Track Record',
            'investors': 'Government agencies'
        },
        'presidential': {
            'name': 'Presidential Briefing',
            'amount': 'National Impact',
            'focus': 'Job Creation, Economic Growth, Global Competitiveness',
            'investors': 'National leaders, policy makers'
        }
    }
    
    return jsonify({
        'success': True,
        'levels': levels
    })
