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
            # Use gemini-pro (stable, widely available) instead of gemini-1.5-flash
            self.model = genai.GenerativeModel('gemini-pro')
            self.enabled = True
            logger.info("✅ Real AI Analysis Engine initialized (Gemini Pro)")
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

{doc_section}Please provide a comprehensive analysis with:
1. Executive Summary (2-3 sentences)
2. Key Findings (bullet points, specific and actionable)
3. Risk Assessment (if applicable)
4. Recommendations (concrete next steps)
5. Confidence Score (0-100%, based on information quality)

Be specific, cite evidence, and provide actionable insights.
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
                'model': 'gemini-pro',
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
            
            # Detect sections
            if 'summary' in line.lower() or 'executive' in line.lower():
                current_section = 'summary'
                continue
            elif 'finding' in line.lower() or 'key point' in line.lower():
                current_section = 'findings'
                continue
            elif 'recommendation' in line.lower() or 'next step' in line.lower():
                current_section = 'recommendations'
                continue
            elif 'confidence' in line.lower():
                # Extract confidence score
                import re
                match = re.search(r'(\d+)%', line)
                if match:
                    confidence = int(match.group(1)) / 100.0
                continue
            
            # Add to appropriate section
            if current_section == 'summary' and len(line) > 20:
                summary += line + " "
            elif current_section == 'findings' and line.startswith(('-', '•', '*', '1', '2', '3')):
                findings.append(line.lstrip('-•*123456789. '))
            elif current_section == 'recommendations' and line.startswith(('-', '•', '*', '1', '2', '3')):
                recommendations.append(line.lstrip('-•*123456789. '))
        
        # Fallback if parsing fails
        if not summary:
            summary = ai_text[:300] + "..." if len(ai_text) > 300 else ai_text
        
        if not findings:
            findings = ["Analysis completed. See full response for details."]
        
        if not recommendations:
            recommendations = ["Review full analysis for recommended actions."]
        
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
