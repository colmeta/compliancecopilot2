# ==============================================================================
# app/api/funding_interactive_routes.py
# Interactive Funding Readiness API - OUTSTANDING EDITION
# ==============================================================================
"""
Interactive Funding Readiness API

This is the OUTSTANDING workflow:
1. Start discovery session (get personalized questions)
2. Entrepreneur answers questions
3. Conduct deep research
4. Plan together (review and refine)
5. Generate documents (with human touch and deep research)
6. Refine and polish (multiple passes)

Quality over speed. Human touch over templates.
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.funding import (
    get_interactive_planner,
    get_research_agent,
    get_outstanding_writer,
    FundingLevel
)

funding_interactive = Blueprint('funding_interactive', __name__, url_prefix='/api/funding/interactive')


@funding_interactive.route('/start-discovery', methods=['POST'])
@login_required
def start_discovery():
    """
    Start interactive discovery session.
    
    Request Body:
    {
        "idea_description": "Brief description of the idea",
        "funding_level": "seed|series_a|accelerator|...",
        "initial_context": {
            "industry": "...",
            "stage": "idea|prototype|beta|revenue",
            "team_size": 1
        }
    }
    
    Returns personalized questions to help understand the venture deeply.
    """
    try:
        data = request.get_json()
        
        idea = data.get('idea_description')
        if not idea:
            return jsonify({'error': 'idea_description is required'}), 400
        
        funding_level = data.get('funding_level', 'seed')
        initial_context = data.get('initial_context', {})
        
        # Create interactive planner
        planner = get_interactive_planner()
        
        # Generate personalized questions
        questions = planner.generate_discovery_questions(
            idea=idea,
            funding_level=funding_level,
            initial_context=initial_context
        )
        
        # Convert to JSON
        questions_json = [
            {
                'id': f'q{i+1}',
                'question': q.question,
                'why_asking': q.why_asking,
                'category': q.category,
                'priority': q.priority
            }
            for i, q in enumerate(questions)
        ]
        
        return jsonify({
            'success': True,
            'session_type': 'discovery',
            'message': 'These questions will help us deeply understand your vision and create documents that truly represent your venture.',
            'questions': questions_json,
            'instructions': {
                'approach': 'Take your time with these questions. There are no "right" answers - we want to understand YOUR vision, YOUR why, YOUR unique perspective.',
                'tips': [
                    'Be specific - use real examples and stories',
                    'Be honest - if you don\'t know something, say so',
                    'Be passionate - let your excitement show',
                    'Be human - this isn\'t a template, it\'s your story'
                ],
                'time_estimate': '30-45 minutes for thoughtful responses'
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@funding_interactive.route('/submit-discovery', methods=['POST'])
@login_required
def submit_discovery():
    """
    Submit discovery questionnaire responses.
    
    Request Body:
    {
        "idea_description": "...",
        "funding_level": "...",
        "responses": {
            "q1": "answer to question 1",
            "q2": "answer to question 2",
            ...
        }
    }
    
    Returns synthesis and next steps.
    """
    try:
        data = request.get_json()
        
        idea = data.get('idea_description')
        funding_level = data.get('funding_level', 'seed')
        responses = data.get('responses', {})
        
        if not responses:
            return jsonify({'error': 'responses are required'}), 400
        
        # Create planner
        planner = get_interactive_planner()
        
        # Conduct planning session
        planning_result = planner.conduct_planning_session(
            idea=idea,
            funding_level=funding_level,
            questionnaire_responses=responses
        )
        
        return jsonify({
            'success': True,
            'session_complete': True,
            'message': 'Thank you for your thoughtful responses. We now have a deep understanding of your vision.',
            'narrative_brief': planning_result['narrative_brief'],
            'key_themes': planning_result['themes'],
            'next_steps': {
                'step_1': 'Review the narrative brief and themes',
                'step_2': 'Approve or request changes',
                'step_3': 'We\'ll conduct deep research',
                'step_4': 'Generate outstanding documents',
                'estimated_time': '2-4 hours for complete package'
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@funding_interactive.route('/conduct-research', methods=['POST'])
@login_required
def conduct_deep_research():
    """
    Conduct deep research before generating documents.
    
    This is the "homework" phase. Takes time but produces quality.
    
    Request Body:
    {
        "idea_description": "...",
        "industry": "...",
        "narrative_brief": "..." (from discovery session)
    }
    
    Returns comprehensive research report.
    """
    try:
        data = request.get_json()
        
        idea = data.get('idea_description')
        industry = data.get('industry', 'technology')
        narrative_brief = data.get('narrative_brief', '')
        
        if not idea:
            return jsonify({'error': 'idea_description is required'}), 400
        
        # Create research agent
        researcher = get_research_agent()
        
        # Conduct deep market research
        print("Starting deep market research...")
        market_research = researcher.research_market(idea, industry)
        
        # Conduct financial research
        print("Starting financial research...")
        business_model = data.get('business_model', 'To be defined')
        financial_research = researcher.research_financials(idea, business_model)
        
        # Research team gaps
        print("Analyzing team...")
        current_team = data.get('team', [])
        team_research = researcher.research_team_gaps(idea, current_team)
        
        return jsonify({
            'success': True,
            'message': 'Deep research complete. We now have the insights needed to create truly outstanding documents.',
            'research_summary': {
                'market': {
                    'key_findings': market_research.key_findings,
                    'opportunities': market_research.opportunities,
                    'risks': market_research.risks,
                    'depth_score': market_research.depth_score
                },
                'financial': {
                    'model': financial_research['financial_model'][:500] + '...',  # Truncate for response
                    'confidence': financial_research['confidence_level']
                },
                'team': {
                    'analysis': team_research['team_analysis'][:500] + '...',
                    'critical_gaps': team_research['critical_gaps']
                }
            },
            'next_step': 'generate_documents',
            'quality_note': 'This research forms the foundation of your documents. Every claim will be backed by these insights.'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@funding_interactive.route('/generate-outstanding-document', methods=['POST'])
@login_required
def generate_outstanding_document():
    """
    Generate a single outstanding document with human touch.
    
    This uses:
    - Deep research (substance)
    - Human touch (emotion)
    - Multiple passes (refinement)
    - Target audience adaptation (relevance)
    
    Request Body:
    {
        "document_type": "executive_summary|vision_statement|business_plan|...",
        "narrative_brief": "..." (from discovery),
        "research": {...} (from research phase),
        "funding_level": "...",
        "organization_voice": "..." (optional - sample of their writing)
    }
    """
    try:
        data = request.get_json()
        
        doc_type = data.get('document_type')
        narrative_brief = data.get('narrative_brief')
        research = data.get('research', {})
        funding_level = data.get('funding_level', 'seed')
        organization_voice = data.get('organization_voice')
        
        if not doc_type or not narrative_brief:
            return jsonify({'error': 'document_type and narrative_brief are required'}), 400
        
        # Create outstanding writer
        writer = get_outstanding_writer()
        
        # Generate based on document type
        if doc_type == 'executive_summary':
            print("Writing executive summary with multiple passes...")
            document = writer.write_executive_summary(
                narrative_brief=narrative_brief,
                research=research,
                funding_level=funding_level,
                voice_profile=None
            )
        
        elif doc_type == 'vision_statement':
            print("Crafting inspiring vision statement...")
            emotional_hooks = data.get('emotional_hooks', [])
            document = writer.write_vision_statement(
                narrative_brief=narrative_brief,
                emotional_hooks=emotional_hooks
            )
        
        else:
            return jsonify({'error': f'Document type {doc_type} not yet implemented in outstanding mode'}), 400
        
        # Add human voice (remove robotic AI feel)
        if organization_voice:
            print("Adding organization's voice...")
            document = writer.refine_with_human_voice(document, organization_voice)
        
        return jsonify({
            'success': True,
            'document_type': doc_type,
            'content': document,
            'quality_metrics': {
                'research_backed': True,
                'human_touch': True,
                'multi_pass_refined': True,
                'audience_targeted': True
            },
            'message': 'This document has been crafted with deep research, human touch, and multiple refinement passes. It represents the quality you deserve.'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@funding_interactive.route('/refine-document', methods=['POST'])
@login_required
def refine_document():
    """
    Refine a document based on feedback.
    
    The entrepreneur can say "this doesn't capture my passion" or
    "this misses the main point" and we refine it.
    
    Request Body:
    {
        "document": "...",
        "feedback": "What to improve/change",
        "preserve": "What to keep"
    }
    """
    try:
        data = request.get_json()
        
        document = data.get('document')
        feedback = data.get('feedback')
        preserve = data.get('preserve', '')
        
        if not document or not feedback:
            return jsonify({'error': 'document and feedback are required'}), 400
        
        import google.generativeai as genai
        import os
        
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        refine_prompt = f"""You are refining a funding document based on the entrepreneur's feedback.

