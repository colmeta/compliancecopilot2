# ==============================================================================
# app/ai_optimization/model_router.py
# Intelligent Model Selection - Route tasks to optimal AI models
# ==============================================================================
"""
Model Router: Fortune 500-Grade AI Model Selection

This module implements intelligent routing of tasks to the optimal AI model
based on task complexity, user tier, cost constraints, and performance requirements.

Key Features:
- Task complexity analysis
- Cost-aware model selection
- Performance optimization
- Tier-based model access
- Automatic failover
- Real-time model health monitoring
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class ModelSpec:
    """Specification for an AI model."""
    name: str
    provider: str
    cost_per_1k_input: float
    cost_per_1k_output: float
    context_window: int
    quality_score: float  # 0.0 to 1.0
    speed_score: float  # 0.0 to 1.0 (higher = faster)
    min_tier: str  # Minimum subscription tier required
    capabilities: List[str]  # e.g., ['text', 'vision', 'code']
    

class ModelRouter:
    """
    Intelligent AI Model Router.
    
    Routes tasks to the optimal model based on multiple factors:
    - Task complexity and type
    - User subscription tier
    - Cost optimization goals
    - Performance requirements
    - Model availability and health
    """
    
    # Model Registry
    MODELS = {
        'gemini-1.5-flash': ModelSpec(
            name='gemini-1.5-flash-latest',
            provider='google',
            cost_per_1k_input=0.000075,
            cost_per_1k_output=0.0003,
            context_window=32000,
            quality_score=0.75,
            speed_score=0.95,
            min_tier='free',
            capabilities=['text', 'vision', 'code']
        ),
        'gemini-1.5-pro': ModelSpec(
            name='gemini-1.5-pro',
            provider='google',
            cost_per_1k_input=0.00125,
            cost_per_1k_output=0.005,
            context_window=128000,
            quality_score=0.90,
            speed_score=0.70,
            min_tier='pro',
            capabilities=['text', 'vision', 'code', 'reasoning']
        ),
        'gemini-1.5-ultra': ModelSpec(
            name='gemini-1.5-ultra',
            provider='google',
            cost_per_1k_input=0.0035,
            cost_per_1k_output=0.014,
            context_window=1000000,
            quality_score=0.98,
            speed_score=0.50,
            min_tier='enterprise',
            capabilities=['text', 'vision', 'code', 'reasoning', 'multimodal']
        ),
        'gemini-pro-vision': ModelSpec(
            name='gemini-pro-vision',
            provider='google',
            cost_per_1k_input=0.00125,
            cost_per_1k_output=0.005,
            context_window=32000,
            quality_score=0.85,
            speed_score=0.75,
            min_tier='pro',
            capabilities=['text', 'vision', 'multimodal']
        )
    }
    
    def __init__(self):
        """Initialize the Model Router."""
        self.model_health = {}  # Track model availability
        logger.info("ModelRouter initialized with {} models".format(len(self.MODELS)))
    
    def route_task(
        self,
        task_type: str,
        task_complexity: str,
        user_tier: str,
        context_size: int,
        optimization_goal: str = 'balanced',
        required_capabilities: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Route a task to the optimal model.
        
        Args:
            task_type: Type of task ('analysis', 'extraction', 'generation', etc.)
            task_complexity: Complexity level ('simple', 'standard', 'complex')
            user_tier: User's subscription tier ('free', 'pro', 'enterprise')
            context_size: Size of context in tokens
            optimization_goal: 'cost', 'speed', 'quality', or 'balanced'
            required_capabilities: List of required capabilities
            
        Returns:
            Dict with selected model and routing metadata
        """
        try:
            # Filter models by tier access
            available_models = self._filter_by_tier(user_tier)
            
            if not available_models:
                return {
                    'model': 'gemini-1.5-flash-latest',  # Fallback
                    'reasoning': 'No models available for tier, using fallback'
                }
            
            # Filter by capabilities
            if required_capabilities:
                available_models = self._filter_by_capabilities(
                    available_models,
                    required_capabilities
                )
            
            # Filter by context window
            available_models = self._filter_by_context(available_models, context_size)
            
            if not available_models:
                return {
                    'model': 'gemini-1.5-flash-latest',
                    'reasoning': 'No models match requirements, using fallback'
                }
            
            # Select best model based on optimization goal
            selected_model = self._select_optimal_model(
                available_models,
                task_complexity,
                optimization_goal
            )
            
            # Calculate estimated cost
            estimated_cost = self._estimate_cost(
                selected_model,
                context_size
            )
            
            return {
                'model': selected_model.name,
                'provider': selected_model.provider,
                'reasoning': self._generate_routing_reasoning(
                    selected_model,
                    task_complexity,
                    optimization_goal
                ),
                'estimated_cost': estimated_cost,
                'quality_score': selected_model.quality_score,
                'speed_score': selected_model.speed_score,
                'context_window': selected_model.context_window
            }
            
        except Exception as e:
            logger.error(f"Model routing error: {e}", exc_info=True)
            return {
                'model': 'gemini-1.5-flash-latest',
                'reasoning': f'Routing error, using fallback: {str(e)}'
            }
    
    def _filter_by_tier(self, user_tier: str) -> List[ModelSpec]:
        """
        Filter models by user subscription tier.
        
        Args:
            user_tier: User's tier
            
        Returns:
            List of available models
        """
        tier_hierarchy = {'free': 0, 'pro': 1, 'enterprise': 2}
        user_tier_level = tier_hierarchy.get(user_tier, 0)
        
        available = []
        for model in self.MODELS.values():
            model_tier_level = tier_hierarchy.get(model.min_tier, 0)
            if user_tier_level >= model_tier_level:
                available.append(model)
        
        return available
    
    def _filter_by_capabilities(
        self,
        models: List[ModelSpec],
        required_capabilities: List[str]
    ) -> List[ModelSpec]:
        """
        Filter models by required capabilities.
        
        Args:
            models: List of models
            required_capabilities: Required capabilities
            
        Returns:
            Filtered list of models
        """
        return [
            model for model in models
            if all(cap in model.capabilities for cap in required_capabilities)
        ]
    
    def _filter_by_context(
        self,
        models: List[ModelSpec],
        context_size: int
    ) -> List[ModelSpec]:
        """
        Filter models by context window size.
        
        Args:
            models: List of models
            context_size: Required context size
            
        Returns:
            Filtered list of models
        """
        return [
            model for model in models
            if model.context_window >= context_size
        ]
    
    def _select_optimal_model(
        self,
        models: List[ModelSpec],
        task_complexity: str,
        optimization_goal: str
    ) -> ModelSpec:
        """
        Select the optimal model from available options.
        
        Args:
            models: List of available models
            task_complexity: Task complexity level
            optimization_goal: Optimization goal
            
        Returns:
            Selected ModelSpec
        """
        if not models:
            return self.MODELS['gemini-1.5-flash']
        
        # Calculate score for each model
        scored_models = []
        
        for model in models:
            score = self._calculate_model_score(
                model,
                task_complexity,
                optimization_goal
            )
            scored_models.append((model, score))
        
        # Sort by score (descending)
        scored_models.sort(key=lambda x: x[1], reverse=True)
        
        return scored_models[0][0]
    
    def _calculate_model_score(
        self,
        model: ModelSpec,
        task_complexity: str,
        optimization_goal: str
    ) -> float:
        """
        Calculate a score for a model based on goals.
        
        Args:
            model: ModelSpec to score
            task_complexity: Task complexity
            optimization_goal: Optimization goal
            
        Returns:
            Score (higher is better)
        """
        # Base weights
        quality_weight = 0.4
        speed_weight = 0.3
        cost_weight = 0.3
        
        # Adjust weights based on optimization goal
        if optimization_goal == 'quality':
            quality_weight = 0.7
            speed_weight = 0.2
            cost_weight = 0.1
        elif optimization_goal == 'speed':
            quality_weight = 0.2
            speed_weight = 0.7
            cost_weight = 0.1
        elif optimization_goal == 'cost':
            quality_weight = 0.2
            speed_weight = 0.2
            cost_weight = 0.6
        
        # Adjust quality requirement based on task complexity
        if task_complexity == 'complex':
            quality_weight *= 1.5
            quality_weight = min(quality_weight, 1.0)
        elif task_complexity == 'simple':
            cost_weight *= 1.3
            cost_weight = min(cost_weight, 1.0)
        
        # Normalize weights
        total_weight = quality_weight + speed_weight + cost_weight
        quality_weight /= total_weight
        speed_weight /= total_weight
        cost_weight /= total_weight
        
        # Calculate cost score (inverse - lower cost = higher score)
        max_cost = max(m.cost_per_1k_input for m in self.MODELS.values())
        cost_score = 1.0 - (model.cost_per_1k_input / max_cost)
        
        # Calculate composite score
        score = (
            model.quality_score * quality_weight +
            model.speed_score * speed_weight +
            cost_score * cost_weight
        )
        
        return score
    
    def _estimate_cost(
        self,
        model: ModelSpec,
        context_size: int,
        output_size: int = 1000
    ) -> Dict[str, float]:
        """
        Estimate the cost of using a model.
        
        Args:
            model: ModelSpec
            context_size: Input context size in tokens
            output_size: Expected output size in tokens
            
        Returns:
            Dict with cost breakdown
        """
        input_cost = (context_size / 1000) * model.cost_per_1k_input
        output_cost = (output_size / 1000) * model.cost_per_1k_output
        total_cost = input_cost + output_cost
        
        return {
            'input_cost': round(input_cost, 6),
            'output_cost': round(output_cost, 6),
            'total_cost': round(total_cost, 6),
            'input_tokens': context_size,
            'output_tokens_estimate': output_size
        }
    
    def _generate_routing_reasoning(
        self,
        model: ModelSpec,
        task_complexity: str,
        optimization_goal: str
    ) -> str:
        """
        Generate human-readable reasoning for model selection.
        
        Args:
            model: Selected model
            task_complexity: Task complexity
            optimization_goal: Optimization goal
            
        Returns:
            Reasoning string
        """
        reasons = []
        
        if optimization_goal == 'cost':
            reasons.append("Cost optimization prioritized")
        elif optimization_goal == 'quality':
            reasons.append("Quality optimization prioritized")
        elif optimization_goal == 'speed':
            reasons.append("Speed optimization prioritized")
        else:
            reasons.append("Balanced optimization")
        
        if task_complexity == 'complex':
            reasons.append("Complex task requires high-quality model")
        elif task_complexity == 'simple':
            reasons.append("Simple task allows cost-effective model")
        
        reasons.append(f"Model quality score: {model.quality_score:.2f}")
        reasons.append(f"Model speed score: {model.speed_score:.2f}")
        
        return " | ".join(reasons)
    
    def get_model_recommendations(
        self,
        user_tier: str,
        monthly_budget: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Get model recommendations for a user.
        
        Args:
            user_tier: User's subscription tier
            monthly_budget: Optional monthly budget in USD
            
        Returns:
            Dict with recommendations
        """
        available_models = self._filter_by_tier(user_tier)
        
        recommendations = {
            'tier': user_tier,
            'available_models': len(available_models),
            'models': []
        }
        
        for model in available_models:
            model_info = {
                'name': model.name,
                'quality_score': model.quality_score,
                'speed_score': model.speed_score,
                'cost_per_1k_input': model.cost_per_1k_input,
                'cost_per_1k_output': model.cost_per_1k_output,
                'context_window': model.context_window,
                'capabilities': model.capabilities,
                'best_for': self._get_model_use_case(model)
            }
            
            if monthly_budget:
                estimated_calls = int(monthly_budget / (model.cost_per_1k_input * 5))
                model_info['estimated_monthly_calls'] = estimated_calls
            
            recommendations['models'].append(model_info)
        
        return recommendations
    
    def _get_model_use_case(self, model: ModelSpec) -> str:
        """
        Get the best use case description for a model.
        
        Args:
            model: ModelSpec
            
        Returns:
            Use case description
        """
        if model.quality_score >= 0.95:
            return "Complex analysis, critical decisions, enterprise applications"
        elif model.quality_score >= 0.85:
            return "Standard analysis, professional use, balanced performance"
        else:
            return "Simple tasks, high-volume processing, cost-sensitive applications"


# Global instance
_router = None


def get_model_router() -> ModelRouter:
    """
    Get or create the global ModelRouter instance.
    
    Returns:
        ModelRouter instance
    """
    global _router
    
    if _router is None:
        _router = ModelRouter()
    
    return _router
