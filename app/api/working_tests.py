"""
WORKING TEST ENDPOINTS - Guaranteed to work for immediate testing
No dependencies, no complications, just working endpoints
"""

from flask import Blueprint, jsonify, request
import logging
from datetime import datetime

working = Blueprint('working', __name__)
logger = logging.getLogger(__name__)


@working.route('/working/ping', methods=['GET'])
def ping():
    """Simple ping test"""
    return jsonify({
        'success': True,
        'message': 'Ferrari is alive!',
        'timestamp': datetime.now().isoformat()
    }), 200


@working.route('/working/echo', methods=['POST'])
def echo():
    """Echo back whatever you send"""
    data = request.get_json() or {}
    return jsonify({
        'success': True,
        'message': 'Echo test working',
        'you_sent': data,
        'timestamp': datetime.now().isoformat()
    }), 200


@working.route('/working/ai-simple', methods=['POST'])
def simple_ai_test():
    """Test AI with simplest possible call"""
    try:
        import os
        import google.generativeai as genai
        
        api_key = os.getenv('GOOGLE_API_KEY')
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'GOOGLE_API_KEY not set'
            }), 503
        
        # Configure and test
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        data = request.get_json() or {}
        prompt = data.get('prompt', 'Say hello')
        
        response = model.generate_content(prompt)
        
        return jsonify({
            'success': True,
            'message': 'AI is working!',
            'prompt': prompt,
            'response': response.text,
            'model': 'gemini-1.5-flash'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'AI test failed'
        }), 500


@working.route('/working/routes-count', methods=['GET'])
def count_routes():
    """Count how many routes are registered"""
    from flask import current_app
    
    routes = list(current_app.url_map.iter_rules())
    
    # Group by blueprint
    by_blueprint = {}
    for rule in routes:
        bp = rule.endpoint.split('.')[0] if '.' in rule.endpoint else 'main'
        if bp not in by_blueprint:
            by_blueprint[bp] = 0
        by_blueprint[bp] += 1
    
    return jsonify({
        'success': True,
        'total_routes': len(routes),
        'by_blueprint': by_blueprint,
        'has_real_ai': any('real_analysis' in rule.endpoint for rule in routes),
        'has_v2_funding': any('real_funding_v2' in rule.endpoint for rule in routes),
        'has_ocr': any('ocr' in rule.endpoint for rule in routes)
    }), 200
