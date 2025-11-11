# ==============================================================================
# app/middleware/tier_check.py
# Tier Check Middleware - The Access Control Guardian
# ==============================================================================
"""
This module provides middleware for checking user tier limits and tracking usage.
Ensures users don't exceed their subscription limits and provides upgrade prompts.
"""

import functools
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from flask import request, jsonify, current_app, g
from app.models import User, Subscription, UsageMetrics
from app.tiers import (
    get_tier_limits, can_use_feature, get_feature_limit, 
    is_unlimited, get_upgrade_prompt, get_current_period
)
from app import db

logger = logging.getLogger(__name__)

# ==============================================================================
# TIER CHECKING DECORATORS
# ==============================================================================

def check_tier_limit(feature: str, increment: int = 1):
    """
    Decorator to check if user can use a feature based on their tier.
    
    Args:
        feature: Feature name to check
        increment: Amount to increment usage by
        
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Get current user from request context
            user = getattr(g, 'current_user', None)
            if not user:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Get user's subscription
            subscription = get_user_subscription(user.id)
            if not subscription:
                return jsonify({'error': 'No active subscription found'}), 403
            
            # Check if feature is available
            if not can_use_feature(subscription.tier, feature):
                upgrade_prompt = get_upgrade_prompt(subscription.tier, feature)
                return jsonify({
                    'error': f'Feature not available in {subscription.tier} tier',
                    'upgrade_prompt': upgrade_prompt,
                    'current_tier': subscription.tier
                }), 403
            
            # Check usage limits
            if not is_unlimited(subscription.tier, feature):
                limit = get_feature_limit(subscription.tier, feature)
                current_usage = get_current_usage(user.id, feature)
                
                if current_usage + increment > limit:
                    upgrade_prompt = get_upgrade_prompt(subscription.tier, feature)
                    return jsonify({
                        'error': f'Usage limit exceeded for {feature}',
                        'current_usage': current_usage,
                        'limit': limit,
                        'upgrade_prompt': upgrade_prompt,
                        'current_tier': subscription.tier
                    }), 429
            
            # Track usage
            track_usage(user.id, feature, increment)
            
            # Call original function
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_tier(min_tier: str, feature: str = None):
    """
    Decorator to require a minimum tier for access.
    
    Args:
        min_tier: Minimum required tier (free, pro, enterprise)
        feature: Optional feature name for upgrade prompt
        
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Get current user from request context
            user = getattr(g, 'current_user', None)
            if not user:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Get user's subscription
            subscription = get_user_subscription(user.id)
            if not subscription:
                return jsonify({'error': 'No active subscription found'}), 403
            
            # Check tier requirement
            if not meets_tier_requirement(subscription.tier, min_tier):
                upgrade_prompt = get_upgrade_prompt(subscription.tier, feature or min_tier)
                return jsonify({
                    'error': f'Requires {min_tier} tier or higher',
                    'current_tier': subscription.tier,
                    'required_tier': min_tier,
                    'upgrade_prompt': upgrade_prompt
                }), 403
            
            # Call original function
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def track_usage(user_id: int, feature: str, amount: int = 1, metadata: Dict[str, Any] = None):
    """
    Track user usage for a specific feature.
    
    Args:
        user_id: User ID
        feature: Feature name
        amount: Amount to increment
        metadata: Additional metadata
    """
    try:
        current_period = get_current_period()
        
        # Get or create usage metric
        usage_metric = UsageMetrics.query.filter_by(
            user_id=user_id,
            metric_type=feature,
            period=current_period
        ).first()
        
        if usage_metric:
            # Update existing metric
            usage_metric.count += amount
            usage_metric.timestamp = datetime.utcnow()
            if metadata:
                usage_metric.extra_data = str(metadata)
        else:
            # Create new metric
            usage_metric = UsageMetrics(
                user_id=user_id,
                metric_type=feature,
                count=amount,
                period=current_period,
                metadata=str(metadata) if metadata else None
            )
            db.session.add(usage_metric)
        
        db.session.commit()
        
        logger.info(f"Tracked usage - User: {user_id}, Feature: {feature}, Amount: {amount}")
        
    except Exception as e:
        logger.error(f"Failed to track usage for user {user_id}: {e}")
        db.session.rollback()


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_user_subscription(user_id: int) -> Optional[Subscription]:
    """
    Get user's active subscription.
    
    Args:
        user_id: User ID
        
    Returns:
        Subscription object or None
    """
    return Subscription.query.filter_by(
        user_id=user_id,
        status='active'
    ).first()


def get_current_usage(user_id: int, feature: str) -> int:
    """
    Get current usage for a feature in the current period.
    
    Args:
        user_id: User ID
        feature: Feature name
        
    Returns:
        Current usage count
    """
    current_period = get_current_period()
    
    usage_metric = UsageMetrics.query.filter_by(
        user_id=user_id,
        metric_type=feature,
        period=current_period
    ).first()
    
    return usage_metric.count if usage_metric else 0


def meets_tier_requirement(current_tier: str, required_tier: str) -> bool:
    """
    Check if current tier meets the requirement.
    
    Args:
        current_tier: User's current tier
        required_tier: Required tier
        
    Returns:
        True if requirement is met
    """
    tier_hierarchy = {
        'free': 0,
        'pro': 1,
        'enterprise': 2
    }
    
    current_level = tier_hierarchy.get(current_tier, 0)
    required_level = tier_hierarchy.get(required_tier, 0)
    
    return current_level >= required_level


