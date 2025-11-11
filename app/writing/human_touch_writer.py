# ==============================================================================
# app/writing/human_touch_writer.py
# The Human Touch Writer - Fortune 500-Grade Writing Intelligence
# ==============================================================================
"""
Human Touch Writer: Makes AI Writing Indistinguishable from Human Writing

This module analyzes your organization's existing writing samples, learns
your unique voice and tone, and ensures all AI-generated content maintains
that authentic human character.

The system:
1. Analyzes sample documents to extract voice/tone characteristics
2. Identifies industry-specific language patterns
3. Matches formality levels
4. Adds appropriate personality and variation
5. Ensures emotional intelligence in messaging
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import os
import re
import google.generativeai as genai

logger = logging.getLogger(__name__)


@dataclass
class VoiceProfile:
    """
    Voice and tone profile for an organization.
    
    Attributes:
        organization_name: Name of the organization
        formality_level: Formality level (1-10, 1=casual, 10=formal)
        personality_traits: List of personality traits
        industry: Industry/domain
        key_phrases: Common phrases used
        tone_descriptors: Words describing the tone
        writing_samples: Sample documents used for training
        created_at: Profile creation date
    """
    organization_name: str
    formality_level: int
    personality_traits: List[str]
    industry: str
    key_phrases: List[str]
    tone_descriptors: List[str]
    writing_samples: List[str]
    created_at: datetime


@dataclass
class WritingStyle:
    """
    Writing style parameters for content generation.
    
    Attributes:
        voice_profile: VoiceProfile to match
        content_type: Type of content ('proposal', 'email', 'report', etc.)
        target_audience: Who will read this
        purpose: Purpose of the writing
        length_preference: Preferred length ('brief', 'standard', 'detailed')
        include_personality: Whether to add personality/humanity
    """
    voice_profile: VoiceProfile
    content_type: str
    target_audience: str
    purpose: str
    length_preference: str = 'standard'
    include_personality: bool = True


class HumanTouchWriter:
    """
    Human Touch Writer: Transforms AI writing into authentic human voice.
    
    This system ensures that every piece of content feels genuinely human,
    matches your organization's voice, and resonates with your audience.
    """
    
    def __init__(self):
        """Initialize the Human Touch Writer."""
        try:
            genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            self.initialized = True
            logger.info("HumanTouchWriter initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize HumanTouchWriter: {e}")
            self.initialized = False
    
    def analyze_voice(
        self,
        sample_documents: List[str],
        organization_name: str,
        industry: str
    ) -> VoiceProfile:
        """
        Analyze writing samples to create a voice profile.
        
        Args:
            sample_documents: List of sample documents
            organization_name: Organization name
            industry: Industry/domain
            
        Returns:
            VoiceProfile object
        """
        if not self.initialized or not sample_documents:
            return self._create_default_profile(organization_name, industry)
        
        try:
            # Combine samples (limited to prevent token overflow)
            combined_samples = "\n\n---\n\n".join(
                [sample[:5000] for sample in sample_documents[:5]]
            )
            
            # Build analysis prompt
            prompt = self._build_voice_analysis_prompt(combined_samples, organization_name, industry)
            
            # Call LLM
            response = self.model.generate_content(prompt)
            
            # Parse response
            profile = self._parse_voice_profile(
                response.text,
                organization_name,
                industry,
                sample_documents
            )
            
            logger.info(f"Created voice profile for {organization_name}")
            
            return profile
            
        except Exception as e:
            logger.error(f"Voice analysis error: {e}", exc_info=True)
            return self._create_default_profile(organization_name, industry)
    
    def _build_voice_analysis_prompt(
        self,
        combined_samples: str,
        organization_name: str,
        industry: str
    ) -> str:
        """Build prompt for voice analysis."""
        return f"""You are an expert writing analyst and linguist. Analyze the following writing samples from {organization_name} ({industry} industry) to create a comprehensive voice and tone profile.

WRITING SAMPLES:
{combined_samples}

YOUR MISSION: Create a detailed analysis of this organization's writing voice.

Analyze and extract:
1. FORMALITY LEVEL (1-10):
   - 1-3: Casual, conversational, friendly
   - 4-6: Professional but approachable
   - 7-10: Formal, traditional, corporate

2. PERSONALITY TRAITS (pick 3-5):
   - Examples: confident, humble, innovative, traditional, bold, cautious, warm, direct, etc.

3. TONE DESCRIPTORS (pick 3-5 words):
   - Examples: professional, enthusiastic, authoritative, empathetic, technical, etc.

4. KEY PHRASES (5-10 phrases they commonly use):
   - Extract actual recurring phrases or terminology

