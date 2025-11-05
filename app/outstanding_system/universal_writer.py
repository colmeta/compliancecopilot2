# ==============================================================================
# app/outstanding_system/universal_writer.py
# Universal Outstanding Writer - Works for ALL Domains
# ==============================================================================
"""
Universal Outstanding Writer

This writer can produce presidential-grade content for ANY domain:
- Legal briefs
- Financial reports
- Proposal Intelligence
- Grant proposals
- Pitch decks
- Security assessments
- Healthcare analyses
- Engineering documents
- Market research
- Education reports

It uses 5-pass refinement and human touch for EVERY output.
"""

import os
from typing import Dict, List, Any, Optional


class UniversalOutstandingWriter:
    """
    Universal Writer that applies Outstanding quality to ANY domain.
    
    NOT domain-specific templates.
    NOT one-shot generation.
    
    EVERY domain gets:
    - Deep research integration
    - Human touch (stories, emotion)
    - Multi-pass refinement (5 passes)
    - Audience adaptation
    - Refinement loops
    """
    
    def __init__(self):
        """Initialize universal writer."""
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
    
    def write_with_outstanding_quality(
        self,
        content_type: str,  # "brief", "report", "proposal", "analysis", etc.
        domain: str,  # "legal", "financial", "security", etc.
        context: Dict[str, Any],  # All the context needed
        research: Dict[str, Any],  # Research findings
        audience: str = "professional",  # "executive", "technical", "presidential"
        organization_voice: Optional[str] = None
    ) -> str:
        """
        Write OUTSTANDING content for ANY domain.
        
        This is the universal entry point. No matter what domain,
        the content goes through the same rigorous process:
        
        Pass 1: Research-backed draft (substance)
        Pass 2: Human touch (emotion)
        Pass 3: Clarity refinement (polish)
        Pass 4: Audience adaptation (relevance)
        Pass 5: Final excellence (perfection)
        """
        import google.generativeai as genai
        
        genai.configure(api_key=self.google_api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # PASS 1: Research-Backed Draft (SUBSTANCE)
        draft_1_prompt = self._build_research_draft_prompt(
            content_type, domain, context, research
        )
        draft_1 = model.generate_content(draft_1_prompt).text
        
        # PASS 2: Human Touch (EMOTION)
        draft_2_prompt = self._build_human_touch_prompt(
            draft_1, content_type, domain, context
        )
        draft_2 = model.generate_content(draft_2_prompt).text
        
        # PASS 3: Clarity Refinement (POLISH)
        draft_3_prompt = self._build_clarity_prompt(draft_2, domain)
        draft_3 = model.generate_content(draft_3_prompt).text
        
        # PASS 4: Audience Adaptation (RELEVANCE)
        draft_4_prompt = self._build_audience_prompt(
            draft_3, audience, domain, content_type
        )
        draft_4 = model.generate_content(draft_4_prompt).text
        
        # PASS 5: Final Excellence (PERFECTION)
        final_prompt = self._build_final_polish_prompt(
            draft_4, domain, content_type
        )
        final = model.generate_content(final_prompt).text
        
        # Optional: Add organization voice
        if organization_voice:
            final = self._apply_voice(final, organization_voice, model)
        
        return final
    
    def _build_research_draft_prompt(
        self, content_type: str, domain: str, context: Dict[str, Any], research: Dict[str, Any]
    ) -> str:
        """Build Pass 1 prompt: Research-backed draft."""
        return f"""You are writing a {content_type} for the {domain} domain.

CONTEXT:
{context}

RESEARCH FINDINGS:
{research}

Write PASS 1: RESEARCH-BACKED DRAFT

Focus on SUBSTANCE:
- Use SPECIFIC DATA from research (not "significant growth" but "23% YoY growth")
- Cite EVIDENCE for every claim
- Include NUMBERS, METRICS, BENCHMARKS
- Reference SOURCES and STUDIES
- Show PROOF, not assertions

Requirements:
1. Dense with factual information
2. Every claim backed by research
3. Specific numbers and data points
4. Professional terminology
5. Comprehensive coverage

This is a FIRST DRAFT - prioritize substance over style.
May be dry/dense - that's OK, we'll add human touch in next pass.

Length: Comprehensive (don't hold back on detail)."""
    
    def _build_human_touch_prompt(
        self, draft: str, content_type: str, domain: str, context: Dict[str, Any]
    ) -> str:
        """Build Pass 2 prompt: Add human touch."""
        return f"""You are a master storyteller bringing a {domain} {content_type} to life.

CURRENT DRAFT (substantive but dry):
{draft}

CONTEXT FOR HUMAN ELEMENTS:
{context}

Write PASS 2: ADD HUMAN TOUCH

Transform this from dry analysis to COMPELLING NARRATIVE:

1. OPENING: Start with a human story
   ❌ NOT: "The financial sector faces challenges"
   ✅ BUT: "Meet Elena, CFO of a mid-size manufacturer. Last quarter, she discovered a $2M discrepancy that nobody else caught. Here's how..."
   
2. THROUGHOUT: Connect to real lives
   ❌ NOT: "Efficiency increased by 40%"
   ✅ BUT: "That 40% efficiency gain means Sarah's team goes home at 6pm instead of 9pm - time with family, not just a metric"
   
3. EMOTION: Make people CARE
   - Why does this matter beyond the numbers?
   - Whose life changes?
   - What's at stake?
   
4. VOICE: Make it human, not robotic
   - Vary sentence length (long, short, medium)
   - Use active voice
   - Show appropriate passion
   - Use analogies that resonate
   
5. EXAMPLES: Use specific, named people
   - Not "customers" but "Sarah, a 45-year-old business owner in Austin"
   - Not "we helped clients" but "we helped Marcus save his family business"

KEEP ALL the research and data from Pass 1.
ADD the heart that makes readers feel something.

This should make readers CARE, not just understand."""
    
    def _build_clarity_prompt(self, draft: str, domain: str) -> str:
        """Build Pass 3 prompt: Clarity refinement."""
        return f"""You are an editor at a top-tier {domain} publication.

CURRENT DRAFT (has substance and emotion):
{draft}

Write PASS 3: REFINE FOR CLARITY

Make this CRISP, CLEAR, COMPELLING:

1. STRUCTURE: Logical flow?
   - Does each paragraph build on the last?
   - Are transitions smooth?
   - Is the arc clear?
   
2. CLARITY: Every sentence clear?
   - Remove jargon (or explain it)
   - Simplify complex ideas
   - Cut unnecessary words
   - Replace passive voice with active
   
3. IMPACT: Every sentence earns its place?
   - Does it advance the narrative?
   - Does it add value?
   - If not, cut it
   
4. RHYTHM: Does it read well?
   - Vary sentence structure
   - Create momentum
   - Build to key points
   - Read aloud test
   
5. PRECISION: Exact language?
   - Replace vague with specific
   - Replace weak verbs with strong
   - Remove hedging ("perhaps", "maybe", "might")

Cut 20% of words while keeping 100% of substance."""
    
    def _build_audience_prompt(
        self, draft: str, audience: str, domain: str, content_type: str
    ) -> str:
        """Build Pass 4 prompt: Audience adaptation."""
        audience_guidelines = {
            'executive': {
                'focus': 'Strategic implications, ROI, competitive advantage',
                'language': 'Business language, focus on outcomes and value',
                'format': 'Executive summary style, start with conclusion',
                'metrics': 'Business metrics (revenue, profit, market share, ROI)'
            },
            'technical': {
                'focus': 'Implementation details, technical specifications, methodology',
                'language': 'Technical precision, specific terminology',
                'format': 'Detailed analysis, methodology-first',
                'metrics': 'Technical metrics (performance, accuracy, efficiency)'
            },
            'presidential': {
                'focus': 'National impact, job creation, competitiveness, policy implications',
                'language': 'Policy language, macro-level thinking',
                'format': 'Briefing style, context → situation → options → recommendation',
                'metrics': 'National metrics (jobs, GDP impact, strategic advantage)'
            },
            'investor': {
                'focus': 'Market opportunity, traction, unit economics, return potential',
                'language': 'VC/finance language (TAM/SAM/SOM, LTV:CAC, burn rate)',
                'format': 'Investment thesis, risk-return analysis',
                'metrics': 'Investment metrics (IRR, exit multiples, market size)'
            },
            'regulatory': {
                'focus': 'Compliance, risk management, regulatory requirements',
                'language': 'Legal/regulatory terminology, precise definitions',
                'format': 'Compliance framework, evidence-based',
                'metrics': 'Compliance metrics (adherence %, audit findings, risk levels)'
            }
        }
        
        guidelines = audience_guidelines.get(audience, audience_guidelines['executive'])
        
        return f"""You are adapting a {domain} {content_type} for a {audience} audience.

CURRENT DRAFT:
{draft}

Write PASS 4: AUDIENCE ADAPTATION

Adapt for {audience.upper()} AUDIENCE:

1. FOCUS: {guidelines['focus']}
2. LANGUAGE: {guidelines['language']}
3. FORMAT: {guidelines['format']}
4. METRICS: {guidelines['metrics']}

Specific adaptations:
- Lead with what matters MOST to this audience
- Use THEIR language and mental models
- Frame benefits in THEIR terms
- Address THEIR concerns and objections
- Use THEIR metrics and KPIs

Keep all substance and human touch from previous passes.
Reframe for maximum relevance to THIS audience."""
    
    def _build_final_polish_prompt(
        self, draft: str, domain: str, content_type: str
    ) -> str:
        """Build Pass 5 prompt: Final polish."""
        return f"""You are performing final quality review on a {domain} {content_type}.

CURRENT DRAFT (almost there):
{draft}

Write PASS 5: FINAL EXCELLENCE

This is the version that goes out. Make it PERFECT:

1. READ-ALOUD TEST: Does it flow smoothly?
2. CONSISTENCY: Tone, voice, terminology consistent?
3. ACCURACY: All facts, figures, names correct?
4. COMPLETENESS: Nothing important missing?
5. IMPACT: Opens strong? Closes strong?
6. PROFESSIONAL: Typo-free, polished, publication-ready?

Make final adjustments:
- Perfect the opening (hook reader immediately)
- Perfect the closing (leave lasting impression)
- Perfect the transitions (seamless flow)
- Perfect the rhythm (varied, engaging)
- Perfect the polish (flawless execution)

This is the version a Fortune 50 CEO / President / Top Investor would read.
Make it worthy of them."""
    
    def _apply_voice(self, content: str, voice_sample: str, model: Any) -> str:
        """Apply organization's voice to content."""
        voice_prompt = f"""Analyze this writing sample to understand the organization's voice:

ORGANIZATION'S WRITING SAMPLE:
{voice_sample}

Now rewrite this content to match that voice:

CONTENT TO REWRITE:
{content}

Maintain:
- All facts and data
- All structure and flow
- All key messages

Adjust:
- Tone and style
- Word choice and phrasing
- Sentence structure
- Personality and voice

Make it sound like THEIR writing, not generic AI."""
        
        return model.generate_content(voice_prompt).text
    
    def refine_with_feedback(
        self,
        content: str,
        feedback: str,
        preserve: str,
        domain: str
    ) -> str:
        """Refine content based on user feedback."""
        import google.generativeai as genai
        
        genai.configure(api_key=self.google_api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        prompt = f"""You are refining a {domain} document based on user feedback.

CURRENT DOCUMENT:
{content}

WHAT TO PRESERVE:
{preserve}

USER FEEDBACK / WHAT TO IMPROVE:
{feedback}

Refine the document to:
1. Address ALL feedback points
2. Preserve what works
3. Maintain Outstanding quality (research-backed, human touch, clear, audience-adapted)

The user knows their vision best. Honor their feedback while maintaining excellence."""
        
        return model.generate_content(prompt).text


def get_universal_writer() -> UniversalOutstandingWriter:
    """Get or create universal outstanding writer."""
    return UniversalOutstandingWriter()
