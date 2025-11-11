# ==============================================================================
# app/data_science/insight_generator.py
# Insight Generator - Narrative Generation from Data
# ==============================================================================
"""
Insight Generator: Presidential-Grade Narrative from Data

Transforms raw data and statistics into compelling narratives suitable for:
- Presidential briefings
- Board presentations
- Executive summaries
- Policy documents
- Strategic reports

The system generates insights that are:
- Actionable
- Evidence-based
- Clearly communicated
- Strategically relevant
"""

import logging
from typing import Dict, Any, List
import os
import google.generativeai as genai
import json

logger = logging.getLogger(__name__)


class InsightGenerator:
    """
    Insight Generator: Presidential-Grade Narratives.
    
    Transforms data analysis into compelling stories and actionable recommendations.
    """
    
    def __init__(self):
        """Initialize the Insight Generator."""
        try:
            genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            self.initialized = True
            logger.info("InsightGenerator initialized - Presidential-Grade Narratives Ready")
        except Exception as e:
            logger.error(f"Failed to initialize InsightGenerator: {e}")
            self.initialized = False
    
    def generate_executive_summary(
        self,
        analysis_results: Dict[str, Any],
        context: str = "general"
    ) -> str:
        """
        Generate an executive summary from analysis results.
        
        Args:
            analysis_results: Results from AnalyticsEngine
            context: Context for the summary (e.g., 'board_meeting', 'policy', 'strategy')
            
        Returns:
            Executive summary text
        """
        if not self.initialized:
            return "Insight generation not available"
        
        try:
            # Build prompt
            prompt = self._build_summary_prompt(analysis_results, context)
            
            # Generate summary
            response = self.model.generate_content(prompt)
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Summary generation error: {e}")
            return "Error generating executive summary"
    
    def _build_summary_prompt(
        self,
        analysis_results: Dict[str, Any],
        context: str
    ) -> str:
        """Build prompt for executive summary generation."""
        insights = analysis_results.get('insights', [])
        stats = analysis_results.get('summary', {})
        
        insights_text = "\n".join([
            f"- {insight['title']}: {insight['description']} (Impact: {insight['impact']}, Confidence: {insight['confidence']*100:.0f}%)"
            for insight in insights[:5]  # Top 5 insights
        ])
        
        context_instructions = {
            'general': "for general business understanding",
            'board_meeting': "for presentation to a corporate board of directors",
            'policy': "for policy makers and government officials",
            'strategy': "for strategic planning and decision-making",
            'presidential': "for presentation to heads of state and senior government officials"
        }
        
        instruction = context_instructions.get(context, context_instructions['general'])
        
        return f"""You are a senior data analyst preparing an executive summary {instruction}.

DATA ANALYSIS RESULTS:
Dataset: {stats.get('rows', 0)} rows, {stats.get('columns', 0)} columns
Key Insights Identified: {stats.get('total_insights', 0)}

TOP INSIGHTS:
{insights_text}

YOUR MISSION: Write a concise, powerful executive summary (250-300 words) that:
1. Opens with the most critical finding
2. Explains why it matters
3. Provides 2-3 key supporting insights
4. Ends with clear, actionable recommendations
5. Uses confident, authoritative language
6. Focuses on business impact, not technical details

TONE: Professional, authoritative, action-oriented
AUDIENCE: Senior executives and decision-makers

Write the executive summary now:"""
    
    def generate_recommendation_report(
        self,
        insights: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a detailed recommendation report.
        
        Args:
            insights: List of insights from analysis
            
        Returns:
            Detailed recommendation report
        """
        if not self.initialized:
            return "Report generation not available"
        
        try:
            prompt = f"""You are a management consultant preparing strategic recommendations.

INSIGHTS FROM DATA ANALYSIS:
{json.dumps(insights, indent=2)}

YOUR MISSION: Create a detailed recommendation report with:
1. **Executive Summary** (2-3 paragraphs)
2. **Key Findings** (5-7 bullet points)
3. **Strategic Recommendations** (3-5 specific actions)
4. **Implementation Roadmap** (phased approach)
5. **Expected Outcomes** (quantified where possible)

FORMAT: Use markdown with clear headers and bullet points.
TONE: Authoritative, strategic, actionable.

Write the recommendation report now:"""
            
            response = self.model.generate_content(prompt)
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Report generation error: {e}")
            return "Error generating recommendation report"
    
    def generate_data_story(
        self,
        data_description: str,
        key_findings: List[str]
    ) -> str:
        """
        Generate a compelling data story.
        
        Args:
            data_description: Description of the dataset
            key_findings: List of key findings
            
        Returns:
            Narrative data story
        """
        if not self.initialized:
            return "Story generation not available"
        
        try:
            findings_text = "\n".join([f"- {finding}" for finding in key_findings])
            
            prompt = f"""You are a data storyteller for Visual Capitalist or The Economist.

DATASET: {data_description}

KEY FINDINGS:
{findings_text}

YOUR MISSION: Write a compelling data story (400-500 words) that:
1. Starts with a hook that captures attention
2. Weaves the data findings into a narrative
3. Explains the "so what" - why this matters
4. Uses analogies and context to make numbers relatable
5. Ends with implications and future outlook

STYLE: Like Visual Capitalist - clear, engaging, visual-friendly
TONE: Informative but engaging, not dry or academic

Write the data story now:"""
            
            response = self.model.generate_content(prompt)
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Story generation error: {e}")
            return "Error generating data story"


# Global instance
_generator = None


def get_insight_generator() -> InsightGenerator:
    """Get or create the global InsightGenerator instance."""
    global _generator
    
    if _generator is None:
        _generator = InsightGenerator()
    
    return _generator
