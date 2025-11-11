"""
AI PROVIDERS MANAGEMENT ROUTES
Monitor and manage multi-provider AI system
"""

from flask import Blueprint, jsonify
from app.ai.multi_provider_engine import get_multi_provider
import logging

logger = logging.getLogger(__name__)

ai_providers = Blueprint('ai_providers', __name__)

@ai_providers.route('/ai/providers', methods=['GET'])
def list_providers():
    """List all available AI providers and their status"""
    try:
        multi_ai = get_multi_provider()
        providers = multi_ai.get_provider_info()
        
        return jsonify({
            'success': True,
            'total_providers': len(providers),
            'providers': providers,
            'message': f'{len(providers)} AI providers configured'
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing providers: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_providers.route('/ai/providers/stats', methods=['GET'])
def provider_stats():
    """Get usage statistics for all providers"""
    try:
        multi_ai = get_multi_provider()
        stats = multi_ai.get_stats()
        
        return jsonify({
            'success': True,
            'stats': stats,
            'message': 'Provider statistics retrieved'
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_providers.route('/ai/providers/test', methods=['POST'])
def test_providers():
    """Test all AI providers with a simple prompt"""
    try:
        multi_ai = get_multi_provider()
        
        test_prompt = "Respond with exactly: 'AI provider working correctly.'"
        
        results = []
        for provider_name in multi_ai.get_available_providers():
            try:
                response, metadata = multi_ai.generate(
                    prompt=test_prompt,
                    max_tokens=50,
                    temperature=0,
                    preferred_provider=provider_name
                )
                
                results.append({
                    'provider': provider_name,
                    'status': 'success',
                    'response': response[:100],  # First 100 chars
                    'time_taken': metadata['time_taken'],
                    'model': metadata['model']
                })
            except Exception as e:
                results.append({
                    'provider': provider_name,
                    'status': 'failed',
                    'error': str(e)
                })
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        
        return jsonify({
            'success': True,
            'total_providers': len(results),
            'successful': success_count,
            'results': results,
            'message': f'{success_count}/{len(results)} providers working'
        }), 200
        
    except Exception as e:
        logger.error(f"Error testing providers: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_providers.route('/ai/health', methods=['GET'])
def ai_health():
    """Check if AI system is healthy"""
    try:
        multi_ai = get_multi_provider()
        providers = multi_ai.get_available_providers()
        stats = multi_ai.get_stats()
        
        if not providers:
            return jsonify({
                'healthy': False,
                'message': 'No AI providers available',
                'providers': [],
                'recommendation': 'Set at least one API key: ANTHROPIC_API_KEY, GROQ_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY'
            }), 503
        
        return jsonify({
            'healthy': True,
            'message': f'{len(providers)} AI providers ready',
            'providers': providers,
            'stats': stats,
            'primary_provider': providers[0] if providers else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error checking AI health: {e}")
        return jsonify({
            'healthy': False,
            'error': str(e)
        }), 500
