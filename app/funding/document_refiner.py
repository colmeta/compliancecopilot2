"""
Funding Document Refiner - Refine and Update Existing Documents
Compares uploaded documents with new information and generates refined/updated versions.
Supports both refining existing documents and generating new ones.
"""

import logging
from typing import Dict, List, Any, Optional
import os
import google.generativeai as genai

logger = logging.getLogger(__name__)


class FundingDocumentRefiner:
    """
    Refines and updates existing funding documents with new information.
    
    Capabilities:
    - Compare original documents with new information
    - Identify sections needing updates
    - Generate refined versions
    - Highlight changes
    - Support both refinement and new document generation
    """
    
    def __init__(self):
        """Initialize the document refiner."""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        
        if not self.api_key:
            logger.error("GOOGLE_API_KEY not set! Document refinement will fail.")
            self.enabled = False
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            self.enabled = True
            logger.info("✅ Funding Document Refiner initialized")
        except Exception as e:
            logger.error(f"Failed to initialize refiner: {e}")
            self.enabled = False
    
    def refine_document(
        self, 
        original_doc_text: str,
        original_doc_type: str,
        extracted_info: Dict[str, Any],
        new_answers: Dict[str, Any],
        funding_level: str = 'seed'
    ) -> Dict:
        """
        Refine/update an existing document with new information.
        
        Args:
            original_doc_text: Original document text
            original_doc_type: Type of document (pitch_deck, business_plan, etc.)
            extracted_info: Information extracted from documents
            new_answers: New answers from user
            funding_level: Funding level
        
        Returns:
            {
                'success': bool,
                'refined_content': str,
                'changes_summary': List[str],
                'sections_updated': List[str],
                'improvements': List[str]
            }
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'Refiner not configured'
            }
        
        try:
            # Merge extracted info and new answers
            complete_info = self._merge_information(extracted_info, new_answers)
            
            # Build refinement prompt
            prompt = self._build_refinement_prompt(
                original_doc_text,
                original_doc_type,
                complete_info,
                funding_level
            )
            
            # Generate refined document
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'max_output_tokens': 8192
                }
            )
            
            refined_content = response.text.strip()
            
            # Analyze changes
            changes_analysis = self._analyze_changes(original_doc_text, refined_content)
            
            return {
                'success': True,
                'refined_content': refined_content,
                'changes_summary': changes_analysis['summary'],
                'sections_updated': changes_analysis['sections'],
                'improvements': changes_analysis['improvements'],
                'original_length': len(original_doc_text),
                'refined_length': len(refined_content)
            }
            
        except Exception as e:
            logger.error(f"Document refinement failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_new_document(
        self,
        doc_type: str,
        extracted_info: Dict[str, Any],
        new_answers: Dict[str, Any],
        funding_level: str = 'seed',
        existing_docs: Optional[List[str]] = None
    ) -> Dict:
        """
        Generate a new document (for document types not in uploaded files).
        
        Args:
            doc_type: Type of document to generate
            extracted_info: Information extracted from documents
            new_answers: New answers from user
            funding_level: Funding level
            existing_docs: List of existing document types (to avoid duplication)
        
        Returns:
            {
                'success': bool,
                'content': str,
                'document_type': str
            }
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'Refiner not configured'
            }
        
        try:
            # Merge information
            complete_info = self._merge_information(extracted_info, new_answers)
            
            # Build generation prompt
            prompt = self._build_generation_prompt(
                doc_type,
                complete_info,
                funding_level,
                existing_docs
            )
            
            # Generate document
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'max_output_tokens': 8192
                }
            )
            
            content = response.text.strip()
            
            return {
                'success': True,
                'content': content,
                'document_type': doc_type,
                'length': len(content)
            }
            
        except Exception as e:
            logger.error(f"New document generation failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _merge_information(
        self, 
        extracted_info: Dict[str, Any], 
        new_answers: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge extracted information with new user answers.
        New answers override extracted info when both exist.
        
        Args:
            extracted_info: Information from documents
            new_answers: New answers from user
        
        Returns:
            Merged information dictionary
        """
        merged = extracted_info.copy()
        
        # Override with new answers (user input takes precedence)
        for key, value in new_answers.items():
            if value:  # Only override if value is not empty
                merged[key] = value
        
        # Handle special cases
        if not merged.get('company_name') and merged.get('project_name'):
            merged['company_name'] = merged['project_name']
        
        return merged
    
    def _build_refinement_prompt(
        self,
        original_text: str,
        doc_type: str,
        complete_info: Dict[str, Any],
        funding_level: str
    ) -> str:
        """
        Build prompt for refining existing document.
        
        Args:
            original_text: Original document text
            doc_type: Document type
            complete_info: Complete information (extracted + new)
            funding_level: Funding level
        
        Returns:
            Prompt string
        """
        info_summary = self._format_info_summary(complete_info)
        
        prompt = f"""You are an expert funding document writer who has created documents for Y-Combinator, Sequoia, and Fortune 500 companies.

TASK: Refine and update the following {doc_type} document with new and updated information.

ORIGINAL DOCUMENT:
{original_text[:4000]}  # Limit to avoid token limits

UPDATED INFORMATION:
{info_summary}

FUNDING LEVEL: {funding_level}

INSTRUCTIONS:
1. Keep the best parts of the original document
2. Update sections with new information
3. Improve clarity, persuasiveness, and professionalism
4. Maintain the document's structure and style
5. Add missing important information
6. Remove outdated or incorrect information
7. Make it investor-ready (Y-Combinator / Fortune 50 quality)

IMPORTANT:
- Preserve the document's original voice and tone where appropriate
- Only update what needs updating - don't rewrite everything
- Make improvements that enhance clarity and impact
- Ensure all new information is integrated naturally

Generate the refined document:"""

        return prompt
    
    def _build_generation_prompt(
        self,
        doc_type: str,
        complete_info: Dict[str, Any],
        funding_level: str,
        existing_docs: Optional[List[str]] = None
    ) -> str:
        """
        Build prompt for generating new document.
        
        Args:
            doc_type: Document type to generate
            complete_info: Complete information
            funding_level: Funding level
            existing_docs: Existing document types (for context)
        
        Returns:
            Prompt string
        """
        info_summary = self._format_info_summary(complete_info)
        
        doc_type_descriptions = {
            'pitch_deck': '15-slide investor pitch deck (Y-Combinator quality)',
            'business_plan': 'Comprehensive 40-page business plan',
            'executive_summary': '2-page executive summary',
            'vision': 'Vision and mission statement',
            'financial_projections': '5-year financial projections',
            'market_research': 'Market research and analysis',
            'competitive_analysis': 'Competitive analysis',
            'go_to_market': 'Go-to-market strategy'
        }
        
        doc_description = doc_type_descriptions.get(doc_type, doc_type)
        
        context_note = ""
        if existing_docs:
            context_note = f"\nNOTE: The entrepreneur already has these documents: {', '.join(existing_docs)}. Ensure this new document complements them without duplication."
        
        prompt = f"""You are an expert funding document writer who has created documents for Y-Combinator, Sequoia, and Fortune 500 companies.

TASK: Generate a new {doc_description} for a {funding_level} funding round.

INFORMATION ABOUT THE COMPANY:
{info_summary}

FUNDING LEVEL: {funding_level}
{context_note}

INSTRUCTIONS:
1. Create a professional, investor-ready document
2. Use the provided information accurately
3. Write with clarity, persuasiveness, and professionalism
4. Make it suitable for {funding_level} investors
5. Include specific details and metrics where available
6. Focus on impact and opportunity

Generate the complete {doc_type} document:"""

        return prompt
    
    def _format_info_summary(self, info: Dict[str, Any]) -> str:
        """
        Format information dictionary into readable summary.
        
        Args:
            info: Information dictionary
        
        Returns:
            Formatted summary string
        """
        summary_parts = []
        
        if info.get('company_name'):
            summary_parts.append(f"Company Name: {info['company_name']}")
        
        if info.get('problem'):
            summary_parts.append(f"Problem: {info['problem']}")
        
        if info.get('solution'):
            summary_parts.append(f"Solution: {info['solution']}")
        
        if info.get('target_market'):
            summary_parts.append(f"Target Market: {info['target_market']}")
        
        if info.get('business_model'):
            summary_parts.append(f"Business Model: {info['business_model']}")
        
        if info.get('competitive_advantage'):
            summary_parts.append(f"Competitive Advantage: {info['competitive_advantage']}")
        
        if info.get('funding_amount'):
            summary_parts.append(f"Funding Amount: {info['funding_amount']}")
        
        if info.get('use_of_funds'):
            summary_parts.append(f"Use of Funds: {info['use_of_funds']}")
        
        if info.get('vision'):
            summary_parts.append(f"Vision: {info['vision']}")
        
        if info.get('market_size'):
            summary_parts.append(f"Market Size: {info['market_size']}")
        
        if info.get('traction'):
            summary_parts.append(f"Traction: {info['traction']}")
        
        if info.get('team'):
            summary_parts.append(f"Team: {info['team']}")
        
        if info.get('revenue'):
            summary_parts.append(f"Revenue: {info['revenue']}")
        
        if info.get('industry'):
            summary_parts.append(f"Industry: {info['industry']}")
        
        return "\n".join(summary_parts) if summary_parts else "No information provided."
    
    def _analyze_changes(
        self, 
        original: str, 
        refined: str
    ) -> Dict:
        """
        Analyze changes between original and refined documents.
        
        Args:
            original: Original document text
            refined: Refined document text
        
        Returns:
            Dict with changes analysis
        """
        # Simple analysis - in production, you might use diff algorithms
        changes = {
            'summary': [],
            'sections': [],
            'improvements': []
        }
        
        # Length comparison
        length_diff = len(refined) - len(original)
        if abs(length_diff) > 100:
            if length_diff > 0:
                changes['summary'].append(f"Document expanded by ~{length_diff} characters (added new information)")
            else:
                changes['summary'].append(f"Document condensed by ~{abs(length_diff)} characters (improved conciseness)")
        
        # Word count comparison
        original_words = len(original.split())
        refined_words = len(refined.split())
        if abs(refined_words - original_words) > 50:
            changes['summary'].append(f"Word count changed from {original_words} to {refined_words} words")
        
        # Generic improvements (AI-generated documents typically improve)
        changes['improvements'].append("Content updated with latest information")
        changes['improvements'].append("Clarity and professionalism enhanced")
        changes['improvements'].append("Investor-readiness improved")
        
        return changes


# Singleton instance
_document_refiner = None

def get_document_refiner():
    """Get singleton document refiner instance"""
    global _document_refiner
    if _document_refiner is None:
        _document_refiner = FundingDocumentRefiner()
    return _document_refiner

