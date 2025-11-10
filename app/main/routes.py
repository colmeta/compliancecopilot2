# =======================================================
# app/main/routes.py -- COMPLETE VERSION WITH DASHBOARD & API KEY MANAGEMENT
# =======================================================
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import APIKey, FinalizedBriefing
import json

main = Blueprint('main', __name__)

@main.route('/')
def homepage():
    """API root - Returns JSON (frontend on Vercel)"""
    try:
        return jsonify({
            'name': 'CLARITY Engine API',
            'version': '5.0',
            'status': 'live',
            'features': ['multi_llm', 'funding_engine', 'outstanding_writing', 'ocr', 'expense_mgmt'],
            'frontend_url': 'https://clarity-frontend.vercel.app',
            'health': '/health',
            'docs': '/api/docs'
        }), 200
    except Exception as e:
        return jsonify({'error': 'Root route failed', 'details': str(e)}), 500

@main.route('/dashboard')
@login_required
def dashboard():
    """Fortune 50 Command Deck - Main dashboard"""
    # Get all API keys for the current user
    api_keys = APIKey.query.filter_by(user_id=current_user.id).order_by(APIKey.created_at.desc()).all()
    return render_template('dashboard_presidential.html', api_keys=api_keys)

@main.route('/analysis')
@login_required
def analysis():
    """CLARITY analysis interface."""
    return render_template('analysis.html')

@main.route('/about')
@login_required
def about():
    """About CLARITY Engine page."""
    return render_template('about.html')

@main.route('/vault')
@login_required
def vault():
    """Intelligence Vault management page."""
    return render_template('vault.html')

@main.route('/funding')
@login_required
def funding():
    """Funding Readiness Engine - Presidential Interface"""
    return render_template('funding_interface.html')

@main.route('/dashboard/generate-key', methods=['POST'])
@login_required
def generate_key():
    """Generate a new API key for the current user."""
    try:
        # Generate new API key
        new_key_str, hashed_key = APIKey.generate_key()
        
        # Create new API key record
        new_api_key = APIKey(user_id=current_user.id)
        new_api_key.key_hash = hashed_key
        
        db.session.add(new_api_key)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'api_key': new_key_str,
            'message': 'API key generated successfully'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/dashboard/revoke-key/<int:key_id>', methods=['POST'])
@login_required
def revoke_key(key_id):
    """Revoke an API key (set is_active=False)."""
    try:
        # Find the key and verify it belongs to current user
        api_key = APIKey.query.filter_by(id=key_id, user_id=current_user.id).first()
        
        if not api_key:
            flash('API key not found or access denied', 'error')
            return redirect(url_for('main.dashboard'))
        
        # Revoke the key
        api_key.is_active = False
        db.session.commit()
        
        flash('API key revoked successfully', 'success')
        return redirect(url_for('main.dashboard'))
        
    except Exception as e:
        flash(f'Error revoking API key: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

@main.route('/briefings')
@login_required
def view_briefings():
    """View all finalized briefings for the current user."""
    try:
        # Get all finalized briefings for the current user, ordered by most recent
        briefings = FinalizedBriefing.query.filter_by(user_id=current_user.id)\
                                          .order_by(FinalizedBriefing.timestamp.desc())\
                                          .all()
        
        # Parse the JSON content for each briefing
        parsed_briefings = []
        for briefing in briefings:
            try:
                content = json.loads(briefing.final_content)
                parsed_briefings.append({
                    'id': briefing.id,
                    'job_id': briefing.original_job_id,
                    'timestamp': briefing.timestamp,
                    'content': content
                })
            except json.JSONDecodeError:
                # Skip briefings with invalid JSON
                continue
        
        return render_template('briefings.html', briefings=parsed_briefings)
        
    except Exception as e:
        flash(f'Error loading briefings: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

@main.route('/briefings/<int:briefing_id>')
@login_required
def view_briefing(briefing_id):
    """View a specific finalized briefing."""
    try:
        # Find the briefing and verify it belongs to current user
        briefing = FinalizedBriefing.query.filter_by(id=briefing_id, user_id=current_user.id).first()
        
        if not briefing:
            flash('Briefing not found or access denied', 'error')
            return redirect(url_for('main.view_briefings'))
        
        # Parse the JSON content
        content = json.loads(briefing.final_content)
        
        return render_template('briefing_detail.html', briefing=briefing, content=content)
        
    except Exception as e:
        flash(f'Error loading briefing: {str(e)}', 'error')
        return redirect(url_for('main.view_briefings'))
