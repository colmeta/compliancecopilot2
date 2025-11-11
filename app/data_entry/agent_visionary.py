# ==============================================================================
# app/data_entry/agent_visionary.py
# Agent Visionary - The Eye (OCR & Vision Processing)
# ==============================================================================
"""
Agent Visionary: The first agent in the Data Keystone pipeline.

Mission: Convert physical or scanned documents into machine-readable text
with maximum fidelity and accuracy.

Capabilities:
- Multi-service OCR orchestration (Tesseract, Google Vision, AWS Textract)
- Image preprocessing (deskewing, noise reduction, contrast enhancement)
- Intelligent service selection based on document type and user tier
- Confidence scoring for OCR quality
"""

import logging
from typing import Dict, Any, Optional
import io
import base64
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

logger = logging.getLogger(__name__)


class AgentVisionary:
    """
    Agent Visionary - OCR and vision processing specialist.
    
    This agent handles all text extraction from images, scanned PDFs,
    and other visual documents.
    """
    
    def __init__(self):
        """Initialize Agent Visionary with OCR services."""
        self.tesseract_available = self._check_tesseract()
        self.google_vision_available = self._check_google_vision()
        self.aws_textract_available = self._check_aws_textract()
        
        logger.info(
            f"Agent Visionary initialized - "
            f"Tesseract: {self.tesseract_available}, "
            f"Google Vision: {self.google_vision_available}, "
            f"AWS Textract: {self.aws_textract_available}"
        )
    
    def _check_tesseract(self) -> bool:
        """Check if Tesseract OCR is available."""
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            return True
        except Exception as e:
            logger.warning(f"Tesseract not available: {e}")
            return False
    
    def _check_google_vision(self) -> bool:
        """Check if Google Vision API is available."""
        try:
            from google.cloud import vision
            from config import Config
            return Config.GOOGLE_VISION_API_KEY is not None
        except Exception as e:
            logger.warning(f"Google Vision not available: {e}")
            return False
    
    def _check_aws_textract(self) -> bool:
        """Check if AWS Textract is available."""
        try:
            import boto3
            from config import Config
            return (Config.AWS_ACCESS_KEY_ID is not None and 
                   Config.AWS_SECRET_ACCESS_KEY is not None)
        except Exception as e:
            logger.warning(f"AWS Textract not available: {e}")
            return False
    
    def extract_text(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract text from a document using the best available OCR service.
        
        Args:
            document: Document dict with 'content_base64', 'filename', 'content_type'
            
        Returns:
            Dict with 'success', 'text', 'confidence', 'service_used'
        """
        try:
            content_type = document.get('content_type', '')
            filename = document.get('filename', 'unknown')
            
            # Check if document is an image or image-based PDF
            is_image = content_type.startswith('image/') or self._is_scanned_pdf(document)
            
            if not is_image:
                # Not an image, use regular text extraction
                return {
                    'success': True,
                    'text': self._extract_text_from_document(document),
                    'confidence': 1.0,
                    'service_used': 'direct_extraction'
                }
            
            # Decode and preprocess image
            image = self._decode_image(document['content_base64'])
            if image is None:
                return {
                    'success': False,
                    'error': 'Failed to decode image',
                    'text': '',
                    'confidence': 0.0
                }
            
            # Preprocess for better OCR
            preprocessed_image = self._preprocess_image(image)
            
            # Select and use OCR service
            ocr_result = self._perform_ocr(preprocessed_image, document)
            
            return ocr_result
            
        except Exception as e:
            logger.error(f"Agent Visionary error: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0.0
            }
    
    def _is_scanned_pdf(self, document: Dict[str, Any]) -> bool:
        """
        Determine if a PDF is scanned (image-based).
        
        Args:
            document: Document dict
            
        Returns:
            True if PDF appears to be scanned
        """
        # For now, assume PDFs need OCR if they're in the data entry pipeline
        # This can be enhanced with actual image detection
        return document.get('filename', '').lower().endswith('.pdf')
    
    def _decode_image(self, content_base64: str) -> Optional[Image.Image]:
        """
        Decode base64 image content.
        
        Args:
            content_base64: Base64 encoded image
            
        Returns:
            PIL Image or None
        """
        try:
            image_bytes = base64.b64decode(content_base64)
            return Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            logger.error(f"Failed to decode image: {e}")
            return None
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR results.
        
        Applies:
        - Grayscale conversion
        - Contrast enhancement
        - Noise reduction
        - Sharpening
        
        Args:
            image: PIL Image
            
        Returns:
            Preprocessed PIL Image
        """
        try:
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Apply slight sharpening
            image = image.filter(ImageFilter.SHARPEN)
            
            # Reduce noise
            image = image.filter(ImageFilter.MedianFilter(size=3))
            
            return image
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}")
            return image  # Return original if preprocessing fails
    
    def _perform_ocr(self, image: Image.Image, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform OCR using the best available service.
        
        Priority (by accuracy):
        1. AWS Textract (enterprise tier)
        2. Google Vision (pro tier)
        3. Tesseract (free tier)
        
        Args:
            image: Preprocessed PIL Image
            document: Document metadata
            
        Returns:
            Dict with OCR result
        """
        # Try services in order of availability and quality
        if self.aws_textract_available:
            return self._ocr_with_textract(image)
        elif self.google_vision_available:
            return self._ocr_with_google_vision(image)
        elif self.tesseract_available:
            return self._ocr_with_tesseract(image)
        else:
            return {
                'success': False,
                'error': 'No OCR service available',
                'text': '',
                'confidence': 0.0
            }
    
    def _ocr_with_tesseract(self, image: Image.Image) -> Dict[str, Any]:
        """
        Perform OCR using Tesseract.
        
        Args:
            image: PIL Image
            
        Returns:
            Dict with OCR result
        """
        try:
            import pytesseract
            
            # Get text with confidence data
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Extract text
            text = pytesseract.image_to_string(image)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'success': True,
                'text': text,
                'confidence': avg_confidence / 100.0,  # Convert to 0-1 scale
                'service_used': 'tesseract'
            }
            
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0.0
            }
    
    def _ocr_with_google_vision(self, image: Image.Image) -> Dict[str, Any]:
        """
        Perform OCR using Google Cloud Vision API.
        
        Args:
            image: PIL Image
            
        Returns:
            Dict with OCR result
        """
        try:
            from google.cloud import vision
            
            client = vision.ImageAnnotatorClient()
            
            # Convert PIL Image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            content = img_byte_arr.getvalue()
            
            # Perform OCR
            image_vision = vision.Image(content=content)
            response = client.text_detection(image=image_vision)
            texts = response.text_annotations
            
            if texts:
                full_text = texts[0].description
                confidence = 0.95  # Google Vision is generally very accurate
                
                return {
                    'success': True,
                    'text': full_text,
                    'confidence': confidence,
                    'service_used': 'google_vision'
                }
            else:
                return {
                    'success': True,
                    'text': '',
                    'confidence': 0.0,
                    'service_used': 'google_vision'
                }
            
        except Exception as e:
            logger.error(f"Google Vision OCR failed: {e}")
            # Fallback to Tesseract
            if self.tesseract_available:
                return self._ocr_with_tesseract(image)
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0.0
            }
    
    def _ocr_with_textract(self, image: Image.Image) -> Dict[str, Any]:
        """
        Perform OCR using AWS Textract.
        
        Args:
            image: PIL Image
            
        Returns:
            Dict with OCR result
        """
        try:
            import boto3
            from config import Config
            
            client = boto3.client(
                'textract',
                aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                region_name=Config.AWS_REGION
            )
            
            # Convert PIL Image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            
            # Perform OCR
            response = client.detect_document_text(
                Document={'Bytes': img_bytes}
            )
            
            # Extract text from blocks
            text_lines = []
            total_confidence = 0
            count = 0
            
            for block in response['Blocks']:
                if block['BlockType'] == 'LINE':
                    text_lines.append(block['Text'])
                    if 'Confidence' in block:
                        total_confidence += block['Confidence']
                        count += 1
            
            full_text = '\n'.join(text_lines)
            avg_confidence = (total_confidence / count / 100.0) if count > 0 else 0.0
            
            return {
                'success': True,
                'text': full_text,
                'confidence': avg_confidence,
                'service_used': 'aws_textract'
            }
            
        except Exception as e:
            logger.error(f"AWS Textract OCR failed: {e}")
            # Fallback to Google Vision or Tesseract
            if self.google_vision_available:
                return self._ocr_with_google_vision(image)
            elif self.tesseract_available:
                return self._ocr_with_tesseract(image)
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0.0
            }
    
    def _extract_text_from_document(self, document: Dict[str, Any]) -> str:
        """
        Extract text from non-image documents (PDF, DOCX, etc.).
        
        Args:
            document: Document dict
            
        Returns:
            Extracted text
        """
        try:
            import PyPDF2
            import docx
            
            content_base64 = document['content_base64']
            filename = document.get('filename', '')
            
            content_bytes = base64.b64decode(content_base64)
            
            if filename.lower().endswith('.pdf'):
                # Extract from PDF
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(content_bytes))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
                
            elif filename.lower().endswith('.docx'):
                # Extract from DOCX
                doc = docx.Document(io.BytesIO(content_bytes))
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
                
            else:
                # Try as plain text
                return content_bytes.decode('utf-8', errors='ignore')
            
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return ""
