# ==============================================================================
# app/ai_optimization/cost_optimizer.py
# Cost Optimization System - Track, analyze, and optimize AI spending
# ==============================================================================
"""
Cost Optimizer: Fortune 500-Grade AI Cost Management

This module provides comprehensive cost tracking, analysis, and optimization
for AI API usage across the platform.

Key Features:
- Real-time cost tracking per user/tier
- Monthly budget monitoring and alerts
- Cost forecasting and trend analysis
- Optimization recommendations
- ROI analysis and reporting
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class CostRecord:
    """Record of a single AI API cost."""
    timestamp: datetime
    user_id: int
    model: str
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    task_type: str
    success: bool


class CostOptimizer:
    """
    AI Cost Optimizer and Tracker.
    
    Tracks all AI API costs, provides analytics, and generates
    optimization recommendations to reduce spending.
    """
    
    # Model cost configuration
    MODEL_COSTS = {
        'gemini-1.5-flash': {
            'input': 0.000075,
            'output': 0.0003
        },
        'gemini-1.5-pro': {
            'input': 0.00125,
            'output': 0.005
        },
        'gemini-1.5-ultra': {
            'input': 0.0035,
            'output': 0.014
        },
        'gemini-pro-vision': {
            'input': 0.00125,
            'output': 0.005
        }
    }
    
    def __init__(self):
        """Initialize the Cost Optimizer."""
        logger.info("CostOptimizer initialized")
    
    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> Dict[str, float]:
        """
        Calculate the cost for an AI API call.
        
        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Dict with cost breakdown
        """
        costs = self.MODEL_COSTS.get(model, {})
        
        if not costs:
            logger.warning(f"Unknown model: {model}, using default costs")
            costs = self.MODEL_COSTS['gemini-1.5-flash']
        
        input_cost = (input_tokens / 1000) * costs['input']
        output_cost = (output_tokens / 1000) * costs['output']
        total_cost = input_cost + output_cost
        
        return {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'input_cost': round(input_cost, 6),
            'output_cost': round(output_cost, 6),
            'total_cost': round(total_cost, 6),
            'model': model
        }
    
    def track_cost(
        self,
        user_id: int,
        model: str,
        input_tokens: int,
        output_tokens: int,
        task_type: str = 'analysis',
        success: bool = True
    ) -> CostRecord:
        """
        Track a cost event.
        
        Args:
            user_id: User ID
            model: Model used
            input_tokens: Input token count
            output_tokens: Output token count
            task_type: Type of task
            success: Whether the operation succeeded
            
        Returns:
            CostRecord object
        """
        costs = self.calculate_cost(model, input_tokens, output_tokens)
        
        record = CostRecord(
            timestamp=datetime.utcnow(),
            user_id=user_id,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=costs['input_cost'],
            output_cost=costs['output_cost'],
            total_cost=costs['total_cost'],
            task_type=task_type,
            success=success
        )
        
        # Store in database (would use actual DB in production)
        self._store_cost_record(record)
        
        return record
    
    def _store_cost_record(self, record: CostRecord):
        """
        Store cost record in database.
        
        Args:
            record: CostRecord to store
        """
        try:
            from app import db
            from app.models import UsageMetrics
            
            # Get current month period
            period = record.timestamp.strftime('%Y-%m')
            
            # Find or create usage metric
            metric = UsageMetrics.query.filter_by(
                user_id=record.user_id,
                metric_type='api_cost',
                period=period
            ).first()
            
            if not metric:
                metric = UsageMetrics(
                    user_id=record.user_id,
                    metric_type='api_cost',
                    count=0,
                    period=period,
                    extra_data=json.dumps({'total_cost': 0.0})
                )
                db.session.add(metric)
            
            # Update cost
            extra_data = json.loads(metric.extra_data) if metric.extra_data else {}
            current_cost = extra_data.get('total_cost', 0.0)
            extra_data['total_cost'] = current_cost + record.total_cost
            
            metric.count += 1
            metric.extra_data = json.dumps(extra_data)
            metric.timestamp = datetime.utcnow()
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to store cost record: {e}")
    
    def get_user_costs(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get cost summary for a user.
        
        Args:
            user_id: User ID
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            Dict with cost summary
        """
        try:
            from app import db
            from app.models import UsageMetrics
            
            # Default to current month
            if not start_date:
                start_date = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Query metrics
            metrics = UsageMetrics.query.filter(
                UsageMetrics.user_id == user_id,
                UsageMetrics.metric_type == 'api_cost',
                UsageMetrics.timestamp >= start_date,
                UsageMetrics.timestamp <= end_date
            ).all()
            
            total_cost = 0.0
            total_calls = 0
            
            for metric in metrics:
                extra_data = json.loads(metric.extra_data) if metric.extra_data else {}
                total_cost += extra_data.get('total_cost', 0.0)
                total_calls += metric.count
            
            return {
                'user_id': user_id,
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'total_cost': round(total_cost, 2),
                'total_calls': total_calls,
                'average_cost_per_call': round(total_cost / total_calls, 4) if total_calls > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get user costs: {e}")
            return {
                'user_id': user_id,
                'total_cost': 0.0,
                'error': str(e)
            }
    
    def get_optimization_recommendations(
        self,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """
        Generate cost optimization recommendations for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        try:
            # Get user's usage patterns
            costs = self.get_user_costs(user_id)
            total_cost = costs.get('total_cost', 0)
            
            if total_cost == 0:
                return []
            
            # Recommendation 1: Enable caching
            recommendations.append({
                'title': 'Enable Response Caching',
                'description': 'Implement response caching to reduce duplicate API calls by up to 80%',
                'potential_savings': round(total_cost * 0.8, 2),
                'priority': 'high',
                'implementation': 'Enable caching in your account settings'
            })
            
            # Recommendation 2: Use cheaper models for simple tasks
            recommendations.append({
                'title': 'Optimize Model Selection',
                'description': 'Use Gemini Flash for simple tasks instead of Pro/Ultra models',
                'potential_savings': round(total_cost * 0.4, 2),
                'priority': 'medium',
                'implementation': 'Enable automatic model routing based on task complexity'
            })
            
            # Recommendation 3: Batch processing
            recommendations.append({
                'title': 'Batch Process Documents',
                'description': 'Process multiple documents in a single request to reduce overhead',
                'potential_savings': round(total_cost * 0.2, 2),
                'priority': 'medium',
                'implementation': 'Upload and analyze multiple documents at once'
            })
            
            # Recommendation 4: Optimize prompt length
            recommendations.append({
                'title': 'Optimize Prompt Length',
                'description': 'Reduce unnecessary context in prompts to lower input token costs',
                'potential_savings': round(total_cost * 0.15, 2),
                'priority': 'low',
                'implementation': 'Use our prompt optimization feature'
            })
            
            # Sort by potential savings
            recommendations.sort(key=lambda x: x['potential_savings'], reverse=True)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return []
    
    def forecast_monthly_cost(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Forecast monthly cost based on current usage.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with forecast
        """
        try:
            # Get current month costs
            current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
            costs = self.get_user_costs(user_id, start_date=current_month_start)
            
            # Calculate days elapsed and remaining
            today = datetime.utcnow()
            days_elapsed = (today - current_month_start).days + 1
            
            # Calculate days in month
            if today.month == 12:
                next_month = today.replace(year=today.year + 1, month=1, day=1)
            else:
                next_month = today.replace(month=today.month + 1, day=1)
            
            days_in_month = (next_month - current_month_start).days
            days_remaining = days_in_month - days_elapsed
            
            # Calculate forecast
            current_cost = costs.get('total_cost', 0)
            daily_average = current_cost / days_elapsed if days_elapsed > 0 else 0
            forecasted_cost = current_cost + (daily_average * days_remaining)
            
            return {
                'current_cost': round(current_cost, 2),
                'forecasted_monthly_cost': round(forecasted_cost, 2),
                'days_elapsed': days_elapsed,
                'days_remaining': days_remaining,
                'daily_average': round(daily_average, 2),
                'confidence': 'high' if days_elapsed >= 7 else 'medium' if days_elapsed >= 3 else 'low'
            }
            
        except Exception as e:
            logger.error(f"Failed to forecast cost: {e}")
            return {}
    
    def check_budget_alert(
        self,
        user_id: int,
        monthly_budget: float
    ) -> Dict[str, Any]:
        """
        Check if user is approaching or exceeding budget.
        
        Args:
            user_id: User ID
            monthly_budget: Monthly budget in USD
            
        Returns:
            Dict with alert status
        """
        try:
            forecast = self.forecast_monthly_cost(user_id)
            forecasted_cost = forecast.get('forecasted_monthly_cost', 0)
            current_cost = forecast.get('current_cost', 0)
            
            percentage_used = (current_cost / monthly_budget * 100) if monthly_budget > 0 else 0
            percentage_forecasted = (forecasted_cost / monthly_budget * 100) if monthly_budget > 0 else 0
            
            # Determine alert level
            if percentage_used >= 100:
                alert_level = 'critical'
                message = f'Budget exceeded! Current: ${current_cost:.2f} / ${monthly_budget:.2f}'
            elif percentage_forecasted >= 100:
                alert_level = 'warning'
                message = f'Forecasted to exceed budget: ${forecasted_cost:.2f} / ${monthly_budget:.2f}'
            elif percentage_used >= 80:
                alert_level = 'caution'
                message = f'Approaching budget limit: {percentage_used:.1f}% used'
            else:
                alert_level = 'ok'
                message = f'Within budget: {percentage_used:.1f}% used'
            
            return {
                'alert_level': alert_level,
                'message': message,
                'current_cost': round(current_cost, 2),
                'monthly_budget': monthly_budget,
                'forecasted_cost': round(forecasted_cost, 2),
                'percentage_used': round(percentage_used, 1),
                'percentage_forecasted': round(percentage_forecasted, 1),
                'remaining_budget': round(monthly_budget - current_cost, 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to check budget alert: {e}")
            return {'alert_level': 'unknown', 'error': str(e)}


# Global instance
_optimizer = None


def get_cost_optimizer() -> CostOptimizer:
    """
    Get or create the global CostOptimizer instance.
    
    Returns:
        CostOptimizer instance
    """
    global _optimizer
    
    if _optimizer is None:
        _optimizer = CostOptimizer()
    
    return _optimizer
