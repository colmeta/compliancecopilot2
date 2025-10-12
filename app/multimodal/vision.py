# ==============================================================================
# app/multimodal/vision.py
# Vision/OCR Processing System - The Visual Intelligence
# ==============================================================================
"""
This module provides OCR and vision processing capabilities using multiple services.
Includes Tesseract (free), Google Vision API, and AWS Textract with intelligent failover.
"""

import os
import io
import logging
import tempfile
from typing import Dict, Any, Optional, List, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass
import base64
from PIL import Image

# OCR imports
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    from google.cloud import vision
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False

try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_TEXTRACT_AVAILABLE = True
except ImportError:
    AWS_TEXTRACT_AVAILABLE = False

try:
    from pdf2image import convert_from_bytes
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

from config import Config

logger = logging.getLogger(__name__)

# ==============================================================================
# DATA STRUCTURES
# ==============================================================================

@dataclass
class OCRResult:
    """Result of OCR processing."""
    text: str
    confidence: float
    language: str
    service_used: str
    metadata: Dict[str, Any]
    bounding_boxes: Optional[List[Dict[str, Any]]] = None
    blocks: Optional[List[Dict[str, Any]]] = None

@dataclass
class ImageInfo:
    """Image file information."""
    width: int
    height: int
    format: str
    mode: str
    size_bytes: int
    dpi: Optional[Tuple[int, int]] = None

# ==============================================================================
# BASE OCR CLASS
# ==============================================================================

class BaseOCR(ABC):
    """Base class for all OCR services."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    def extract_text(self, image_data: bytes, metadata: Dict[str, Any] = None) -> OCRResult:
        """
        Extract text from image data.
        
        Args:
            image_data: Raw image bytes
            metadata: Additional metadata
            
        Returns:
            OCRResult
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the service is available."""
        pass
    
    def get_image_info(self, image_data: bytes) -> ImageInfo:
        """Get information about image data."""
        try:
            image = Image.open(io.BytesIO(image_data))
            return ImageInfo(
                width=image.width,
                height=image.height,
                format=image.format,
                mode=image.mode,
                size_bytes=len(image_data),
                dpi=image.info.get('dpi')
            )
        except Exception as e:
            self.logger.error(f"Failed to get image info: {e}")
            return ImageInfo(0, 0, "unknown", "unknown", len(image_data))

# ==============================================================================
# TESSERACT OCR (FREE)
# ==============================================================================

class TesseractOCR(BaseOCR):
    """
    Tesseract OCR - Free, local processing.
    Best for: Free tier users, privacy-conscious users, offline processing.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("tesseract", config)
        self.language = self.config.get('language', 'eng')
        self.psm = self.config.get('psm', 6)  # Page segmentation mode
        self.oem = self.config.get('oem', 3)  # OCR Engine mode
    
    def is_available(self) -> bool:
        """Check if Tesseract is available."""
        if not TESSERACT_AVAILABLE:
            return False
        
        try:
            # Test if tesseract is installed
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False
    
    def extract_text(self, image_data: bytes, metadata: Dict[str, Any] = None) -> OCRResult:
        """Extract text using Tesseract OCR."""
        if not self.is_available():
            raise RuntimeError("Tesseract is not available")
        
        metadata = metadata or {}
        
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Configure Tesseract
            config = f'--oem {self.oem} --psm {self.psm} -l {self.language}'
            
            # Extract text
            text = pytesseract.image_to_string(image, config=config)
            
            # Get confidence data
            try:
                data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
                
                # Calculate average confidence
                confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                avg_confidence = sum(confidences) / len(confidences) / 100.0 if confidences else 0.0
                
                # Extract bounding boxes
                bounding_boxes = []
                for i in range(len(data['text'])):
                    if int(data['conf'][i]) > 0:
                        bounding_boxes.append({
                            'text': data['text'][i],
                            'confidence': int(data['conf'][i]) / 100.0,
                            'x': data['left'][i],
                            'y': data['top'][i],
                            'width': data['width'][i],
                            'height': data['height'][i]
                        })
                
            except Exception as e:
                self.logger.warning(f"Failed to get confidence data: {e}")
                avg_confidence = 0.5  # Default confidence
                bounding_boxes = []
            
            return OCRResult(
                text=text.strip(),
                confidence=avg_confidence,
                language=self.language,
                service_used=self.name,
                metadata={
                    'psm': self.psm,
                    'oem': self.oem,
                    'word_count': len(text.split()),
                    'image_size': f"{image.width}x{image.height}"
                },
                bounding_boxes=bounding_boxes
            )
        
        except Exception as e:
            self.logger.error(f"Tesseract OCR failed: {e}")
            raise

