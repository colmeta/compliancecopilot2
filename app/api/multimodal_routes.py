# ==============================================================================
# app/api/multimodal_routes.py
# Multi-Modal Processing API Routes - The Intelligence Gateway
# ==============================================================================
"""
This module provides API endpoints for multi-modal processing including:
- Audio transcription
- OCR and image text extraction
- Video processing and analysis
- PDF text extraction

All endpoints require authentication and respect tier limits.
"""

from flask import Blueprint, request, jsonify, current_app, g
from functools import wraps
import base64
import logging
from app.api.routes import api_key_required
from app.middleware.tier_check import check_tier_limit, track_usage
from app.multimodal.audio import AudioOrchestrator, validate_audio_data
from app.multimodal.vision import VisionOrchestrator, validate_image_data, extract_text_from_pdf
from app.multimodal.video import VideoProcessor, VideoAnalyzer, validate_video_data
from app.models import User, Subscription
from app import db

# Configure logging
logger = logging.getLogger(__name__)

# Create multimodal blueprint
multimodal = Blueprint('multimodal', __name__)

# ==============================================================================
# AUDIO TRANSCRIPTION ENDPOINTS
# ==============================================================================

@multimodal.route('/transcribe', methods=['POST'])
@api_key_required
@check_tier_limit('audio_transcription', 1)
def transcribe_audio():
    """
    Transcribe audio files to text.
    
    Supports multiple audio formats and services based on user tier:
    - Free: Whisper (local processing)
    - Pro: Whisper + Google Speech-to-Text
    - Enterprise: All services (Whisper, Google Speech, AssemblyAI)
    
    Request:
        - files: Audio files (MP3, WAV, M4A, etc.)
        - language: Optional language code (auto-detect if not provided)
        - service: Optional service preference
    
    Response:
        - transcriptions: List of transcription results
        - service_used: Service that performed the transcription
        - confidence: Average confidence score
    """
    try:
        # Get current user
        user = g.current_user
        subscription = Subscription.query.filter_by(user_id=user.id, status='active').first()
        user_tier = subscription.tier if subscription else 'free'
        
        # Get uploaded files
        uploaded_files = request.files.getlist('files')
        if not uploaded_files:
            return jsonify({'error': 'No audio files uploaded'}), 400
        
        # Get optional parameters
        language = request.form.get('language')
        service_preference = request.form.get('service')
        
        # Initialize audio orchestrator
        orchestrator = AudioOrchestrator()
        
        # Process each file
        results = []
        total_confidence = 0
        services_used = set()
        
        for file in uploaded_files:
            if file.filename == '':
                continue
            
            # Read file content
            audio_data = file.read()
            
            # Validate audio data
            validation = validate_audio_data(audio_data)
            if not validation['valid']:
                results.append({
                    'filename': file.filename,
                    'error': validation['error'],
                    'success': False
                })
                continue
            
            # Prepare metadata
            metadata = {
                'filename': file.filename,
                'language': language,
                'duration': validation.get('audio_info', {}).get('duration', 0),
                'service_preference': service_preference
            }
            
            try:
                # Transcribe audio
                result = orchestrator.transcribe(audio_data, user_tier, metadata)
                
                results.append({
                    'filename': file.filename,
                    'text': result.text,
                    'confidence': result.confidence,
                    'language': result.language,
                    'duration': result.duration,
                    'service_used': result.service_used,
                    'segments': result.segments,
                    'success': True
                })
                
                total_confidence += result.confidence
                services_used.add(result.service_used)
                
            except Exception as e:
                logger.error(f"Transcription failed for {file.filename}: {e}")
                results.append({
                    'filename': file.filename,
                    'error': str(e),
                    'success': False
                })
        
        # Calculate average confidence
        successful_results = [r for r in results if r.get('success', False)]
        avg_confidence = total_confidence / len(successful_results) if successful_results else 0
        
        return jsonify({
            'success': True,
            'transcriptions': results,
            'summary': {
                'total_files': len(uploaded_files),
                'successful': len(successful_results),
                'failed': len(results) - len(successful_results),
                'average_confidence': avg_confidence,
                'services_used': list(services_used)
            },
            'user_tier': user_tier
        }), 200
        
    except Exception as e:
        logger.error(f"Audio transcription endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==============================================================================
# OCR AND IMAGE PROCESSING ENDPOINTS
# ==============================================================================

@multimodal.route('/ocr', methods=['POST'])
@api_key_required
@check_tier_limit('ocr_processing', 1)
def extract_text_from_images():
    """
    Extract text from images using OCR.
    
    Supports multiple OCR services based on user tier:
    - Free: Tesseract (local processing)
    - Pro: Tesseract + Google Vision API
    - Enterprise: All services (Tesseract, Google Vision, AWS Textract)
    
    Request:
        - files: Image files (PNG, JPG, PDF, etc.)
        - language: Optional language code
        - service: Optional service preference
        - enhance: Whether to enhance images for better OCR
    
    Response:
        - extractions: List of OCR results
        - service_used: Service that performed the OCR
        - confidence: Average confidence score
    """
    try:
        # Get current user
        user = g.current_user
        subscription = Subscription.query.filter_by(user_id=user.id, status='active').first()
        user_tier = subscription.tier if subscription else 'free'
        
        # Get uploaded files
        uploaded_files = request.files.getlist('files')
        if not uploaded_files:
            return jsonify({'error': 'No image files uploaded'}), 400
        
        # Get optional parameters
        language = request.form.get('language')
        service_preference = request.form.get('service')
        enhance = request.form.get('enhance', 'false').lower() == 'true'
        
        # Initialize vision orchestrator
        orchestrator = VisionOrchestrator()
        
        # Process each file
        results = []
        total_confidence = 0
        services_used = set()
        
        for file in uploaded_files:
            if file.filename == '':
                continue
            
            # Read file content
            image_data = file.read()
            
            # Check if it's a PDF
            if file.filename.lower().endswith('.pdf'):
                try:
                    # Extract text from PDF
                    pdf_results = extract_text_from_pdf(image_data, user_tier, {
                        'filename': file.filename,
                        'language': language
                    })
                    
                    # Combine results
                    combined_text = []
                    combined_confidence = 0
                    
                    for i, result in enumerate(pdf_results):
                        combined_text.append(f"Page {i+1}: {result.text}")
                        combined_confidence += result.confidence
                    
                    avg_confidence = combined_confidence / len(pdf_results) if pdf_results else 0
                    
                    results.append({
                        'filename': file.filename,
                        'text': '\n\n'.join(combined_text),
                        'confidence': avg_confidence,
                        'language': pdf_results[0].language if pdf_results else 'unknown',
                        'service_used': pdf_results[0].service_used if pdf_results else 'unknown',
                        'pages': len(pdf_results),
                        'success': True
                    })
                    
                    total_confidence += avg_confidence
                    if pdf_results:
                        services_used.add(pdf_results[0].service_used)
                    
                except Exception as e:
                    logger.error(f"PDF processing failed for {file.filename}: {e}")
                    results.append({
                        'filename': file.filename,
                        'error': str(e),
                        'success': False
                    })
                
                continue
            
            # Validate image data
            validation = validate_image_data(image_data)
            if not validation['valid']:
                results.append({
                    'filename': file.filename,
                    'error': validation['error'],
                    'success': False
                })
                continue
            
            # Prepare metadata
            metadata = {
                'filename': file.filename,
                'language': language,
                'service_preference': service_preference,
                'enhance': enhance
            }
            
            try:
                # Extract text using OCR
                result = orchestrator.extract_text(image_data, user_tier, metadata)
                
                results.append({
                    'filename': file.filename,
                    'text': result.text,
                    'confidence': result.confidence,
                    'language': result.language,
                    'service_used': result.service_used,
                    'bounding_boxes': result.bounding_boxes,
                    'success': True
                })
                
                total_confidence += result.confidence
                services_used.add(result.service_used)
                
            except Exception as e:
                logger.error(f"OCR failed for {file.filename}: {e}")
                results.append({
                    'filename': file.filename,
                    'error': str(e),
                    'success': False
                })
        
        # Calculate average confidence
        successful_results = [r for r in results if r.get('success', False)]
        avg_confidence = total_confidence / len(successful_results) if successful_results else 0
        
        return jsonify({
            'success': True,
            'extractions': results,
            'summary': {
                'total_files': len(uploaded_files),
                'successful': len(successful_results),
                'failed': len(results) - len(successful_results),
                'average_confidence': avg_confidence,
                'services_used': list(services_used)
            },
            'user_tier': user_tier
        }), 200
        
    except Exception as e:
        logger.error(f"OCR endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==============================================================================
# VIDEO PROCESSING ENDPOINTS
# ==============================================================================

@multimodal.route('/video/analyze', methods=['POST'])
@api_key_required
@check_tier_limit('video_processing', 1)
def analyze_video():
    """
    Analyze video files and extract key information.
    
    Available for Pro and Enterprise tiers:
    - Frame extraction
    - Scene detection
    - Audio transcription
    - Visual text extraction
    
    Request:
        - files: Video files (MP4, AVI, MOV, etc.)
        - extract_audio: Whether to extract and transcribe audio
        - extract_frames: Whether to extract key frames
        - detect_scenes: Whether to detect scenes
    
    Response:
        - analyses: List of video analysis results
        - summary: Analysis summary
    """
    try:
        # Get current user
        user = g.current_user
        subscription = Subscription.query.filter_by(user_id=user.id, status='active').first()
        user_tier = subscription.tier if subscription else 'free'
        
        # Check if user has access to video processing
        if user_tier == 'free':
            return jsonify({
                'error': 'Video processing requires Pro or Enterprise tier',
                'upgrade_prompt': 'Upgrade to Pro to analyze video files'
            }), 403
        
        # Get uploaded files
        uploaded_files = request.files.getlist('files')
        if not uploaded_files:
            return jsonify({'error': 'No video files uploaded'}), 400
        
        # Get optional parameters
        extract_audio = request.form.get('extract_audio', 'true').lower() == 'true'
        extract_frames = request.form.get('extract_frames', 'true').lower() == 'true'
        detect_scenes = request.form.get('detect_scenes', 'true').lower() == 'true'
        
        # Initialize video analyzer
        analyzer = VideoAnalyzer()
        
        # Process each file
        results = []
        
        for file in uploaded_files:
            if file.filename == '':
                continue
            
            # Read file content
            video_data = file.read()
            
            # Validate video data
            validation = validate_video_data(video_data)
            if not validation['valid']:
                results.append({
                    'filename': file.filename,
                    'error': validation['error'],
                    'success': False
                })
                continue
            
            # Prepare metadata
            metadata = {
                'filename': file.filename,
                'extract_audio': extract_audio,
                'extract_frames': extract_frames,
                'detect_scenes': detect_scenes
            }
            
            try:
                # Analyze video
                analysis = analyzer.analyze_video(video_data, user_tier, metadata)
                
                # Generate summary
                summary = analyzer.generate_summary(analysis)
                
                results.append({
                    'filename': file.filename,
                    'analysis': analysis,
                    'summary': summary,
                    'success': True
                })
                
            except Exception as e:
                logger.error(f"Video analysis failed for {file.filename}: {e}")
                results.append({
                    'filename': file.filename,
                    'error': str(e),
                    'success': False
                })
        
        # Calculate summary
        successful_results = [r for r in results if r.get('success', False)]
        
        return jsonify({
            'success': True,
            'analyses': results,
            'summary': {
                'total_files': len(uploaded_files),
                'successful': len(successful_results),
                'failed': len(results) - len(successful_results)
            },
            'user_tier': user_tier
        }), 200
        
    except Exception as e:
        logger.error(f"Video analysis endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==============================================================================
# SERVICE INFORMATION ENDPOINTS
# ==============================================================================

@multimodal.route('/services', methods=['GET'])
@api_key_required
def get_available_services():
    """
    Get information about available multi-modal services for the user's tier.
    
    Response:
        - audio_services: Available audio transcription services
        - vision_services: Available OCR services
        - user_tier: User's current tier
        - limits: Tier limits for multi-modal features
    """
    try:
        # Get current user
        user = g.current_user
        subscription = Subscription.query.filter_by(user_id=user.id, status='active').first()
        user_tier = subscription.tier if subscription else 'free'
        
        # Get service information
        audio_orchestrator = AudioOrchestrator()
        vision_orchestrator = VisionOrchestrator()
        
        # Get tier limits
        from app.tiers import get_tier_limits
        tier_limits = get_tier_limits(user_tier)
        
        return jsonify({
            'success': True,
            'user_tier': user_tier,
            'audio_services': audio_orchestrator.get_service_info(),
            'vision_services': vision_orchestrator.get_service_info(),
            'video_processing': {
                'available': tier_limits.get('video_processing', False),
                'description': 'Video analysis, frame extraction, scene detection'
            },
            'tier_limits': {
                'audio_transcription': tier_limits.get('audio_transcription', False),
                'video_processing': tier_limits.get('video_processing', False),
                'ocr_processing': tier_limits.get('ocr_processing', False)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Services endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==============================================================================
# HEALTH CHECK ENDPOINTS
# ==============================================================================

@multimodal.route('/health', methods=['GET'])
def multimodal_health():
    """
    Check the health of multi-modal processing services.
    
    Response:
        - status: Overall system status
        - services: Status of individual services
    """
    try:
        # Check audio services
        audio_orchestrator = AudioOrchestrator()
        audio_services = audio_orchestrator.get_service_info()
        
        # Check vision services
        vision_orchestrator = VisionOrchestrator()
        vision_services = vision_orchestrator.get_service_info()
        
        # Determine overall status
        audio_available = any(service['available'] for service in audio_services.values())
        vision_available = any(service['available'] for service in vision_services.values())
        
        overall_status = 'healthy' if (audio_available or vision_available) else 'degraded'
        
        return jsonify({
            'status': overall_status,
            'audio_services': audio_services,
            'vision_services': vision_services,
            'video_processing': {
                'available': True,  # Assume available if dependencies are installed
                'dependencies': {
                    'opencv': True,  # Would check actual availability
                    'moviepy': True,
                    'scenedetect': True
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Multi-modal health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# ==============================================================================
# ERROR HANDLERS
# ==============================================================================

@multimodal.errorhandler(413)
def too_large(e):
    """Handle file too large errors."""
    return jsonify({
        'error': 'File too large',
        'message': 'Please upload smaller files or upgrade your tier for larger file support'
    }), 413

@multimodal.errorhandler(415)
def unsupported_media_type(e):
    """Handle unsupported media type errors."""
    return jsonify({
        'error': 'Unsupported media type',
        'message': 'Please upload supported file formats (MP3, WAV, PNG, JPG, MP4, etc.)'
    }), 415