5. WRITING CHARACTERISTICS:
   - Sentence structure (simple/complex/varied)
   - Use of jargon/technical terms
   - First person (we/our) vs third person usage
   - Active vs passive voice preference
   - Emotional expressiveness

Return your analysis as valid JSON:
{{
    "formality_level": 7,
    "personality_traits": ["confident", "innovative", "client-focused"],
    "tone_descriptors": ["professional", "solution-oriented", "clear"],
    "key_phrases": ["phrase 1", "phrase 2", ...],
    "writing_characteristics": {{
        "sentence_structure": "varied",
        "technical_language": "moderate",
        "point_of_view": "first_person_plural",
        "voice_preference": "active",
        "emotional_expressiveness": "medium"
    }}
}}

CRITICAL: Return ONLY valid JSON, no markdown or explanations.

BEGIN ANALYSIS:"""
    
    def _parse_voice_profile(
        self,
        response_text: str,
        organization_name: str,
        industry: str,
        samples: List[str]
    ) -> VoiceProfile:
        """Parse voice analysis response into VoiceProfile."""
        try:
            # Clean and parse JSON
            cleaned = response_text.strip().replace('```json', '').replace('```', '').strip()
            parsed = json.loads(cleaned)
            
            # Create VoiceProfile
            profile = VoiceProfile(
                organization_name=organization_name,
                formality_level=parsed.get('formality_level', 6),
                personality_traits=parsed.get('personality_traits', []),
                industry=industry,
                key_phrases=parsed.get('key_phrases', []),
                tone_descriptors=parsed.get('tone_descriptors', []),
                writing_samples=samples,
                created_at=datetime.utcnow()
            )
            
            return profile
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse voice profile: {e}")
            return self._create_default_profile(organization_name, industry)
        except Exception as e:
            logger.error(f"Voice profile parsing error: {e}")
            return self._create_default_profile(organization_name, industry)
    
    def _create_default_profile(
        self,
        organization_name: str,
        industry: str
    ) -> VoiceProfile:
        """Create a default voice profile."""
        return VoiceProfile(
            organization_name=organization_name,
            formality_level=6,
            personality_traits=['professional', 'reliable', 'client-focused'],
            industry=industry,
            key_phrases=['our team', 'committed to', 'solution', 'partnership'],
            tone_descriptors=['professional', 'clear', 'confident'],
            writing_samples=[],
            created_at=datetime.utcnow()
        )
    
    def humanize_content(
        self,
        content: str,
        writing_style: WritingStyle
    ) -> str:
        """
        Humanize AI-generated content to match voice profile.
        
        Args:
            content: AI-generated content to humanize
            writing_style: WritingStyle parameters
            
        Returns:
            Humanized content string
        """
        if not self.initialized:
            return content
        
        try:
            # Build humanization prompt
            prompt = self._build_humanization_prompt(content, writing_style)
            
            # Call LLM
            response = self.model.generate_content(prompt)
            
            # Extract humanized content
            humanized = self._extract_humanized_content(response.text)
            
            logger.info(f"Humanized content for {writing_style.voice_profile.organization_name}")
            
            return humanized
            
        except Exception as e:
            logger.error(f"Humanization error: {e}", exc_info=True)
            return content
    
    def _build_humanization_prompt(
        self,
        content: str,
        style: WritingStyle
    ) -> str:
        """Build prompt for humanizing content."""
        profile = style.voice_profile
        
        # Build voice instructions
        voice_instructions = self._format_voice_instructions(profile)
        
        prompt = f"""You are a professional writer and editor for {profile.organization_name}. Your mission is to rewrite the following content to match the organization's authentic voice and tone while maintaining ALL factual information.

ORGANIZATION VOICE PROFILE:
{voice_instructions}

CONTENT TYPE: {style.content_type}
TARGET AUDIENCE: {style.target_audience}
PURPOSE: {style.purpose}

ORIGINAL CONTENT TO REWRITE:
{content}

YOUR MISSION: Rewrite this content to sound authentically human and match the organization's voice.

CRITICAL REQUIREMENTS:
1. MAINTAIN ALL FACTS: Do not change any factual information, data, or key points
2. MATCH VOICE: Use the formality level, personality, and tone described above
3. ADD HUMANITY: Include natural variations, transitions, and human touches
4. USE KEY PHRASES: Incorporate the organization's typical phrases naturally
5. AVOID AI TELLS: No robotic lists, repetitive structures, or generic corporate speak
6. KEEP LENGTH: Similar length to original (adjust based on: {style.length_preference})

HUMANIZATION TECHNIQUES TO APPLY:
- Vary sentence structure and length
- Use natural transitions between ideas
- Add appropriate emphasis or emotion
- Include relatable examples or analogies if helpful
- Use active voice when appropriate
- Break up dense information
- Add personality through word choice

Return ONLY the rewritten content. No explanations, no commentary, no markdown formatting.

