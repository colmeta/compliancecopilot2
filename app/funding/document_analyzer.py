"""
Funding Document Analyzer - Extract Information from Uploaded Documents
Uses OCR and AI to extract structured information from funding documents
"""

import os
import logging
import base64
import tempfile
from typing import Dict, List, Any, Optional
from datetime import datetime
import google.generativeai as genai
from app.ocr.ocr_engine import get_ocr_engine
from app.data_entry.agent_extractor import AgentExtractor

logger = logging.getLogger(__name__)


class FundingDocumentAnalyzer:
    """
    Analyzes uploaded funding documents and extracts structured information.
    
    Capabilities:
    - Extract text from PDF, Word, images using OCR
    - Use AI to extract structured data mapping to discovery_answers format
    - Provide confidence scores for each extracted field
    - Handle multiple document types (pitch decks, business plans, financials, etc.)
    """
    
    def __init__(self):
        """Initialize the document analyzer."""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        
        if not self.api_key:
            logger.error("GOOGLE_API_KEY not set! Document analysis will fail.")
            self.enabled = False
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            self.ocr_engine = get_ocr_engine()
            self.extractor = AgentExtractor()
            self.enabled = True
            logger.info("✅ Funding Document Analyzer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize analyzer: {e}")
            self.enabled = False
    
    def analyze_documents(self, uploaded_files: List[Dict]) -> Dict:
        """
        Extract information from uploaded funding documents.
        
        Args:
            uploaded_files: List of document dicts with:
                - filename: str
                - content_base64: str (base64 encoded)
                - content_type: str (e.g., 'application/pdf', 'image/jpeg')
        
        Returns:
            {
                'success': bool,
                'extracted_info': Dict[str, Any],  # Maps to discovery_answers format
                'confidence_scores': Dict[str, float],
                'document_types': List[str],  # Detected document types
                'processing_summary': Dict,
                'errors': List[str]
            }
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'Analyzer not configured',
                'message': 'GOOGLE_API_KEY not set'
            }
        
        if not uploaded_files:
            return {
                'success': False,
                'error': 'No documents provided'
            }
        
        logger.info(f"Analyzing {len(uploaded_files)} document(s)...")
        
        # Step 1: Extract text from all documents
        all_texts = []
        document_types = []
        processing_summary = {
            'documents_processed': 0,
            'documents_failed': 0,
            'total_pages': 0,
            'total_words': 0
        }
        errors = []
        
        for doc in uploaded_files:
            try:
                filename = doc.get('filename', 'unknown')
                content_type = doc.get('content_type', '')
                content_base64 = doc.get('content_base64', '')
                
                logger.info(f"Processing document: {filename} ({content_type})")
                
                # Decode base64
                try:
                    content_bytes = base64.b64decode(content_base64)
                except Exception as e:
                    errors.append(f"Failed to decode {filename}: {e}")
                    processing_summary['documents_failed'] += 1
                    continue
                
                # Extract text based on content type
                text_result = self._extract_text_from_document(
                    content_bytes, 
                    content_type, 
                    filename
                )
                
                if text_result['success']:
                    all_texts.append({
                        'filename': filename,
                        'text': text_result['text'],
                        'confidence': text_result.get('confidence', 0.8),
                        'word_count': text_result.get('word_count', 0)
                    })
                    
                    # Detect document type
                    doc_type = self._detect_document_type(filename, text_result['text'])
                    document_types.append(doc_type)
                    
                    processing_summary['documents_processed'] += 1
                    processing_summary['total_words'] += text_result.get('word_count', 0)
                else:
                    errors.append(f"Failed to extract text from {filename}: {text_result.get('error')}")
                    processing_summary['documents_failed'] += 1
                    
            except Exception as e:
                logger.error(f"Error processing document {doc.get('filename', 'unknown')}: {e}")
                errors.append(f"Error processing {doc.get('filename', 'unknown')}: {str(e)}")
                processing_summary['documents_failed'] += 1
        
        if not all_texts:
            return {
                'success': False,
                'error': 'Failed to extract text from any documents',
                'errors': errors,
                'processing_summary': processing_summary
            }
        
        # Step 2: Combine all text
        combined_text = "\n\n--- DOCUMENT SEPARATOR ---\n\n".join(
            [f"=== {doc['filename']} ===\n{doc['text']}" for doc in all_texts]
        )
        
        # Step 3: Extract structured information using AI
        extraction_result = self._extract_structured_info(combined_text)
        
        if not extraction_result['success']:
            return {
                'success': False,
                'error': extraction_result.get('error', 'Failed to extract structured information'),
                'errors': errors + [extraction_result.get('error', '')],
                'processing_summary': processing_summary
            }
        
        # Step 4: Return results
        return {
            'success': True,
            'extracted_info': extraction_result['data'],
            'confidence_scores': extraction_result.get('field_confidences', {}),
            'document_types': list(set(document_types)),
            'processing_summary': {
                **processing_summary,
                'extraction_confidence': extraction_result.get('confidence', 0.8)
            },
            'errors': errors if errors else None
        }
    
    def _extract_text_from_document(
        self, 
        content_bytes: bytes, 
        content_type: str, 
        filename: str
    ) -> Dict:
        """
        Extract text from a document based on its content type.
        
        Args:
            content_bytes: Document content as bytes
            content_type: MIME type (e.g., 'application/pdf', 'image/jpeg')
            filename: Original filename
        
        Returns:
            Dict with 'success', 'text', 'confidence', 'word_count'
        """
        try:
            # Handle images (use OCR)
            if content_type.startswith('image/'):
                logger.info(f"Using OCR for image: {filename}")
                ocr_result = self.ocr_engine.extract_text(content_bytes)
                
                if ocr_result['success']:
                    return {
                        'success': True,
                        'text': ocr_result['text'],
                        'confidence': ocr_result.get('confidence', 0.8) / 100.0,  # Convert to 0-1 scale
                        'word_count': ocr_result.get('word_count', 0),
                        'engine': ocr_result.get('engine', 'unknown')
                    }
                else:
                    return {
                        'success': False,
                        'error': ocr_result.get('error', 'OCR failed')
                    }
            
            # Handle PDF
            elif content_type == 'application/pdf':
                logger.info(f"Extracting text from PDF: {filename}")
                # For PDF, we'll use a simple approach - save to temp file and use OCR
                # In production, you might want to use PyPDF2 or pdfplumber for text-based PDFs
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                    tmp_file.write(content_bytes)
                    tmp_path = tmp_file.name
                
                try:
                    # Try OCR on PDF (convert pages to images)
                    ocr_results = self.ocr_engine.extract_from_pdf(tmp_path, max_pages=20)
                    
                    if ocr_results and ocr_results[0].get('success'):
                        # Combine all pages
                        all_text = "\n\n".join([r.get('text', '') for r in ocr_results if r.get('success')])
                        avg_confidence = sum([r.get('confidence', 0) for r in ocr_results if r.get('success')]) / len([r for r in ocr_results if r.get('success')]) if ocr_results else 0
                        
                        os.unlink(tmp_path)  # Clean up
                        
                        return {
                            'success': True,
                            'text': all_text,
                            'confidence': (avg_confidence / 100.0) if avg_confidence else 0.8,
                            'word_count': len(all_text.split()),
                            'engine': 'ocr',
                            'pages': len(ocr_results)
                        }
                    else:
                        os.unlink(tmp_path)
                        return {
                            'success': False,
                            'error': 'Failed to extract text from PDF'
                        }
                except Exception as e:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                    return {
                        'success': False,
                        'error': f'PDF processing error: {str(e)}'
                    }
            
            # Handle Word documents (.docx)
            elif content_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
                                  'application/msword']:
                logger.info(f"Extracting text from Word document: {filename}")
                try:
                    from docx import Document
                    from io import BytesIO
                    
                    doc = Document(BytesIO(content_bytes))
                    text = "\n".join([para.text for para in doc.paragraphs])
                    
                    return {
                        'success': True,
                        'text': text,
                        'confidence': 0.95,  # Word docs are usually high confidence
                        'word_count': len(text.split()),
                        'engine': 'docx_parser'
                    }
                except ImportError:
                    return {
                        'success': False,
                        'error': 'python-docx not installed'
                    }
                except Exception as e:
                    return {
                        'success': False,
                        'error': f'Word document parsing error: {str(e)}'
                    }
            
            # Handle plain text
            elif content_type.startswith('text/'):
                text = content_bytes.decode('utf-8', errors='ignore')
                return {
                    'success': True,
                    'text': text,
                    'confidence': 1.0,
                    'word_count': len(text.split()),
                    'engine': 'text_parser'
                }
            
            else:
                return {
                    'success': False,
                    'error': f'Unsupported content type: {content_type}'
                }
                
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _detect_document_type(self, filename: str, text: str) -> str:
        """
        Detect the type of funding document based on filename and content.
        
        Args:
            filename: Document filename
            text: Extracted text
        
        Returns:
            Document type string (e.g., 'pitch_deck', 'business_plan', 'financials')
        """
        filename_lower = filename.lower()
        text_lower = text.lower()[:500]  # Check first 500 chars
        
        # Check filename patterns
        if 'pitch' in filename_lower or 'deck' in filename_lower:
            return 'pitch_deck'
        if 'business' in filename_lower and 'plan' in filename_lower:
            return 'business_plan'
        if 'financial' in filename_lower or 'projection' in filename_lower:
            return 'financials'
        if 'executive' in filename_lower and 'summary' in filename_lower:
            return 'executive_summary'
        if 'vision' in filename_lower or 'mission' in filename_lower:
            return 'vision'
        if 'market' in filename_lower or 'research' in filename_lower:
            return 'market_research'
        
        # Check content patterns
        if 'slide' in text_lower or 'presentation' in text_lower:
            return 'pitch_deck'
        if 'revenue' in text_lower and 'projection' in text_lower:
            return 'financials'
        if 'problem' in text_lower and 'solution' in text_lower:
            return 'business_plan'
        
        return 'unknown'
    
    def _extract_structured_info(self, combined_text: str) -> Dict:
        """
        Use AI to extract structured information from combined document text.
        Maps to discovery_answers format.
        
        Args:
            combined_text: All extracted text from documents
        
        Returns:
            Dict with 'success', 'data', 'confidence', 'field_confidences'
        """
        try:
            # Define schema for funding document information
            funding_schema = {
                'company_name': {
                    'type': 'string',
                    'description': 'Company or project name',
                    'required': True
                },
                'project_name': {
                    'type': 'string',
                    'description': 'Project or venture name (alternative to company_name)',
                    'required': False
                },
                'vision': {
                    'type': 'string',
                    'description': 'Company vision statement or long-term goal',
                    'required': False
                },
                'mission': {
                    'type': 'string',
                    'description': 'Company mission statement',
                    'required': False
                },
                'problem': {
                    'type': 'string',
                    'description': 'The problem the company is solving',
                    'required': False
                },
                'solution': {
                    'type': 'string',
                    'description': 'The solution or product offering',
                    'required': False
                },
                'target_market': {
                    'type': 'string',
                    'description': 'Target market or customer segment',
                    'required': False
                },
                'market_size': {
                    'type': 'string',
                    'description': 'Total addressable market (TAM) or market size',
                    'required': False
                },
                'business_model': {
                    'type': 'string',
                    'description': 'How the company makes money',
                    'required': False
                },
                'competitive_advantage': {
                    'type': 'string',
                    'description': 'Competitive advantages or differentiators',
                    'required': False
                },
                'traction': {
                    'type': 'string',
                    'description': 'Current traction, metrics, or milestones',
                    'required': False
                },
                'team': {
                    'type': 'string',
                    'description': 'Team members and their backgrounds',
                    'required': False
                },
                'funding_amount': {
                    'type': 'string',
                    'description': 'Funding amount being sought',
                    'required': False
                },
                'use_of_funds': {
                    'type': 'string',
                    'description': 'How funding will be used',
                    'required': False
                },
                'revenue': {
                    'type': 'string',
                    'description': 'Current or projected revenue',
                    'required': False
                },
                'industry': {
                    'type': 'string',
                    'description': 'Industry or sector',
                    'required': False
                },
                'stage': {
                    'type': 'string',
                    'description': 'Company stage (idea, prototype, beta, revenue, etc.)',
                    'required': False
                }
            }
            
            # Use Agent Extractor to extract structured data
            extraction_result = self.extractor.extract_data(combined_text, funding_schema)
            
            if not extraction_result['success']:
                # Fallback: Use direct AI prompt if extractor fails
                return self._extract_with_direct_ai(combined_text, funding_schema)
            
            # Map extracted data to discovery_answers format
            extracted_data = extraction_result['data']
            
            # Ensure company_name or project_name exists
            if not extracted_data.get('company_name') and extracted_data.get('project_name'):
                extracted_data['company_name'] = extracted_data['project_name']
            
            return {
                'success': True,
                'data': extracted_data,
                'confidence': extraction_result.get('confidence', 0.8),
                'field_confidences': extraction_result.get('field_confidences', {})
            }
            
        except Exception as e:
            logger.error(f"Error extracting structured info: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_with_direct_ai(self, text: str, schema: Dict) -> Dict:
        """
        Fallback: Extract information using direct AI prompt.
        
        Args:
            text: Document text
            schema: Target schema
        
        Returns:
            Dict with extracted data
        """
        try:
            schema_fields = list(schema.keys())
            
            prompt = f"""You are an expert at analyzing funding documents (pitch decks, business plans, financials).

