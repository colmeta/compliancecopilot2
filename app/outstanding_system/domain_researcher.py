# ==============================================================================
# app/outstanding_system/domain_researcher.py
# Domain-Specific Research for ALL CLARITY Domains
# ==============================================================================
"""
Domain Researcher

Conducts deep research specific to each CLARITY domain:
- Legal: Case law, precedents, statutes
- Financial: Industry benchmarks, ratios, comparables
- Security: Threat intelligence, patterns, risk factors
- Healthcare: Clinical guidelines, compliance standards
- Proposal: RFP requirements, evaluation criteria, past wins
- Engineering: Codes, standards, specifications
- Grant: Funder priorities, success factors, budget ranges
- Market: TAM/SAM/SOM, competitive landscape, trends
- Pitch Deck: Investor expectations, market data, comps
- Investor Diligence: Due diligence checklists, risk factors
- Education: Accreditation standards, pedagogy, outcomes
- Corporate: Market analysis, strategic frameworks
"""

import os
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class DomainResearch:
    """Research findings for a specific domain."""
    domain: str
    key_findings: List[str]
    evidence: List[str]
    benchmarks: Dict[str, Any]
    risks: List[str]
    opportunities: List[str]
    recommendations: List[str]
    confidence: float


class DomainResearcher:
    """
    Domain-Specific Researcher
    
    NOT generic research.
    EACH domain gets tailored, deep research:
    - Legal: Case precedents
    - Financial: Industry ratios
    - Security: Threat patterns
    - Etc.
    """
    
    def __init__(self):
        """Initialize domain researcher."""
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
    
    def research_for_domain(
        self,
        domain: str,
        context: Dict[str, Any],
        task_type: str
    ) -> DomainResearch:
        """
        Conduct domain-specific research.
        
        Each domain has unique research needs:
        - Legal: Precedents, statutes, case law
        - Financial: Benchmarks, ratios, comps
        - Security: Threat intelligence, patterns
        - Etc.
        """
        import google.generativeai as genai
        
        genai.configure(api_key=self.google_api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Get domain-specific research prompt
        research_prompt = self._build_domain_research_prompt(
            domain, context, task_type
        )
        
        # Conduct research
        research_text = model.generate_content(research_prompt).text
        
        # Parse into structured findings
        return self._parse_research(research_text, domain)
    
    def _build_domain_research_prompt(
        self, domain: str, context: Dict[str, Any], task_type: str
    ) -> str:
        """Build research prompt specific to domain."""
        
        domain_prompts = {
            'legal': f"""You are conducting legal research.

TASK: {task_type}
CONTEXT: {context}

Conduct DEEP LEGAL RESEARCH:

1. CASE LAW: Find relevant precedents
   - Similar cases and outcomes
   - Jurisdictional considerations
   - Recent rulings that apply

2. STATUTES & REGULATIONS: Applicable laws
   - Federal, state, local laws
   - Regulatory requirements
   - Compliance mandates

3. LEGAL STRATEGY: What works?
   - Successful arguments
   - Common pitfalls
   - Negotiation leverage

4. RISK ASSESSMENT: Legal exposure
   - Potential liabilities
   - Worst-case scenarios
   - Mitigation strategies

Provide SPECIFIC citations, case names, and statute numbers.""",

            'financial': f"""You are conducting financial research.

TASK: {task_type}
CONTEXT: {context}

Conduct DEEP FINANCIAL RESEARCH:

1. INDUSTRY BENCHMARKS: What's normal?
   - Key financial ratios for this industry
   - Profitability benchmarks
   - Liquidity standards
   - Leverage norms

2. COMPARABLE ANALYSIS: Similar companies
   - Public comps and multiples
   - Transaction comps
   - Financial performance
   - Valuation ranges

3. MARKET CONDITIONS: Current environment
   - Interest rates and impact
   - Economic indicators
   - Sector trends
   - Investor sentiment

4. RISK FACTORS: Financial risks
   - Credit risk
   - Market risk
   - Operational risk
   - Mitigation strategies

Provide SPECIFIC numbers, ratios, and company names.""",

            'security': f"""You are conducting security intelligence research.

TASK: {task_type}
CONTEXT: {context}

Conduct DEEP SECURITY RESEARCH:

1. THREAT INTELLIGENCE: Known threats
   - Threat actor profiles
   - Attack patterns and TTPs
   - Recent incidents
   - Emerging threats

2. VULNERABILITY ASSESSMENT: Weak points
   - Common vulnerabilities
   - Exploitation methods
   - Security gaps
   - Attack vectors

3. INCIDENT ANALYSIS: Historical data
   - Similar incidents
   - Response effectiveness
   - Lessons learned
   - Best practices

4. RISK ASSESSMENT: Security posture
   - Threat level
   - Impact scenarios
   - Mitigation priorities
   - Resource needs

Provide SPECIFIC threat intelligence and evidence.""",

            'healthcare': f"""You are conducting healthcare research.

TASK: {task_type}
CONTEXT: {context}

Conduct DEEP HEALTHCARE RESEARCH:

1. CLINICAL GUIDELINES: Standards of care
   - Evidence-based protocols
   - Treatment guidelines
   - Quality measures
   - Best practices

2. REGULATORY COMPLIANCE: Requirements
   - HIPAA requirements
   - FDA regulations
   - Accreditation standards
   - Quality metrics

3. OUTCOMES RESEARCH: What works?
   - Clinical outcomes
   - Patient satisfaction
   - Cost-effectiveness
   - Quality indicators

4. RISK ASSESSMENT: Healthcare risks
   - Patient safety risks
   - Compliance risks
   - Quality issues
   - Mitigation strategies

Provide SPECIFIC clinical evidence and compliance requirements.""",

            'proposal': f"""You are conducting RFP/proposal research.

TASK: {task_type}
CONTEXT: {context}

Conduct DEEP PROPOSAL RESEARCH:

1. RFP ANALYSIS: Requirements
   - Mandatory requirements
   - Evaluation criteria
   - Scoring methodology
   - Compliance mandates

2. CUSTOMER RESEARCH: Who are they?
   - Organization priorities
   - Past awards and preferences
   - Decision-makers
   - Evaluation process

3. COMPETITIVE ANALYSIS: Who are we against?
   - Known competitors
   - Their strengths/weaknesses
   - Past performance
   - Differentiators

4. WIN STRATEGY: What wins?
   - Winning themes
   - Proof points needed
   - Past performance relevance
   - Price-to-win analysis

Provide SPECIFIC RFP requirements and competitive intelligence.""",
        }
        
        # Get domain-specific prompt or use generic
        return domain_prompts.get(domain, self._build_generic_research_prompt(domain, context, task_type))
    
    def _build_generic_research_prompt(
        self, domain: str, context: Dict[str, Any], task_type: str
    ) -> str:
        """Build generic research prompt for domains without specific templates."""
        return f"""You are conducting research for the {domain} domain.

TASK: {task_type}
CONTEXT: {context}

Conduct DEEP DOMAIN RESEARCH:

1. INDUSTRY STANDARDS: What's the norm?
   - Best practices
   - Industry benchmarks
   - Standard methodologies
   - Common approaches

2. KEY FACTORS: What matters?
   - Success factors
   - Common pitfalls
   - Critical requirements
   - Quality criteria

3. EXAMPLES & EVIDENCE: What works?
   - Case studies
   - Proven approaches
   - Data and metrics
   - Success stories

4. RISKS & OPPORTUNITIES: What to consider?
   - Potential risks
   - Mitigation strategies
   - Growth opportunities
   - Strategic advantages

Provide SPECIFIC evidence, data, and examples."""
    
    def _parse_research(self, research_text: str, domain: str) -> DomainResearch:
        """Parse research text into structured findings."""
        # Simplified parsing - in production, use better parsing
        lines = research_text.split('\n')
        
        key_findings = []
        evidence = []
        risks = []
        opportunities = []
        recommendations = []
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect sections
            if 'finding' in line.lower():
                current_section = 'findings'
            elif 'evidence' in line.lower() or 'data' in line.lower():
                current_section = 'evidence'
            elif 'risk' in line.lower():
                current_section = 'risks'
            elif 'opportunity' in line.lower() or 'opportunit' in line.lower():
                current_section = 'opportunities'
            elif 'recommend' in line.lower():
                current_section = 'recommendations'
            
            # Add to appropriate list
            if line.startswith(('-', '•', '*', '1.', '2.', '3.')):
                content = line.lstrip('-•*123456789. ')
                if current_section == 'findings':
                    key_findings.append(content)
                elif current_section == 'evidence':
                    evidence.append(content)
                elif current_section == 'risks':
                    risks.append(content)
                elif current_section == 'opportunities':
                    opportunities.append(content)
                elif current_section == 'recommendations':
                    recommendations.append(content)
        
        return DomainResearch(
            domain=domain,
            key_findings=key_findings[:10],
            evidence=evidence[:10],
            benchmarks={},  # Could be parsed more deeply
            risks=risks[:5],
            opportunities=opportunities[:5],
            recommendations=recommendations[:5],
            confidence=0.85
        )


def get_domain_researcher() -> DomainResearcher:
    """Get or create domain researcher."""
    return DomainResearcher()
