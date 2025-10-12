# ==============================================================================
# app/ai_optimization/cost_optimizer.py
# Cost Optimization System - The Budget Guardian
# ==============================================================================
"""
This module provides cost optimization for CLARITY.
Tracks AI usage costs, optimizes model selection, and provides cost analytics.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import desc, and_, or_, func
from app.models import User, Subscription, UsageMetrics, AuditLog
from app import db
import redis
from config import Config

logger = logging.getLogger(__name__)

# ==============================================================================
# COST OPTIMIZER
# ==============================================================================

class CostOptimizer:
    """
    Cost optimization system for AI model usage.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize Redis connection for cost tracking
        try:
            self.redis_client = redis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                db=Config.REDIS_DB,
                decode_responses=True
            )
            self.redis_client.ping()
            self.logger.info("Redis connection established for cost optimization")
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis for cost optimization: {e}")
            self.redis_client = None
        
        # Model cost configurations (per 1K tokens)
        self.model_costs = {
            'gemini-1.5-flash': {
                'input_cost': 0.000075,   # $0.075 per 1M input tokens
                'output_cost': 0.0003,    # $0.30 per 1M output tokens
                'tier': 'free'
            },
            'gemini-1.5-pro': {
                'input_cost': 0.00125,    # $1.25 per 1M input tokens
                'output_cost': 0.005,     # $5.00 per 1M output tokens
                'tier': 'pro'
            },
            'gemini-1.5-ultra': {
                'input_cost': 0.0035,     # $3.50 per 1M input tokens
                'output_cost': 0.014,     # $14.00 per 1M output tokens
                'tier': 'enterprise'
            },
            'gemini-pro-vision': {
                'input_cost': 0.00125,    # $1.25 per 1M input tokens
                'output_cost': 0.005,     # $5.00 per 1M output tokens
                'tier': 'pro'
            }
        }
    
    def calculate_cost(self, user_id: int, model_id: str, input_tokens: int,
                      output_tokens: int, task_type: str = None) -> Dict[str, Any]:
        """
        Calculate the cost of an AI request.
        
        Args:
            user_id: ID of the user
            model_id: Model used for the request
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            task_type: Type of task performed (optional)
            
        Returns:
            Dict with cost calculation result
        """
        try:
            # Get model cost configuration
            if model_id not in self.model_costs:
                return {'success': False, 'error': f'Unknown model: {model_id}'}
            
            cost_config = self.model_costs[model_id]
            
            # Calculate costs
            input_cost = (input_tokens / 1000) * cost_config['input_cost']
            output_cost = (output_tokens / 1000) * cost_config['output_cost']
            total_cost = input_cost + output_cost
            
            # Get user's subscription tier
            subscription = Subscription.query.filter_by(user_id=user_id, status='active').first()
            user_tier = subscription.tier if subscription else 'free'
            
            # Apply tier-based cost adjustments
            tier_multiplier = self._get_tier_cost_multiplier(user_tier)
            adjusted_cost = total_cost * tier_multiplier
            
            # Store cost data
            self._store_cost_data(user_id, model_id, input_tokens, output_tokens, 
                                total_cost, adjusted_cost, task_type)
            
            # Update user's monthly cost tracking
            self._update_monthly_cost_tracking(user_id, adjusted_cost, model_id)
            
            return {
                'success': True,
                'cost_breakdown': {
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens,
                    'input_cost': round(input_cost, 6),
                    'output_cost': round(output_cost, 6),
                    'base_cost': round(total_cost, 6),
                    'tier_multiplier': tier_multiplier,
                    'final_cost': round(adjusted_cost, 6)
                },
                'model_id': model_id,
                'user_tier': user_tier,
                'calculated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate cost: {e}")
            return {'success': False, 'error': str(e)}
    
    def optimize_model_usage(self, user_id: int, task_type: str, content_length: int,
                           complexity_score: float = None, budget_limit: float = None) -> Dict[str, Any]:
        """
        Optimize model usage for cost efficiency.
        
        Args:
            user_id: ID of the user
            task_type: Type of task to perform
            content_length: Length of content to process
            complexity_score: Complexity score of the task (0-1)
            budget_limit: Maximum budget for the request (optional)
            
        Returns:
            Dict with optimization recommendations
        """
        try:
            # Get user's subscription tier
            subscription = Subscription.query.filter_by(user_id=user_id, status='active').first()
            user_tier = subscription.tier if subscription else 'free'
            
            # Get available models for user's tier
            available_models = self._get_available_models_for_tier(user_tier)
            
            if not available_models:
                return {
                    'success': False,
                    'error': 'No models available for your tier'
                }
            
            # Calculate complexity score if not provided
            if complexity_score is None:
                complexity_score = self._calculate_complexity_score(content_length, task_type)
            
            # Estimate token usage
            estimated_input_tokens = content_length / 4  # Rough approximation
            estimated_output_tokens = self._estimate_output_tokens(task_type, complexity_score)
            
            # Evaluate each model
            model_evaluations = []
            for model_id in available_models:
                evaluation = self._evaluate_model_for_optimization(
                    model_id, estimated_input_tokens, estimated_output_tokens,
                    complexity_score, budget_limit
                )
                model_evaluations.append(evaluation)
            
            # Sort by cost efficiency score
            model_evaluations.sort(key=lambda x: x['cost_efficiency_score'], reverse=True)
            
            # Get user's cost history
            cost_history = self._get_user_cost_history(user_id)
            
            # Generate recommendations
            recommendations = self._generate_cost_optimization_recommendations(
                model_evaluations, cost_history, user_tier
            )
            
            return {
                'success': True,
                'user_tier': user_tier,
                'task_analysis': {
                    'task_type': task_type,
                    'content_length': content_length,
                    'complexity_score': complexity_score,
                    'estimated_input_tokens': estimated_input_tokens,
                    'estimated_output_tokens': estimated_output_tokens
                },
                'model_evaluations': model_evaluations,
                'recommendations': recommendations,
                'cost_history': cost_history
            }
            
        except Exception as e:
            self.logger.error(f"Failed to optimize model usage: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_cost_analytics(self, user_id: int = None, days: int = 30) -> Dict[str, Any]:
        """
        Get cost analytics for a user or system-wide.
        
        Args:
            user_id: ID of the user (optional, for user-specific analytics)
            days: Number of days to analyze
            
        Returns:
            Dict with cost analytics
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get cost data from Redis
            cost_data = self._get_cost_data_from_redis(user_id, start_date, end_date)
            
            # Calculate analytics
            analytics = {
                'period_days': days,
                'total_cost': sum(entry['cost'] for entry in cost_data),
                'total_requests': len(cost_data),
                'avg_cost_per_request': 0,
                'cost_by_model': {},
                'cost_by_task_type': {},
                'daily_cost_trend': {},
                'cost_efficiency_metrics': {}
            }
            
            if cost_data:
                analytics['avg_cost_per_request'] = analytics['total_cost'] / len(cost_data)
                
                # Cost by model
                for entry in cost_data:
                    model_id = entry['model_id']
                    if model_id not in analytics['cost_by_model']:
                        analytics['cost_by_model'][model_id] = 0
                    analytics['cost_by_model'][model_id] += entry['cost']
                
                # Cost by task type
                for entry in cost_data:
                    task_type = entry.get('task_type', 'unknown')
                    if task_type not in analytics['cost_by_task_type']:
                        analytics['cost_by_task_type'][task_type] = 0
                    analytics['cost_by_task_type'][task_type] += entry['cost']
                
                # Daily cost trend
                for entry in cost_data:
                    date_str = entry['timestamp'].date().isoformat()
                    if date_str not in analytics['daily_cost_trend']:
                        analytics['daily_cost_trend'][date_str] = 0
                    analytics['daily_cost_trend'][date_str] += entry['cost']
                
                # Cost efficiency metrics
                analytics['cost_efficiency_metrics'] = self._calculate_cost_efficiency_metrics(cost_data)
            
            return {
                'success': True,
                'user_id': user_id,
                'analytics': analytics,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get cost analytics: {e}")
            return {'success': False, 'error': str(e)}
    
    def recommend_cost_savings(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Recommend cost savings strategies for a user.
        
        Args:
            user_id: ID of the user
            days: Number of days to analyze for recommendations
            
        Returns:
            Dict with cost savings recommendations
        """
        try:
            # Get user's cost analytics
            analytics_result = self.get_cost_analytics(user_id, days)
            if not analytics_result['success']:
                return analytics_result
            
            analytics = analytics_result['analytics']
            
            # Get user's subscription tier
            subscription = Subscription.query.filter_by(user_id=user_id, status='active').first()
            user_tier = subscription.tier if subscription else 'free'
            
            # Generate recommendations
            recommendations = []
            
            # Model usage optimization
            if analytics['cost_by_model']:
                most_expensive_model = max(analytics['cost_by_model'].items(), key=lambda x: x[1])
                if most_expensive_model[0] in ['gemini-1.5-ultra', 'gemini-1.5-pro']:
                    recommendations.append({
                        'type': 'model_optimization',
                        'title': 'Consider Model Downgrade',
                        'description': f"You're spending ${most_expensive_model[1]:.2f} on {most_expensive_model[0]}. Consider using cheaper models for simple tasks.",
                        'potential_savings': f"${most_expensive_model[1] * 0.3:.2f}",
                        'priority': 'high'
                    })
            
            # Task type optimization
            if analytics['cost_by_task_type']:
                expensive_tasks = [(task, cost) for task, cost in analytics['cost_by_task_type'].items() 
                                 if cost > analytics['total_cost'] * 0.2]
                if expensive_tasks:
                    recommendations.append({
                        'type': 'task_optimization',
                        'title': 'Optimize Expensive Tasks',
                        'description': f"Consider optimizing {expensive_tasks[0][0]} tasks which cost ${expensive_tasks[0][1]:.2f}",
                        'potential_savings': f"${expensive_tasks[0][1] * 0.2:.2f}",
                        'priority': 'medium'
                    })
            
            # Tier upgrade recommendations
            if user_tier == 'free' and analytics['total_cost'] > 10:
                recommendations.append({
                    'type': 'tier_upgrade',
                    'title': 'Consider Pro Tier',
                    'description': 'Pro tier offers better cost efficiency and advanced features',
                    'potential_savings': f"${analytics['total_cost'] * 0.2:.2f}",
                    'priority': 'medium'
                })
            
            # Usage pattern optimization
            if analytics['avg_cost_per_request'] > 0.01:
                recommendations.append({
                    'type': 'usage_optimization',
                    'title': 'Optimize Request Patterns',
                    'description': 'Consider batching requests or using more efficient prompts',
                    'potential_savings': f"${analytics['total_cost'] * 0.15:.2f}",
                    'priority': 'low'
                })
            
            # Caching recommendations
            if analytics['total_requests'] > 100:
                recommendations.append({
                    'type': 'caching',
                    'title': 'Enable Response Caching',
                    'description': 'Enable caching to reduce redundant API calls',
                    'potential_savings': f"${analytics['total_cost'] * 0.25:.2f}",
                    'priority': 'high'
                })
            
            return {
                'success': True,
                'user_id': user_id,
                'analysis_period_days': days,
                'current_monthly_cost': analytics['total_cost'],
                'recommendations': recommendations,
                'total_potential_savings': sum(float(rec['potential_savings'].replace('$', '')) for rec in recommendations),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to recommend cost savings: {e}")
            return {'success': False, 'error': str(e)}
    
    # ==============================================================================
    # HELPER METHODS
    # ==============================================================================
    
    def _get_tier_cost_multiplier(self, user_tier: str) -> float:
        """Get cost multiplier based on user tier."""
        multipliers = {
            'free': 1.0,      # No discount
            'pro': 0.8,       # 20% discount
            'enterprise': 0.6  # 40% discount
        }
        return multipliers.get(user_tier, 1.0)
    
    def _store_cost_data(self, user_id: int, model_id: str, input_tokens: int,
                        output_tokens: int, base_cost: float, adjusted_cost: float,
                        task_type: str = None):
        """Store cost data in Redis for analytics."""
        try:
            if not self.redis_client:
                return
            
            cost_entry = {
                'user_id': user_id,
                'model_id': model_id,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'base_cost': base_cost,
                'adjusted_cost': adjusted_cost,
                'task_type': task_type or 'unknown',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Store with timestamp as key for easy querying
            timestamp = int(datetime.utcnow().timestamp())
            cost_key = f"cost_data:{user_id}:{timestamp}"
            
            self.redis_client.hset(cost_key, mapping=cost_entry)
            self.redis_client.expire(cost_key, 90 * 24 * 60 * 60)  # 90 days
            
        except Exception as e:
            self.logger.error(f"Failed to store cost data: {e}")
    
    def _update_monthly_cost_tracking(self, user_id: int, cost: float, model_id: str):
        """Update monthly cost tracking for the user."""
        try:
            current_month = datetime.utcnow().strftime('%Y-%m')
            
            # Update total cost
            total_cost_key = f"monthly_cost:{user_id}:{current_month}"
            self.redis_client.incrbyfloat(total_cost_key, cost)
            self.redis_client.expire(total_cost_key, 90 * 24 * 60 * 60)  # 90 days
            
            # Update model-specific cost
            model_cost_key = f"monthly_cost:{user_id}:{current_month}:{model_id}"
            self.redis_client.incrbyfloat(model_cost_key, cost)
            self.redis_client.expire(model_cost_key, 90 * 24 * 60 * 60)  # 90 days
            
        except Exception as e:
            self.logger.error(f"Failed to update monthly cost tracking: {e}")
    
    def _get_available_models_for_tier(self, user_tier: str) -> List[str]:
        """Get available models for a user tier."""
        available = []
        
        for model_id, cost_config in self.model_costs.items():
            if self._is_model_accessible_for_tier(user_tier, cost_config['tier']):
                available.append(model_id)
        
        return available
    
    def _is_model_accessible_for_tier(self, user_tier: str, model_tier: str) -> bool:
        """Check if user tier can access a model."""
        tier_hierarchy = {'free': 0, 'pro': 1, 'enterprise': 2}
        user_level = tier_hierarchy.get(user_tier, 0)
        model_level = tier_hierarchy.get(model_tier, 0)
        
        return user_level >= model_level
    
    def _calculate_complexity_score(self, content_length: int, task_type: str) -> float:
        """Calculate complexity score for cost optimization."""
        score = 0.0
        
        # Content length factor
        if content_length < 1000:
            score += 0.2
        elif content_length < 5000:
            score += 0.4
        elif content_length < 20000:
            score += 0.6
        else:
            score += 0.8
        
        # Task type factor
        task_complexity = {
            'simple_question': 0.1,
            'summarization': 0.3,
            'analysis': 0.5,
            'complex_analysis': 0.7,
            'research': 0.8
        }
        score += task_complexity.get(task_type, 0.5)
        
        return min(score, 1.0)
    
    def _estimate_output_tokens(self, task_type: str, complexity_score: float) -> int:
        """Estimate output tokens based on task type and complexity."""
        base_tokens = {
            'simple_question': 50,
            'summarization': 200,
            'analysis': 500,
            'complex_analysis': 1000,
            'research': 1500
        }
        
        base = base_tokens.get(task_type, 300)
        complexity_multiplier = 0.5 + (complexity_score * 1.5)  # 0.5 to 2.0
        
        return int(base * complexity_multiplier)
    
    def _evaluate_model_for_optimization(self, model_id: str, input_tokens: int,
                                       output_tokens: int, complexity_score: float,
                                       budget_limit: float = None) -> Dict[str, Any]:
        """Evaluate a model for cost optimization."""
        cost_config = self.model_costs[model_id]
        
        # Calculate cost
        input_cost = (input_tokens / 1000) * cost_config['input_cost']
        output_cost = (output_tokens / 1000) * cost_config['output_cost']
        total_cost = input_cost + output_cost
        
        # Check budget constraint
        within_budget = budget_limit is None or total_cost <= budget_limit
        
        # Calculate cost efficiency score
        quality_score = self._get_model_quality_score(model_id)
        cost_efficiency_score = quality_score / (total_cost + 0.001)  # Avoid division by zero
        
        return {
            'model_id': model_id,
            'estimated_cost': round(total_cost, 6),
            'input_cost': round(input_cost, 6),
            'output_cost': round(output_cost, 6),
            'quality_score': quality_score,
            'cost_efficiency_score': cost_efficiency_score,
            'within_budget': within_budget,
            'recommendation': 'recommended' if cost_efficiency_score > 100 else 'not_recommended'
        }
    
    def _get_model_quality_score(self, model_id: str) -> float:
        """Get quality score for a model."""
        quality_scores = {
            'gemini-1.5-flash': 0.7,
            'gemini-1.5-pro': 0.9,
            'gemini-1.5-ultra': 0.95,
            'gemini-pro-vision': 0.9
        }
        return quality_scores.get(model_id, 0.5)
    
    def _get_user_cost_history(self, user_id: int) -> Dict[str, Any]:
        """Get user's cost history for optimization."""
        try:
            if not self.redis_client:
                return {}
            
            # Get last 30 days of cost data
            current_month = datetime.utcnow().strftime('%Y-%m')
            total_cost_key = f"monthly_cost:{user_id}:{current_month}"
            
            total_cost = self.redis_client.get(total_cost_key)
            if total_cost:
                return {
                    'current_month_cost': float(total_cost),
                    'trend': 'stable'  # Would calculate actual trend
                }
            
            return {}
        except Exception as e:
            self.logger.error(f"Failed to get user cost history: {e}")
            return {}
    
    def _generate_cost_optimization_recommendations(self, model_evaluations: List[Dict[str, Any]],
                                                  cost_history: Dict[str, Any],
                                                  user_tier: str) -> List[Dict[str, Any]]:
        """Generate cost optimization recommendations."""
        recommendations = []
        
        # Find best cost-efficient model
        best_model = max(model_evaluations, key=lambda x: x['cost_efficiency_score'])
        
        recommendations.append({
            'type': 'model_selection',
            'title': 'Optimal Model Selection',
            'description': f"Use {best_model['model_id']} for best cost efficiency",
            'estimated_cost': best_model['estimated_cost'],
            'cost_efficiency_score': best_model['cost_efficiency_score']
        })
        
        # Budget recommendations
        if cost_history.get('current_month_cost', 0) > 50:
            recommendations.append({
                'type': 'budget_management',
                'title': 'Budget Monitoring',
                'description': 'Consider setting monthly budget limits',
                'current_cost': cost_history.get('current_month_cost', 0)
            })
        
        return recommendations
    
    def _get_cost_data_from_redis(self, user_id: int = None, start_date: datetime = None,
                                 end_date: datetime = None) -> List[Dict[str, Any]]:
        """Get cost data from Redis for analytics."""
        try:
            if not self.redis_client:
                return []
            
            cost_data = []
            
            if user_id:
                # Get user-specific cost data
                pattern = f"cost_data:{user_id}:*"
            else:
                # Get all cost data
                pattern = "cost_data:*"
            
            keys = self.redis_client.keys(pattern)
            
            for key in keys:
                try:
                    data = self.redis_client.hgetall(key)
                    if data:
                        # Parse timestamp
                        timestamp = datetime.fromisoformat(data['timestamp'])
                        
                        # Filter by date range if specified
                        if start_date and timestamp < start_date:
                            continue
                        if end_date and timestamp > end_date:
                            continue
                        
                        cost_data.append({
                            'user_id': int(data['user_id']),
                            'model_id': data['model_id'],
                            'input_tokens': int(data['input_tokens']),
                            'output_tokens': int(data['output_tokens']),
                            'cost': float(data['adjusted_cost']),
                            'task_type': data.get('task_type', 'unknown'),
                            'timestamp': timestamp
                        })
                except Exception as e:
                    self.logger.warning(f"Failed to parse cost data from key {key}: {e}")
                    continue
            
            return cost_data
            
        except Exception as e:
            self.logger.error(f"Failed to get cost data from Redis: {e}")
            return []
    
    def _calculate_cost_efficiency_metrics(self, cost_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate cost efficiency metrics."""
        if not cost_data:
            return {}
        
        total_cost = sum(entry['cost'] for entry in cost_data)
        total_tokens = sum(entry['input_tokens'] + entry['output_tokens'] for entry in cost_data)
        
        return {
            'cost_per_token': total_cost / total_tokens if total_tokens > 0 else 0,
            'avg_cost_per_request': total_cost / len(cost_data),
            'total_requests': len(cost_data),
            'total_tokens': total_tokens
        }

# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

def calculate_cost(user_id: int, model_id: str, input_tokens: int,
                  output_tokens: int, task_type: str = None) -> Dict[str, Any]:
    """Calculate the cost of an AI request."""
    optimizer = CostOptimizer()
    return optimizer.calculate_cost(user_id, model_id, input_tokens, output_tokens, task_type)

def optimize_model_usage(user_id: int, task_type: str, content_length: int,
                        complexity_score: float = None, budget_limit: float = None) -> Dict[str, Any]:
    """Optimize model usage for cost efficiency."""
    optimizer = CostOptimizer()
    return optimizer.optimize_model_usage(user_id, task_type, content_length, complexity_score, budget_limit)

def get_cost_analytics(user_id: int = None, days: int = 30) -> Dict[str, Any]:
    """Get cost analytics."""
    optimizer = CostOptimizer()
    return optimizer.get_cost_analytics(user_id, days)

def recommend_cost_savings(user_id: int, days: int = 30) -> Dict[str, Any]:
    """Recommend cost savings strategies."""
    optimizer = CostOptimizer()
    return optimizer.recommend_cost_savings(user_id, days)

