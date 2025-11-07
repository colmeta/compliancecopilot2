"""
CLARITY Expense Management API
Scan receipts, track spending, optimize costs
"""

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
from app.ocr.ocr_engine import get_ocr_engine
from app.expenses.expense_manager import get_expense_manager
import logging

expense_bp = Blueprint('expenses', __name__)
logger = logging.getLogger(__name__)


@expense_bp.route('/expenses/scan', methods=['POST'])
def scan_receipt():
    """
    Scan receipt and extract expense data
    
    POST /expenses/scan
    Form Data:
    - file: Receipt image (JPG, PNG, PDF)
    - user_id: User/company ID (optional)
    - email: Email to send results (optional)
    
    Response:
    {
        "success": true,
        "expense": {
            "id": "exp_20251106143022",
            "merchant": "Staples",
            "amount": 45.99,
            "date": "2025-11-06",
            "category": "Office Supplies",
            "tax_deductible": true,
            "line_items": [...]
        },
        "recommendations": [...],
        "demo_mode": true (if OCR not configured)
    }
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded',
                'message': 'Please upload a receipt image (JPG, PNG, or PDF)'
            }), 400
        
        file = request.files['file']
        user_id = request.form.get('user_id')
        user_email = request.form.get('email')
        
        # OCR extraction
        ocr_engine = get_ocr_engine()
        file_data = file.read()
        
        logger.info(f"📄 Scanning receipt: {file.filename}")
        ocr_result = ocr_engine.extract_text(file_data)
        
        # Check if in demo mode
        demo_mode = ocr_result.get('demo_mode', False)
        
        # Process receipt
        expense_manager = get_expense_manager()
        result = expense_manager.process_receipt(ocr_result, user_id=user_id)
        
        # Add demo mode flag to response
        if demo_mode:
            result['demo_mode'] = True
            result['message'] = '🎭 Demo mode active - showing sample receipt data. Install Tesseract or Google Vision for real OCR.'
        
        # If email provided, mention that (email sending will be implemented later)
        if user_email:
            result['email'] = user_email
            result['email_note'] = 'Email delivery feature coming soon!'
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Receipt scanning failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Receipt scanning failed. Please try again or contact support.'
        }), 500


@expense_bp.route('/expenses/summary', methods=['GET'])
def get_spending_summary():
    """
    Get spending summary and analytics
    
    GET /expenses/summary?user_id=xxx&days=30
    
    Response:
    {
        "total_expenses": 1234.56,
        "expense_count": 25,
        "average_expense": 49.38,
        "by_category": {...},
        "tax_deductible_total": 987.65,
        "recommendations": [...]
    }
    """
    try:
        user_id = request.args.get('user_id')
        days = int(request.args.get('days', 30))
        
        expense_manager = get_expense_manager()
        summary = expense_manager.get_spending_summary(user_id=user_id, days=days)
        
        return jsonify({
            'success': True,
            'summary': summary
        }), 200
        
    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@expense_bp.route('/expenses/health', methods=['GET'])
def health_check():
    """Health check for expense management system"""
    return jsonify({
        'success': True,
        'status': 'operational',
        'features': [
            'Receipt OCR scanning',
            'Automatic categorization',
            'Spending analytics',
            'Tax deduction tracking',
            'Cost optimization'
        ]
    }), 200