def get_usage_summary(user_id: int, period: str = None) -> Dict[str, Any]:
    """
    Get usage summary for a user.
    
    Args:
        user_id: User ID
        period: Period to get summary for (default: current)
        
    Returns:
        Usage summary dictionary
    """
    if period is None:
        period = get_current_period()
    
    # Get subscription
    subscription = get_user_subscription(user_id)
    if not subscription:
        return {'error': 'No active subscription'}
    
    # Get usage metrics
    usage_metrics = UsageMetrics.query.filter_by(
        user_id=user_id,
        period=period
    ).all()
    
    # Get tier limits
    tier_limits = get_tier_limits(subscription.tier)
    
    # Build summary
    summary = {
        'user_id': user_id,
        'tier': subscription.tier,
        'period': period,
        'usage': {},
        'limits': {},
        'warnings': []
    }
    
    for metric in usage_metrics:
        feature = metric.metric_type
        current_usage = metric.count
        limit = tier_limits.get(feature, 0)
        
        summary['usage'][feature] = current_usage
        summary['limits'][feature] = limit
        
        # Check for warnings
        if not is_unlimited(subscription.tier, feature) and current_usage >= limit * 0.8:
            summary['warnings'].append({
                'feature': feature,
                'usage': current_usage,
                'limit': limit,
                'percentage': (current_usage / limit) * 100
            })
    
    return summary


def reset_usage_for_period(user_id: int, period: str):
    """
    Reset usage for a specific period (admin function).
    
    Args:
        user_id: User ID
        period: Period to reset
    """
    try:
        UsageMetrics.query.filter_by(
            user_id=user_id,
            period=period
        ).delete()
        
        db.session.commit()
        logger.info(f"Reset usage for user {user_id} in period {period}")
        
    except Exception as e:
        logger.error(f"Failed to reset usage for user {user_id}: {e}")
        db.session.rollback()


def upgrade_user_tier(user_id: int, new_tier: str, stripe_customer_id: str = None):
    """
    Upgrade user to a new tier.
    
    Args:
        user_id: User ID
        new_tier: New tier name
        stripe_customer_id: Stripe customer ID for payment processing
    """
    try:
        subscription = get_user_subscription(user_id)
        
        if subscription:
            # Update existing subscription
            subscription.tier = new_tier
            subscription.stripe_customer_id = stripe_customer_id
        else:
            # Create new subscription
            subscription = Subscription(
                user_id=user_id,
                tier=new_tier,
                status='active',
                stripe_customer_id=stripe_customer_id
            )
            db.session.add(subscription)
        
        db.session.commit()
        
        logger.info(f"Upgraded user {user_id} to {new_tier} tier")
        
    except Exception as e:
        logger.error(f"Failed to upgrade user {user_id} to {new_tier}: {e}")
        db.session.rollback()


def downgrade_user_tier(user_id: int, new_tier: str):
    """
    Downgrade user to a new tier.
    
    Args:
        user_id: User ID
        new_tier: New tier name
    """
    try:
        subscription = get_user_subscription(user_id)
        
        if subscription:
            subscription.tier = new_tier
            subscription.status = 'active'
            db.session.commit()
            
            logger.info(f"Downgraded user {user_id} to {new_tier} tier")
        
    except Exception as e:
        logger.error(f"Failed to downgrade user {user_id} to {new_tier}: {e}")
        db.session.rollback()


# ==============================================================================
# USAGE ANALYTICS
# ==============================================================================

def get_tier_usage_stats(period: str = None) -> Dict[str, Any]:
    """
    Get usage statistics across all tiers.
    
    Args:
        period: Period to analyze (default: current)
        
    Returns:
        Usage statistics
    """
    if period is None:
        period = get_current_period()
    
    # Get all active subscriptions
    subscriptions = Subscription.query.filter_by(status='active').all()
    
    # Group by tier
    tier_stats = {}
    
    for subscription in subscriptions:
        tier = subscription.tier
        if tier not in tier_stats:
            tier_stats[tier] = {
                'user_count': 0,
                'total_usage': {},
                'avg_usage': {}
            }
        
        tier_stats[tier]['user_count'] += 1
        
        # Get user's usage
        user_usage = UsageMetrics.query.filter_by(
            user_id=subscription.user_id,
            period=period
        ).all()
        
        for usage in user_usage:
            feature = usage.metric_type
            if feature not in tier_stats[tier]['total_usage']:
                tier_stats[tier]['total_usage'][feature] = 0
            tier_stats[tier]['total_usage'][feature] += usage.count
    
    # Calculate averages
    for tier, stats in tier_stats.items():
        user_count = stats['user_count']
        for feature, total in stats['total_usage'].items():
            stats['avg_usage'][feature] = total / user_count if user_count > 0 else 0
    
    return {
        'period': period,
        'tier_stats': tier_stats,
        'total_users': sum(stats['user_count'] for stats in tier_stats.values())
    }


def get_feature_popularity(period: str = None) -> Dict[str, Any]:
    """
    Get feature popularity statistics.
    
    Args:
        period: Period to analyze (default: current)
        
    Returns:
        Feature popularity data
    """
    if period is None:
        period = get_current_period()
    
    # Get all usage metrics for the period
    usage_metrics = UsageMetrics.query.filter_by(period=period).all()
    
    feature_stats = {}
    
    for metric in usage_metrics:
        feature = metric.metric_type
        if feature not in feature_stats:
            feature_stats[feature] = {
                'total_usage': 0,
                'unique_users': set(),
                'avg_per_user': 0
            }
        
        feature_stats[feature]['total_usage'] += metric.count
        feature_stats[feature]['unique_users'].add(metric.user_id)
    
    # Convert sets to counts and calculate averages
    for feature, stats in feature_stats.items():
        stats['unique_users'] = len(stats['unique_users'])
        stats['avg_per_user'] = (
            stats['total_usage'] / stats['unique_users'] 
            if stats['unique_users'] > 0 else 0
        )
    
    return {
        'period': period,
        'feature_stats': feature_stats,
        'total_features': len(feature_stats)
    }

