"""
CLARITY OCR API Routes
Extract text from images and scanned documents
FREE tier available (Tesseract) + Premium tier (Google Vision)
"""

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
from app.ocr.ocr_engine import get_ocr_engine
import logging
import os
import tempfile

ocr_bp = Blueprint('ocr', __name__)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'tiff', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@ocr_bp.route('/ocr/extract', methods=['POST'])
def extract_text_from_image():
    """
    Extract text from uploaded image or PDF
    
    POST /ocr/extract
    Content-Type: multipart/form-data
    
    Form Data:
    - file: Image or PDF file
    - use_premium: 'true' | 'false' (optional, default: false)
    - language: 'eng' | 'fra' | 'spa' etc. (optional, default: eng)
    - auto_fallback: 'true' | 'false' (optional, default: true)
    
    Response:
    {
        "success": true,
        "text": "Extracted text content...",
        "confidence": 92.5,
        "engine": "tesseract" | "google_vision",
        "cost": 0.0,
        "word_count": 245,
        "processing_time": 1.2,
        "free_tier": true
    }
    """
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded',
                'message': 'Please upload an image or PDF file'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type',
                'message': f'Allowed types: {", ".join(ALLOWED_EXTENSIONS)}',
                'allowed_extensions': list(ALLOWED_EXTENSIONS)
            }), 400
        
        # Get parameters
        use_premium = request.form.get('use_premium', 'false').lower() == 'true'
        language = request.form.get('language', 'eng')
        auto_fallback = request.form.get('auto_fallback', 'true').lower() == 'true'
        
        # Read file data
        file_data = file.read()
        file_size_mb = len(file_data) / (1024 * 1024)
        
        logger.info(f"📄 OCR request: {file.filename} ({file_size_mb:.2f} MB)")
        
        # Check file size (max 25MB)
        if file_size_mb > 25:
            return jsonify({
                'success': False,
                'error': 'File too large',
                'message': 'Maximum file size is 25MB',
                'file_size_mb': file_size_mb
            }), 400
        
        # Get OCR engine
        ocr_engine = get_ocr_engine()
        
        # Handle PDF separately
        if file.filename.lower().endswith('.pdf'):
            # Save temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(file_data)
                tmp_path = tmp_file.name
            
            try:
                # Extract from PDF (up to 10 pages)
                results = ocr_engine.extract_from_pdf(tmp_path, max_pages=10)
                
                # Combine all pages
                combined_text = "\n\n".join([r['text'] for r in results if r['success']])
                total_confidence = sum([r['confidence'] for r in results if r['success']]) / len(results) if results else 0
                total_cost = sum([r.get('cost', 0) for r in results])
                
                return jsonify({
                    'success': True,
                    'text': combined_text,
                    'confidence': round(total_confidence, 2),
                    'engine': results[0]['engine'] if results else 'unknown',
                    'cost': round(total_cost, 4),
                    'pages_processed': len(results),
                    'pages': results,
                    'word_count': len(combined_text.split()),
                    'file_type': 'pdf'
                }), 200
                
            finally:
                # Clean up
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        
        # Handle image
        else:
            result = ocr_engine.extract_text(
                image_data=file_data,
                use_premium=use_premium,
                language=language,
                auto_fallback=auto_fallback
            )
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'text': result['text'],
                    'confidence': result['confidence'],
                    'engine': result['engine'],
                    'cost': result['cost'],
                    'word_count': result.get('word_count', 0),
                    'processing_time': result.get('processing_time', 0),
                    'language': result.get('language', language),
                    'free_tier': result.get('free_tier', True),
                    'file_type': 'image'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'OCR failed'),
                    'message': result.get('message', 'Could not extract text from image')
                }), 500
        
    except Exception as e:
        logger.error(f"OCR endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'OCR processing failed'
        }), 500


@ocr_bp.route('/ocr/status', methods=['GET'])
def get_ocr_status():
    """
    Get OCR engine status and usage
    
    GET /ocr/status
    
    Response:
    {
        "engines_available": {
            "tesseract": true,
            "google_vision": true
        },
        "google_vision_usage": {
            "monthly_usage": 245,
            "free_limit": 1000,
            "remaining_free": 755,
            "cost_after_free_tier": "$1.50 per 1,000 pages"
        },
        "recommendations": [...]
    }
    """
    try:
        ocr_engine = get_ocr_engine()
        status = ocr_engine.get_status()
        
        return jsonify({
            'success': True,
            'status': status,
            'pricing': {
                'tesseract': {
                    'cost': '$0 (FREE forever)',
                    'accuracy': '80-90%',
                    'speed': 'Fast',
                    'best_for': 'Printed text, receipts, simple documents'
                },
                'google_vision': {
                    'free_tier': '1,000 pages/month',
                    'paid_tier': '$1.50 per 1,000 pages',
                    'accuracy': '95-99%',
                    'speed': 'Fast',
                    'best_for': 'Handwriting, complex layouts, multiple languages'
                }
            },
            'supported_formats': list(ALLOWED_EXTENSIONS),
            'max_file_size_mb': 25
        }), 200
        
    except Exception as e:
        logger.error(f"OCR status error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ocr_bp.route('/ocr/health', methods=['GET'])
def ocr_health_check():
    """Quick health check for OCR service"""
    try:
        ocr_engine = get_ocr_engine()
        status = ocr_engine.get_status()
        
        engines = status['engines_available']
        
        if engines['tesseract'] or engines['google_vision']:
            return jsonify({
                'success': True,
                'status': 'operational',
                'engines': engines,
                'message': 'OCR service is ready'
            }), 200
        else:
            return jsonify({
                'success': False,
                'status': 'no_engines',
                'message': 'No OCR engines available',
                'setup_required': True,
                'instructions': {
                    'tesseract': 'Install: sudo apt-get install tesseract-ocr (FREE)',
                    'google_vision': 'Set GOOGLE_APPLICATION_CREDENTIALS env var (Premium)'
                }
            }), 503
            
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'error': str(e)
        }), 500
