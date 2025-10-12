# ==============================================================================
# app/multimodal/__init__.py
# Multi-Modal Processing Package - The Intelligence Extractor
# ==============================================================================
"""
This package contains multi-modal processing capabilities for CLARITY.
Handles audio transcription, OCR, video processing, and other media types.
"""

from .audio import (
    WhisperTranscriber,
    GoogleSpeechTranscriber,
    AssemblyAITranscriber,
    AudioOrchestrator
)

from .vision import (
    TesseractOCR,
    GoogleVisionOCR,
    AWSTextractOCR,
    VisionOrchestrator
)

from .video import (
    VideoProcessor,
    VideoAnalyzer
)

__all__ = [
    # Audio
    'WhisperTranscriber',
    'GoogleSpeechTranscriber', 
    'AssemblyAITranscriber',
    'AudioOrchestrator',
    
    # Vision
    'TesseractOCR',
    'GoogleVisionOCR',
    'AWSTextractOCR',
    'VisionOrchestrator',
    
    # Video
    'VideoProcessor',
    'VideoAnalyzer'
]

