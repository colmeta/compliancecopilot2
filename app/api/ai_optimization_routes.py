# ==============================================================================
# app/api/ai_optimization_routes.py
# AI Optimization API Routes - The Intelligence Engine Gateway
# ==============================================================================
"""
This module provides API endpoints for AI optimization features.
Includes model routing, response caching, prompt optimization, and cost management.
"""

from flask import Blueprint, request, jsonify, current_app, g
from functools import wraps
import logging
from datetime import datetime, timedelta
from app.api.routes import api_key_required
from app.middleware.tier_check import check_tier_limit, require_tier
from app.ai_optimization.model_router import ModelRouter
from app.ai_optimization.response_cache import ResponseCache
from app.ai_optimization.prompt_optimizer import PromptOptimizer
from app.ai_optimization.cost_optimizer import CostOptimizer
from app.models import User, Subscription

# Configure logging
logger = logging.getLogger(__name__)

# Create AI optimization blueprint
ai_optimization = Blueprint('ai_optimization', __name__)

# ==============================================================================
# MODEL ROUTING ENDPOINTS
# ==============================================================================

@ai_optimization.route('/model/select', methods=['POST'])
@api_key_required
@check_tier_limit('model_routing', 1)
def select_optimal_model():
    """
    Select the optimal AI model for a task.
    
    Available for Pro and Enterprise tiers.
    
    Request:
        - task_type: Type of task ('analysis', 'summarization', 'question_answering', etc.)
        - content_length: Length of content to process
        - complexity_score: Complexity score (0-1, optional)
        - domain: Domain of the content (optional)
        - has_images: Whether the content includes images (boolean)
    
    Response:
        - selected_model: Optimal model information
        - reasoning: Explanation for model selection
        - alternatives: Alternative model options
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get request data
        data = request.get_json()
        if not data or 'task_type' not in data or 'content_length' not in data:
            return jsonify({'error': 'task_type and content_length are required'}), 400
        
        task_type = data['task_type']
        content_length = int(data['content_length'])
        complexity_score = data.get('complexity_score')
        domain = data.get('domain')
        has_images = data.get('has_images', False)
        
        # Select optimal model
        router = ModelRouter()
        result = router.select_optimal_model(
            user.id, task_type, content_length, complexity_score, domain, has_images
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'selected_model': result['selected_model'],
                'model_name': result['model_name'],
                'confidence_score': result['confidence_score'],
                'reasoning': result['reasoning'],
                'alternatives': result['alternatives'],
                'estimated_cost': result['estimated_cost'],
                'estimated_latency': result['estimated_latency']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error'],
                'recommended_upgrade': result.get('recommended_upgrade')
            }), 400
        
    except Exception as e:
        logger.error(f"Select optimal model endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_optimization.route('/model/recommendations', methods=['GET'])
@api_key_required
@check_tier_limit('model_routing', 1)
def get_model_recommendations():
    """
    Get model recommendations for a user.
    
    Available for Pro and Enterprise tiers.
    
    Query Parameters:
        - task_type: Specific task type (optional)
        - domain: Specific domain (optional)
    
    Response:
        - recommendations: List of recommended models
        - usage_stats: User's model usage statistics
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get query parameters
        task_type = request.args.get('task_type')
        domain = request.args.get('domain')
        
        # Get model recommendations
        router = ModelRouter()
        result = router.get_model_recommendations(user.id, task_type, domain)
        
        if result['success']:
            return jsonify({
                'success': True,
                'user_tier': result['user_tier'],
                'recommendations': result['recommendations'],
                'usage_stats': result['usage_stats'],
                'performance_metrics': result['performance_metrics']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get model recommendations endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_optimization.route('/model/performance', methods=['POST'])
@api_key_required
@check_tier_limit('model_routing', 1)
def track_model_performance():
    """
    Track model performance for optimization.
    
    Available for Pro and Enterprise tiers.
    
    Request:
        - model_id: Model that was used
        - task_type: Type of task performed
        - response_time: Time taken to respond (seconds)
        - success: Whether the request was successful (boolean)
        - quality_score: Quality score of the response (0-1, optional)
        - cost: Cost of the request (optional)
    
    Response:
        - result: Performance tracking result
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get request data
        data = request.get_json()
        if not data or 'model_id' not in data or 'task_type' not in data:
            return jsonify({'error': 'model_id and task_type are required'}), 400
        
        model_id = data['model_id']
        task_type = data['task_type']
        response_time = float(data.get('response_time', 0))
        success = data.get('success', True)
        quality_score = data.get('quality_score')
        cost = data.get('cost')
        
        # Track model performance
        router = ModelRouter()
        result = router.track_model_performance(
            user.id, model_id, task_type, response_time, success, quality_score, cost
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'tracked_at': result['tracked_at'],
                'model_id': result['model_id'],
                'task_type': result['task_type']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Track model performance endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==============================================================================
# RESPONSE CACHING ENDPOINTS
# ==============================================================================

@ai_optimization.route('/cache/response', methods=['POST'])
@api_key_required
@check_tier_limit('response_caching', 1)
def cache_response():
    """
    Cache an AI response.
    
    Available for Pro and Enterprise tiers.
    
    Request:
        - prompt: The prompt that generated the response
        - response: The AI response to cache
        - model_id: Model that generated the response
        - task_type: Type of task performed
        - metadata: Additional metadata (optional)
        - ttl: Time to live in seconds (optional)
    
    Response:
        - result: Caching result
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get request data
        data = request.get_json()
        if not data or 'prompt' not in data or 'response' not in data:
            return jsonify({'error': 'prompt and response are required'}), 400
        
        prompt = data['prompt']
        response = data['response']
        model_id = data.get('model_id', 'unknown')
        task_type = data.get('task_type', 'unknown')
        metadata = data.get('metadata')
        ttl = data.get('ttl')
        
        # Cache response
        cache = ResponseCache()
        result = cache.cache_response(
            user.id, prompt, response, model_id, task_type, metadata, ttl
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'cache_key': result['cache_key'],
                'cached_at': result['cached_at'],
                'ttl': result['ttl']
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Cache response endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_optimization.route('/cache/retrieve', methods=['POST'])
@api_key_required
@check_tier_limit('response_caching', 1)
def get_cached_response():
    """
    Retrieve a cached response.
    
    Available for Pro and Enterprise tiers.
    
    Request:
        - prompt: The prompt to find a response for
        - model_id: Model that should have generated the response
        - task_type: Type of task
        - similarity_threshold: Minimum similarity threshold (optional)
    
    Response:
        - cached_response: Cached response or null if not found
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get request data
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({'error': 'prompt is required'}), 400
        
        prompt = data['prompt']
        model_id = data.get('model_id', 'unknown')
        task_type = data.get('task_type', 'unknown')
        similarity_threshold = data.get('similarity_threshold')
        
        # Get cached response
        cache = ResponseCache()
        result = cache.get_cached_response(
            user.id, prompt, model_id, task_type, similarity_threshold
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'cached': result['cached'],
                'response': result.get('response'),
                'model_id': result.get('model_id'),
                'cached_at': result.get('cached_at'),
                'match_type': result.get('match_type'),
                'similarity': result.get('similarity'),
                'original_prompt': result.get('original_prompt')
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get cached response endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_optimization.route('/cache/stats', methods=['GET'])
@api_key_required
@check_tier_limit('response_caching', 1)
def get_cache_stats():
    """
    Get cache statistics.
    
    Available for Pro and Enterprise tiers.
    
    Response:
        - statistics: Cache statistics
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get cache statistics
        cache = ResponseCache()
        result = cache.get_cache_stats(user.id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'user_id': user.id,
                'statistics': result['statistics']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get cache stats endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==============================================================================
# PROMPT OPTIMIZATION ENDPOINTS
# ==============================================================================

@ai_optimization.route('/prompt/optimize', methods=['POST'])
@api_key_required
@check_tier_limit('prompt_optimization', 1)
def optimize_prompt():
    """
    Optimize a prompt using A/B testing.
    
    Available for Pro and Enterprise tiers.
    
    Request:
        - domain: Domain of the prompt (e.g., 'legal', 'financial', 'security')
        - base_prompt: Base prompt to optimize
        - optimization_goal: Goal for optimization ('effectiveness', 'speed', 'cost')
    
    Response:
        - selected_variant: Optimal prompt variant
        - testing_strategy: Testing strategy information
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get request data
        data = request.get_json()
        if not data or 'domain' not in data or 'base_prompt' not in data:
            return jsonify({'error': 'domain and base_prompt are required'}), 400
        
        domain = data['domain']
        base_prompt = data['base_prompt']
        optimization_goal = data.get('optimization_goal', 'effectiveness')
        
        # Optimize prompt
        optimizer = PromptOptimizer()
        result = optimizer.optimize_prompt(user.id, domain, base_prompt, optimization_goal)
        
        if result['success']:
            return jsonify({
                'success': True,
                'domain': result['domain'],
                'selected_variant': result['selected_variant'],
                'total_variants': result['total_variants'],
                'optimization_goal': result['optimization_goal'],
                'testing_strategy': result['testing_strategy']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Optimize prompt endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_optimization.route('/prompt/test', methods=['POST'])
@api_key_required
@check_tier_limit('prompt_optimization', 1)
def test_prompt_variants():
    """
    Run A/B testing for prompt variants.
    
    Available for Pro and Enterprise tiers.
    
    Request:
        - domain: Domain to test
        - test_duration_days: Duration of the test in days (optional, default: 7)
    
    Response:
        - test_results: A/B testing results
        - winner: Winning prompt variant
        - recommendations: Optimization recommendations
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get request data
        data = request.get_json()
        if not data or 'domain' not in data:
            return jsonify({'error': 'domain is required'}), 400
        
        domain = data['domain']
        test_duration_days = data.get('test_duration_days', 7)
        
        # Test prompt variants
        optimizer = PromptOptimizer()
        result = optimizer.test_prompt_variants(user.id, domain, test_duration_days)
        
        if result['success']:
            return jsonify({
                'success': True,
                'domain': result['domain'],
                'test_duration_days': result['test_duration_days'],
                'variants_tested': result['variants_tested'],
                'test_statistics': result['test_statistics'],
                'winner': result['winner'],
                'recommendations': result['recommendations'],
                'completed_at': result['completed_at']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Test prompt variants endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_optimization.route('/prompt/performance', methods=['GET'])
@api_key_required
@check_tier_limit('prompt_optimization', 1)
def get_prompt_performance():
    """
    Get performance metrics for prompts.
    
    Available for Pro and Enterprise tiers.
    
    Query Parameters:
        - domain: Filter by domain (optional)
        - variant_id: Filter by specific variant (optional)
    
    Response:
        - performance_metrics: List of prompt performance metrics
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get query parameters
        domain = request.args.get('domain')
        variant_id = request.args.get('variant_id')
        
        if variant_id:
            variant_id = int(variant_id)
        
        # Get prompt performance
        optimizer = PromptOptimizer()
        result = optimizer.get_prompt_performance(domain, variant_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'performance_metrics': result['performance_metrics'],
                'total_variants': result['total_variants']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get prompt performance endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==============================================================================
# COST OPTIMIZATION ENDPOINTS
# ==============================================================================

@ai_optimization.route('/cost/calculate', methods=['POST'])
@api_key_required
def calculate_cost():
    """
    Calculate the cost of an AI request.
    
    Available for all tiers.
    
    Request:
        - model_id: Model used for the request
        - input_tokens: Number of input tokens
        - output_tokens: Number of output tokens
        - task_type: Type of task performed (optional)
    
    Response:
        - cost_breakdown: Detailed cost breakdown
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get request data
        data = request.get_json()
        if not data or 'model_id' not in data or 'input_tokens' not in data or 'output_tokens' not in data:
            return jsonify({'error': 'model_id, input_tokens, and output_tokens are required'}), 400
        
        model_id = data['model_id']
        input_tokens = int(data['input_tokens'])
        output_tokens = int(data['output_tokens'])
        task_type = data.get('task_type')
        
        # Calculate cost
        optimizer = CostOptimizer()
        result = optimizer.calculate_cost(user.id, model_id, input_tokens, output_tokens, task_type)
        
        if result['success']:
            return jsonify({
                'success': True,
                'cost_breakdown': result['cost_breakdown'],
                'model_id': result['model_id'],
                'user_tier': result['user_tier'],
                'calculated_at': result['calculated_at']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Calculate cost endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_optimization.route('/cost/optimize', methods=['POST'])
@api_key_required
@check_tier_limit('cost_optimization', 1)
def optimize_model_usage():
    """
    Optimize model usage for cost efficiency.
    
    Available for Pro and Enterprise tiers.
    
    Request:
        - task_type: Type of task to perform
        - content_length: Length of content to process
        - complexity_score: Complexity score of the task (0-1, optional)
        - budget_limit: Maximum budget for the request (optional)
    
    Response:
        - model_evaluations: Evaluation of different models
        - recommendations: Cost optimization recommendations
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get request data
        data = request.get_json()
        if not data or 'task_type' not in data or 'content_length' not in data:
            return jsonify({'error': 'task_type and content_length are required'}), 400
        
        task_type = data['task_type']
        content_length = int(data['content_length'])
        complexity_score = data.get('complexity_score')
        budget_limit = data.get('budget_limit')
        
        if complexity_score:
            complexity_score = float(complexity_score)
        if budget_limit:
            budget_limit = float(budget_limit)
        
        # Optimize model usage
        optimizer = CostOptimizer()
        result = optimizer.optimize_model_usage(
            user.id, task_type, content_length, complexity_score, budget_limit
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'user_tier': result['user_tier'],
                'task_analysis': result['task_analysis'],
                'model_evaluations': result['model_evaluations'],
                'recommendations': result['recommendations'],
                'cost_history': result['cost_history']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Optimize model usage endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_optimization.route('/cost/analytics', methods=['GET'])
@api_key_required
@check_tier_limit('cost_optimization', 1)
def get_cost_analytics():
    """
    Get cost analytics for a user.
    
    Available for Pro and Enterprise tiers.
    
    Query Parameters:
        - days: Number of days to analyze (default: 30)
    
    Response:
        - analytics: Cost analytics data
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get query parameters
        days = int(request.args.get('days', 30))
        
        # Get cost analytics
        optimizer = CostOptimizer()
        result = optimizer.get_cost_analytics(user.id, days)
        
        if result['success']:
            return jsonify({
                'success': True,
                'user_id': user.id,
                'analytics': result['analytics'],
                'generated_at': result['generated_at']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get cost analytics endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_optimization.route('/cost/recommendations', methods=['GET'])
@api_key_required
@check_tier_limit('cost_optimization', 1)
def get_cost_savings_recommendations():
    """
    Get cost savings recommendations.
    
    Available for Pro and Enterprise tiers.
    
    Query Parameters:
        - days: Number of days to analyze for recommendations (default: 30)
    
    Response:
        - recommendations: Cost savings recommendations
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get query parameters
        days = int(request.args.get('days', 30))
        
        # Get cost savings recommendations
        optimizer = CostOptimizer()
        result = optimizer.recommend_cost_savings(user.id, days)
        
        if result['success']:
            return jsonify({
                'success': True,
                'user_id': user.id,
                'analysis_period_days': result['analysis_period_days'],
                'current_monthly_cost': result['current_monthly_cost'],
                'recommendations': result['recommendations'],
                'total_potential_savings': result['total_potential_savings'],
                'generated_at': result['generated_at']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get cost savings recommendations endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==============================================================================
# ERROR HANDLERS
# ==============================================================================

@ai_optimization.errorhandler(404)
def not_found(e):
    """Handle not found errors."""
    return jsonify({
        'error': 'Resource not found',
        'message': 'The requested AI optimization resource could not be found'
    }), 404

@ai_optimization.errorhandler(403)
def forbidden(e):
    """Handle forbidden errors."""
    return jsonify({
        'error': 'Access forbidden',
        'message': 'You do not have permission to access this AI optimization resource'
    }), 403

