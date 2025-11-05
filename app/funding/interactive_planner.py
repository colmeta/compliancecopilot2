# ==============================================================================
# app/funding/interactive_planner.py
# Interactive Planning Session - Plan WITH the Entrepreneur
# ==============================================================================
"""
Interactive Planning Session

This is NOT "give me your idea and I'll generate docs".

This is: "Let's sit down together and really understand your vision."

We ask questions. We listen. We understand. THEN we create.
"""

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class Question:
    """A question to ask the entrepreneur."""
    question: str
    why_asking: str  # Context for why this matters
    category: str  # vision, market, team, etc.
    priority: str  # critical, important, nice-to-have


class InteractivePlanner:
    """
    Interactive Planning Session
    
    Before generating ANY documents, we need to truly understand:
    - The VISION (what world are you creating?)
    - The WHY (why does this matter?)
    - The IMPACT (whose lives will change?)
    - The PASSION (what drives you?)
    
    This makes documents REAL, not generic.
    """
    
    def __init__(self):
        """Initialize interactive planner."""
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
    
    def generate_discovery_questions(
        self,
        idea: str,
        funding_level: str,
        initial_context: Dict[str, Any]
    ) -> List[Question]:
        """
        Generate personalized discovery questions.
        
        These aren't generic questions. These are specific to THIS idea,
        THIS entrepreneur, THIS vision.
        """
        import google.generativeai as genai
        
        genai.configure(api_key=self.google_api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        prompt = f"""You are a wise business mentor conducting a discovery session with an entrepreneur.

THEIR IDEA:
{idea}

TARGET FUNDING LEVEL: {funding_level}

WHAT THEY'VE SHARED:
{initial_context}

Your job is to ask DEEP, THOUGHTFUL questions that will help you understand:
1. Their VISION (what world are they creating?)
2. Their WHY (why does this matter to them personally?)
3. The IMPACT (whose lives will change and how?)
4. The CHALLENGES (what keeps them up at night?)
5. The TEAM (who's on this journey?)
6. The MARKET (who desperately needs this?)

Generate 15-20 questions that are:
- Specific to THIS idea (not generic startup questions)
- Open-ended (require thoughtful answers)
- Insightful (reveal what investors need to know)
- Human (connect to real emotions and motivations)

Format each as:
QUESTION: [the question]
WHY: [why this matters for their funding readiness]
CATEGORY: [vision|why|impact|market|team|operations|financials]
PRIORITY: [critical|important|nice-to-have]

Example of a GREAT question:
QUESTION: "You mentioned this could save small businesses $50K/year. Tell me about the specific business owner you're picturing when you say that - what's their name, what keeps them up at night, how will their life change when they use your solution?"
WHY: This reveals if they deeply understand their customer (critical for investors)
CATEGORY: impact
PRIORITY: critical

Example of a BAD question (too generic):
"What is your target market?" ❌

Now generate questions specific to THEIR idea."""
        
        response = model.generate_content(prompt)
        
        # Parse questions
        questions = self._parse_questions(response.text)
        
        return questions
    
    def conduct_planning_session(
        self,
        idea: str,
        funding_level: str,
        questionnaire_responses: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Conduct a full planning session.
        
        This creates a "brief" - a comprehensive understanding of the venture
        that will guide all document creation.
        
        Think of this as the "brief" you'd give to a top-tier consulting firm.
        """
        import google.generativeai as genai
        
        genai.configure(api_key=self.google_api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Synthesize responses into a coherent narrative
        responses_text = "\n\n".join([
            f"Q: {q}\nA: {a}"
            for q, a in questionnaire_responses.items()
        ])
        
        synthesis_prompt = f"""You are synthesizing a discovery session with an entrepreneur.

THEIR IDEA:
{idea}

DISCOVERY SESSION (Questions & Answers):
{responses_text}

Create a comprehensive BRIEF that captures:

1. THE VISION (Paint the picture)
   - What world are they creating?
   - What's their 10-year vision?
   - What's the ultimate impact?
   
2. THE WHY (Personal motivation)
   - Why does THIS person care about THIS problem?
   - What's their personal connection?
   - What drives them?
   
3. THE PROBLEM (Deep understanding)
   - Who suffers from this problem today?
   - How does it affect their lives?
   - What's the human cost of not solving this?
   
4. THE SOLUTION (Unique approach)
   - How does this solve it differently?
   - Why hasn't this been done before?
   - What makes it inevitable?
   
5. THE IMPACT (Lives changed)
   - Whose life changes first?
   - How does impact scale?
   - What's the ripple effect?
   
6. THE OPPORTUNITY (Market timing)
   - Why now?
   - What's changing?
   - What's the urgency?
   
7. THE TEAM (Why them?)
   - What makes them uniquely qualified?
   - What's their unfair advantage?
   - What gaps need filling?
   
8. THE ASK (What they need)
   - What specifically do they need to succeed?
   - What milestones will funding achieve?
   - What's the return for investors?

Write this as a NARRATIVE, not bullets. Make it compelling. Make it human.
This should read like a story that investors can't put down."""
        
        narrative = model.generate_content(synthesis_prompt).text
        
        # Extract key themes and messages
        themes_prompt = f"""Based on this narrative:

{narrative}

Extract:
1. CORE MESSAGE (one sentence that captures everything)
2. EMOTIONAL HOOKS (what makes people care?)
3. KEY DIFFERENTIATORS (what sets this apart?)
4. PROOF POINTS (what evidence exists?)
5. COMPELLING STORY ELEMENTS (what makes this memorable?)

Format as JSON."""
        
        themes = model.generate_content(themes_prompt).text
        
        return {
            "narrative_brief": narrative,
            "themes": themes,
            "questionnaire_responses": questionnaire_responses,
            "confidence": "high"  # We have deep understanding
        }
    
    def _parse_questions(self, text: str) -> List[Question]:
        """Parse questions from LLM response."""
        questions = []
        lines = text.split('\n')
        
        current_question = {}
        for line in lines:
            line = line.strip()
            
            if line.startswith('QUESTION:'):
                if current_question:  # Save previous
                    questions.append(Question(
                        question=current_question.get('question', ''),
                        why_asking=current_question.get('why', ''),
                        category=current_question.get('category', 'general'),
                        priority=current_question.get('priority', 'important')
                    ))
                current_question = {'question': line.replace('QUESTION:', '').strip()}
            
            elif line.startswith('WHY:'):
                current_question['why'] = line.replace('WHY:', '').strip()
            
            elif line.startswith('CATEGORY:'):
                current_question['category'] = line.replace('CATEGORY:', '').strip()
            
            elif line.startswith('PRIORITY:'):
                current_question['priority'] = line.replace('PRIORITY:', '').strip()
        
        # Add last question
        if current_question:
            questions.append(Question(
                question=current_question.get('question', ''),
                why_asking=current_question.get('why', ''),
                category=current_question.get('category', 'general'),
                priority=current_question.get('priority', 'important')
            ))
        
        return questions


def get_interactive_planner() -> InteractivePlanner:
    """Get or create interactive planner."""
    return InteractivePlanner()
