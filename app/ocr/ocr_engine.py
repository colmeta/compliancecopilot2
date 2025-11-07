"""
CLARITY OCR Engine - Extract Text from Images and Scanned Documents
Supports both FREE (Tesseract) and PREMIUM (Google Cloud Vision) OCR
Smart fallback system to minimize costs
"""

import os
import logging
from typing import Dict, Optional, Tuple, List
from datetime import datetime
from PIL import Image
import io

# Tesseract (FREE)
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("Tesseract not installed - OCR will be limited to Google Vision")

# Google Cloud Vision (PAID but has FREE tier: 1,000 pages/month)
try:
    from google.cloud import vision
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False
    logging.warning("Google Cloud Vision not installed")

logger = logging.getLogger(__name__)


class OCREngine:
    """
    Extract text from images and scanned documents
    
    Features:
    - FREE: Tesseract OCR (80-90% accuracy, local processing)
    - PREMIUM: Google Cloud Vision (95-99% accuracy, 1,000 free/month)
    - Smart fallback: Try free first, use premium if needed
    - Usage tracking: Prevent surprise charges
    - Multi-language support
    """
    
    def __init__(self):
        self.tesseract_enabled = TESSERACT_AVAILABLE
        self.google_vision_enabled = GOOGLE_VISION_AVAILABLE
        
        # Google Cloud Vision client (if credentials available)
        self.vision_client = None
        google_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        if GOOGLE_VISION_AVAILABLE and google_credentials:
            try:
                self.vision_client = vision.ImageAnnotatorClient()
                logger.info("✅ Google Cloud Vision OCR initialized")
            except Exception as e:
                logger.warning(f"⚠️  Google Vision initialization failed: {e}")
        
        # Usage tracking (to avoid surprise charges)
        self.monthly_google_usage = 0
        self.google_free_limit = 1000  # Free tier limit
    
    def extract_text(self, 
                    image_data: bytes, 
                    use_premium: bool = False,
                    language: str = 'eng',
                    auto_fallback: bool = True) -> Dict:
        """
        Extract text from image with smart fallback
        
        Args:
            image_data: Image bytes (JPEG, PNG, PDF page)
            use_premium: Force use of Google Vision (paid)
            language: OCR language (eng, fra, spa, etc.)
            auto_fallback: Automatically try premium if free fails
        
        Returns:
            {
                'success': bool,
                'text': str,
                'confidence': float,
                'engine': 'tesseract' | 'google_vision',
                'cost': float (in USD),
                'language': str,
                'word_count': int,
                'processing_time': float
            }
        """
        start_time = datetime.now()
        
        try:
            # Strategy 1: Try FREE Tesseract first (if not forced premium)
            if not use_premium and self.tesseract_enabled:
                logger.info("🆓 Attempting FREE Tesseract OCR...")
                result = self._extract_with_tesseract(image_data, language)
                
                # If good confidence, use it!
                if result['success'] and result['confidence'] >= 85:
                    result['processing_time'] = (datetime.now() - start_time).total_seconds()
                    logger.info(f"✅ Tesseract succeeded: {result['confidence']}% confidence (FREE)")
                    return result
                
                # If auto_fallback disabled, return Tesseract result anyway
                if not auto_fallback:
                    result['processing_time'] = (datetime.now() - start_time).total_seconds()
                    return result
                
                logger.info(f"⚠️  Tesseract low confidence ({result['confidence']}%), trying Google Vision...")
            
            # Strategy 2: Use Google Vision (if available and within budget)
            if self.vision_client and self.monthly_google_usage < self.google_free_limit:
                logger.info("🌟 Using Google Cloud Vision OCR (premium)...")
                result = self._extract_with_google_vision(image_data, language)
                result['processing_time'] = (datetime.now() - start_time).total_seconds()
                
                if result['success']:
                    self.monthly_google_usage += 1
                    logger.info(f"✅ Google Vision succeeded: {result['confidence']}% confidence")
                    logger.info(f"📊 Monthly usage: {self.monthly_google_usage}/{self.google_free_limit} (FREE tier)")
                
                return result
            
            # Strategy 3: Fallback to Tesseract if Google not available
            elif self.tesseract_enabled:
                logger.info("🆓 Using Tesseract OCR (Google Vision not available)...")
                result = self._extract_with_tesseract(image_data, language)
                result['processing_time'] = (datetime.now() - start_time).total_seconds()
                return result
            
            # No OCR available - fail gracefully
            return {
                'success': False,
                'text': '',
                'confidence': 0,
                'engine': 'none',
                'cost': 0,
                'error': 'No OCR engine available',
                'message': 'OCR configuration error - contact system administrator',
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return {
                'success': False,
                'text': '',
                'confidence': 0,
                'engine': 'error',
                'cost': 0,
                'error': str(e),
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
    
    def _extract_with_tesseract(self, image_data: bytes, language: str) -> Dict:
        """
        Extract text using FREE Tesseract OCR
        
        Pros: Free, fast, local processing
        Cons: Lower accuracy (80-90%), struggles with handwriting
        """
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text with confidence
            data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Extract text
            text = pytesseract.image_to_string(image, lang=language)
            
            # Clean text
            text = text.strip()
            word_count = len(text.split())
            
            return {
                'success': True,
                'text': text,
                'confidence': round(avg_confidence, 2),
                'engine': 'tesseract',
                'cost': 0.0,  # FREE!
                'language': language,
                'word_count': word_count,
                'image_size': len(image_data)
            }
            
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            return {
                'success': False,
                'text': '',
                'confidence': 0,
                'engine': 'tesseract',
                'cost': 0,
                'error': str(e)
            }
    
    def _extract_with_google_vision(self, image_data: bytes, language: str) -> Dict:
        """
        Extract text using Google Cloud Vision OCR (PREMIUM)
        
        Pros: High accuracy (95-99%), handles handwriting, multi-language
        Cons: Costs money after 1,000 pages/month ($1.50 per 1,000)
        
        FREE TIER: 1,000 pages/month
        """
        try:
            # Create image object
            image = vision.Image(content=image_data)
            
            # Detect text (document_text_detection is better for documents)
            response = self.vision_client.document_text_detection(image=image)
            
            if response.error.message:
                raise Exception(response.error.message)
            
            # Extract full text
            text = response.full_text_annotation.text if response.full_text_annotation else ''
            
            # Calculate confidence from pages
            confidence = 0
            if response.full_text_annotation and response.full_text_annotation.pages:
                page = response.full_text_annotation.pages[0]
                if page.confidence:
                    confidence = page.confidence * 100
                else:
                    confidence = 95  # Google is typically 95%+ accurate
            else:
                confidence = 90  # Default for Google Vision
            
            # Calculate cost (after free tier)
            cost = 0
            if self.monthly_google_usage >= self.google_free_limit:
                cost = 0.0015  # $1.50 per 1,000 = $0.0015 per page
            
            word_count = len(text.split())
            
            return {
                'success': True,
                'text': text.strip(),
                'confidence': round(confidence, 2),
                'engine': 'google_vision',
                'cost': cost,
                'language': language,
                'word_count': word_count,
                'image_size': len(image_data),
                'free_tier': self.monthly_google_usage < self.google_free_limit
            }
            
        except Exception as e:
            logger.error(f"Google Vision OCR failed: {e}")
            return {
                'success': False,
                'text': '',
                'confidence': 0,
                'engine': 'google_vision',
                'cost': 0,
                'error': str(e)
            }
    
    def extract_from_pdf(self, pdf_path: str, max_pages: int = 10) -> List[Dict]:
        """
        Extract text from multi-page PDF
        
        Args:
            pdf_path: Path to PDF file
            max_pages: Maximum pages to process (to avoid huge costs)
        
        Returns:
            List of results (one per page)
        """
        try:
            from pdf2image import convert_from_path
            
            # Convert PDF to images
            images = convert_from_path(pdf_path, first_page=1, last_page=max_pages)
            
            results = []
            for page_num, image in enumerate(images, 1):
                logger.info(f"Processing page {page_num}/{len(images)}...")
                
                # Convert PIL Image to bytes
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_bytes = img_byte_arr.getvalue()
                
                # Extract text
                result = self.extract_text(img_bytes)
                result['page_number'] = page_num
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"PDF OCR failed: {e}")
            return [{
                'success': False,
                'text': '',
                'error': str(e),
                'page_number': 0
            }]
    
    def get_status(self) -> Dict:
        """Get OCR engine status and usage"""
        return {
            'engines_available': {
                'tesseract': self.tesseract_enabled,
                'google_vision': self.vision_client is not None
            },
            'google_vision_usage': {
                'monthly_usage': self.monthly_google_usage,
                'free_limit': self.google_free_limit,
                'remaining_free': max(0, self.google_free_limit - self.monthly_google_usage),
                'cost_after_free_tier': '$1.50 per 1,000 pages'
            },
            'recommendations': self._get_recommendations()
        }
    
    def _get_recommendations(self) -> List[str]:
        """Get recommendations based on current setup"""
        recs = []
        
        if not self.tesseract_enabled and not self.vision_client:
            recs.append("⚠️  No OCR engine available. Install Tesseract or configure Google Vision.")
        
        if not self.tesseract_enabled and self.vision_client:
            recs.append("💡 Install Tesseract for FREE OCR fallback (reduces Google Vision costs)")
        
        if self.monthly_google_usage >= self.google_free_limit * 0.8:
            recs.append(f"⚠️  Approaching Google Vision free limit ({self.monthly_google_usage}/{self.google_free_limit})")
        
        if self.monthly_google_usage >= self.google_free_limit:
            recs.append("💰 Exceeded free tier - now paying $1.50 per 1,000 pages")
        
        if not self.vision_client and self.tesseract_enabled:
            recs.append("✅ Using FREE Tesseract OCR (80-90% accuracy)")
        
        return recs


# Singleton instance
_ocr_engine = None

def get_ocr_engine():
    """Get singleton OCR engine instance"""
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = OCREngine()
    return _ocr_engine
