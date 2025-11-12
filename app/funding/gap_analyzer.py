"""
Funding Gap Analyzer - Identify Missing Information and Generate Smart Questions
Compares extracted information from documents against required discovery_answers fields
and generates targeted questions for only missing information.
"""

import logging
from typing import Dict, List, Any, Optional
import os
import google.generativeai as genai

logger = logging.getLogger(__name__)


class FundingGapAnalyzer:
    """
    Analyzes extracted information and identifies gaps.
    Generates smart, targeted questions for only missing information.
    """
    
    def __init__(self):
        """Initialize the gap analyzer."""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        
        if not self.api_key:
            logger.error("GOOGLE_API_KEY not set! Gap analysis will fail.")
            self.enabled = False
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            self.enabled = True
            logger.info("✅ Funding Gap Analyzer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize gap analyzer: {e}")
            self.enabled = False
    
    def identify_gaps(
        self, 
        extracted_info: Dict[str, Any], 
        funding_level: str = 'seed',
        required_fields: Optional[List[str]] = None
    ) -> Dict:
        """
        Identify what information is missing from extracted data.
        
        Args:
            extracted_info: Information extracted from documents
            funding_level: Funding level (seed, series_a, etc.)
            required_fields: Optional list of required fields (if None, uses defaults)
        
        Returns:
            {
                'gaps': List[Dict],  # Missing fields with priority and questions
                'completeness_score': float,  # 0.0 to 1.0
                'high_priority_gaps': List[str],
                'medium_priority_gaps': List[str],
                'low_priority_gaps': List[str]
            }
        """
        if not self.enabled:
            return {
                'gaps': [],
                'completeness_score': 0.0,
                'error': 'Gap analyzer not configured'
            }
        
        # Define required fields by priority
        if required_fields is None:
            required_fields = self._get_required_fields(funding_level)
        
        # Identify gaps
        gaps = []
        found_fields = []
        missing_fields = []
        
        for field in required_fields:
            field_name = field if isinstance(field, str) else field.get('name', field)
            field_info = field if isinstance(field, dict) else {'name': field, 'priority': 'medium'}
            
            value = extracted_info.get(field_name)
            confidence = extracted_info.get('_confidence', {}).get(field_name, 0.0) if isinstance(extracted_info.get('_confidence'), dict) else 0.0
            
            # Check if field is missing or has low confidence
            is_missing = value is None or value == '' or str(value).strip() == ''
            is_low_confidence = confidence < 0.7
            
            if is_missing or is_low_confidence:
                priority = field_info.get('priority', self._get_field_priority(field_name))
                
                gap = {
                    'field': field_name,
                    'priority': priority,
                    'reason': 'missing' if is_missing else 'low_confidence',
                    'confidence': confidence if not is_missing else 0.0,
                    'question': self._generate_question(field_name, funding_level, extracted_info),
                    'why_important': self._get_why_important(field_name, funding_level)
                }
                
                gaps.append(gap)
                missing_fields.append(field_name)
            else:
                found_fields.append(field_name)
        
        # Calculate completeness score
        total_fields = len(required_fields)
        found_count = len(found_fields)
        completeness_score = found_count / total_fields if total_fields > 0 else 0.0
        
        # Categorize gaps by priority
        high_priority_gaps = [g['field'] for g in gaps if g['priority'] == 'high']
        medium_priority_gaps = [g['field'] for g in gaps if g['priority'] == 'medium']
        low_priority_gaps = [g['field'] for g in gaps if g['priority'] == 'low']
        
        # Sort gaps by priority (high first)
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        gaps.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return {
            'gaps': gaps,
            'completeness_score': round(completeness_score, 2),
            'found_fields': found_fields,
            'missing_fields': missing_fields,
            'high_priority_gaps': high_priority_gaps,
            'medium_priority_gaps': medium_priority_gaps,
            'low_priority_gaps': low_priority_gaps,
            'total_required': total_fields,
            'found_count': found_count,
            'missing_count': len(missing_fields)
        }
    
    def _get_required_fields(self, funding_level: str) -> List[Dict]:
        """
        Get required fields based on funding level.
        
        Args:
            funding_level: seed, series_a, series_b, etc.
        
        Returns:
            List of field definitions with priorities
        """
        # Core fields (always required)
        core_fields = [
            {'name': 'company_name', 'priority': 'high', 'description': 'Company or project name'},
            {'name': 'problem', 'priority': 'high', 'description': 'The problem being solved'},
            {'name': 'solution', 'priority': 'high', 'description': 'The solution or product'},
            {'name': 'target_market', 'priority': 'high', 'description': 'Target market or customers'},
        ]
        
        # Important fields (high priority for most funding levels)
        important_fields = [
            {'name': 'business_model', 'priority': 'high', 'description': 'How the company makes money'},
            {'name': 'competitive_advantage', 'priority': 'high', 'description': 'Competitive advantages'},
            {'name': 'funding_amount', 'priority': 'high', 'description': 'Funding amount sought'},
            {'name': 'use_of_funds', 'priority': 'high', 'description': 'How funding will be used'},
        ]
        
        # Vision/Strategy fields
        vision_fields = [
            {'name': 'vision', 'priority': 'medium', 'description': 'Company vision'},
            {'name': 'mission', 'priority': 'medium', 'description': 'Company mission'},
        ]
        
        # Market/Traction fields
        market_fields = [
            {'name': 'market_size', 'priority': 'medium', 'description': 'Total addressable market'},
            {'name': 'traction', 'priority': 'medium', 'description': 'Current traction or metrics'},
        ]
        
        # Team/Financial fields
        team_fields = [
            {'name': 'team', 'priority': 'medium', 'description': 'Team members and backgrounds'},
            {'name': 'revenue', 'priority': 'low', 'description': 'Current or projected revenue'},
            {'name': 'industry', 'priority': 'low', 'description': 'Industry or sector'},
            {'name': 'stage', 'priority': 'low', 'description': 'Company stage'},
        ]
        
        # Combine based on funding level
        if funding_level in ['seed', 'pre_seed']:
            # Seed stage: Focus on problem, solution, market, team
            return core_fields + important_fields[:2] + vision_fields + market_fields[:1] + team_fields[:1]
        elif funding_level in ['series_a', 'series_b']:
            # Series A/B: Need traction, financials, market validation
            return core_fields + important_fields + vision_fields + market_fields + team_fields
        else:
            # Growth/IPO: Need everything
            return core_fields + important_fields + vision_fields + market_fields + team_fields
    
    def _get_field_priority(self, field_name: str) -> str:
        """
        Get default priority for a field.
        
        Args:
            field_name: Field name
        
        Returns:
            Priority level: 'high', 'medium', or 'low'
        """
        high_priority_fields = [
            'company_name', 'project_name', 'problem', 'solution', 
            'target_market', 'business_model', 'funding_amount'
        ]
        
        medium_priority_fields = [
            'vision', 'mission', 'competitive_advantage', 'market_size',
            'traction', 'team', 'use_of_funds'
        ]
        
        if field_name in high_priority_fields:
            return 'high'
        elif field_name in medium_priority_fields:
            return 'medium'
        else:
            return 'low'
    
    def _generate_question(
        self, 
        field_name: str, 
        funding_level: str,
        extracted_info: Dict
    ) -> str:
        """
        Generate a smart, contextual question for a missing field.
        
        Args:
            field_name: Field that needs information
            funding_level: Funding level context
            extracted_info: Already extracted information (for context)
        
        Returns:
            Question string
        """
        # Use AI to generate contextual questions
        try:
            context = self._build_context_summary(extracted_info)
            
            prompt = f"""You are a funding readiness consultant helping entrepreneurs prepare for {funding_level} funding.

The entrepreneur has already provided some information:
{context}

They are missing information about: {field_name}

Generate a single, clear, friendly question that will help them provide this information. The question should:
- Be conversational and encouraging (not intimidating)
- Reference what they've already shared if relevant
- Be specific enough to get useful information
- Feel like a helpful consultant asking, not a form

Field needed: {field_name}
Funding level: {funding_level}

Generate ONLY the question, nothing else:"""

            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'max_output_tokens': 200
                }
            )
            
            question = response.text.strip()
            # Clean up any quotes or formatting
            question = question.strip('"').strip("'").strip()
            
            return question
            
        except Exception as e:
            logger.warning(f"Failed to generate AI question for {field_name}: {e}")
            # Fallback to template questions
            return self._get_template_question(field_name, funding_level)
    
    def _get_template_question(self, field_name: str, funding_level: str) -> str:
        """
        Get a template question if AI generation fails.
        
        Args:
            field_name: Field name
            funding_level: Funding level
        
        Returns:
            Template question
        """
        questions = {
            'company_name': "What is the name of your company or project?",
            'project_name': "What is the name of your project or venture?",
            'problem': "What problem are you solving? Tell us about the pain point your customers experience.",
            'solution': "What is your solution? How does your product or service solve the problem?",
            'target_market': "Who is your target market? Describe your ideal customers.",
            'business_model': "How does your company make money? What is your revenue model?",
            'competitive_advantage': "What makes you different? What are your competitive advantages?",
            'funding_amount': f"What funding amount are you seeking for your {funding_level} round?",
            'use_of_funds': "How will you use the funding? What are your key priorities?",
            'vision': "What is your long-term vision? Where do you see the company in 5-10 years?",
            'mission': "What is your company's mission? What drives you every day?",
            'market_size': "What is the size of your total addressable market (TAM)?",
            'traction': "What traction do you have? Share any metrics, customers, or milestones.",
            'team': "Tell us about your team. Who are the key people and what are their backgrounds?",
            'revenue': "What is your current or projected revenue?",
            'industry': "What industry or sector are you in?",
            'stage': "What stage is your company at? (idea, prototype, beta, revenue, etc.)"
        }
        
        return questions.get(field_name, f"Can you provide more information about {field_name}?")
    
    def _get_why_important(self, field_name: str, funding_level: str) -> str:
        """
        Explain why a field is important.
        
        Args:
            field_name: Field name
            funding_level: Funding level
        
        Returns:
            Explanation string
        """
        explanations = {
            'company_name': "Investors need to know who they're investing in. A clear company name builds credibility.",
            'problem': "Investors invest in problems worth solving. A clear problem statement shows market opportunity.",
            'solution': "Your solution is the core of your pitch. Investors need to understand what you're building.",
            'target_market': "Knowing your target market shows you understand your customers and have a clear go-to-market strategy.",
            'business_model': "Investors need to see a path to revenue. A clear business model shows how you'll make money.",
            'competitive_advantage': "Investors see many pitches. Your competitive advantage shows why you'll win.",
            'funding_amount': "Investors need to know how much you're raising to evaluate if it aligns with their check size.",
            'use_of_funds': "Investors want to see a clear plan for how their money will be used to grow the business.",
            'vision': "A compelling vision shows investors the long-term potential and your ambition.",
            'market_size': "A large market size shows investors the opportunity for significant returns.",
            'traction': "Traction proves you're not just an idea - you're building something people want.",
            'team': "Investors invest in teams. A strong team increases confidence in execution."
        }
        
        return explanations.get(field_name, f"This information helps investors understand your {field_name}.")
    
    def _build_context_summary(self, extracted_info: Dict) -> str:
        """
        Build a summary of already extracted information for context.
        
        Args:
            extracted_info: Extracted information
        
        Returns:
            Context summary string
        """
        summary_parts = []
        
        if extracted_info.get('company_name'):
            summary_parts.append(f"Company: {extracted_info['company_name']}")
        
        if extracted_info.get('problem'):
            summary_parts.append(f"Problem: {extracted_info['problem'][:100]}...")
        
        if extracted_info.get('solution'):
            summary_parts.append(f"Solution: {extracted_info['solution'][:100]}...")
        
        if extracted_info.get('industry'):
            summary_parts.append(f"Industry: {extracted_info['industry']}")
        
        if not summary_parts:
            return "No information has been provided yet."
        
        return "\n".join(summary_parts)


# Singleton instance
_gap_analyzer = None

def get_gap_analyzer():
    """Get singleton gap analyzer instance"""
    global _gap_analyzer
    if _gap_analyzer is None:
        _gap_analyzer = FundingGapAnalyzer()
    return _gap_analyzer

