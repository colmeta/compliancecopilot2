"""
Simple POST endpoint to diagnose POST request issues
"""

from flask import Blueprint, jsonify, request

post_test = Blueprint('post_test', __name__)


@post_test.route('/test/post', methods=['POST', 'OPTIONS'])
def test_post():
    """Simple POST test - should work if POST requests work at all"""
    if request.method == 'OPTIONS':
        # Handle preflight
        return jsonify({'message': 'CORS preflight OK'}), 200
    
    data = request.get_json(silent=True) or {}
    
    return jsonify({
        'success': True,
        'message': 'POST request working!',
        'you_sent': data,
        'method': request.method,
        'content_type': request.content_type
    }), 200


@post_test.route('/test/post-simple', methods=['POST'])
def test_post_simple():
    """Simplest possible POST endpoint"""
    return jsonify({'status': 'post works'}), 200
