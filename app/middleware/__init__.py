# ==============================================================================
# app/middleware/__init__.py
# Middleware Package - The Security & Access Control Layer
# ==============================================================================
"""
This package contains middleware components for CLARITY.
Includes tier checking, rate limiting, and access control.
"""

from .tier_check import check_tier_limit, require_tier, track_usage
from .rate_limiter import AdvancedRateLimiter

__all__ = [
    'check_tier_limit',
    'require_tier', 
    'track_usage',
    'AdvancedRateLimiter'
]

