"""
CLARITY OCR Module
Extract text from images and scanned documents
"""

from .ocr_engine import get_ocr_engine, OCREngine

__all__ = ['get_ocr_engine', 'OCREngine']