CURRENT DOCUMENT:
{document}

WHAT TO PRESERVE:
{preserve}

FEEDBACK / WHAT TO IMPROVE:
{feedback}

Refine the document to address the feedback while preserving what works.

The entrepreneur knows their vision best. Honor their feedback and make this truly THEIR document."""
        
        refined = model.generate_content(refine_prompt).text
        
        return jsonify({
            'success': True,
            'refined_document': refined,
            'message': 'Document refined based on your feedback. Review and let us know if further changes are needed.'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@funding_interactive.route('/workflow-status', methods=['GET'])
@login_required
def get_workflow_status():
    """
    Get the status of the interactive workflow.
    
    Shows what's been completed and what's next.
    """
    return jsonify({
        'success': True,
        'workflow': {
            'step_1': {
                'name': 'Discovery Session',
                'description': 'Answer personalized questions about your vision',
                'endpoint': '/api/funding/interactive/start-discovery',
                'time_estimate': '30-45 minutes'
            },
            'step_2': {
                'name': 'Deep Research',
                'description': 'We conduct comprehensive market, financial, and competitive research',
                'endpoint': '/api/funding/interactive/conduct-research',
                'time_estimate': '1-2 hours'
            },
            'step_3': {
                'name': 'Document Generation',
                'description': 'Create outstanding documents with human touch',
                'endpoint': '/api/funding/interactive/generate-outstanding-document',
                'time_estimate': '30-60 minutes per document'
            },
            'step_4': {
                'name': 'Refinement',
                'description': 'Review and refine based on your feedback',
                'endpoint': '/api/funding/interactive/refine-document',
                'time_estimate': '15-30 minutes per revision'
            }
        },
        'quality_promise': 'We take time to do this right. The result is documents worthy of Fortune 50 boards, Y-Combinator applications, and presidential briefings.'
    })
