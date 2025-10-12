# ==============================================================================
# app/ai_optimization/__init__.py
# AI Model Optimization Package - The Intelligence Engine
# ==============================================================================
"""
This package contains AI model optimization features for CLARITY.
Includes intelligent model selection, response caching, prompt optimization, and cost management.
"""

from .model_router import (
    ModelRouter,
    select_optimal_model,
    get_model_recommendations,
    track_model_performance
)

from .response_cache import (
    ResponseCache,
    cache_response,
    get_cached_response,
    invalidate_cache,
    get_cache_stats
)

from .prompt_optimizer import (
    PromptOptimizer,
    optimize_prompt,
    test_prompt_variants,
    get_prompt_performance,
    deploy_optimal_prompt
)

from .cost_optimizer import (
    CostOptimizer,
    calculate_cost,
    optimize_model_usage,
    get_cost_analytics,
    recommend_cost_savings
)

__all__ = [
    # Model Routing
    'ModelRouter',
    'select_optimal_model',
    'get_model_recommendations',
    'track_model_performance',
    
    # Response Caching
    'ResponseCache',
    'cache_response',
    'get_cached_response',
    'invalidate_cache',
    'get_cache_stats',
    
    # Prompt Optimization
    'PromptOptimizer',
    'optimize_prompt',
    'test_prompt_variants',
    'get_prompt_performance',
    'deploy_optimal_prompt',
    
    # Cost Optimization
    'CostOptimizer',
    'calculate_cost',
    'optimize_model_usage',
    'get_cost_analytics',
    'recommend_cost_savings'
]

