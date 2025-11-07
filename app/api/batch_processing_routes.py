"""
CLARITY Batch Processing - Process 100+ Documents at Once
Perfect for digitizing paper archives
"""

from flask import Blueprint, jsonify, request
import uuid
import logging
from datetime import datetime
from app.ocr.ocr_engine import get_ocr_engine
from app.vault.document_vault import get_document_vault

batch_bp = Blueprint('batch', __name__)
logger = logging.getLogger(__name__)


@batch_bp.route('/batch/scan', methods=['POST'])
def batch_scan_documents():
    """
    Batch scan multiple documents at once
    
    POST /batch/scan
    Form Data:
    - files[]: Multiple image/PDF files
    - user_id: User ID
    - category: Category for all documents
    - auto_categorize: Auto-categorize each document (default: false)
    
    Response:
    {
        "success": true,
        "batch_id": "batch_xxx",
        "total_files": 50,
        "processed": 48,
        "failed": 2,
        "results": [...]
    }
    """
    try:
        if 'files[]' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No files uploaded'
            }), 400
        
        files = request.files.getlist('files[]')
        user_id = request.form.get('user_id', 'default')
        category = request.form.get('category', 'uncategorized')
        auto_categorize = request.form.get('auto_categorize', 'false').lower() == 'true'
        
        batch_id = f"batch_{uuid.uuid4().hex[:12]}"
        
        logger.info(f"📦 Starting batch scan: {len(files)} files")
        
        ocr_engine = get_ocr_engine()
        vault = get_document_vault()
        
        results = []
        processed = 0
        failed = 0
        
        for idx, file in enumerate(files, 1):
            logger.info(f"Processing {idx}/{len(files)}: {file.filename}")
            
            try:
                # OCR extraction
                file_data = file.read()
                ocr_result = ocr_engine.extract_text(file_data)
                
                if ocr_result['success']:
                    # Store in vault
                    vault_result = vault.store_document(
                        file_data=file_data,
                        filename=file.filename,
                        user_id=user_id,
                        ocr_text=ocr_result['text'],
                        category=category,
                        metadata={
                            'batch_id': batch_id,
                            'ocr_confidence': ocr_result['confidence'],
                            'ocr_engine': ocr_result['engine']
                        }
                    )
                    
                    if vault_result['success']:
                        results.append({
                            'file': file.filename,
                            'status': 'success',
                            'document_id': vault_result['document_id'],
                            'text_preview': ocr_result['text'][:200] + '...' if len(ocr_result['text']) > 200 else ocr_result['text'],
                            'confidence': ocr_result['confidence']
                        })
                        processed += 1
                    else:
                        results.append({
                            'file': file.filename,
                            'status': 'failed',
                            'error': 'Vault storage failed'
                        })
                        failed += 1
                else:
                    results.append({
                        'file': file.filename,
                        'status': 'failed',
                        'error': 'OCR failed'
                    })
                    failed += 1
                    
            except Exception as e:
                logger.error(f"File processing failed: {e}")
                results.append({
                    'file': file.filename,
                    'status': 'failed',
                    'error': str(e)
                })
                failed += 1
        
        logger.info(f"✅ Batch complete: {processed}/{len(files)} successful")
        
        return jsonify({
            'success': True,
            'batch_id': batch_id,
            'total_files': len(files),
            'processed': processed,
            'failed': failed,
            'success_rate': f"{(processed/len(files)*100):.1f}%",
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@batch_bp.route('/batch/status/<batch_id>', methods=['GET'])
def get_batch_status(batch_id):
    """Get status of batch processing job"""
    # In production, would check database/queue
    return jsonify({
        'success': True,
        'batch_id': batch_id,
        'status': 'completed',
        'message': 'Batch processing complete'
    }), 200
