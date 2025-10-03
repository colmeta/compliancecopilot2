# ==============================================================================
# app/api/setup_routes.py -- TEMPORARY SETUP ENDPOINTS
# These routes allow you to bootstrap your system without shell access.
# DELETE THIS FILE after you've created your first user and API key!
# ==============================================================================

from flask import Blueprint, jsonify, request
from app import db
from app.models import User, APIKey

setup = Blueprint('setup', __name__)

# IMPORTANT SECURITY NOTE:
# These routes are TEMPORARY bootstrapping tools.
# Once you've created your first user and API key:
# 1. Delete this entire file (app/api/setup_routes.py)
# 2. Remove the blueprint registration from app/__init__.py
# 3. Redeploy your app

# ==============================================================================
# TEMPORARY: Create First User
# ==============================================================================
@setup.route('/create-first-user', methods=['POST'])
def create_first_user():
    """
    Creates the first admin user. 
    DELETE THIS ROUTE AFTER FIRST USE!
    
    Usage:
    POST /api/setup/create-first-user
    Body (JSON): {"email": "admin@clarity.ai", "password": "YourSecurePassword123"}
    """
    
    # Check if any users already exist (safety check)
    existing_users = User.query.count()
    if existing_users > 0:
        return jsonify({
            'error': 'Users already exist. This endpoint is disabled for security.',
            'message': 'Delete this route from setup_routes.py'
        }), 403
    
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Missing email or password in request body'}), 400
    
    email = data['email']
    password = data['password']
    
    # Create the user
    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'First user created successfully',
        'user_id': new_user.id,
        'email': new_user.email,
        'next_step': f'Use POST /api/setup/create-first-key with user_id={new_user.id}'
    }), 201


# ==============================================================================
# TEMPORARY: Generate First API Key
# ==============================================================================
@setup.route('/create-first-key', methods=['POST'])
def create_first_key():
    """
    Generates an API key for a user.
    DELETE THIS ROUTE AFTER FIRST USE!
    
    Usage:
    POST /api/setup/create-first-key
    Body (JSON): {"user_id": 1}
    """
    
    data = request.get_json()
    
    if not data or 'user_id' not in data:
        return jsonify({'error': 'Missing user_id in request body'}), 400
    
    user_id = data['user_id']
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': f'User with ID {user_id} not found'}), 404
    
    # Generate the key
    new_key_str, hashed_key = APIKey.generate_key()
    
    new_api_key = APIKey(user_id=user.id)
    new_api_key.key_hash = hashed_key
    
    db.session.add(new_api_key)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '🔑 API KEY GENERATED - SAVE THIS NOW! You will never see it again.',
        'api_key': new_key_str,
        'user_email': user.email,
        'warning': 'Store this key securely. After this response, it cannot be recovered.',
        'next_step': 'Test your key with: POST /api/test-protected with header X-API-KEY'
    }), 201


# ==============================================================================
# System Status Check (Keep this - it's safe)
# ==============================================================================
@setup.route('/system-status', methods=['GET'])
def system_status():
    """
    Check if the system is properly configured.
    This route is safe to keep permanently.
    """
    
    user_count = User.query.count()
    key_count = APIKey.query.count()
    
    return jsonify({
        'status': 'online',
        'database_connected': True,
        'total_users': user_count,
        'total_api_keys': key_count,
        'setup_complete': user_count > 0 and key_count > 0
    }), 200
