# ==============================================================================
# app/analytics/__init__.py
# Advanced Analytics & Insights Package - The Intelligence Dashboard
# ==============================================================================
"""
This package contains advanced analytics and insights for CLARITY.
Includes user analytics, admin analytics, AI performance tracking, and business intelligence.
"""

from .user_analytics import (
    UserAnalyticsManager,
    get_user_usage_stats,
    get_user_document_analytics,
    get_user_workspace_analytics,
    get_user_performance_insights
)

from .admin_analytics import (
    AdminAnalyticsManager,
    get_system_metrics,
    get_user_engagement_metrics,
    get_business_metrics,
    get_ai_performance_metrics
)

from .ai_performance import (
    AIPerformanceTracker,
    track_analysis_performance,
    get_model_performance_stats,
    get_prompt_effectiveness_metrics
)

__all__ = [
    # User Analytics
    'UserAnalyticsManager',
    'get_user_usage_stats',
    'get_user_document_analytics',
    'get_user_workspace_analytics',
    'get_user_performance_insights',
    
    # Admin Analytics
    'AdminAnalyticsManager',
    'get_system_metrics',
    'get_user_engagement_metrics',
    'get_business_metrics',
    'get_ai_performance_metrics',
    
    # AI Performance
    'AIPerformanceTracker',
    'track_analysis_performance',
    'get_model_performance_stats',
    'get_prompt_effectiveness_metrics'
]

