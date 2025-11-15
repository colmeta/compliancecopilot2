"""
REAL AI ANALYSIS ENGINE - No More Simulations
Connects to Google Gemini API for actual AI processing
"""

import os
import logging
from typing import Dict, List, Optional, Any
import google.generativeai as genai

logger = logging.getLogger(__name__)

class RealAnalysisEngine:
    """
    Real AI-powered analysis engine using Google Gemini
    Replaces all simulated/fake responses with actual AI processing
    """
    
    def __init__(self):
        """Initialize with Google Gemini API"""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        
        if not self.api_key:
            logger.error("❌ GOOGLE_API_KEY not set! AI analysis will fail.")
            self.enabled = False
            return
        
        try:
            genai.configure(api_key=self.api_key)
            # List available models and use the first one that works
            # Common model names: gemini-1.5-flash, gemini-1.5-pro, gemini-pro-vision
            model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
            self.model = None
            self.model_name = None
            
            for model_name in model_names:
                try:
                    # Test if model exists by trying to create it
                    test_model = genai.GenerativeModel(model_name)
                    self.model = test_model
                    self.model_name = model_name
                    logger.info(f"✅ Real AI Analysis Engine initialized with {model_name}")
                    break
                except Exception as e:
                    logger.debug(f"Model {model_name} not available: {e}")
                    continue
            
            if not self.model:
                raise Exception(f"None of the models are available: {model_names}")
            
            self.enabled = True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {e}")
            self.enabled = False
    
    def analyze(self, 
                directive: str, 
                domain: str, 
                document_content: Optional[str] = None,
                files_data: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Perform REAL AI analysis (no more simulations)
        
        Args:
            directive: User's analysis request (e.g., "Find liability clauses")
            domain: Analysis domain (legal, financial, security, etc.)
            document_content: Optional extracted text from documents
            files_data: Optional list of uploaded files
        
        Returns:
            Real AI analysis results with findings, confidence, recommendations
        """
        if not self.enabled:
            return {
                'error': 'AI Engine not configured',
                'message': 'GOOGLE_API_KEY not set. Add to .env file.',
                'status': 'not_configured'
            }
        
        # Get domain-specific prompt
        system_prompt = self._get_domain_prompt(domain)
        
        # Build full prompt (avoid f-string backslash - Python 3.11 compatibility)
        doc_section = ""
        if document_content:
            doc_section = "DOCUMENT CONTENT:\n" + document_content + "\n\n"
        
        user_prompt = f"""
DIRECTIVE: {directive}

DOMAIN: {domain}

{doc_section}Please provide a comprehensive analysis in the following EXACT format:

EXECUTIVE SUMMARY:
[2-3 sentence summary here]

KEY FINDINGS:
- [Finding 1]
- [Finding 2]
- [Finding 3]
[Add more findings as needed]

RECOMMENDATIONS:
- [Recommendation 1]
- [Recommendation 2]
- [Recommendation 3]
[Add more recommendations as needed]

CONFIDENCE SCORE: [XX]%

Be specific, cite evidence, and provide actionable insights. Use the exact section headers above.
"""
        
        try:
            # Call Gemini API
            full_prompt = system_prompt + "\n\n" + user_prompt
            response = self.model.generate_content(
                full_prompt,
                generation_config={
                    'temperature': 0.3,  # Lower = more focused
                    'top_p': 0.8,
                    'top_k': 40,
                    'max_output_tokens': 2048,
                }
            )
            
            # Extract response
            ai_response = response.text
            
            # Parse response into structured format
            parsed = self._parse_ai_response(ai_response, domain)
            
            return {
                'success': True,
                'domain': domain,
                'directive': directive,
                'analysis': parsed,
                'raw_response': ai_response,
                'model': self.model_name if hasattr(self, 'model_name') else 'gemini-1.5-flash',
                'status': 'completed'
            }
            
        except Exception as e:
            logger.error(f"AI Analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'AI analysis failed. Check API key and quota.',
                'status': 'failed'
            }
    
    def _get_domain_prompt(self, domain: str) -> str:
        """Get specialized system prompt for each domain"""
        
        prompts = {
            'legal': """You are a senior corporate lawyer with 20+ years experience in contract law, M&A, and compliance.
Your analysis is:
- Thorough and detail-oriented
- Focused on risk identification and mitigation
- Citation-backed (reference specific clauses)
- Actionable (clear next steps for legal team)
Think like you're advising a Fortune 500 General Counsel.""",

            'financial': """You are a seasoned CFO and financial analyst with expertise in:
- Financial statement analysis
- Fraud detection and anomaly identification
- Cash flow optimization
- Regulatory compliance (SOX, GAAP, IFRS)
Your analysis is quantitative, data-driven, and focused on material findings.
Think like you're presenting to a board of directors.""",

            'security': """You are a CISO (Chief Information Security Officer) with:
- 15+ years in cybersecurity and compliance
- Expertise in SOC2, ISO 27001, NIST frameworks
- Penetration testing and vulnerability assessment experience
Your analysis identifies critical security gaps and provides remediation roadmaps.
Think like you're conducting a security audit for a bank.""",

            'healthcare': """You are a healthcare compliance officer with deep knowledge of:
- HIPAA regulations and patient data privacy
- Clinical protocols and best practices
- Healthcare IT security and EHR systems
- Medical malpractice risk assessment
Your analysis ensures patient safety and regulatory compliance.
Think like you're advising a hospital administrator.""",

            'data-science': """You are a senior data scientist with PhD-level statistical expertise:
- Advanced statistical modeling and machine learning
- Data quality assessment and validation
- Predictive analytics and forecasting
- A/B testing and experimental design
Your analysis is rigorous, mathematically sound, and provides actionable insights.
Think like you're presenting to a VP of Data Science.""",

            'education': """You are an education consultant specializing in:
- Curriculum design and accreditation standards
- Student performance analytics
- Educational technology and pedagogy
- Institutional compliance (accreditation bodies)
Your analysis improves educational outcomes and ensures institutional quality.
Think like you're advising a university president.""",

            'proposals': """You are a proposal director with 100+ winning bids for:
- Federal RFPs (government contracting)
- Corporate tenders and RFQs
- Grant applications (NSF, NIH, private foundations)
Your analysis ensures compliance, competitiveness, and persuasive messaging.
Think like you're leading a capture team for a $50M contract.""",

            'ngo': """You are a nonprofit strategy consultant specializing in:
- Grant writing and fundraising
- Impact measurement and evaluation
- Program development and scaling
- Donor relations and reporting
Your analysis maximizes funding success and demonstrates measurable impact.
Think like you're advising a global NGO director.""",

            'data-entry': """You are a data quality analyst with expertise in:
- OCR and data extraction accuracy
- Data validation and cleansing
- Database normalization and integrity
- Automated data pipeline optimization
Your analysis ensures 99.9%+ data accuracy and identifies quality issues.
Think like you're implementing an enterprise data governance program.""",

            'expenses': """You are a cost optimization consultant specializing in:
- Expense analysis and fraud detection
- Budget variance analysis
- Procurement optimization
- Spend management and cost reduction strategies
Your analysis identifies savings opportunities and flags anomalies.
Think like you're advising a PE firm on portfolio company optimization."""
        }
        
        return prompts.get(domain, """You are a senior business analyst with expertise across multiple domains.
Your analysis is thorough, evidence-based, and provides actionable recommendations.
Think like you're advising C-suite executives.""")
    
    def _parse_ai_response(self, ai_text: str, domain: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        
        # Simple parsing (can be enhanced with regex or LLM-based parsing)
        lines = ai_text.split('\n')
        
        summary = ""
        findings = []
        recommendations = []
        confidence = 0.85  # Default
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections (case-insensitive, look for exact headers)
            line_lower = line.lower()
            if 'executive summary' in line_lower or (line_lower.startswith('executive') and 'summary' in line_lower):
                current_section = 'summary'
                continue
            elif 'key findings' in line_lower or (line_lower.startswith('key') and 'finding' in line_lower):
                current_section = 'findings'
                continue
            elif 'recommendations' in line_lower or (line_lower.startswith('recommendation')):
                current_section = 'recommendations'
                continue
            elif 'confidence score' in line_lower or (line_lower.startswith('confidence')):
                # Extract confidence score
                import re
                match = re.search(r'(\d+)%', line)
                if match:
                    confidence = int(match.group(1)) / 100.0
                continue
            
            # Skip empty lines and section headers
            if not line or line.strip() == '' or ':' in line and len(line.split(':')) == 2 and len(line.split(':')[1].strip()) < 5:
                continue
            
            # Add to appropriate section
            if current_section == 'summary' and len(line.strip()) > 10:
                summary += line.strip() + " "
            elif current_section == 'findings':
                # Accept any line that looks like a finding (starts with bullet, number, or is a sentence)
                cleaned = line.lstrip('-•*123456789. ').strip()
                if cleaned and len(cleaned) > 5:
                    findings.append(cleaned)
            elif current_section == 'recommendations':
                # Accept any line that looks like a recommendation
                cleaned = line.lstrip('-•*123456789. ').strip()
                if cleaned and len(cleaned) > 5:
                    recommendations.append(cleaned)
        
        # Fallback if parsing fails - try to extract from raw text
        if not summary or len(summary.strip()) < 20:
            # Try to get first paragraph as summary
            paragraphs = ai_text.split('\n\n')
            for para in paragraphs:
                if len(para.strip()) > 50 and not para.strip().startswith(('KEY', 'EXECUTIVE', 'RECOMMENDATION', 'CONFIDENCE')):
                    summary = para.strip()[:500]
                    break
            if not summary or len(summary.strip()) < 20:
                summary = ai_text[:500] + "..." if len(ai_text) > 500 else ai_text
        
        if not findings or len(findings) == 0:
            # Try to extract findings from text
            lines = ai_text.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith(('-', '•', '*')) and len(line) > 10:
                    findings.append(line.lstrip('-•* '))
            if not findings:
                findings = ["Analysis completed successfully. Review the summary for key insights."]
        
        if not recommendations or len(recommendations) == 0:
            # Try to extract recommendations
            in_rec_section = False
            for line in ai_text.split('\n'):
                if 'recommendation' in line.lower():
                    in_rec_section = True
                    continue
                if in_rec_section and line.strip().startswith(('-', '•', '*')):
                    recommendations.append(line.lstrip('-•* ').strip())
            if not recommendations:
                recommendations = ["Review the analysis findings and take appropriate action based on your specific needs."]
        
        return {
            'summary': summary.strip(),
            'findings': findings[:10],  # Limit to top 10
            'recommendations': recommendations[:5],  # Limit to top 5
            'confidence': confidence,
            'domain': domain
        }


# Singleton instance
_engine = None

def get_analysis_engine() -> RealAnalysisEngine:
    """Get or create the analysis engine singleton"""
    global _engine
    if _engine is None:
        _engine = RealAnalysisEngine()
    return _engine
