"""
Extended Diagnostics - Check what's actually running
"""

from flask import Blueprint, jsonify
import os
import sys

diagnostics_extended = Blueprint('diagnostics_extended', __name__)

@diagnostics_extended.route('/system/diagnostics', methods=['GET'])
def extended_diagnostics():
    """
    Complete system diagnostic
    Shows what code is actually running
    """
    
    try:
        # Check if multi-provider exists
        try:
            from app.ai.multi_provider_engine import get_multi_provider
            multi_provider_exists = True
            try:
                mp = get_multi_provider()
                providers = mp.get_available_providers()
                provider_count = len(providers)
            except Exception as e:
                providers = []
                provider_count = 0
        except ImportError:
            multi_provider_exists = False
            providers = []
            provider_count = 0
        
        # Check environment variables
        env_vars = {
            'ANTHROPIC_API_KEY': bool(os.getenv('ANTHROPIC_API_KEY')),
            'GROQ_API_KEY': bool(os.getenv('GROQ_API_KEY')),
            'OPENAI_API_KEY': bool(os.getenv('OPENAI_API_KEY')),
            'GOOGLE_API_KEY': bool(os.getenv('GOOGLE_API_KEY')),
        }
        
        # Check Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        # Get git commit (if available)
        try:
            import subprocess
            git_commit = subprocess.check_output(
                ['git', 'rev-parse', '--short', 'HEAD'],
                cwd='/opt/render/project/src',
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except:
            git_commit = "unknown"
        
        return jsonify({
            'success': True,
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'system': {
                'python_version': python_version,
                'git_commit': git_commit,
            },
            'code_status': {
                'multi_provider_exists': multi_provider_exists,
                'provider_count': provider_count,
                'providers_available': providers,
            },
            'environment': {
                'api_keys_set': env_vars,
                'keys_count': sum(env_vars.values()),
            },
            'verdict': {
                'multi_provider_deployed': multi_provider_exists and provider_count > 0,
                'ready_for_production': multi_provider_exists and provider_count >= 1,
                'recommendation': 'DEPLOY NEW CODE' if not multi_provider_exists else 'ALL GOOD'
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Diagnostic failed'
        }), 500
