"""
FERRARI DIAGNOSTICS - See exactly what's registered
"""

from flask import Blueprint, jsonify, current_app
import sys
import os

diagnostics = Blueprint('diagnostics', __name__)


@diagnostics.route('/diagnostics/routes', methods=['GET'])
def list_all_routes():
    """List ALL registered routes in the app"""
    routes = []
    for rule in current_app.url_map.iter_rules():
        if rule.endpoint != 'static':
            routes.append({
                'path': rule.rule,
                'methods': list(rule.methods - {'HEAD', 'OPTIONS'}),
                'endpoint': rule.endpoint
            })
    
    routes.sort(key=lambda x: x['path'])
    
    return jsonify({
        'success': True,
        'total_routes': len(routes),
        'routes': routes
    }), 200


@diagnostics.route('/diagnostics/blueprints', methods=['GET'])
def list_blueprints():
    """List ALL registered blueprints"""
    blueprints = {}
    for name, blueprint in current_app.blueprints.items():
        blueprints[name] = {
            'name': name,
            'import_name': blueprint.import_name,
            'url_prefix': blueprint.url_prefix
        }
    
    return jsonify({
        'success': True,
        'total_blueprints': len(blueprints),
        'blueprints': blueprints
    }), 200


@diagnostics.route('/diagnostics/env', methods=['GET'])
def check_environment():
    """Check critical environment variables (without exposing secrets)"""
    env_status = {
        'GOOGLE_API_KEY': bool(os.getenv('GOOGLE_API_KEY')),
        'MAIL_USERNAME': bool(os.getenv('MAIL_USERNAME')),
        'MAIL_PASSWORD': bool(os.getenv('MAIL_PASSWORD')),
        'DATABASE_URL': bool(os.getenv('DATABASE_URL')),
        'AWS_ACCESS_KEY_ID': bool(os.getenv('AWS_ACCESS_KEY_ID')),
        'GOOGLE_APPLICATION_CREDENTIALS': bool(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
    }
    
    return jsonify({
        'success': True,
        'environment': env_status,
        'python_version': sys.version,
        'platform': sys.platform
    }), 200


@diagnostics.route('/diagnostics/modules', methods=['GET'])
def check_modules():
    """Check if critical Python modules are importable"""
    modules_to_check = [
        'google.generativeai',
        'reportlab',
        'docx',
        'pptx',
        'markdown2',
        'pytesseract',
        'PIL',
        'boto3'
    ]
    
    results = {}
    for module_name in modules_to_check:
        try:
            __import__(module_name)
            results[module_name] = 'installed'
        except ImportError:
            results[module_name] = 'missing'
    
    return jsonify({
        'success': True,
        'modules': results
    }), 200


@diagnostics.route('/diagnostics/full', methods=['GET'])
def full_diagnostics():
    """Complete system diagnostic"""
    return jsonify({
        'success': True,
        'message': 'Ferrari full diagnostic',
        'checks': {
            'routes': f'/diagnostics/routes',
            'blueprints': f'/diagnostics/blueprints',
            'environment': f'/diagnostics/env',
            'modules': f'/diagnostics/modules'
        }
    }), 200