BEGIN REWRITING:"""
        
        return prompt
    
    def _format_voice_instructions(self, profile: VoiceProfile) -> str:
        """Format voice profile into instructions."""
        formality_desc = "Very formal" if profile.formality_level >= 8 else "Professional" if profile.formality_level >= 5 else "Casual and friendly"
        
        instructions = f"""
Organization: {profile.organization_name}
Industry: {profile.industry}
Formality Level: {profile.formality_level}/10 ({formality_desc})
Personality: {', '.join(profile.personality_traits)}
Tone: {', '.join(profile.tone_descriptors)}
Key Phrases to Use: {', '.join(profile.key_phrases[:5])}
"""
        return instructions
    
    def _extract_humanized_content(self, response_text: str) -> str:
        """Extract humanized content from response."""
        # Remove any markdown formatting
        cleaned = response_text.strip()
        cleaned = re.sub(r'```.*?```', '', cleaned, flags=re.DOTALL)
        cleaned = cleaned.replace('```', '')
        
        return cleaned.strip()
    
    def generate_content(
        self,
        prompt: str,
        writing_style: WritingStyle,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate content from scratch with human touch.
        
        Args:
            prompt: What to write about
            writing_style: WritingStyle parameters
            context: Optional additional context
            
        Returns:
            Generated content string
        """
        if not self.initialized:
            return "Error: Human Touch Writer not initialized"
        
        try:
            # Build generation prompt
            generation_prompt = self._build_generation_prompt(prompt, writing_style, context)
            
            # Call LLM
            response = self.model.generate_content(generation_prompt)
            
            # Extract content
            content = self._extract_humanized_content(response.text)
            
            logger.info(f"Generated content for {writing_style.content_type}")
            
            return content
            
        except Exception as e:
            logger.error(f"Content generation error: {e}", exc_info=True)
            return f"Error generating content: {str(e)}"
    
    def _build_generation_prompt(
        self,
        prompt: str,
        style: WritingStyle,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for content generation."""
        profile = style.voice_profile
        voice_instructions = self._format_voice_instructions(profile)
        
        context_str = ""
        if context:
            context_str = f"\nADDITIONAL CONTEXT:\n{json.dumps(context, indent=2)}"
        
        return f"""You are a professional writer for {profile.organization_name}. Write compelling, authentic content that matches the organization's voice perfectly.

ORGANIZATION VOICE PROFILE:
{voice_instructions}

CONTENT TYPE: {style.content_type}
TARGET AUDIENCE: {style.target_audience}
PURPOSE: {style.purpose}
LENGTH: {style.length_preference}

WRITING TASK:
{prompt}{context_str}

YOUR MISSION: Create original content that:
1. Matches the organization's voice and tone perfectly
2. Sounds genuinely human, not AI-generated
3. Engages the target audience effectively
4. Serves the stated purpose clearly
5. Uses natural language and varied structure
6. Incorporates appropriate personality

HUMANIZATION REQUIREMENTS:
- Write as a real person would write
- Vary sentence structure naturally
- Use transitions that flow
- Add appropriate emphasis
- Include relevant examples
- Avoid robotic patterns
- Show personality through word choice

Return ONLY the content. No explanations or meta-commentary.

BEGIN WRITING:"""
    
    def compare_voices(
        self,
        profile1: VoiceProfile,
        profile2: VoiceProfile
    ) -> Dict[str, Any]:
        """
        Compare two voice profiles.
        
        Args:
            profile1: First VoiceProfile
            profile2: Second VoiceProfile
            
        Returns:
            Dict with comparison analysis
        """
        formality_diff = abs(profile1.formality_level - profile2.formality_level)
        
        shared_traits = set(profile1.personality_traits) & set(profile2.personality_traits)
        shared_tones = set(profile1.tone_descriptors) & set(profile2.tone_descriptors)
        
        similarity_score = (
            (10 - formality_diff) / 10 * 0.3 +
            len(shared_traits) / max(len(profile1.personality_traits), len(profile2.personality_traits)) * 0.35 +
            len(shared_tones) / max(len(profile1.tone_descriptors), len(profile2.tone_descriptors)) * 0.35
        )
        
        return {
            'similarity_score': round(similarity_score, 2),
            'formality_difference': formality_diff,
            'shared_traits': list(shared_traits),
            'shared_tones': list(shared_tones),
            'profile1_name': profile1.organization_name,
            'profile2_name': profile2.organization_name
        }


# Global instance
_writer = None


def get_human_touch_writer() -> HumanTouchWriter:
    """
    Get or create the global HumanTouchWriter instance.
    
    Returns:
        HumanTouchWriter instance
    """
    global _writer
    
    if _writer is None:
        _writer = HumanTouchWriter()
    
    return _writer
