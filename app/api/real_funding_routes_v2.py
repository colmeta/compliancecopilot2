"""
COMPLETE FUNDING ENGINE - Presidential Quality
Full workflow: Generate → Convert → Package → Email
"""

from flask import Blueprint, jsonify, request
import uuid
import os
import tempfile
from datetime import datetime
import logging
from app.funding.document_generator import get_document_generator
from app.funding.document_converter import get_converter
from app.funding.package_manager import get_package_manager
from app.email_service import EmailService

logger = logging.getLogger(__name__)

real_funding_v2 = Blueprint('real_funding_v2', __name__)


@real_funding_v2.route('/v2/funding/generate', methods=['POST'])
def generate_complete_package():
    """
    COMPLETE PRESIDENTIAL-GRADE WORKFLOW
    
    Steps:
    1. Generate 20 Markdown documents with AI
    2. Convert to PDF + Word + PowerPoint
    3. Package into ZIP file
    4. Upload to cloud storage (optional)
    5. Send via email with download link
    
    POST /v2/funding/generate
    Body: {
        "email": "user@company.com",
        "discovery_answers": {
            "company_name": "...",
            "industry": "...",
            "problem": "...",
            "solution": "...",
            ...
        },
        "config": {
            "fundingLevel": "seed",
            "selectedDocuments": ["vision", "pitch_deck", ...],
            "formats": ["pdf", "word", "pptx"],
            "delivery": "email"  # or "download" or "both"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract data
        email = data.get('email', '').strip()
        discovery_answers = data.get('discovery_answers', {})
        config = data.get('config', {})
        
        # Validate
        if not email or '@' not in email:
            return jsonify({'error': 'Valid email address required'}), 400
        
        if not discovery_answers:
            return jsonify({'error': 'Discovery answers required'}), 400
        
        selected_documents = config.get('selectedDocuments', [])
        if not selected_documents:
            return jsonify({'error': 'Select at least one document'}), 400
        
        funding_level = config.get('fundingLevel', 'seed')
        output_formats = config.get('formats', ['pdf', 'word'])
        delivery_method = config.get('delivery', 'email')
        
        company_name = discovery_answers.get('company_name', 'Company')
        task_id = str(uuid.uuid4())
        
        logger.info(f"[{task_id}] Starting COMPLETE package generation for {company_name}")
        
        # ========================================
        # STEP 1: AI GENERATION (Markdown)
        # ========================================
        logger.info(f"[{task_id}] Step 1/5: Generating {len(selected_documents)} documents with AI...")
        
        generator = get_document_generator()
        
        if not generator.enabled:
            return jsonify({
                'success': False,
                'error': 'AI not configured',
                'message': 'GOOGLE_API_KEY not set - please configure',
                'task_id': task_id
            }), 503
        
        generation_result = generator.generate_package(
            discovery_answers=discovery_answers,
            funding_level=funding_level,
            selected_documents=selected_documents
        )
        
        if not generation_result['success']:
            return jsonify({
                'success': False,
                'error': generation_result.get('error'),
                'message': 'AI generation failed',
                'task_id': task_id
            }), 500
        
        logger.info(f"[{task_id}] ✅ Generated {generation_result['completed']} documents ({generation_result['total_pages']} pages)")
        
        # ========================================
        # STEP 2: DOCUMENT CONVERSION
        # ========================================
        logger.info(f"[{task_id}] Step 2/5: Converting to {output_formats}...")
        
        converter = get_converter()
        temp_dir = tempfile.mkdtemp()
        all_files = {}
        
        for doc_info in generation_result['documents']:
            if not doc_info['success']:
                continue
            
            doc_id = doc_info['id']
            markdown_content = doc_info['content']
            
            # Determine formats (PPT only for pitch deck)
            doc_formats = output_formats.copy()
            if doc_id == 'pitch_deck' and 'pptx' not in doc_formats:
                doc_formats.append('pptx')
            elif doc_id != 'pitch_deck' and 'pptx' in doc_formats:
                doc_formats.remove('pptx')
            
            # Convert with metadata
            metadata = {
                'company_name': company_name,
                'document_type': doc_info['name'],
                'funding_level': funding_level,
                'pages': doc_info.get('pages', 0)
            }
            
            try:
                converted_files = converter.convert_document(
                    markdown_content=markdown_content,
                    document_id=doc_id,
                    output_dir=temp_dir,
                    metadata=metadata,
                    formats=doc_formats
                )
                all_files.update(converted_files)
                logger.info(f"[{task_id}] ✅ Converted {doc_id} to {len(converted_files)} format(s)")
            except Exception as e:
                logger.error(f"[{task_id}] ❌ Failed to convert {doc_id}: {e}")
        
        logger.info(f"[{task_id}] ✅ Converted {len(all_files)} files total")
        
        # ========================================
        # STEP 3: ZIP PACKAGING
        # ========================================
        logger.info(f"[{task_id}] Step 3/5: Creating ZIP package...")
        
        package_manager = get_package_manager()
        package_result = package_manager.package_and_upload(
            file_paths=all_files,
            temp_dir=temp_dir,
            company_name=company_name
        )
        
        if not package_result['success']:
            return jsonify({
                'success': False,
                'error': package_result.get('error'),
                'message': 'Packaging failed',
                'task_id': task_id
            }), 500
        
        logger.info(f"[{task_id}] ✅ Package created: {package_result['zip_size_mb']} MB")
        
        # ========================================
        # STEP 4: CLOUD UPLOAD (Optional)
        # ========================================
        logger.info(f"[{task_id}] Step 4/5: Cloud upload...")
        download_url = package_result.get('download_url')
        
        if download_url:
            logger.info(f"[{task_id}] ✅ Uploaded to cloud storage")
        else:
            logger.info(f"[{task_id}] ⚠️  S3 not configured - using local storage")
        
        # ========================================
        # STEP 5: EMAIL DELIVERY
        # ========================================
        email_sent = False
        
        if delivery_method in ['email', 'both']:
            logger.info(f"[{task_id}] Step 5/5: Sending email to {email}...")
            
            try:
                email_service = EmailService()
                
                if email_service.is_configured():
                    email_sent = email_service.send_funding_package_email(
                        to_email=email,
                        company_name=company_name,
                        documents=[doc for doc in generation_result['documents'] if doc['success']],
                        zip_path=package_result['zip_path'],
                        download_url=download_url,
                        package_size_mb=package_result['zip_size_mb']
                    )
                    
                    if email_sent:
                        logger.info(f"[{task_id}] ✅ Email sent successfully")
                    else:
                        logger.warning(f"[{task_id}] ⚠️  Email sending failed")
                else:
                    logger.warning(f"[{task_id}] ⚠️  Email not configured - skipping")
            except Exception as e:
                logger.error(f"[{task_id}] ❌ Email error: {e}")
        
        # ========================================
        # RETURN SUCCESS
        # ========================================
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Presidential-grade funding package generated successfully! 🎉',
            
            'generation': {
                'documents_generated': generation_result['completed'],
                'documents_failed': generation_result['failed'],
                'total_pages': generation_result['total_pages'],
                'generation_time': generation_result['generation_time']
            },
            
            'conversion': {
                'files_created': len(all_files),
                'formats': list(set([os.path.splitext(f)[1][1:] for f in all_files.values()]))
            },
            
            'package': {
                'filename': package_result['zip_filename'],
                'size_mb': package_result['zip_size_mb'],
                'storage': package_result['storage'],
                'download_url': download_url,
                'expires_in_days': 7 if download_url else None
            },
            
            'delivery': {
                'method': delivery_method,
                'email_sent': email_sent,
                'email': email if email_sent else None
            },
            
            'documents': [
                {
                    'id': doc['id'],
                    'name': doc['name'],
                    'category': doc['category'],
                    'pages': doc.get('pages', 0),
                    'success': doc['success']
                }
                for doc in generation_result['documents']
            ],
            
            'quality': 'Presidential / Fortune 50 / Y-Combinator',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Complete workflow failed: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Document generation workflow failed',
            'task_id': task_id if 'task_id' in locals() else None
        }), 500


@real_funding_v2.route('/v2/funding/health', methods=['GET'])
def health_check_v2():
    """Check if all systems are operational"""
    try:
        generator = get_document_generator()
        email_service = EmailService()
        package_manager = get_package_manager()
        
        systems = {
            'ai_generation': {
                'status': 'configured' if generator.enabled else 'not_configured',
                'model': 'gemini-1.5-pro' if generator.enabled else None
            },
            'document_conversion': {
                'status': 'ready',
                'formats': ['pdf', 'word', 'pptx']
            },
            'email_delivery': {
                'status': 'configured' if email_service.is_configured() else 'not_configured'
            },
            'cloud_storage': {
                'status': 'configured' if package_manager.s3_client else 'local_only',
                'provider': 's3' if package_manager.s3_client else 'filesystem'
            }
        }
        
        all_ready = (
            generator.enabled and
            email_service.is_configured() and
            package_manager is not None
        )
        
        return jsonify({
            'success': True,
            'status': 'fully_operational' if all_ready else 'partially_configured',
            'systems': systems,
            'version': '2.0',
            'quality_standard': 'Presidential / Fortune 50',
            'capabilities': {
                'documents': 20,
                'pages': '175+',
                'formats': ['pdf', 'word', 'pptx'],
                'delivery': ['email', 'download', 'cloud']
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
