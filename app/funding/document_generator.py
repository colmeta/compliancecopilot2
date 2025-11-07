"""
REAL DOCUMENT GENERATOR - Funding Readiness Engine
Generates 14-25 high-quality funding documents (vision, pitch decks, business plans, etc.)
NO MORE SIMULATIONS
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
import google.generativeai as genai
from io import BytesIO
import json

logger = logging.getLogger(__name__)

class FundingDocumentGenerator:
    """
    Multi-agent document generation system
    Generates real, high-quality funding documents using AI
    """
    
    def __init__(self):
        """Initialize with Google Gemini API"""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        
        if not self.api_key:
            logger.error("❌ GOOGLE_API_KEY not set! Document generation will fail.")
            self.enabled = False
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')  # Pro for better quality
            self.enabled = True
            logger.info("✅ Funding Document Generator initialized (Gemini Pro)")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {e}")
            self.enabled = False
    
    def generate_package(self,
                        discovery_answers: Dict[str, str],
                        funding_level: str,
                        selected_documents: List[str]) -> Dict:
        """
        Generate complete funding package
        
        Args:
            discovery_answers: User's answers to discovery questions
            funding_level: seed/series-a/series-b/growth/ipo
            selected_documents: List of document IDs to generate
        
        Returns:
            Dictionary with generated documents and metadata
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'AI not configured',
                'message': 'GOOGLE_API_KEY not set'
            }
        
        logger.info(f"Generating {len(selected_documents)} documents for {funding_level} funding")
        
        results = {
            'success': True,
            'documents': [],
            'total': len(selected_documents),
            'completed': 0,
            'failed': 0,
            'metadata': {
                'project_name': discovery_answers.get('project_name', 'Untitled'),
                'funding_level': funding_level,
                'generated_at': datetime.utcnow().isoformat()
            }
        }
        
        # Generate each document
        for doc_id in selected_documents:
            try:
                doc_result = self._generate_document(doc_id, discovery_answers, funding_level)
                if doc_result['success']:
                    results['documents'].append(doc_result)
                    results['completed'] += 1
                else:
                    results['failed'] += 1
                    logger.error(f"Failed to generate {doc_id}: {doc_result.get('error')}")
            except Exception as e:
                logger.error(f"Error generating {doc_id}: {e}")
                results['failed'] += 1
        
        return results
    
    def _generate_document(self, 
                          doc_id: str, 
                          answers: Dict[str, str],
                          funding_level: str) -> Dict:
        """Generate a single document using AI"""
        
        # Get document template/prompt
        template = self._get_document_template(doc_id, funding_level)
        
        if not template:
            return {
                'success': False,
                'error': f'Unknown document type: {doc_id}'
            }
        
        # Build context from discovery answers
        context = self._build_context(answers)
        
        # Build prompt
        prompt = f"""
{template['system_prompt']}

PROJECT CONTEXT:
{context}

FUNDING LEVEL: {funding_level}

REQUIREMENTS:
{template['requirements']}

Generate a complete, professional {template['name']} following these guidelines:
- Write with human touch (not robotic)
- Use compelling, concrete language
- Include specific numbers and metrics where provided
- Make it presentable to investors, Y-Combinator, Fortune 50 executives
- Focus on impact and innovation
- Be clear, concise, and persuasive

Format the output as follows:
{template['format']}
"""
        
        try:
            # Call AI
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,  # More creative for writing
                    'top_p': 0.9,
                    'max_output_tokens': 8192,  # Longer for documents
                }
            )
            
            content = response.text
            
            return {
                'success': True,
                'id': doc_id,
                'name': template['name'],
                'category': template['category'],
                'content': content,
                'format': template['output_format'],
                'pages': template.get('pages', 'variable'),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AI generation failed for {doc_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'id': doc_id,
                'name': template['name']
            }
    
    def _build_context(self, answers: Dict[str, str]) -> str:
        """Build context string from discovery answers"""
        context_parts = []
        
        if answers.get('project_name'):
            context_parts.append(f"PROJECT NAME: {answers['project_name']}")
        
        if answers.get('vision'):
            context_parts.append(f"VISION: {answers['vision']}")
        
        if answers.get('why'):
            context_parts.append(f"FOUNDER'S STORY: {answers['why']}")
        
        if answers.get('problem'):
            context_parts.append(f"PROBLEM: {answers['problem']}")
        
        if answers.get('solution'):
            context_parts.append(f"SOLUTION: {answers['solution']}")
        
        if answers.get('impact'):
            context_parts.append(f"IMPACT: {answers['impact']}")
        
        if answers.get('market'):
            context_parts.append(f"MARKET: {answers['market']}")
        
        if answers.get('team'):
            context_parts.append(f"TEAM: {answers['team']}")
        
        if answers.get('traction'):
            context_parts.append(f"TRACTION: {answers['traction']}")
        
        if answers.get('funding_need'):
            context_parts.append(f"FUNDING NEED: {answers['funding_need']}")
        
        return "\n\n".join(context_parts)
    
    def _get_document_template(self, doc_id: str, funding_level: str) -> Optional[Dict]:
        """Get template for specific document type"""
        
        templates = {
            'vision': {
                'name': 'Vision & Mission Statement',
                'category': 'core',
                'pages': 2,
                'output_format': 'markdown',
                'system_prompt': """You are a strategic communications expert who has written vision statements for Fortune 500 companies and successful startups backed by Y-Combinator, Sequoia, and a16z.
Your vision statements are:
- Inspiring and aspirational (paint a picture of the future)
- Concrete and specific (not vague platitudes)
- Human and emotional (connect to real impact)
- Memorable and quotable (stick in people's minds)
- Aligned with the founder's authentic passion""",
                'requirements': """
1. Vision Statement (150-200 words):
   - The world you want to create
   - Why it matters to humanity
   - The transformation you envision
   
2. Mission Statement (100-150 words):
   - What you do (present tense)
   - Who you serve
   - How you're different
   
3. Core Values (5-7 values with 1-sentence explanations)
   - Authentic to founder's story
   - Actionable and specific
""",
                'format': """
# Vision & Mission Statement

## Our Vision
[Inspiring 150-200 word vision statement]

## Our Mission
[Clear 100-150 word mission statement]

## Core Values
1. **[Value Name]**: [1-sentence explanation]
2. **[Value Name]**: [1-sentence explanation]
...
"""
            },
            
            'executive_summary': {
                'name': 'Executive Summary',
                'category': 'core',
                'pages': 2,
                'output_format': 'markdown',
                'system_prompt': """You are a venture capital analyst who has reviewed 10,000+ startups and knows exactly what investors want to see in the first 2 pages.
Your executive summaries are:
- Concise and scannable (busy investors read in 60 seconds)
- Compelling and urgent (why now?)
- Concrete with metrics (numbers over adjectives)
- Credible and realistic (no hype)
- Clear on ask (what you need and why)""",
                'requirements': """
1. The Opportunity (3-4 sentences)
   - Problem size and urgency
   - Market opportunity (TAM/SAM/SOM)
   
2. The Solution (3-4 sentences)
   - What you built
   - Key innovation/differentiation
   
3. Traction (2-3 sentences with metrics)
   - Customers, revenue, growth rate
   - Key milestones achieved
   
4. Team (2-3 sentences)
   - Relevant experience and expertise
   - Why you will win
   
5. The Ask (2-3 sentences)
   - Amount raising
   - Use of funds
   - Key milestones to achieve
""",
                'format': """
# Executive Summary

## The Opportunity
[Market problem and size]

## The Solution
[Your innovation]

## Traction
[Metrics and proof]

## Team
[Why you'll win]

## The Ask
[Funding request and use]
"""
            },
            
            'pitch_deck': {
                'name': 'Investor Pitch Deck (15 slides)',
                'category': 'core',
                'pages': 15,
                'output_format': 'markdown',
                'system_prompt': """You are a pitch deck consultant who has helped companies raise over $500M from top-tier VCs (Sequoia, a16z, YC, Founders Fund).
Your pitch decks follow the proven formula:
- 15 slides maximum (one idea per slide)
- Visual and scannable (bullet points, not paragraphs)
- Story-driven (problem → solution → traction → vision)
- Data-backed (metrics, not claims)
- Action-oriented (clear next steps)
The deck should work standalone (investor can understand without you presenting).""",
                'requirements': """
Create content for all 15 slides:
1. Cover: Company name, tagline, contact
2. Problem: The pain point (real, urgent, expensive)
3. Solution: Your product/service (1 sentence + key features)
4. Why Now: Market timing and catalysts
5. Market Size: TAM/SAM/SOM with sources
6. Product: How it works (user flow or demo)
7. Traction: Growth metrics, customer logos
8. Business Model: How you make money
9. Competition: Competitive landscape
10. Competitive Advantage: Your moat
11. Team: Founders and key hires
12. Financial Projections: 3-5 year forecast
13. Use of Funds: What you'll build with this raise
14. Milestones: What success looks like in 12-18 months
15. Close: The ask and contact info
""",
                'format': """
# [Company Name] - Investor Pitch Deck

## Slide 1: Cover
**[Company Name]**
[One-line tagline]
[Founder name and contact]

## Slide 2: Problem
**The Problem:**
- [Problem point 1]
- [Problem point 2]
- [Problem point 3]

## Slide 3: Solution
...
[Continue for all 15 slides with clear headers and bullet points]
"""
            },
            
            'business_plan': {
                'name': 'Comprehensive Business Plan',
                'category': 'core',
                'pages': 40,
                'output_format': 'markdown',
                'system_prompt': """You are a business strategy consultant with an MBA from Harvard who has written business plans for companies that went on to raise $100M+.
Your business plans are:
- Comprehensive yet readable (40 pages that investors actually read)
- Strategic and analytical (deep thinking, not just descriptions)
- Realistic and credible (conservative assumptions, not hockey sticks)
- Action-oriented (clear roadmap and milestones)
- Investor-focused (answers all due diligence questions upfront)
Think like you're advising the CEO of a Fortune 500 company launching a new division.""",
                'requirements': """
Create a comprehensive business plan with these sections:

1. Executive Summary (2 pages)
2. Company Overview (3 pages)
   - Vision, mission, values
   - Company history and milestones
   - Legal structure and ownership
3. Market Analysis (8 pages)
   - Industry overview and trends
   - Target market definition and size
   - Customer segments and personas
   - Competitive analysis and positioning
4. Product/Service Description (6 pages)
   - Detailed product overview
   - Features and benefits
   - Technology/IP
   - Product roadmap
5. Marketing & Sales Strategy (6 pages)
   - Go-to-market strategy
   - Customer acquisition channels
   - Pricing strategy
   - Sales process and team
6. Operations Plan (5 pages)
   - Key processes and workflows
   - Technology infrastructure
   - Suppliers and partnerships
   - Facilities and equipment
7. Team & Management (4 pages)
   - Founders and key team members
   - Organizational structure
   - Hiring plan
   - Advisory board
8. Financial Plan (10 pages)
   - Revenue model
   - Cost structure
   - 5-year financial projections
   - Funding requirements and use
   - Break-even analysis
   - Exit strategy
9. Risk Analysis (3 pages)
   - Market risks
   - Operational risks
   - Mitigation strategies
10. Appendices (3 pages)
    - Detailed financial tables
    - Market research sources
    - Product specifications
""",
                'format': """
# Business Plan: [Company Name]

## Executive Summary
[2-page compelling summary]

## 1. Company Overview
### 1.1 Vision & Mission
[Content]

### 1.2 Company History
[Content]

## 2. Market Analysis
[Continue with all sections, using clear headers and subheaders]
...
"""
            }
            
            # TODO: Add more document types (financial projections, go-to-market, etc.)
        }
        
        return templates.get(doc_id)


# Singleton instance
_generator = None

def get_document_generator() -> FundingDocumentGenerator:
    """Get or create the document generator singleton"""
    global _generator
    if _generator is None:
        _generator = FundingDocumentGenerator()
    return _generator
