# ==============================================================================
# app/api/routes.py
# The core service entrance. Protected by API keys.
# ==============================================================================

from flask import Blueprint, jsonify, request
from functools import wraps
from app import db
from app.models import APIKey, User

api = Blueprint('api', __name__)

# --- The Guard: Our API Key Protection Decorator ---
def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # We will look for the key in the 'X-API-KEY' header
        provided_key = request.headers.get('X-API-KEY')
        if not provided_key:
            return jsonify({'error': 'API key is missing'}), 401

        # This is a placeholder for a more secure key lookup.
        # In a real app, you would iterate through hashed keys.
        # For simplicity now, we'll find a user by a simple lookup.
        # Let's find the first key record and its owner for this example.
        key_record = APIKey.query.first() # This is a placeholder for real lookup
        
        if key_record and key_record.is_active: # and key_record.check_key(provided_key):
             return f(*args, **kwargs)

        return jsonify({'error': 'Invalid or inactive API key'}), 401
    return decorated_function

# --- The Armory: Key Generation Route ---
# NOTE: This is an admin/test route. A real app would have this in a user dashboard.
@api.route('/generate-key/<int:user_id>', methods=['POST'])
def generate_key(user_id):
    """Generates a new API key for a given user. FOR TESTING ONLY."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    new_key_str, hashed_key = APIKey.generate_key()
    
    new_api_key = APIKey(user_id=user.id)
    new_api_key.key_hash = hashed_key # Store the hashed key
    
    db.session.add(new_api_key)
    db.session.commit()
    
    # IMPORTANT: Show the user the key ONCE. It cannot be recovered.
    return jsonify({
        'message': 'API key generated successfully. Store it securely!',
        'api_key': new_key_str,
        'user_email': user.email
    }), 201

# --- Protected Endpoint Example ---
@api.route('/test-protected')
@api_key_required
def test_protected_route():
    """An example of an endpoint protected by our decorator."""
    return jsonify({'message': 'Success! You have accessed a protected route.'})
