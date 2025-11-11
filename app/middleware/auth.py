"""
API Key Authentication Middleware
"""

import os
from functools import wraps
from flask import request, jsonify

def require_api_key(f):
    """
    Decorator to require API key for protected routes
    
    Usage:
        @app.route('/protected')
        @require_api_key
        def protected_route():
            return jsonify({'message': 'Access granted'})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get expected API key from environment
        expected_key = os.getenv('CLARITY_API_KEY')
        
        # If no key is set in environment, allow access (backward compatible)
        if not expected_key:
            return f(*args, **kwargs)
        
        # Get API key from request headers
        provided_key = request.headers.get('X-API-KEY') or request.headers.get('Authorization')
        
        # Remove "Bearer " prefix if present
        if provided_key and provided_key.startswith('Bearer '):
            provided_key = provided_key[7:]
        
        # Check if key matches
        if provided_key != expected_key:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Valid API key required',
                'status': 401
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function
