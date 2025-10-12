# ==============================================================================
# app/ai_optimization/model_router.py
# Intelligent Model Selection System - The AI Brain Router
# ==============================================================================
"""
This module provides intelligent model selection for CLARITY.
Automatically chooses the optimal AI model based on task complexity, user tier, and performance metrics.
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import desc, and_, or_
from app.models import User, Subscription, PromptVariant, PromptPerformance, AuditLog
from app import db
import redis
from config import Config

logger = logging.getLogger(__name__)

# ==============================================================================
# MODEL ROUTER
# ==============================================================================

class ModelRouter:
    """
    Intelligent model selection system that routes requests to optimal AI models.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize Redis connection for model performance tracking
        try:
            self.redis_client = redis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                db=Config.REDIS_DB,
                decode_responses=True
            )
            self.redis_client.ping()
            self.logger.info("Redis connection established for model routing")
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis for model routing: {e}")
            self.redis_client = None
        
        # Model configurations
        self.model_configs = {
            'gemini-1.5-flash': {
                'name': 'Gemini 1.5 Flash',
                'tier': 'free',
                'cost_per_1k_tokens': 0.000075,  # $0.075 per 1M tokens
                'max_tokens': 8192,
                'speed': 'fast',
                'quality': 'good',
                'use_cases': ['simple_analysis', 'quick_questions', 'basic_summarization'],
                'latency_ms': 500
            },
            'gemini-1.5-pro': {
                'name': 'Gemini 1.5 Pro',
                'tier': 'pro',
                'cost_per_1k_tokens': 0.00125,  # $1.25 per 1M tokens
                'max_tokens': 32768,
                'speed': 'medium',
                'quality': 'excellent',
                'use_cases': ['complex_analysis', 'detailed_reports', 'technical_documents'],
                'latency_ms': 1500
            },
            'gemini-1.5-ultra': {
                'name': 'Gemini 1.5 Ultra',
                'tier': 'enterprise',
                'cost_per_1k_tokens': 0.0035,  # $3.50 per 1M tokens
                'max_tokens': 65536,
                'speed': 'slow',
                'quality': 'premium',
                'use_cases': ['research_analysis', 'legal_documents', 'complex_reasoning'],
                'latency_ms': 3000
            },
            'gemini-pro-vision': {
                'name': 'Gemini Pro Vision',
                'tier': 'pro',
                'cost_per_1k_tokens': 0.00125,
                'max_tokens': 16384,
                'speed': 'medium',
                'quality': 'excellent',
                'use_cases': ['image_analysis', 'multimodal_content', 'visual_documents'],
                'latency_ms': 2000
            }
        }
    
    def select_optimal_model(self, user_id: int, task_type: str, content_length: int,
                           complexity_score: float = None, domain: str = None,
                           has_images: bool = False) -> Dict[str, Any]:
        """
        Select the optimal model for a given task.
        
        Args:
            user_id: ID of the user making the request
            task_type: Type of task ('analysis', 'summarization', 'question_answering', etc.)
            content_length: Length of content to process
            complexity_score: Complexity score (0-1, optional)
            domain: Domain of the content (optional)
            has_images: Whether the content includes images
            
        Returns:
            Dict with model selection result
        """
        try:
            # Get user's subscription tier
            subscription = Subscription.query.filter_by(user_id=user_id, status='active').first()
            user_tier = subscription.tier if subscription else 'free'
            
            # Calculate complexity score if not provided
            if complexity_score is None:
                complexity_score = self._calculate_complexity_score(content_length, task_type, domain)
            
            # Filter available models based on user tier
            available_models = self._get_available_models(user_tier, has_images)
            
            if not available_models:
                return {
                    'success': False,
                    'error': 'No models available for your tier',
                    'recommended_upgrade': self._get_upgrade_recommendation(user_tier)
                }
            
            # Score each available model
            model_scores = {}
            for model_id in available_models:
                score = self._calculate_model_score(
                    model_id, task_type, content_length, complexity_score, 
                    user_tier, domain, has_images
                )
                model_scores[model_id] = score
            
            # Select the best model
            optimal_model = max(model_scores.items(), key=lambda x: x[1])
            model_id = optimal_model[0]
            score = optimal_model[1]
            
            # Get model configuration
            model_config = self.model_configs[model_id]
            
            # Log model selection
            self._log_model_selection(user_id, model_id, task_type, score, model_scores)
            
            # Track model usage
            self._track_model_usage(user_id, model_id, task_type)
            
            return {
                'success': True,
                'selected_model': model_id,
                'model_name': model_config['name'],
                'confidence_score': score,
                'reasoning': self._get_selection_reasoning(model_id, task_type, complexity_score),
                'alternatives': self._get_alternative_models(model_scores, model_id),
                'estimated_cost': self._estimate_cost(model_id, content_length),
                'estimated_latency': model_config['latency_ms']
            }
            
        except Exception as e:
            self.logger.error(f"Failed to select optimal model: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_model_recommendations(self, user_id: int, task_type: str = None,
                                domain: str = None) -> Dict[str, Any]:
        """
        Get model recommendations for a user based on their usage patterns.
        
        Args:
            user_id: ID of the user
            task_type: Specific task type (optional)
            domain: Specific domain (optional)
            
        Returns:
            Dict with model recommendations
        """
        try:
            # Get user's subscription tier
            subscription = Subscription.query.filter_by(user_id=user_id, status='active').first()
            user_tier = subscription.tier if subscription else 'free'
            
            # Get user's historical model usage
            usage_stats = self._get_user_model_usage(user_id)
            
            # Get performance metrics for user's tier
            performance_metrics = self._get_model_performance_metrics(user_tier)
            
            # Generate recommendations
            recommendations = []
            
            for model_id, config in self.model_configs.items():
                if config['tier'] == user_tier or self._is_model_accessible(user_tier, model_id):
                    # Calculate recommendation score
                    score = self._calculate_recommendation_score(
                        model_id, user_id, task_type, domain, usage_stats, performance_metrics
                    )
                    
                    recommendations.append({
                        'model_id': model_id,
                        'model_name': config['name'],
                        'recommendation_score': score,
                        'use_cases': config['use_cases'],
                        'cost_per_1k_tokens': config['cost_per_1k_tokens'],
                        'max_tokens': config['max_tokens'],
                        'speed': config['speed'],
                        'quality': config['quality']
                    })
            
            # Sort by recommendation score
            recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
            
            return {
                'success': True,
                'user_tier': user_tier,
                'recommendations': recommendations,
                'usage_stats': usage_stats,
                'performance_metrics': performance_metrics
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get model recommendations: {e}")
            return {'success': False, 'error': str(e)}
    
    def track_model_performance(self, user_id: int, model_id: str, task_type: str,
                              response_time: float, success: bool, quality_score: float = None,
                              cost: float = None) -> Dict[str, Any]:
        """
        Track model performance for optimization.
        
        Args:
            user_id: ID of the user
            model_id: Model that was used
            task_type: Type of task performed
            response_time: Time taken to respond (seconds)
            success: Whether the request was successful
            quality_score: Quality score of the response (0-1, optional)
            cost: Cost of the request (optional)
            
        Returns:
            Dict with tracking result
        """
        try:
            # Store performance data in Redis
            if self.redis_client:
                timestamp = int(time.time())
                performance_key = f"model_performance:{model_id}:{task_type}:{timestamp}"
                
                performance_data = {
                    'user_id': user_id,
                    'model_id': model_id,
                    'task_type': task_type,
                    'response_time': response_time,
                    'success': success,
                    'quality_score': quality_score,
                    'cost': cost,
                    'timestamp': timestamp
                }
                
                # Store with 30-day expiration
                self.redis_client.hset(performance_key, mapping=performance_data)
                self.redis_client.expire(performance_key, 30 * 24 * 60 * 60)  # 30 days
            
            # Update model performance statistics
            self._update_model_statistics(model_id, task_type, response_time, success, quality_score)
            
            # Log performance tracking
            from app.security.audit_logger import log_user_action
            log_user_action(
                user_id=user_id,
                action='model_performance_tracked',
                resource_type='ai_model',
                details={
                    'model_id': model_id,
                    'task_type': task_type,
                    'response_time': response_time,
                    'success': success,
                    'quality_score': quality_score
                }
            )
            
            self.logger.info(f"Model performance tracked: {model_id} for user {user_id}")
            
            return {
                'success': True,
                'tracked_at': datetime.utcnow().isoformat(),
                'model_id': model_id,
                'task_type': task_type
            }
            
        except Exception as e:
            self.logger.error(f"Failed to track model performance: {e}")
            return {'success': False, 'error': str(e)}
    
    # ==============================================================================
    # HELPER METHODS
    # ==============================================================================
    
    def _calculate_complexity_score(self, content_length: int, task_type: str, domain: str = None) -> float:
        """Calculate complexity score based on content and task characteristics."""
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
            'research': 0.8,
            'legal_analysis': 0.9
        }
        score += task_complexity.get(task_type, 0.5)
        
        # Domain factor
        if domain:
            domain_complexity = {
                'legal': 0.3,
                'medical': 0.3,
                'technical': 0.2,
                'financial': 0.2,
                'academic': 0.2
            }
            score += domain_complexity.get(domain, 0.0)
        
        return min(score, 1.0)
    
    def _get_available_models(self, user_tier: str, has_images: bool) -> List[str]:
        """Get list of available models for user tier."""
        available = []
        
        for model_id, config in self.model_configs.items():
            # Check tier access
            if not self._is_model_accessible(user_tier, model_id):
                continue
            
            # Check image requirements
            if has_images and model_id != 'gemini-pro-vision':
                continue
            
            available.append(model_id)
        
        return available
    
    def _is_model_accessible(self, user_tier: str, model_id: str) -> bool:
        """Check if user tier can access the model."""
        model_tier = self.model_configs[model_id]['tier']
        
        tier_hierarchy = {'free': 0, 'pro': 1, 'enterprise': 2}
        user_level = tier_hierarchy.get(user_tier, 0)
        model_level = tier_hierarchy.get(model_tier, 0)
        
        return user_level >= model_level
    
    def _calculate_model_score(self, model_id: str, task_type: str, content_length: int,
                             complexity_score: float, user_tier: str, domain: str = None,
                             has_images: bool = False) -> float:
        """Calculate score for a model based on task requirements."""
        config = self.model_configs[model_id]
        score = 0.0
        
        # Quality vs complexity matching
        quality_scores = {'good': 0.3, 'excellent': 0.7, 'premium': 0.9}
        quality_score = quality_scores.get(config['quality'], 0.5)
        
        # Match quality to complexity
        if complexity_score > 0.7 and quality_score > 0.6:
            score += 0.4  # High complexity needs high quality
        elif complexity_score < 0.4 and quality_score < 0.6:
            score += 0.4  # Low complexity can use lower quality
        else:
            score += 0.2  # Partial match
        
        # Speed vs urgency
        speed_scores = {'fast': 0.8, 'medium': 0.6, 'slow': 0.4}
        speed_score = speed_scores.get(config['speed'], 0.5)
        
        # For simple tasks, prioritize speed
        if complexity_score < 0.3:
            score += speed_score * 0.3
        else:
            score += (1 - speed_score) * 0.2  # For complex tasks, quality over speed
        
        # Cost efficiency
        cost_efficiency = 1.0 / (config['cost_per_1k_tokens'] + 0.001)  # Avoid division by zero
        score += min(cost_efficiency * 0.1, 0.2)  # Cap cost factor
        
        # Use case matching
        if task_type in config['use_cases']:
            score += 0.2
        
        # Token limit check
        if content_length > config['max_tokens']:
            score -= 0.5  # Penalize models that can't handle the content
        
        return max(score, 0.0)
    
    def _get_selection_reasoning(self, model_id: str, task_type: str, complexity_score: float) -> str:
        """Generate human-readable reasoning for model selection."""
        config = self.model_configs[model_id]
        
        reasons = []
        
        if complexity_score > 0.7:
            reasons.append("High complexity content requires advanced model")
        
        if config['quality'] == 'premium':
            reasons.append("Premium quality needed for this task")
        elif config['quality'] == 'excellent':
            reasons.append("Excellent quality for reliable results")
        
        if config['speed'] == 'fast':
            reasons.append("Fast response time prioritized")
        
        if task_type in config['use_cases']:
            reasons.append(f"Optimized for {task_type} tasks")
        
        return "; ".join(reasons) if reasons else "Best overall match for requirements"
    
    def _get_alternative_models(self, model_scores: Dict[str, float], selected_model: str) -> List[Dict[str, Any]]:
        """Get alternative model recommendations."""
        alternatives = []
        
        # Sort by score and get top 3 alternatives
        sorted_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
        
        for model_id, score in sorted_models[:3]:
            if model_id != selected_model:
                config = self.model_configs[model_id]
                alternatives.append({
                    'model_id': model_id,
                    'model_name': config['name'],
                    'score': score,
                    'reason': f"Alternative with {config['quality']} quality"
                })
        
        return alternatives
    
    def _estimate_cost(self, model_id: str, content_length: int) -> float:
        """Estimate cost for processing content with the model."""
        config = self.model_configs[model_id]
        
        # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
        estimated_tokens = content_length / 4
        
        # Calculate cost
        cost = (estimated_tokens / 1000) * config['cost_per_1k_tokens']
        
        return round(cost, 6)
    
    def _log_model_selection(self, user_id: int, model_id: str, task_type: str,
                           score: float, all_scores: Dict[str, float]):
        """Log model selection for analytics."""
        try:
            if self.redis_client:
                timestamp = int(time.time())
                selection_key = f"model_selection:{user_id}:{timestamp}"
                
                selection_data = {
                    'user_id': user_id,
                    'selected_model': model_id,
                    'task_type': task_type,
                    'selection_score': score,
                    'all_scores': str(all_scores),
                    'timestamp': timestamp
                }
                
                self.redis_client.hset(selection_key, mapping=selection_data)
                self.redis_client.expire(selection_key, 7 * 24 * 60 * 60)  # 7 days
        except Exception as e:
            self.logger.error(f"Failed to log model selection: {e}")
    
    def _track_model_usage(self, user_id: int, model_id: str, task_type: str):
        """Track model usage for analytics."""
        try:
            if self.redis_client:
                # Increment usage counters
                usage_key = f"model_usage:{user_id}:{model_id}:{task_type}"
                self.redis_client.incr(usage_key)
                self.redis_client.expire(usage_key, 30 * 24 * 60 * 60)  # 30 days
        except Exception as e:
            self.logger.error(f"Failed to track model usage: {e}")
    
    def _get_upgrade_recommendation(self, user_tier: str) -> str:
        """Get upgrade recommendation for users with limited model access."""
        if user_tier == 'free':
            return "Upgrade to Pro to access advanced models like Gemini Pro"
        elif user_tier == 'pro':
            return "Upgrade to Enterprise to access premium models like Gemini Ultra"
        else:
            return "Contact support for additional model access"
    
    def _get_user_model_usage(self, user_id: int) -> Dict[str, Any]:
        """Get user's historical model usage statistics."""
        try:
            if not self.redis_client:
                return {}
            
            # Get usage patterns from Redis
            usage_patterns = {}
            
            for model_id in self.model_configs.keys():
                for task_type in ['analysis', 'summarization', 'question_answering']:
                    key = f"model_usage:{user_id}:{model_id}:{task_type}"
                    count = self.redis_client.get(key)
                    if count:
                        if model_id not in usage_patterns:
                            usage_patterns[model_id] = {}
                        usage_patterns[model_id][task_type] = int(count)
            
            return usage_patterns
        except Exception as e:
            self.logger.error(f"Failed to get user model usage: {e}")
            return {}
    
    def _get_model_performance_metrics(self, user_tier: str) -> Dict[str, Any]:
        """Get model performance metrics for the user's tier."""
        # This would typically come from a performance database
        # For now, return placeholder data
        return {
            'gemini-1.5-flash': {'avg_response_time': 0.5, 'success_rate': 0.95},
            'gemini-1.5-pro': {'avg_response_time': 1.5, 'success_rate': 0.98},
            'gemini-1.5-ultra': {'avg_response_time': 3.0, 'success_rate': 0.99}
        }
    
    def _calculate_recommendation_score(self, model_id: str, user_id: int, task_type: str,
                                      domain: str, usage_stats: Dict[str, Any],
                                      performance_metrics: Dict[str, Any]) -> float:
        """Calculate recommendation score for a model."""
        score = 0.0
        
        # Base score from model quality
        config = self.model_configs[model_id]
        quality_scores = {'good': 0.3, 'excellent': 0.7, 'premium': 0.9}
        score += quality_scores.get(config['quality'], 0.5)
        
        # Usage history bonus
        if model_id in usage_stats:
            total_usage = sum(usage_stats[model_id].values())
            if total_usage > 0:
                score += 0.2  # Bonus for previously used models
        
        # Performance metrics
        if model_id in performance_metrics:
            perf = performance_metrics[model_id]
            score += perf['success_rate'] * 0.2
        
        # Task type matching
        if task_type and task_type in config['use_cases']:
            score += 0.1
        
        return min(score, 1.0)
    
    def _update_model_statistics(self, model_id: str, task_type: str, response_time: float,
                               success: bool, quality_score: float = None):
        """Update model performance statistics."""
        try:
            if self.redis_client:
                # Update running averages
                stats_key = f"model_stats:{model_id}:{task_type}"
                
                # Get current stats
                current_stats = self.redis_client.hgetall(stats_key)
                
                # Calculate new averages
                total_requests = int(current_stats.get('total_requests', 0)) + 1
                avg_response_time = float(current_stats.get('avg_response_time', 0))
                success_count = int(current_stats.get('success_count', 0))
                
                # Update averages
                new_avg_response_time = ((avg_response_time * (total_requests - 1)) + response_time) / total_requests
                if success:
                    success_count += 1
                
                success_rate = success_count / total_requests
                
                # Store updated stats
                updated_stats = {
                    'total_requests': total_requests,
                    'avg_response_time': new_avg_response_time,
                    'success_count': success_count,
                    'success_rate': success_rate
                }
                
                if quality_score is not None:
                    avg_quality = float(current_stats.get('avg_quality', 0))
                    new_avg_quality = ((avg_quality * (total_requests - 1)) + quality_score) / total_requests
                    updated_stats['avg_quality'] = new_avg_quality
                
                self.redis_client.hset(stats_key, mapping=updated_stats)
                self.redis_client.expire(stats_key, 30 * 24 * 60 * 60)  # 30 days
                
        except Exception as e:
            self.logger.error(f"Failed to update model statistics: {e}")

# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

def select_optimal_model(user_id: int, task_type: str, content_length: int,
                        complexity_score: float = None, domain: str = None,
                        has_images: bool = False) -> Dict[str, Any]:
    """Select the optimal model for a task."""
    router = ModelRouter()
    return router.select_optimal_model(user_id, task_type, content_length, complexity_score, domain, has_images)

def get_model_recommendations(user_id: int, task_type: str = None, domain: str = None) -> Dict[str, Any]:
    """Get model recommendations for a user."""
    router = ModelRouter()
    return router.get_model_recommendations(user_id, task_type, domain)

def track_model_performance(user_id: int, model_id: str, task_type: str,
                          response_time: float, success: bool, quality_score: float = None,
                          cost: float = None) -> Dict[str, Any]:
    """Track model performance."""
    router = ModelRouter()
    return router.track_model_performance(user_id, model_id, task_type, response_time, success, quality_score, cost)

