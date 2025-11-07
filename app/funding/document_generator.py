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
            
            },
            
            'financial_projections': {
                'name': '5-Year Financial Projections',
                'category': 'financial',
                'pages': 12,
                'output_format': 'markdown',
                'system_prompt': """You are a CFO who has raised $500M+ and knows exactly what investors scrutinize in financial projections.
Your projections are:
- Conservative yet ambitious (not hockey sticks, but growth is credible)
- Bottom-up built (unit economics → revenue model → P&L)
- Assumption-transparent (every number has a clear source)
- Scenario-tested (best/base/worst case)
- Milestone-linked (growth tied to product/team milestones)
Think like you're presenting to Sequoia's financial diligence team.""",
                'requirements': """
Create comprehensive 5-year financial projections:

1. Executive Summary of Financials (1 page)
   - Key metrics overview
   - Break-even timeline
   - Capital requirements
   
2. Revenue Model (2 pages)
   - Unit economics (CAC, LTV, payback period)
   - Pricing strategy and justification
   - Revenue streams breakdown
   - Growth assumptions with sources
   
3. 5-Year P&L (2 pages)
   - Revenue by year (with growth rates)
   - Cost of goods sold
   - Operating expenses breakdown
   - EBITDA and net income
   
4. Cash Flow Statement (2 pages)
   - Operating cash flow
   - Capital expenditures
   - Financing activities
   - Cash runway analysis
   
5. Balance Sheet (2 pages)
   - Assets (current and long-term)
   - Liabilities
   - Shareholder equity
   
6. Key Assumptions (2 pages)
   - Market size and penetration rates
   - Customer acquisition assumptions
   - Pricing and churn assumptions
   - Hiring plan and salary assumptions
   
7. Scenario Analysis (1 page)
   - Best case (25% above base)
   - Base case (most likely)
   - Worst case (25% below base)
   
All numbers must be realistic, well-sourced, and defensible in investor meetings.
""",
                'format': """
# 5-Year Financial Projections

## Executive Summary
[Key financial metrics and milestones]

## Revenue Model
### Unit Economics
- Customer Acquisition Cost (CAC): $X
- Lifetime Value (LTV): $Y
- LTV/CAC Ratio: Z:1
- Payback Period: N months

### Revenue Streams
[Detailed breakdown]

## Year-by-Year Projections
[Tables with all financials]

[Continue with all sections]
"""
            },
            
            'go_to_market': {
                'name': 'Go-to-Market Strategy',
                'category': 'market',
                'pages': 8,
                'output_format': 'markdown',
                'system_prompt': """You are a growth strategist who has launched 50+ successful products and knows the difference between a plan and a winning GTM strategy.
Your GTM strategies are:
- Channel-specific with clear playbooks
- Metric-driven (know exactly what success looks like)
- Phase-gated (crawl/walk/run approach)
- Competitive-aware (how to win against incumbents)
- Budget-realistic (ROI on every dollar spent)
Think like you're advising a Series A company entering a competitive market.""",
                'requirements': """
Create a comprehensive go-to-market strategy:

1. Market Entry Strategy (2 pages)
   - Beachhead market (first customers)
   - Expansion sequence (geographic/vertical)
   - Positioning statement
   - Differentiation strategy
   
2. Customer Acquisition Channels (3 pages)
   - Primary channels (with expected CAC and conversion rates)
   - Secondary channels
   - Channel-specific tactics and playbooks
   - Budget allocation by channel
   
3. Sales Strategy (2 pages)
   - Sales process and cycle length
   - Team structure and hiring plan
   - Sales tools and enablement
   - Key partnerships and alliances
   
4. Marketing Strategy (1 page)
   - Brand positioning
   - Content strategy
   - Demand generation tactics
   - PR and thought leadership plan
   
5. Success Metrics (1 page)
   - Month-by-month targets (users, revenue, CAC)
   - Leading indicators to track
   - Pivot triggers (when to adjust)
""",
                'format': """
# Go-to-Market Strategy

## Market Entry
### Beachhead Market
[First target customer segment]

### Positioning
[How we position against competition]

## Customer Acquisition
[Detailed channel strategies]

[Continue with all sections]
"""
            },
            
            'competitive_analysis': {
                'name': 'Competitive Analysis & Market Positioning',
                'category': 'market',
                'pages': 6,
                'output_format': 'markdown',
                'system_prompt': """You are a competitive intelligence analyst who has helped companies win against giants like Amazon, Google, and Microsoft.
Your competitive analyses are:
- Brutally honest (acknowledge competitor strengths)
- Strategically insightful (find the wedge to win)
- Data-backed (market share, funding, customer reviews)
- Forward-looking (where is the market going?)
- Action-oriented (how to compete and win)
Think like you're briefing a CEO before a board meeting.""",
                'requirements': """
Create comprehensive competitive analysis:

1. Competitive Landscape (2 pages)
   - Direct competitors (3-5 companies)
   - Indirect competitors and substitutes
   - Market positioning map
   - Competitive matrix (features, pricing, strengths, weaknesses)
   
2. Competitor Deep Dives (2 pages)
   - Each major competitor's strategy
   - Their strengths (be honest)
   - Their vulnerabilities (where we can win)
   - Recent moves and funding
   
3. Our Competitive Advantages (1 page)
   - Unique value proposition
   - Sustainable moats (technology, network effects, etc.)
   - Defensibility strategy
   
4. Market Trends & Opportunities (1 page)
   - Industry trends favoring us
   - Emerging opportunities
   - Potential threats to monitor
""",
                'format': """
# Competitive Analysis

## Competitive Landscape
[Market overview and key players]

## Competitor Profiles
### [Competitor 1]
- **Strengths**: [Honest assessment]
- **Weaknesses**: [Where we can win]
- **Strategy**: [What they're doing]

[Continue for all competitors]

## Our Competitive Advantages
[Clear differentiation]

## Market Opportunities
[Where we can win]
"""
            },
            
            'product_roadmap': {
                'name': 'Product Roadmap & Development Plan',
                'category': 'operations',
                'pages': 6,
                'output_format': 'markdown',
                'system_prompt': """You are a Head of Product at a top tech company who has shipped products used by millions.
Your product roadmaps are:
- Customer-driven (tied to real pain points)
- Milestone-based (clear success criteria)
- Resource-realistic (achievable with available team)
- Competitive-aware (feature parity where needed, innovation where possible)
- Metric-focused (know how each feature moves KPIs)
Think like you're presenting to a VP of Engineering and CEO.""",
                'requirements': """
Create a detailed product roadmap:

1. Product Vision & Principles (1 page)
   - Long-term product vision (3-5 years)
   - Core product principles
   - Success metrics
   
2. Current Product State (1 page)
   - Features shipped
   - User feedback and insights
   - Technical debt and infrastructure
   
3. 18-Month Roadmap (3 pages)
   - Quarters 1-2: MVP and core features
   - Quarters 3-4: Scale and optimization
   - Quarters 5-6: Advanced features and expansion
   - Each feature with: rationale, user impact, success metrics, dependencies
   
4. Technical Infrastructure (1 page)
   - Technology stack
   - Scalability plan
   - Security and compliance
   - Key technical milestones
""",
                'format': """
# Product Roadmap & Development Plan

## Product Vision
[3-5 year vision]

## Current State
[What we have today]

## 18-Month Roadmap

### Q1-Q2: Foundation
**Feature 1: [Name]**
- **Why**: [Customer pain point]
- **Impact**: [Expected metrics]
- **Timeline**: [Weeks]
- **Resources**: [Team needs]

[Continue for all features]

## Technical Infrastructure
[Stack and scalability plan]
"""
            },
            
            'team_bios': {
                'name': 'Team Bios & Organizational Chart',
                'category': 'operations',
                'pages': 4,
                'output_format': 'markdown',
                'system_prompt': """You are a talent/HR executive who knows that investors invest in teams, not just ideas.
Your team bios are:
- Credibility-building (highlight relevant wins and expertise)
- Story-driven (why this person, for this role, at this company)
- Complementary (show how skills mesh together)
- Ambitious (show ability to scale beyond current stage)
- Human (show passion and cultural fit)
Think like you're writing for a Sequoia partner evaluating team quality.""",
                'requirements': """
Create compelling team documentation:

1. Team Overview (1 page)
   - Team philosophy and culture
   - Why this team will win
   - Hiring plan for next 18 months
   
2. Founder Bios (1-2 pages)
   - Background and relevant experience
   - Previous wins and track record
   - Why they're uniquely qualified for this
   - Roles and responsibilities
   - Personal motivation and story
   
3. Key Team Members (1 page)
   - First 5-10 hires
   - Their backgrounds and expertise
   - What they bring to the company
   
4. Advisory Board (0.5 pages)
   - Advisors and their expertise
   - How they're helping the company
   
5. Organizational Chart (0.5 pages)
   - Current structure
   - 18-month projected structure
""",
                'format': """
# Team Bios & Organizational Structure

## Team Philosophy
[Culture and values]

## Founders

### [Founder Name], CEO
**Background**: [Education, previous roles]
**Track Record**: [Key achievements]
**Expertise**: [Relevant skills]
**Why Now**: [Personal story and motivation]

[Continue for all founders]

## Key Team Members
[Profiles of critical hires]

## Advisory Board
[Advisor profiles]

## Organizational Chart
[Current and projected structure]
"""
            },
            
            'market_research': {
                'name': 'Market Research & Validation Report',
                'category': 'market',
                'pages': 10,
                'output_format': 'markdown',
                'system_prompt': """You are a market research analyst at McKinsey who has conducted 200+ market studies for Fortune 500 companies.
Your market research is:
- Data-driven (cite sources for every claim)
- Segmentation-clear (TAM/SAM/SOM with bottom-up math)
- Trend-aware (macro and micro trends)
- Customer-validated (real customer insights, not assumptions)
- Opportunity-focused (where the white space is)
Think like you're presenting to a PE firm evaluating a $100M investment.""",
                'requirements': """
Create comprehensive market research:

1. Market Size & Segmentation (3 pages)
   - Total Addressable Market (TAM) - top-down and bottom-up
   - Serviceable Addressable Market (SAM)
   - Serviceable Obtainable Market (SOM)
   - Market segments and sizing
   - Sources for all numbers
   
2. Market Dynamics (2 pages)
   - Growth rates and trends
   - Key drivers and accelerators
   - Market maturity and lifecycle stage
   - Regulatory environment
   
3. Customer Analysis (3 pages)
   - Target customer segments (3-5 personas)
   - Customer needs and pain points
   - Buying behavior and decision criteria
   - Customer validation (interviews, surveys, pilot data)
   
4. Market Opportunities (2 pages)
   - Underserved segments
   - Emerging trends creating opportunities
   - White space analysis
   - Market entry barriers and how to overcome
""",
                'format': """
# Market Research & Validation

## Market Size

### Total Addressable Market (TAM)
**Top-Down**: $X billion
- Source: [Industry report]
- Calculation: [Show math]

**Bottom-Up**: $Y billion
- Unit economics: [Show math]
- Number of potential customers: [Data]

[Continue with SAM and SOM]

## Market Dynamics
[Trends and growth drivers]

## Customer Analysis
### Persona 1: [Name]
- **Demographics**: [Profile]
- **Pain Points**: [List]
- **Validation**: [Customer quotes/data]

[Continue for all sections]
"""
            },
            
            'risk_analysis': {
                'name': 'Risk Analysis & Mitigation Strategy',
                'category': 'operations',
                'pages': 5,
                'output_format': 'markdown',
                'system_prompt': """You are a risk management consultant who has helped companies avoid $100M+ in losses.
Your risk analyses are:
- Comprehensive (identify all major risks)
- Realistic (acknowledge probability and impact)
- Actionable (specific mitigation strategies)
- Monitored (how to track and respond)
- Balanced (don't scare investors, but be honest)
Think like you're advising a board on fiduciary responsibility.""",
                'requirements': """
Create comprehensive risk analysis:

1. Market Risks (1.5 pages)
   - Market adoption slower than expected
   - Competitor moves
   - Market dynamics shift
   - Mitigation strategies for each
   
2. Operational Risks (1.5 pages)
   - Team/talent risks
   - Technology/product risks
   - Supply chain/partnership risks
   - Mitigation strategies
   
3. Financial Risks (1 page)
   - Funding risks
   - Unit economics worse than modeled
   - Cash burn higher than projected
   - Mitigation strategies
   
4. Regulatory & Legal Risks (0.5 pages)
   - Compliance risks
   - IP risks
   - Liability risks
   - Mitigation strategies
   
5. Risk Monitoring Framework (0.5 pages)
   - Key risk indicators to track
   - Response triggers
   - Escalation procedures
""",
                'format': """
# Risk Analysis & Mitigation Strategy

## Market Risks

### Risk 1: [Name]
**Probability**: Low/Medium/High
**Impact**: $X or [Description]
**Indicators**: [Early warning signs]
**Mitigation**: [Specific actions]
**Contingency**: [If risk materializes]

[Continue for all risk categories]

## Risk Monitoring
[Dashboard of key indicators]
"""
            },
            
            'impact_assessment': {
                'name': 'Impact Assessment & Social Value',
                'category': 'impact',
                'pages': 6,
                'output_format': 'markdown',
                'system_prompt': """You are an impact measurement expert who has helped social enterprises secure $200M+ in funding from impact investors and foundations.
Your impact assessments are:
- Metric-rigorous (quantified outcomes, not just outputs)
- Theory-driven (clear logic models)
- Evidence-based (cite research and comparable programs)
- Long-term focused (multi-year impact projections)
- ROI-calculated (social return on investment)
Think like you're presenting to Gates Foundation or Omidyar Network.""",
                'requirements': """
Create comprehensive impact assessment:

1. Impact Thesis (1 page)
   - Problem statement (scope and urgency)
   - Theory of change
   - Target beneficiaries
   - Impact goals (3-5 year)
   
2. Impact Metrics (2 pages)
   - Primary outcomes (lives changed, dollars saved, etc.)
   - Secondary outcomes
   - Leading indicators
   - Measurement methodology
   - Comparison to alternatives
   
3. Impact Projections (2 pages)
   - Year 1-5 impact milestones
   - Cumulative impact by end of 5 years
   - Cost per outcome
   - Social return on investment (SROI)
   
4. Impact Evidence (1 page)
   - Pilot results
   - Academic research supporting approach
   - Case studies of similar programs
   - Expert endorsements
""",
                'format': """
# Impact Assessment & Social Value

## Impact Thesis

### The Problem
[Scope, scale, urgency]

### Our Solution
[How we create impact]

### Theory of Change
Problem → Activity → Output → Outcome → Impact

## Impact Metrics

### Primary Outcomes
- **Metric 1**: [Lives improved, dollars saved, etc.]
  - Baseline: [Current state]
  - Target Year 5: [Goal]
  - Measurement: [How we track]

[Continue for all metrics]

## 5-Year Impact Projections
[Detailed projections with methodology]

## Impact Evidence
[Pilot data, research, case studies]
"""
            },
            
            'investor_faq': {
                'name': 'Investor FAQ & Due Diligence Pack',
                'category': 'specialized',
                'pages': 8,
                'output_format': 'markdown',
                'system_prompt': """You are a startup lawyer who has closed 500+ funding rounds and knows every question investors will ask.
Your FAQs are:
- Comprehensive (50+ common investor questions)
- Transparent (honest about challenges)
- Data-backed (specific numbers and evidence)
- Forward-looking (address future plans)
- Legally sound (reviewed and defensible)
Think like you're prepping a founder for partner meetings at top VCs.""",
                'requirements': """
Create comprehensive investor FAQ:

1. Company & Product (15 questions)
   - What do you do? (elevator pitch)
   - Why now?
   - What's your unfair advantage?
   - How does the product work?
   - What's your IP strategy?
   
2. Market & Competition (15 questions)
   - How big is the market?
   - Who are your competitors?
   - Why will you win?
   - What's your go-to-market strategy?
   - Who are your customers?
   
3. Business Model & Financials (15 questions)
   - How do you make money?
   - What's your pricing?
   - What are unit economics?
   - When will you be profitable?
   - What's your burn rate?
   
4. Team & Operations (10 questions)
   - Who's on the team?
   - What's the hiring plan?
   - Where are you based?
   - What are key operational risks?
   - What's your culture?
   
5. Fundraising & Use of Funds (10 questions)
   - How much are you raising?
   - What will you use it for?
   - What milestones will you hit?
   - When will you raise next?
   - What's your exit strategy?
   
Each answer should be 2-4 sentences: concise but complete.
""",
                'format': """
# Investor FAQ & Due Diligence

## Company & Product

**Q: What does [Company] do?**
A: [Elevator pitch - 2-3 sentences]

**Q: Why now? Why is this the right time?**
A: [Market timing and catalysts]

[Continue with all 65+ questions]
"""
            },
            
            'one_pager': {
                'name': 'One-Page Investment Summary',
                'category': 'core',
                'pages': 1,
                'output_format': 'markdown',
                'system_prompt': """You are a venture partner who reviews 1,000 one-pagers per year and knows what makes investors say "tell me more" in 30 seconds.
Your one-pagers are:
- Punchy and scannable (busy investors, 30-second read)
- Metric-heavy (numbers over words)
- Urgency-creating (why invest NOW)
- Team-credible (track record and expertise)
- Vision-inspiring (why this matters)
Think like you're competing for attention at a Demo Day with 50 other companies.""",
                'requirements': """
Create a compelling one-page summary:

1. Header (company name, tagline, contact)
2. The Problem (2-3 sentences, quantified)
3. The Solution (2-3 sentences, what makes it unique)
4. Market Opportunity (TAM/SAM/SOM in one line each)
5. Traction (3-5 key metrics with growth rates)
6. Business Model (one line: how you make money)
7. Team (one line per founder: name, title, previous win)
8. Competition (one line: how you're different)
9. The Ask (amount, use of funds, milestones)
10. Contact Info (email, phone, website)

Must fit on ONE page when printed. Every word counts.
""",
                'format': """
# [Company Name]
**[One-line tagline that captures what you do]**

**PROBLEM**: [2-3 sentences with quantified pain]

**SOLUTION**: [2-3 sentences with unique value prop]

**MARKET**: 
- TAM: $X billion | SAM: $Y billion | SOM: $Z billion (Year 5)

**TRACTION**:
- $X MRR (Y% MoM growth) | Z customers | A% retention
- [Other key metrics]

**BUSINESS MODEL**: [One sentence]

**TEAM**: 
- [Name], CEO: [Previous win] | [Name], CTO: [Previous win]

**COMPETITION**: [One sentence differentiation]

**THE ASK**: Raising $X for [Y months runway] to [Z milestone]

**CONTACT**: [Email] | [Phone] | [Website]
"""
            }
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
