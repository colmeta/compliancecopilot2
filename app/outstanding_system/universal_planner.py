# ==============================================================================
# app/outstanding_system/universal_planner.py
# Universal Planning for ALL CLARITY Domains
# ==============================================================================
"""
Universal Planner

Before generating ANY content in ANY domain, we PLAN:
- What questions to ask?
- What research is needed?
- What's the narrative?
- What's the human angle?

This applies to ALL domains, not just funding.
"""

import os
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class PlanningSession:
    """A planning session for content creation."""
    domain: str
    questions: List[str]
    research_needs: List[str]
    narrative_outline: str
    human_angles: List[str]
    success_criteria: List[str]


class UniversalPlanner:
    """
    Universal Planner for ALL Domains
    
    NOT "just generate".
    EVERY domain gets:
    - Discovery questions
    - Research planning
    - Narrative development
    - Human touch identification
    """
    
    def __init__(self):
        """Initialize universal planner."""
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
    
    def create_plan(
        self,
        domain: str,
        task_type: str,
        initial_context: Dict[str, Any]
    ) -> PlanningSession:
        """
        Create a comprehensive plan BEFORE writing anything.
        
        This ensures every piece of content is:
        - Well-researched
        - Human-centered
        - Strategically structured
        """
        import google.generativeai as genai
        
        genai.configure(api_key=self.google_api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        planning_prompt = f"""You are planning content creation for the {domain} domain.

TASK TYPE: {task_type}
INITIAL CONTEXT: {initial_context}

Create a COMPREHENSIVE PLAN before writing:

1. DISCOVERY QUESTIONS (5-7 questions):
   What do we NEED to know to do this right?
   - Not generic questions
   - Specific to THIS task
   - Will reveal critical insights
   
   Example for legal brief:
   ❌ "What is the case about?" (too generic)
   ✅ "What specific precedent from the 9th Circuit would most strongly support our position on standing?"

2. RESEARCH NEEDS (3-5 areas):
   What research will make this OUTSTANDING?
   - Specific data points needed
   - Benchmarks to find
   - Evidence to gather
   
3. NARRATIVE OUTLINE:
   What's the STORY we're telling?
   - Opening hook
   - Key arguments/points
   - Flow and structure
   - Closing impact
   
4. HUMAN ANGLES (2-3 angles):
   Where are the PEOPLE in this?
   - Specific individuals affected
   - Real-world impact
   - Emotional resonance
   - Why people should CARE
   
5. SUCCESS CRITERIA (3-4 criteria):
   What makes this OUTSTANDING?
   - Quality benchmarks
   - Audience impact goals
   - Specific outcomes desired

Format as clear sections with specific, actionable items."""
        
        plan_text = model.generate_content(planning_prompt).text
        
        return self._parse_plan(plan_text, domain)
    
    def _parse_plan(self, plan_text: str, domain: str) -> PlanningSession:
        """Parse plan text into structured session."""
        lines = plan_text.split('\n')
        
        questions = []
        research_needs = []
        human_angles = []
        success_criteria = []
        narrative_lines = []
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            if 'question' in line.lower():
                current_section = 'questions'
            elif 'research' in line.lower():
                current_section = 'research'
            elif 'narrative' in line.lower() or 'story' in line.lower():
                current_section = 'narrative'
            elif 'human' in line.lower() or 'angle' in line.lower():
                current_section = 'human'
            elif 'success' in line.lower() or 'criteria' in line.lower():
                current_section = 'success'
            
            # Add to appropriate list
            if line.startswith(('-', '•', '*', '1.', '2.', '3.', '4.', '5.', '?')):
                content = line.lstrip('-•*123456789. ')
                if current_section == 'questions':
                    questions.append(content)
                elif current_section == 'research':
                    research_needs.append(content)
                elif current_section == 'human':
                    human_angles.append(content)
                elif current_section == 'success':
                    success_criteria.append(content)
            elif current_section == 'narrative':
                narrative_lines.append(line)
        
        return PlanningSession(
            domain=domain,
            questions=questions,
            research_needs=research_needs,
            narrative_outline='\n'.join(narrative_lines),
            human_angles=human_angles,
            success_criteria=success_criteria
        )


def get_universal_planner() -> UniversalPlanner:
    """Get or create universal planner."""
    return UniversalPlanner()
