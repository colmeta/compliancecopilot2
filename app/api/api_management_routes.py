# ==============================================================================
# app/api/api_management_routes.py
# API Key Management for Clients
# ==============================================================================
"""
API Key Management System for CLARITY

This module provides:
- API key generation for clients
- API key listing and management
- Usage statistics per API key
- API documentation
"""

from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from app import db
from app.models import APIKey, User
from datetime import datetime

api_mgmt = Blueprint('api_mgmt', __name__, url_prefix='/api-management')


@api_mgmt.route('/dashboard')
@login_required
def dashboard():
    """API Management Dashboard."""
    user_keys = APIKey.query.filter_by(user_id=current_user.id).all()
    
    return render_template(
        'api_management/dashboard.html',
        api_keys=user_keys,
        user=current_user
    )


@api_mgmt.route('/generate-key', methods=['POST'])
@login_required
def generate_key():
    """Generate a new API key for the current user."""
    try:
        # Generate new API key
        new_key, hashed_key = APIKey.generate_key()
        
        # Create API key record
        api_key_record = APIKey(user_id=current_user.id)
        api_key_record.key_hash = hashed_key
        api_key_record.created_at = datetime.utcnow()
        api_key_record.is_active = True
        
        db.session.add(api_key_record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'api_key': new_key,  # Only shown once!
            'key_id': api_key_record.id,
            'message': 'API key generated successfully. Save it now - it will not be shown again!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_mgmt.route('/revoke-key/<int:key_id>', methods=['POST'])
@login_required
def revoke_key(key_id):
    """Revoke an API key."""
    try:
        api_key = APIKey.query.filter_by(
            id=key_id,
            user_id=current_user.id
        ).first()
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key not found'
            }), 404
        
        api_key.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'API key revoked successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_mgmt.route('/test-key', methods=['POST'])
@login_required
def test_key():
    """Test an API key."""
    data = request.get_json()
    test_key = data.get('api_key')
    
    if not test_key:
        return jsonify({
            'success': False,
            'error': 'No API key provided'
        }), 400
    
    # Check if key is valid
    active_keys = APIKey.query.filter_by(is_active=True).all()
    
    for key_record in active_keys:
        if key_record.check_key(test_key):
            return jsonify({
                'success': True,
                'valid': True,
                'user_id': key_record.user_id,
                'created_at': key_record.created_at.isoformat()
            })
    
    return jsonify({
        'success': True,
        'valid': False,
        'message': 'Invalid or inactive API key'
    })


@api_mgmt.route('/documentation')
def documentation():
    """API Documentation page."""
    return render_template('api_management/documentation.html')
