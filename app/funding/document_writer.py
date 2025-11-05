# ==============================================================================
# app/funding/document_writer.py
# Outstanding Document Writer - Human Touch + Deep Research
# ==============================================================================
"""
Outstanding Document Writer

This writer combines:
1. Deep research (facts, data, insights)
2. Human touch (emotion, resonance, story)
3. Multiple passes (refine, refine, refine)
4. Innovation in writing (not templates)

The result: Documents worthy of presenting to presidents.
"""

import os
from typing import Dict, List, Any, Optional


class OutstandingDocumentWriter:
    """
    Document Writer that creates OUTSTANDING content.
    
    Not AI slop. Not generic templates. 
    
    Real, researched, human, compelling documents that:
    - Touch people's hearts
    - Speak to real lives
    - Have depth and insight
    - Are innovative in their presentation
    - Make investors/leaders say "I need to be part of this"
    """
    
    def __init__(self):
        """Initialize document writer."""
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
    
    def write_executive_summary(
        self,
        narrative_brief: str,
        research: Dict[str, Any],
        funding_level: str,
        voice_profile: Optional[Any] = None
    ) -> str:
        """
        Write OUTSTANDING executive summary.
        
        Process:
        1. Research-based first draft
        2. Add human touch and emotion
        3. Refine for clarity and impact
        4. Polish for the target audience
        5. Final review for excellence
        """
        import google.generativeai as genai
        
        genai.configure(api_key=self.google_api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # PASS 1: Research-based draft
        draft_1_prompt = f"""You are writing an Executive Summary for Fortune 50 leaders / Y-Combinator / Presidential briefing.

NARRATIVE BRIEF (Deep understanding of the venture):
{narrative_brief}

RESEARCH INSIGHTS:
{research}

TARGET AUDIENCE: {funding_level}

Write the FIRST DRAFT - focus on SUBSTANCE:
- What's the massive problem? (with specific human impact)
- What's the innovative solution? (with proof it works)
- What's the market opportunity? (with hard data)
- What's the business model? (with unit economics)
- Why this team? (with unfair advantages)
- What's the ask? (with ROI projection)

Requirements:
1. Lead with IMPACT (whose lives change and how?)
2. Use SPECIFIC DATA (not "large market" but "$50B market growing 15%/year")
3. Show PROOF (pilot results, early traction, validation)
4. Be CONFIDENT (not arrogant, but assured)
5. Create URGENCY (why act now?)

This is a FIRST DRAFT - prioritize substance over style.
2-3 pages. Dense with insight."""
        
        draft_1 = model.generate_content(draft_1_prompt).text
        
        # PASS 2: Add human touch
        draft_2_prompt = f"""You are a master storyteller who brings documents to life.

Here's a substantive but dry executive summary:

{draft_1}

Now REWRITE it to add HUMAN TOUCH:

1. OPENING: Start with a human story
   - Not "The market is large"
   - But "Meet Sarah, a small business owner who spends 20 hours/week on compliance..."
   
2. THROUGHOUT: Connect to real lives
   - Not "reduces costs by 80%"
   - But "gives 20 hours back to business owners each week - time with family, time to grow"
   
3. EMOTION: Make people CARE
   - Why does this matter beyond money?
   - Whose life is transformed?
   - What world are we creating?
   
4. INNOVATION: Present ideas creatively
   - Use analogies that resonate
   - Frame in unexpected ways
   - Make complex ideas accessible
   
5. VOICE: Make it human, not robotic
   - Vary sentence length
   - Use active voice
   - Show passion (appropriate passion, not hype)

Keep ALL the substance from draft 1. Add the heart.

This should make readers FEEL something. Make them want to be part of this."""
        
        draft_2 = model.generate_content(draft_2_prompt).text
        
        # PASS 3: Refine for clarity
        draft_3_prompt = f"""You are an editor at a top-tier publication.

Here's a draft with substance and heart:

{draft_2}

Now REFINE for CLARITY and IMPACT:

1. STRUCTURE: Is the flow logical?
   - Does each paragraph build on the last?
   - Are transitions smooth?
   
2. CLARITY: Is every sentence clear?
   - Remove jargon
   - Explain complex ideas simply
   - Cut unnecessary words
   
3. IMPACT: Does every sentence earn its place?
   - Cut anything that doesn't advance the narrative
   - Strengthen weak phrases
   - Make every word count
   
4. RHYTHM: Does it read well?
   - Vary sentence structure
   - Create momentum
   - Build to key points

Make this CRISP. CLEAR. COMPELLING."""
        
        draft_3 = model.generate_content(draft_3_prompt).text
        
        # PASS 4: Polish for audience
        final_prompt = f"""You are preparing this executive summary for {funding_level} level review.

CURRENT DRAFT:
{draft_3}

FINAL POLISH for {funding_level}:

If PRESIDENTIAL:
- Emphasize national impact, job creation, competitiveness
- Use language appropriate for policymakers
- Focus on scalable impact

If Y-COMBINATOR:
- Emphasize scalability, tech innovation, team strength
- Use silicon valley language (product-market fit, unit economics, etc.)
- Show understanding of VC metrics

If FORTUNE 50:
- Emphasize strategic value, ROI, enterprise integration
- Use business language
- Focus on partnership benefits

If SERIES A:
- Emphasize traction, growth metrics, scale plan
- Use VC language
- Show clear path to next round

Make final adjustments for audience. This is the version that goes out."""
        
        final = model.generate_content(final_prompt).text
        
        return final
    
    def write_vision_statement(
        self,
        narrative_brief: str,
        emotional_hooks: List[str]
    ) -> str:
        """
        Write OUTSTANDING vision statement.
        
        Not "We want to be the leading provider of..."
        
        But "A world where every small business owner goes home at 5pm with
        peace of mind, knowing their business is compliant, secure, and growing."
        """
        import google.generativeai as genai
        
        genai.configure(api_key=self.google_api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        prompt = f"""You are crafting a VISION STATEMENT that inspires.

UNDERSTANDING OF THE VENTURE:
{narrative_brief}

EMOTIONAL HOOKS:
{emotional_hooks}

Create a vision statement that:

1. PAINTS A PICTURE of the future
   - What does the world look like when you succeed?
   - Be specific and vivid
   
2. IS ASPIRATIONAL yet believable
   - Big enough to inspire
   - Realistic enough to achieve
   
3. CONNECTS TO HUMAN VALUES
   - What do people care about?
   - How do lives improve?
   
4. IS MEMORABLE
   - Short enough to remember
   - Powerful enough to repeat
   
5. CREATES EMOTION
   - Makes people FEEL something
   - Makes them want to be part of it

Examples of GREAT vision statements:
- Microsoft: "A computer on every desk and in every home" (specific, visual, ambitious)
- Tesla: "To accelerate the world's transition to sustainable energy" (urgent, important, clear)

Examples of BAD vision statements:
- "To be the leading provider of..." ❌ (generic, corporate-speak)
- "To leverage synergies in..." ❌ (jargon, meaningless)

Write 3 options, then choose the best one. Explain why it's powerful."""
        
        response = model.generate_content(prompt).text
        
        return response
    
    def refine_with_human_voice(
        self,
        document: str,
        organization_voice: Optional[str] = None
    ) -> str:
        """
        Add human voice and remove robotic AI feel.
        
        This uses our Human Touch Writer to make it sound like
        a real person wrote it, not an AI.
        """
        from app.writing import get_human_touch_writer
        
        writer = get_human_touch_writer()
        
        # If we have organization voice samples, use them
        if organization_voice:
            voice_profile = writer.analyze_writing_samples([organization_voice])
            return writer.rewrite_with_voice(document, voice_profile)
        else:
            # Use default professional but human voice
            return writer.humanize_text(document)


def get_outstanding_writer() -> OutstandingDocumentWriter:
    """Get or create outstanding document writer."""
    return OutstandingDocumentWriter()