# ==============================================================================
# GOOGLE VISION OCR (PAID)
# ==============================================================================

class GoogleVisionOCR(BaseOCR):
    """
    Google Cloud Vision API OCR - Paid, high accuracy.
    Best for: Pro/Enterprise users, high accuracy requirements, multiple languages.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("google_vision", config)
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Vision client."""
        if not GOOGLE_VISION_AVAILABLE:
            self.logger.warning("Google Vision not available - install google-cloud-vision")
            return
        
        if not Config.GOOGLE_VISION_API_KEY:
            self.logger.warning("Google Vision API key not configured")
            return
        
        try:
            # Set credentials
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Config.GOOGLE_VISION_API_KEY
            self.client = vision.ImageAnnotatorClient()
            self.logger.info("Initialized Google Vision client")
        except Exception as e:
            self.logger.error(f"Failed to initialize Google Vision client: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Google Vision is available."""
        return GOOGLE_VISION_AVAILABLE and self.client is not None
    
    def extract_text(self, image_data: bytes, metadata: Dict[str, Any] = None) -> OCRResult:
        """Extract text using Google Vision API."""
        if not self.is_available():
            raise RuntimeError("Google Vision is not available")
        
        metadata = metadata or {}
        
        try:
            # Create image object
            image = vision.Image(content=image_data)
            
            # Perform text detection
            response = self.client.text_detection(image=image)
            
            if response.error.message:
                raise RuntimeError(f"Google Vision API error: {response.error.message}")
            
            # Extract text
            texts = response.text_annotations
            if not texts:
                return OCRResult(
                    text="",
                    confidence=0.0,
                    language="unknown",
                    service_used=self.name,
                    metadata={'no_text_found': True}
                )
            
            # Full text is the first annotation
            full_text = texts[0].description
            
            # Extract bounding boxes for individual words
            bounding_boxes = []
            for text in texts[1:]:  # Skip the first one (full text)
                vertices = text.bounding_poly.vertices
                if len(vertices) >= 2:
                    x = vertices[0].x
                    y = vertices[0].y
                    width = vertices[2].x - vertices[0].x if len(vertices) > 2 else 0
                    height = vertices[2].y - vertices[0].y if len(vertices) > 2 else 0
                    
                    bounding_boxes.append({
                        'text': text.description,
                        'confidence': 0.9,  # Google Vision doesn't provide per-word confidence
                        'x': x,
                        'y': y,
                        'width': width,
                        'height': height
                    })
            
            return OCRResult(
                text=full_text,
                confidence=0.9,  # Google Vision is generally very accurate
                language=metadata.get('language', 'unknown'),
                service_used=self.name,
                metadata={
                    'text_count': len(texts) - 1,
                    'word_count': len(full_text.split()),
                    'detected_language': response.text_annotations[0].locale if response.text_annotations else 'unknown'
                },
                bounding_boxes=bounding_boxes
            )
        
        except Exception as e:
            self.logger.error(f"Google Vision OCR failed: {e}")
            raise

# ==============================================================================
# AWS TEXTRACT OCR (ENTERPRISE)
# ==============================================================================

class AWSTextractOCR(BaseOCR):
    """
    AWS Textract OCR - Enterprise, document analysis.
    Best for: Enterprise users, document processing, table extraction.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("aws_textract", config)
        self.client = None
        self.region = self.config.get('region', Config.AWS_REGION)
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize AWS Textract client."""
        if not AWS_TEXTRACT_AVAILABLE:
            self.logger.warning("AWS Textract not available - install boto3")
            return
        
        if not Config.AWS_ACCESS_KEY_ID or not Config.AWS_SECRET_ACCESS_KEY:
            self.logger.warning("AWS credentials not configured")
            return
        
        try:
            self.client = boto3.client(
                'textract',
                region_name=self.region,
                aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
            )
            self.logger.info("Initialized AWS Textract client")
        except Exception as e:
            self.logger.error(f"Failed to initialize AWS Textract client: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if AWS Textract is available."""
        return AWS_TEXTRACT_AVAILABLE and self.client is not None
    
    def extract_text(self, image_data: bytes, metadata: Dict[str, Any] = None) -> OCRResult:
        """Extract text using AWS Textract."""
        if not self.is_available():
            raise RuntimeError("AWS Textract is not available")
        
        metadata = metadata or {}
        
        try:
            # Call Textract
            response = self.client.detect_document_text(
                Document={'Bytes': image_data}
            )
            
            # Extract text blocks
            blocks = response.get('Blocks', [])
            text_blocks = [block for block in blocks if block['BlockType'] == 'LINE']
            
            # Combine text
            text_lines = []
            bounding_boxes = []
            
            for block in text_blocks:
                text = block.get('Text', '')
                text_lines.append(text)
                
                # Extract bounding box
                geometry = block.get('Geometry', {})
                bounding_box = geometry.get('BoundingBox', {})
                
                if bounding_box:
                    bounding_boxes.append({
                        'text': text,
                        'confidence': block.get('Confidence', 0) / 100.0,
                        'x': bounding_box.get('Left', 0),
                        'y': bounding_box.get('Top', 0),
                        'width': bounding_box.get('Width', 0),
                        'height': bounding_box.get('Height', 0)
                    })
            
            full_text = '\n'.join(text_lines)
            
            # Calculate average confidence
            confidences = [block.get('Confidence', 0) for block in text_blocks]
            avg_confidence = sum(confidences) / len(confidences) / 100.0 if confidences else 0.0
            
            return OCRResult(
                text=full_text,
                confidence=avg_confidence,
                language=metadata.get('language', 'unknown'),
                service_used=self.name,
                metadata={
                    'block_count': len(blocks),
                    'text_block_count': len(text_blocks),
                    'word_count': len(full_text.split()),
                    'region': self.region
                },
                bounding_boxes=bounding_boxes,
                blocks=blocks
            )
        
        except ClientError as e:
            self.logger.error(f"AWS Textract failed: {e}")
            raise RuntimeError(f"AWS Textract error: {e}")
        except Exception as e:
            self.logger.error(f"AWS Textract OCR failed: {e}")
            raise

# ==============================================================================
# VISION ORCHESTRATOR
# ==============================================================================

class VisionOrchestrator:
    """
    Orchestrates different OCR services with intelligent selection.
    Handles failover, tier-based access, and service optimization.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize OCR services
        self.ocr_services = {
            'tesseract': TesseractOCR(self.config.get('tesseract', {})),
            'google_vision': GoogleVisionOCR(self.config.get('google_vision', {})),
            'aws_textract': AWSTextractOCR(self.config.get('aws_textract', {}))
        }
        
        # Service priority order (best to worst)
        self.service_priority = ['aws_textract', 'google_vision', 'tesseract']
    
    def extract_text(self, image_data: bytes, user_tier: str = 'free', 
                     metadata: Dict[str, Any] = None) -> OCRResult:
        """
        Extract text using the best available service for the user's tier.
        
        Args:
            image_data: Raw image bytes
            user_tier: User's subscription tier
            metadata: Additional metadata
            
        Returns:
            OCRResult
        """
        metadata = metadata or {}
        
        # Get available services for user tier
        available_services = self._get_available_services(user_tier)
        
        if not available_services:
            raise RuntimeError("No OCR services available for your tier")
        
        # Try services in priority order
        last_error = None
        
        for service_name in available_services:
            if service_name not in self.ocr_services:
                continue
            
            ocr_service = self.ocr_services[service_name]
            
            if not ocr_service.is_available():
                self.logger.warning(f"Service {service_name} is not available")
                continue
            
            try:
                self.logger.info(f"Attempting OCR with {service_name}")
                result = ocr_service.extract_text(image_data, metadata)
                
                # Add orchestration metadata
                result.metadata['orchestration'] = {
                    'services_tried': [service_name],
                    'user_tier': user_tier,
                    'selected_service': service_name
                }
                
                return result
            
            except Exception as e:
                self.logger.error(f"OCR failed with {service_name}: {e}")
                last_error = e
                continue
        
        # All services failed
        raise RuntimeError(f"All OCR services failed. Last error: {last_error}")
    
    def _get_available_services(self, user_tier: str) -> List[str]:
        """Get list of available services for user tier."""
        from app.tiers import get_available_services
        
        available_services = get_available_services(user_tier, 'ocr_processing')
        
        if not available_services:
            return []
        
        if 'all' in available_services:
            # All services available
            return self.service_priority
        
        # Filter by available services
        tier_services = []
        for service in self.service_priority:
            if service in available_services or service == 'tesseract':  # Tesseract always available
                tier_services.append(service)
        
        return tier_services
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about available services."""
        info = {}
        
        for name, ocr_service in self.ocr_services.items():
            info[name] = {
                'available': ocr_service.is_available(),
                'name': ocr_service.name,
                'config': ocr_service.config
            }
        
        return info
    
    def get_image_info(self, image_data: bytes) -> ImageInfo:
        """Get information about image data."""
        # Use Tesseract OCR for image info (it has the most comprehensive support)
        if 'tesseract' in self.ocr_services:
            return self.ocr_services['tesseract'].get_image_info(image_data)
        else:
            return ImageInfo(0, 0, "unknown", "unknown", len(image_data))

# ==============================================================================
# PDF PROCESSING UTILITIES
# ==============================================================================

def extract_text_from_pdf(pdf_data: bytes, user_tier: str = 'free', 
                         metadata: Dict[str, Any] = None) -> List[OCRResult]:
    """
    Extract text from PDF by converting pages to images and running OCR.
    
    Args:
        pdf_data: Raw PDF bytes
        user_tier: User's subscription tier
        metadata: Additional metadata
        
    Returns:
        List of OCRResult for each page
    """
    if not PDF2IMAGE_AVAILABLE:
        raise RuntimeError("PDF processing not available - install pdf2image")
    
    metadata = metadata or {}
    results = []
    
    try:
        # Convert PDF to images
        images = convert_from_bytes(pdf_data, dpi=300)  # High DPI for better OCR
        
        # Initialize orchestrator
        orchestrator = VisionOrchestrator()
        
        # Process each page
        for i, image in enumerate(images):
            # Convert PIL image to bytes
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG')
            img_data = img_buffer.getvalue()
            
            # Run OCR
            page_metadata = {
                **metadata,
                'page_number': i + 1,
                'total_pages': len(images)
            }
            
            result = orchestrator.extract_text(img_data, user_tier, page_metadata)
            results.append(result)
        
        return results
    
    except Exception as e:
        logger.error(f"PDF text extraction failed: {e}")
        raise

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def validate_image_data(image_data: bytes) -> Dict[str, Any]:
    """
    Validate image data and return information.
    
    Args:
        image_data: Raw image bytes
        
    Returns:
        Validation result with image info
    """
    if not image_data:
        return {'valid': False, 'error': 'No image data provided'}
    
    if len(image_data) < 100:  # Less than 100 bytes
        return {'valid': False, 'error': 'Image data too small'}
    
    try:
        # Try to open as image
        image = Image.open(io.BytesIO(image_data))
        image.verify()  # Verify it's a valid image
        
        # Get image info
        orchestrator = VisionOrchestrator()
        image_info = orchestrator.get_image_info(image_data)
        
        return {
            'valid': True,
            'image_info': image_info,
            'size_bytes': len(image_data)
        }
    
    except Exception as e:
        return {'valid': False, 'error': f'Invalid image data: {e}'}

def preprocess_image_for_ocr(image_data: bytes, enhance: bool = True) -> bytes:
    """
    Preprocess image for better OCR results.
    
    Args:
        image_data: Raw image bytes
        enhance: Whether to apply enhancement
        
    Returns:
        Preprocessed image bytes
    """
    try:
        image = Image.open(io.BytesIO(image_data))
        
        if enhance:
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Enhance contrast
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
        
        # Convert back to bytes
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        return img_buffer.getvalue()
    
    except Exception as e:
        logger.error(f"Image preprocessing failed: {e}")
        return image_data

def detect_image_language(image_data: bytes) -> str:
    """
    Detect the language of text in an image.
    
    Args:
        image_data: Raw image bytes
        
    Returns:
        Detected language code
    """
    # This is a simplified implementation
    # In practice, you might use a language detection service
    
    # For now, return a default
    return 'en'

