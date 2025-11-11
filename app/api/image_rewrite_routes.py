"""
IMAGE TEXT REWRITE - COMPLETE WORKING ENDPOINT
Upload image → Extract text → Rewrite with AI
"""

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
import logging
import os
import tempfile
import time

logger = logging.getLogger(__name__)

image_rewrite = Blueprint('image_rewrite', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'tiff', 'bmp', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@image_rewrite.route('/image/rewrite', methods=['POST'])
def rewrite_image_text():
    """
    Upload image with text → Extract → Rewrite
    
    POST /image/rewrite
    Content-Type: multipart/form-data
    
    Form Data:
    - file: Image file (required)
    - directive: How to rewrite (optional, default: "Rewrite this text professionally")
    
    Response:
    {
        "success": true,
        "original_text": "text from image",
        "rewritten_text": "rewritten version",
        "processing_time": 2.3
    }
    """
    start_time = time.time()
    
    try:
        # 1. CHECK FILE UPLOAD
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded',
                'message': 'Please upload an image file'
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
                'message': f'Allowed: {", ".join(ALLOWED_EXTENSIONS)}',
                'allowed_extensions': list(ALLOWED_EXTENSIONS)
            }), 400
        
        # Get directive
        directive = request.form.get('directive', 'Rewrite this text professionally and clearly')
        
        logger.info(f"📸 Image rewrite: {file.filename}, directive: {directive}")
        
        # 2. EXTRACT TEXT FROM IMAGE
        try:
            from app.ocr.ocr_engine import get_ocr_engine
            ocr_engine = get_ocr_engine()
            
            # Read file
            file_data = file.read()
            
            # Save temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
                tmp.write(file_data)
                tmp_path = tmp.name
            
            try:
                # Extract text
                extracted_text = ocr_engine.extract_text(tmp_path)
                
                if not extracted_text or extracted_text.strip() == '':
                    return jsonify({
                        'success': False,
                        'error': 'No text found in image',
                        'message': 'Could not extract any text from the image. Please ensure the image contains readable text.',
                        'processing_time': time.time() - start_time
                    }), 400
                
                logger.info(f"✅ Extracted text: {len(extracted_text)} characters")
                
            finally:
                # Clean up temp file
                try:
                    os.unlink(tmp_path)
                except:
                    pass
        
        except Exception as ocr_error:
            logger.error(f"OCR failed: {ocr_error}")
            return jsonify({
                'success': False,
                'error': 'OCR extraction failed',
                'message': str(ocr_error),
                'processing_time': time.time() - start_time
            }), 500
        
        # 3. REWRITE TEXT WITH AI
        try:
            # Try multi-provider first
            try:
                from app.ai.multi_provider_engine import get_multi_provider
                
                ai = get_multi_provider()
                
                prompt = f"""You are a professional text rewriter.

ORIGINAL TEXT:
{extracted_text}

DIRECTIVE: {directive}

Rewrite the text according to the directive. Return ONLY the rewritten text, nothing else."""
                
                rewritten_text, metadata = ai.generate(
                    prompt=prompt,
                    max_tokens=2000,
                    temperature=0.7
                )
                
                provider_used = metadata.get('provider', 'multi-provider')
                model_used = metadata.get('model', 'unknown')
                
                logger.info(f"✅ Rewrite complete: {provider_used}/{model_used}")
                
            except ImportError:
                # Fallback to old Gemini if multi-provider not deployed yet
                import google.generativeai as genai
                
                api_key = os.getenv('GOOGLE_API_KEY')
                if not api_key:
                    raise Exception("No AI provider available. Set GOOGLE_API_KEY or deploy multi-provider system.")
                
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-pro')
                
                prompt = f"""You are a professional text rewriter.

ORIGINAL TEXT:
{extracted_text}

DIRECTIVE: {directive}

Rewrite the text according to the directive. Return ONLY the rewritten text, nothing else."""
                
                response = model.generate_content(prompt)
                rewritten_text = response.text
                provider_used = 'gemini'
                model_used = 'gemini-pro'
                
                logger.info(f"✅ Rewrite complete (fallback): {provider_used}")
        
        except Exception as ai_error:
            logger.error(f"AI rewrite failed: {ai_error}")
            return jsonify({
                'success': False,
                'error': 'AI rewrite failed',
                'message': str(ai_error),
                'original_text': extracted_text,  # Still return extracted text
                'processing_time': time.time() - start_time
            }), 500
        
        # 4. SUCCESS RESPONSE
        processing_time = time.time() - start_time
        
        return jsonify({
            'success': True,
            'original_text': extracted_text,
            'original_length': len(extracted_text),
            'rewritten_text': rewritten_text,
            'rewritten_length': len(rewritten_text),
            'directive': directive,
            'provider': provider_used,
            'model': model_used,
            'processing_time': round(processing_time, 2),
            'message': '✅ Image text successfully rewritten'
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Image rewrite error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred processing your request',
            'processing_time': time.time() - start_time
        }), 500


