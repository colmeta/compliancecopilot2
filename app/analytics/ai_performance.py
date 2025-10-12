# ==============================================================================
# app/analytics/ai_performance.py
# AI Performance Tracking System - The Intelligence Optimization Hub
# ==============================================================================
"""
This module provides AI performance tracking and optimization analytics for CLARITY.
Tracks model performance, prompt effectiveness, response quality, and cost optimization.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_, or_
from app.models import (
    User, PromptVariant, PromptPerformance, AuditLog, UsageMetrics,
    Subscription, WorkspaceDocument
)
from app import db

logger = logging.getLogger(__name__)

# ==============================================================================
# AI PERFORMANCE TRACKER
# ==============================================================================

class AIPerformanceTracker:
    """
    Tracks and analyzes AI performance metrics for optimization.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def track_analysis_performance(self, user_id: int, analysis_id: str, 
                                 model_used: str, prompt_variant: str,
                                 response_time: float, confidence_score: float,
                                 success: bool, error_message: str = None) -> Dict[str, Any]:
        """
        Track the performance of an AI analysis.
        
        Args:
            user_id: ID of the user who requested the analysis
            analysis_id: Unique identifier for the analysis
            model_used: AI model that was used
            prompt_variant: Prompt variant that was used
            response_time: Time taken to generate response (seconds)
            confidence_score: Confidence score of the response (0-1)
            success: Whether the analysis was successful
            error_message: Error message if analysis failed
            
        Returns:
            Dict with tracking result
        """
        try:
            # Get user's subscription tier
            subscription = Subscription.query.filter_by(user_id=user_id, status='active').first()
            user_tier = subscription.tier if subscription else 'free'
            
            # Create audit log entry
            audit_log = AuditLog(
                user_id=user_id,
                action='ai_analysis',
                resource_type='analysis',
                resource_id=analysis_id,
                details=f'{{"model": "{model_used}", "prompt_variant": "{prompt_variant}", "response_time": {response_time}, "confidence": {confidence_score}, "success": {str(success).lower()}}}',
                status='success' if success else 'failure'
            )
            
            db.session.add(audit_log)
            
            # Update prompt performance if successful
            if success:
                self._update_prompt_performance(prompt_variant, response_time, confidence_score)
            
            # Update usage metrics
            self._update_usage_metrics(user_id, user_tier, model_used, success)
            
            db.session.commit()
            
            self.logger.info(f"Tracked AI analysis performance for user {user_id}, analysis {analysis_id}")
            
            return {
                'success': True,
                'analysis_id': analysis_id,
                'tracked_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to track analysis performance: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_model_performance_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        Get performance statistics for different AI models.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with model performance statistics
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get audit logs for AI analyses
            analysis_logs = AuditLog.query.filter(
                and_(
                    AuditLog.action == 'ai_analysis',
                    AuditLog.timestamp >= start_date
                )
            ).all()
            
            # Group by model
            model_stats = {}
            
            for log in analysis_logs:
                try:
                    details = eval(log.details) if isinstance(log.details, str) else log.details
                    model = details.get('model', 'unknown')
                    
                    if model not in model_stats:
                        model_stats[model] = {
                            'total_requests': 0,
                            'successful_requests': 0,
                            'failed_requests': 0,
                            'total_response_time': 0,
                            'total_confidence': 0,
                            'response_times': [],
                            'confidence_scores': []
                        }
                    
                    stats = model_stats[model]
                    stats['total_requests'] += 1
                    
                    if log.status == 'success':
                        stats['successful_requests'] += 1
                        response_time = details.get('response_time', 0)
                        confidence = details.get('confidence', 0)
                        
                        stats['total_response_time'] += response_time
                        stats['total_confidence'] += confidence
                        stats['response_times'].append(response_time)
                        stats['confidence_scores'].append(confidence)
                    else:
                        stats['failed_requests'] += 1
                        
                except Exception as e:
                    self.logger.warning(f"Failed to parse audit log details: {e}")
                    continue
            
            # Calculate aggregated statistics
            for model, stats in model_stats.items():
                if stats['successful_requests'] > 0:
                    stats['success_rate'] = stats['successful_requests'] / stats['total_requests']
                    stats['average_response_time'] = stats['total_response_time'] / stats['successful_requests']
                    stats['average_confidence'] = stats['total_confidence'] / stats['successful_requests']
                    
                    # Calculate percentiles
                    if stats['response_times']:
                        sorted_times = sorted(stats['response_times'])
                        stats['p95_response_time'] = sorted_times[int(len(sorted_times) * 0.95)]
                        stats['p99_response_time'] = sorted_times[int(len(sorted_times) * 0.99)]
                    
                    if stats['confidence_scores']:
                        sorted_confidence = sorted(stats['confidence_scores'])
                        stats['p95_confidence'] = sorted_confidence[int(len(sorted_confidence) * 0.95)]
                        stats['p99_confidence'] = sorted_confidence[int(len(sorted_confidence) * 0.99)]
                else:
                    stats['success_rate'] = 0
                    stats['average_response_time'] = 0
                    stats['average_confidence'] = 0
                    stats['p95_response_time'] = 0
                    stats['p99_response_time'] = 0
                    stats['p95_confidence'] = 0
                    stats['p99_confidence'] = 0
                
                # Remove raw data arrays
                del stats['response_times']
                del stats['confidence_scores']
            
            return {
                'success': True,
                'period_days': days,
                'model_performance': model_stats
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get model performance stats: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_prompt_effectiveness_metrics(self, domain: str = None) -> Dict[str, Any]:
        """
        Get prompt effectiveness metrics for A/B testing.
        
        Args:
            domain: Specific domain to analyze (optional)
            
        Returns:
            Dict with prompt effectiveness metrics
        """
        try:
            # Get prompt variants
            query = PromptVariant.query.filter_by(is_active=True)
            if domain:
                query = query.filter_by(domain=domain)
            
            variants = query.all()
            
            if not variants:
                return {
                    'success': True,
                    'domain': domain,
                    'prompt_metrics': {}
                }
            
            # Get performance data for each variant
            prompt_metrics = {}
            
            for variant in variants:
                performance = PromptPerformance.query.filter_by(variant_id=variant.id).first()
                
                if performance:
                    prompt_metrics[variant.variant_name] = {
                        'domain': variant.domain,
                        'usage_count': performance.usage_count,
                        'avg_confidence': performance.avg_confidence,
                        'positive_feedback_ratio': performance.positive_feedback_ratio,
                        'avg_response_time': performance.avg_response_time,
                        'last_updated': performance.last_updated.isoformat()
                    }
                else:
                    prompt_metrics[variant.variant_name] = {
                        'domain': variant.domain,
                        'usage_count': 0,
                        'avg_confidence': 0,
                        'positive_feedback_ratio': 0,
                        'avg_response_time': 0,
                        'last_updated': None
                    }
            
            # Calculate effectiveness rankings
            effectiveness_ranking = self._calculate_prompt_effectiveness_ranking(prompt_metrics)
            
            return {
                'success': True,
                'domain': domain,
                'prompt_metrics': prompt_metrics,
                'effectiveness_ranking': effectiveness_ranking
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get prompt effectiveness metrics: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_cost_optimization_metrics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get cost optimization metrics for AI usage.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with cost optimization metrics
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get usage metrics by tier
            usage_by_tier = {}
            
            # Get all active subscriptions
            subscriptions = Subscription.query.filter_by(status='active').all()
            
            for subscription in subscriptions:
                tier = subscription.tier
                if tier not in usage_by_tier:
                    usage_by_tier[tier] = {
                        'user_count': 0,
                        'total_analyses': 0,
                        'total_documents': 0,
                        'total_workspaces': 0
                    }
                
                usage_by_tier[tier]['user_count'] += 1
                
                # Get user's usage metrics
                user_metrics = UsageMetrics.query.filter_by(user_id=subscription.user_id).all()
                for metric in user_metrics:
                    if metric.period == datetime.utcnow().strftime('%Y-%m'):
                        if metric.metric_type == 'analyses':
                            usage_by_tier[tier]['total_analyses'] += metric.count
                        elif metric.metric_type == 'documents':
                            usage_by_tier[tier]['total_documents'] += metric.count
                        elif metric.metric_type == 'workspaces':
                            usage_by_tier[tier]['total_workspaces'] += metric.count
            
            # Calculate cost efficiency metrics
            cost_efficiency = self._calculate_cost_efficiency(usage_by_tier)
            
            # Get model usage distribution
            model_usage = self._get_model_usage_distribution(start_date, end_date)
            
            # Calculate optimization recommendations
            recommendations = self._generate_cost_optimization_recommendations(usage_by_tier, model_usage)
            
            return {
                'success': True,
                'period_days': days,
                'cost_optimization': {
                    'usage_by_tier': usage_by_tier,
                    'cost_efficiency': cost_efficiency,
                    'model_usage': model_usage,
                    'recommendations': recommendations
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get cost optimization metrics: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_quality_metrics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get AI response quality metrics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with quality metrics
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get analysis logs
            analysis_logs = AuditLog.query.filter(
                and_(
                    AuditLog.action == 'ai_analysis',
                    AuditLog.timestamp >= start_date,
                    AuditLog.status == 'success'
                )
            ).all()
            
            # Calculate quality metrics
            total_analyses = len(analysis_logs)
            confidence_scores = []
            response_times = []
            
            for log in analysis_logs:
                try:
                    details = eval(log.details) if isinstance(log.details, str) else log.details
                    confidence = details.get('confidence', 0)
                    response_time = details.get('response_time', 0)
                    
                    confidence_scores.append(confidence)
                    response_times.append(response_time)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to parse audit log details: {e}")
                    continue
            
            # Calculate statistics
            if confidence_scores:
                avg_confidence = sum(confidence_scores) / len(confidence_scores)
                high_confidence_count = len([c for c in confidence_scores if c > 0.8])
                quality_score = high_confidence_count / len(confidence_scores)
            else:
                avg_confidence = 0
                quality_score = 0
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                fast_response_count = len([r for r in response_times if r < 3.0])
                speed_score = fast_response_count / len(response_times)
            else:
                avg_response_time = 0
                speed_score = 0
            
            # Calculate overall quality score
            overall_quality = (quality_score + speed_score) / 2
            
            return {
                'success': True,
                'period_days': days,
                'quality_metrics': {
                    'total_analyses': total_analyses,
                    'average_confidence': avg_confidence,
                    'quality_score': quality_score,
                    'average_response_time': avg_response_time,
                    'speed_score': speed_score,
                    'overall_quality': overall_quality,
                    'high_confidence_ratio': quality_score,
                    'fast_response_ratio': speed_score
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get quality metrics: {e}")
            return {'success': False, 'error': str(e)}
    
    # ==============================================================================
    # HELPER METHODS
    # ==============================================================================
    
    def _update_prompt_performance(self, prompt_variant: str, response_time: float, confidence_score: float):
        """Update prompt performance metrics."""
        try:
            # Find the prompt variant
            variant = PromptVariant.query.filter_by(variant_name=prompt_variant).first()
            if not variant:
                return
            
            # Get or create performance record
            performance = PromptPerformance.query.filter_by(variant_id=variant.id).first()
            if not performance:
                performance = PromptPerformance(variant_id=variant.id)
                db.session.add(performance)
            
            # Update metrics
            performance.usage_count += 1
            
            # Update average confidence
            if performance.avg_confidence is None:
                performance.avg_confidence = confidence_score
            else:
                performance.avg_confidence = (performance.avg_confidence * (performance.usage_count - 1) + confidence_score) / performance.usage_count
            
            # Update average response time
            if performance.avg_response_time is None:
                performance.avg_response_time = response_time
            else:
                performance.avg_response_time = (performance.avg_response_time * (performance.usage_count - 1) + response_time) / performance.usage_count
            
            performance.last_updated = datetime.utcnow()
            
        except Exception as e:
            self.logger.error(f"Failed to update prompt performance: {e}")
    
    def _update_usage_metrics(self, user_id: int, user_tier: str, model_used: str, success: bool):
        """Update usage metrics for the user."""
        try:
            current_month = datetime.utcnow().strftime('%Y-%m')
            
            # Update analysis count
            analysis_metric = UsageMetrics.query.filter_by(
                user_id=user_id,
                metric_type='analyses',
                period=current_month
            ).first()
            
            if not analysis_metric:
                analysis_metric = UsageMetrics(
                    user_id=user_id,
                    metric_type='analyses',
                    period=current_month,
                    count=0
                )
                db.session.add(analysis_metric)
            
            if success:
                analysis_metric.count += 1
            
            # Update model-specific usage
            model_metric = UsageMetrics.query.filter_by(
                user_id=user_id,
                metric_type=f'model_{model_used}',
                period=current_month
            ).first()
            
            if not model_metric:
                model_metric = UsageMetrics(
                    user_id=user_id,
                    metric_type=f'model_{model_used}',
                    period=current_month,
                    count=0
                )
                db.session.add(model_metric)
            
            if success:
                model_metric.count += 1
                
        except Exception as e:
            self.logger.error(f"Failed to update usage metrics: {e}")
    
    def _calculate_prompt_effectiveness_ranking(self, prompt_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate effectiveness ranking for prompts."""
        rankings = []
        
        for variant_name, metrics in prompt_metrics.items():
            # Calculate effectiveness score (weighted combination of metrics)
            usage_score = min(metrics['usage_count'] / 100, 1.0)  # Normalize to 0-1
            confidence_score = metrics['avg_confidence']
            speed_score = max(0, 1 - (metrics['avg_response_time'] / 10))  # Faster is better
            
            effectiveness_score = (usage_score * 0.3 + confidence_score * 0.5 + speed_score * 0.2)
            
            rankings.append({
                'variant_name': variant_name,
                'effectiveness_score': effectiveness_score,
                'usage_count': metrics['usage_count'],
                'avg_confidence': metrics['avg_confidence'],
                'avg_response_time': metrics['avg_response_time']
            })
        
        # Sort by effectiveness score
        rankings.sort(key=lambda x: x['effectiveness_score'], reverse=True)
        
        return rankings
    
    def _calculate_cost_efficiency(self, usage_by_tier: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate cost efficiency metrics."""
        # This would calculate cost per analysis, cost per user, etc.
        # For now, return placeholder data
        return {
            'cost_per_analysis': 0.05,  # $0.05 per analysis
            'cost_per_user': 2.50,      # $2.50 per user per month
            'efficiency_score': 0.85    # 85% efficiency
        }
    
    def _get_model_usage_distribution(self, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """Get model usage distribution."""
        # This would analyze which models are used most
        return {
            'gemini_flash': 0.6,
            'gemini_pro': 0.3,
            'gemini_ultra': 0.1
        }
    
    def _generate_cost_optimization_recommendations(self, usage_by_tier: Dict[str, Any], 
                                                  model_usage: Dict[str, float]) -> List[Dict[str, str]]:
        """Generate cost optimization recommendations."""
        recommendations = []
        
        # Analyze usage patterns and suggest optimizations
        if model_usage.get('gemini_ultra', 0) > 0.2:
            recommendations.append({
                'type': 'model_optimization',
                'title': 'Consider Model Downgrade',
                'description': 'High usage of expensive models detected. Consider using cheaper models for simple tasks.',
                'impact': 'high'
            })
        
        if usage_by_tier.get('free', {}).get('total_analyses', 0) > 1000:
            recommendations.append({
                'type': 'tier_optimization',
                'title': 'Free Tier Usage High',
                'description': 'High usage in free tier. Consider encouraging upgrades.',
                'impact': 'medium'
            })
        
        return recommendations

# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

def track_analysis_performance(user_id: int, analysis_id: str, model_used: str, 
                             prompt_variant: str, response_time: float, 
                             confidence_score: float, success: bool, 
                             error_message: str = None) -> Dict[str, Any]:
    """Track AI analysis performance."""
    tracker = AIPerformanceTracker()
    return tracker.track_analysis_performance(
        user_id, analysis_id, model_used, prompt_variant, 
        response_time, confidence_score, success, error_message
    )

def get_model_performance_stats(days: int = 30) -> Dict[str, Any]:
    """Get model performance statistics."""
    tracker = AIPerformanceTracker()
    return tracker.get_model_performance_stats(days)

def get_prompt_effectiveness_metrics(domain: str = None) -> Dict[str, Any]:
    """Get prompt effectiveness metrics."""
    tracker = AIPerformanceTracker()
    return tracker.get_prompt_effectiveness_metrics(domain)