Extract the following information from the provided document text. Return ONLY a valid JSON object with the extracted data.

Fields to extract:
{', '.join(schema_fields)}

If a field is not found in the document, set it to null.

DOCUMENT TEXT:
{text[:8000]}  # Limit to avoid token limits

Return a JSON object with this structure:
{{
    "extracted_data": {{
        "company_name": "... or null",
        "project_name": "... or null",
        "vision": "... or null",
        ...
    }},
    "field_confidences": {{
        "company_name": 0.95,
        ...
    }},
    "overall_confidence": 0.90
}}"""

            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.3,  # Lower temperature for extraction
                    'max_output_tokens': 4096
                }
            )
            
            import json
            import re
            
            # Extract JSON from response
            response_text = response.text.strip()
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                parsed = json.loads(json_match.group())
                extracted_data = parsed.get('extracted_data', {})
                field_confidences = parsed.get('field_confidences', {})
                overall_confidence = parsed.get('overall_confidence', 0.8)
                
                return {
                    'success': True,
                    'data': extracted_data,
                    'confidence': overall_confidence,
                    'field_confidences': field_confidences
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to parse AI response as JSON'
                }
                
        except Exception as e:
            logger.error(f"Direct AI extraction failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
_document_analyzer = None

def get_document_analyzer():
    """Get singleton document analyzer instance"""
    global _document_analyzer
    if _document_analyzer is None:
        _document_analyzer = FundingDocumentAnalyzer()
    return _document_analyzer