@image_rewrite.route('/image/rewrite/health', methods=['GET'])
def image_rewrite_health():
    """Check if service is ready"""
    
    # Check OCR
    ocr_available = False
    ocr_engine = None
    try:
        from app.ocr.ocr_engine import get_ocr_engine
        ocr_engine = get_ocr_engine()
        ocr_available = True
    except:
        pass
    
    # Check AI
    ai_available = False
    ai_providers = []
    try:
        from app.ai.multi_provider_engine import get_multi_provider
        ai = get_multi_provider()
        ai_providers = ai.get_available_providers()
        ai_available = len(ai_providers) > 0
    except:
        # Check fallback Gemini
        if os.getenv('GOOGLE_API_KEY'):
            ai_available = True
            ai_providers = ['gemini']
    
    ready = ocr_available and ai_available
    
    return jsonify({
        'service': 'Image Text Rewrite',
        'ready': ready,
        'ocr': {
            'available': ocr_available,
            'engine': 'tesseract' if ocr_engine else 'none'
        },
        'ai': {
            'available': ai_available,
            'providers': ai_providers,
            'count': len(ai_providers)
        },
        'status': 'ready' if ready else 'not_configured',
        'message': '✅ Ready to rewrite image text' if ready else '❌ OCR or AI not configured'
    }), 200 if ready else 503


@image_rewrite.route('/image/rewrite/test', methods=['GET'])
def test_service():
    """Test page - upload image and see result"""
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CLARITY - Image Text Rewrite</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
            }
            input, textarea, button {
                width: 100%;
                margin: 10px 0;
                padding: 10px;
                font-size: 16px;
            }
            button {
                background: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            button:hover {
                background: #0056b3;
            }
            .result {
                margin-top: 20px;
                padding: 20px;
                background: #f0f0f0;
                border-radius: 5px;
            }
            .success {
                background: #d4edda;
                color: #155724;
            }
            .error {
                background: #f8d7da;
                color: #721c24;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📸 Image Text Rewrite</h1>
            <p>Upload an image with text, and AI will rewrite it for you.</p>
            
            <form id="uploadForm">
                <div>
                    <label>Select Image:</label>
                    <input type="file" id="fileInput" accept="image/*" required>
                </div>
                
                <div>
                    <label>Rewrite Directive (optional):</label>
                    <textarea id="directive" rows="3" placeholder="E.g., 'Make this more professional and concise'">Rewrite this text professionally and clearly</textarea>
                </div>
                
                <button type="submit">🚀 Extract & Rewrite</button>
            </form>
            
            <div id="result"></div>
        </div>
        
        <script>
            document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const fileInput = document.getElementById('fileInput');
                const directive = document.getElementById('directive').value;
                const resultDiv = document.getElementById('result');
                
                if (!fileInput.files[0]) {
                    alert('Please select an image');
                    return;
                }
                
                // Show loading
                resultDiv.innerHTML = '<div class="result">⏳ Processing... (OCR + AI rewrite may take 5-10 seconds)</div>';
                
                // Prepare form data
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                formData.append('directive', directive);
                
                try {
                    const response = await fetch('/image/rewrite', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        resultDiv.innerHTML = `
                            <div class="result success">
                                <h3>✅ Success!</h3>
                                <p><strong>Original Text:</strong></p>
                                <p>${data.original_text}</p>
                                <hr>
                                <p><strong>Rewritten Text:</strong></p>
                                <p>${data.rewritten_text}</p>
                                <hr>
                                <small>Provider: ${data.provider} | Model: ${data.model} | Time: ${data.processing_time}s</small>
                            </div>
                        `;
                    } else {
                        resultDiv.innerHTML = `
                            <div class="result error">
                                <h3>❌ Error</h3>
                                <p>${data.message || data.error}</p>
                            </div>
                        `;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `
                        <div class="result error">
                            <h3>❌ Failed to Fetch</h3>
                            <p>Could not connect to server. Error: ${error.message}</p>
                            <p>Backend might be hibernating. Try again in 30 seconds.</p>
                        </div>
                    `;
                }
            });
        </script>
    </body>
    </html>
    """
    
    return html, 200
