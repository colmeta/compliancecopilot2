# ==============================================================================
# app/security/rate_limiter.py
# Advanced Rate Limiting System - The Traffic Controller
# ==============================================================================
"""
This module provides advanced rate limiting for CLARITY.
Includes per-user, per-endpoint, per-feature, and tier-based rate limiting.
"""

import logging
import time
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from flask import request, current_app
from app.models import User, Subscription, UsageMetrics
from app import db
import redis
from config import Config

logger = logging.getLogger(__name__)

# ==============================================================================
# ADVANCED RATE LIMITER
# ==============================================================================

class AdvancedRateLimiter:
    """
    Advanced rate limiting system with multiple strategies.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize Redis connection for rate limiting
        try:
            self.redis_client = redis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                db=Config.REDIS_DB,
                decode_responses=True
            )
            self.redis_client.ping()  # Test connection
            self.logger.info("Redis connection established for rate limiting")
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis for rate limiting: {e}")
            self.redis_client = None
    
    def check_rate_limit(self, user_id: int, endpoint: str, feature: str = None,
                        tier: str = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request is within rate limits.
        
        Args:
            user_id: ID of the user making the request
            endpoint: API endpoint being accessed
            feature: Feature being used (optional)
            tier: User's subscription tier (optional)
            
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        try:
            # Get user's tier if not provided
            if not tier:
                subscription = Subscription.query.filter_by(user_id=user_id, status='active').first()
                tier = subscription.tier if subscription else 'free'
            
            # Get rate limit configuration for tier
            rate_limits = self._get_rate_limits_for_tier(tier)
            
            # Check different types of rate limits
            checks = {
                'global': self._check_global_rate_limit(user_id, rate_limits),
                'endpoint': self._check_endpoint_rate_limit(user_id, endpoint, rate_limits),
                'feature': self._check_feature_rate_limit(user_id, feature, rate_limits) if feature else True,
                'tier': self._check_tier_rate_limit(user_id, tier, rate_limits)
            }
            
            # All checks must pass
            is_allowed = all(checks.values())
            
            # Get current usage info
            usage_info = self._get_usage_info(user_id, endpoint, feature, tier)
            
            return is_allowed, {
                'allowed': is_allowed,
                'checks': checks,
                'usage': usage_info,
                'tier': tier,
                'limits': rate_limits
            }
            
        except Exception as e:
            self.logger.error(f"Failed to check rate limit: {e}")
            # Fail open - allow request if rate limiting fails
            return True, {
                'allowed': True,
                'error': str(e),
                'fallback': True
            }
    
    def get_rate_limit_status(self, user_id: int, endpoint: str = None,
                            feature: str = None) -> Dict[str, Any]:
        """
        Get current rate limit status for a user.
        
        Args:
            user_id: ID of the user
            endpoint: Specific endpoint to check (optional)
            feature: Specific feature to check (optional)
            
        Returns:
            Dict with rate limit status
        """
        try:
            # Get user's tier
            subscription = Subscription.query.filter_by(user_id=user_id, status='active').first()
            tier = subscription.tier if subscription else 'free'
            
            # Get rate limits for tier
            rate_limits = self._get_rate_limits_for_tier(tier)
            
            # Get current usage
            usage_info = self._get_usage_info(user_id, endpoint, feature, tier)
            
            # Calculate remaining limits
            remaining = {}
            for limit_type, limit_value in rate_limits.items():
                current_usage = usage_info.get(limit_type, {}).get('current', 0)
                remaining[limit_type] = max(0, limit_value - current_usage)
            
            return {
                'success': True,
                'user_id': user_id,
                'tier': tier,
                'limits': rate_limits,
                'usage': usage_info,
                'remaining': remaining
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get rate limit status: {e}")
            return {'success': False, 'error': str(e)}
    
    def reset_rate_limit(self, user_id: int, limit_type: str = None) -> Dict[str, Any]:
        """
        Reset rate limits for a user.
        
        Args:
            user_id: ID of the user
            limit_type: Type of limit to reset (optional, resets all if None)
            
        Returns:
            Dict with reset result
        """
        try:
            if not self.redis_client:
                return {'success': False, 'error': 'Redis not available'}
            
            # Get user's tier
            subscription = Subscription.query.filter_by(user_id=user_id, status='active').first()
            tier = subscription.tier if subscription else 'free'
            
            # Build key patterns
            if limit_type:
                key_patterns = [f"rate_limit:{user_id}:{limit_type}:*"]
            else:
                key_patterns = [
                    f"rate_limit:{user_id}:global:*",
                    f"rate_limit:{user_id}:endpoint:*",
                    f"rate_limit:{user_id}:feature:*",
                    f"rate_limit:{user_id}:tier:*"
                ]
            
            # Delete matching keys
            deleted_count = 0
            for pattern in key_patterns:
                keys = self.redis_client.keys(pattern)
                if keys:
                    deleted_count += self.redis_client.delete(*keys)
            
            self.logger.info(f"Reset rate limits for user {user_id}: {deleted_count} keys deleted")
            
            return {
                'success': True,
                'user_id': user_id,
                'deleted_keys': deleted_count,
                'limit_type': limit_type or 'all'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to reset rate limit: {e}")
            return {'success': False, 'error': str(e)}
    
    def increment_usage(self, user_id: int, endpoint: str, feature: str = None,
                       tier: str = None) -> Dict[str, Any]:
        """
        Increment usage counters for rate limiting.
        
        Args:
            user_id: ID of the user
            endpoint: API endpoint being accessed
            feature: Feature being used (optional)
            tier: User's subscription tier (optional)
            
        Returns:
            Dict with increment result
        """
        try:
            if not self.redis_client:
                return {'success': False, 'error': 'Redis not available'}
            
            # Get user's tier if not provided
            if not tier:
                subscription = Subscription.query.filter_by(user_id=user_id, status='active').first()
                tier = subscription.tier if subscription else 'free'
            
            current_time = int(time.time())
            
            # Increment different types of counters
            increments = {}
            
            # Global rate limit
            global_key = f"rate_limit:{user_id}:global:{current_time // 60}"  # Per minute
            increments['global'] = self.redis_client.incr(global_key)
            self.redis_client.expire(global_key, 60)  # Expire after 1 minute
            
            # Endpoint rate limit
            endpoint_key = f"rate_limit:{user_id}:endpoint:{endpoint}:{current_time // 60}"
            increments['endpoint'] = self.redis_client.incr(endpoint_key)
            self.redis_client.expire(endpoint_key, 60)
            
            # Feature rate limit (if specified)
            if feature:
                feature_key = f"rate_limit:{user_id}:feature:{feature}:{current_time // 60}"
                increments['feature'] = self.redis_client.incr(feature_key)
                self.redis_client.expire(feature_key, 60)
            
            # Tier rate limit
            tier_key = f"rate_limit:{user_id}:tier:{tier}:{current_time // 60}"
            increments['tier'] = self.redis_client.incr(tier_key)
            self.redis_client.expire(tier_key, 60)
            
            return {
                'success': True,
                'user_id': user_id,
                'increments': increments,
                'timestamp': current_time
            }
            
        except Exception as e:
            self.logger.error(f"Failed to increment usage: {e}")
            return {'success': False, 'error': str(e)}
    
    # ==============================================================================
    # HELPER METHODS
    # ==============================================================================
    
    def _get_rate_limits_for_tier(self, tier: str) -> Dict[str, int]:
        """Get rate limits for a specific tier."""
        rate_limits = {
            'free': {
                'global': 100,      # 100 requests per minute
                'endpoint': 20,     # 20 requests per endpoint per minute
                'feature': 10,      # 10 requests per feature per minute
                'tier': 100         # 100 requests per minute for tier
            },
            'pro': {
                'global': 500,      # 500 requests per minute
                'endpoint': 100,    # 100 requests per endpoint per minute
                'feature': 50,      # 50 requests per feature per minute
                'tier': 500         # 500 requests per minute for tier
            },
            'enterprise': {
                'global': 2000,     # 2000 requests per minute
                'endpoint': 500,    # 500 requests per endpoint per minute
                'feature': 200,     # 200 requests per feature per minute
                'tier': 2000        # 2000 requests per minute for tier
            }
        }
        
        return rate_limits.get(tier, rate_limits['free'])
    
    def _check_global_rate_limit(self, user_id: int, rate_limits: Dict[str, int]) -> bool:
        """Check global rate limit for user."""
        if not self.redis_client:
            return True  # Fail open
        
        try:
            current_time = int(time.time())
            key = f"rate_limit:{user_id}:global:{current_time // 60}"
            current_usage = int(self.redis_client.get(key) or 0)
            
            return current_usage < rate_limits['global']
        except Exception:
            return True  # Fail open
    
    def _check_endpoint_rate_limit(self, user_id: int, endpoint: str, rate_limits: Dict[str, int]) -> bool:
        """Check endpoint-specific rate limit."""
        if not self.redis_client:
            return True  # Fail open
        
        try:
            current_time = int(time.time())
            key = f"rate_limit:{user_id}:endpoint:{endpoint}:{current_time // 60}"
            current_usage = int(self.redis_client.get(key) or 0)
            
            return current_usage < rate_limits['endpoint']
        except Exception:
            return True  # Fail open
    
    def _check_feature_rate_limit(self, user_id: int, feature: str, rate_limits: Dict[str, int]) -> bool:
        """Check feature-specific rate limit."""
        if not self.redis_client:
            return True  # Fail open
        
        try:
            current_time = int(time.time())
            key = f"rate_limit:{user_id}:feature:{feature}:{current_time // 60}"
            current_usage = int(self.redis_client.get(key) or 0)
            
            return current_usage < rate_limits['feature']
        except Exception:
            return True  # Fail open
    
    def _check_tier_rate_limit(self, user_id: int, tier: str, rate_limits: Dict[str, int]) -> bool:
        """Check tier-specific rate limit."""
        if not self.redis_client:
            return True  # Fail open
        
        try:
            current_time = int(time.time())
            key = f"rate_limit:{user_id}:tier:{tier}:{current_time // 60}"
            current_usage = int(self.redis_client.get(key) or 0)
            
            return current_usage < rate_limits['tier']
        except Exception:
            return True  # Fail open
    
    def _get_usage_info(self, user_id: int, endpoint: str = None, feature: str = None, tier: str = None) -> Dict[str, Any]:
        """Get current usage information."""
        if not self.redis_client:
            return {}
        
        try:
            current_time = int(time.time())
            usage_info = {}
            
            # Global usage
            global_key = f"rate_limit:{user_id}:global:{current_time // 60}"
            usage_info['global'] = {
                'current': int(self.redis_client.get(global_key) or 0),
                'window': '1 minute'
            }
            
            # Endpoint usage
            if endpoint:
                endpoint_key = f"rate_limit:{user_id}:endpoint:{endpoint}:{current_time // 60}"
                usage_info['endpoint'] = {
                    'current': int(self.redis_client.get(endpoint_key) or 0),
                    'window': '1 minute'
                }
            
            # Feature usage
            if feature:
                feature_key = f"rate_limit:{user_id}:feature:{feature}:{current_time // 60}"
                usage_info['feature'] = {
                    'current': int(self.redis_client.get(feature_key) or 0),
                    'window': '1 minute'
                }
            
            # Tier usage
            if tier:
                tier_key = f"rate_limit:{user_id}:tier:{tier}:{current_time // 60}"
                usage_info['tier'] = {
                    'current': int(self.redis_client.get(tier_key) or 0),
                    'window': '1 minute'
                }
            
            return usage_info
            
        except Exception as e:
            self.logger.error(f"Failed to get usage info: {e}")
            return {}

# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

def check_rate_limit(user_id: int, endpoint: str, feature: str = None, tier: str = None) -> Tuple[bool, Dict[str, Any]]:
    """Check rate limit for a request."""
    limiter = AdvancedRateLimiter()
    return limiter.check_rate_limit(user_id, endpoint, feature, tier)

def get_rate_limit_status(user_id: int, endpoint: str = None, feature: str = None) -> Dict[str, Any]:
    """Get rate limit status for a user."""
    limiter = AdvancedRateLimiter()
    return limiter.get_rate_limit_status(user_id, endpoint, feature)

def reset_rate_limit(user_id: int, limit_type: str = None) -> Dict[str, Any]:
    """Reset rate limits for a user."""
    limiter = AdvancedRateLimiter()
    return limiter.reset_rate_limit(user_id, limit_type)

