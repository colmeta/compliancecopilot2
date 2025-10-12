# ==============================================================================
# app/tiers.py
# Multi-Tier Subscription System - The Monetization Engine
# ==============================================================================
"""
This module manages the multi-tier subscription system for CLARITY.
Defines tier limits, feature access, and usage tracking for free/pro/enterprise tiers.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# ==============================================================================
# TIER CONFIGURATION - The Feature Matrix
# ==============================================================================

TIER_LIMITS = {
    'free': {
        # Core Features
        'documents_per_month': 10,
        'analysis_per_month': 20,
        'vault_storage_mb': 100,
        
        # Multi-Modal Features
        'audio_transcription': False,
        'video_processing': False,
        'ocr_processing': 'tesseract',  # Free OCR only
        
        # Collaboration Features
        'team_vaults': False,
        'workspace_members': 0,
        'document_sharing': False,
        
        # Analytics Features
        'advanced_analytics': False,
        'user_analytics': True,  # Basic analytics only
        'admin_analytics': False,
        'ai_performance_tracking': False,
        'analytics_retention_days': 30,
        
        # AI Features
        'model_selection': 'basic',  # Only basic models
        'response_caching': 'shared',  # Shared cache only
        'prompt_optimization': False,
        
        # Security & Compliance
        'audit_logging': False,
        'compliance_frameworks': False,
        'data_retention_policies': False,
        'encryption': 'basic',  # Basic encryption only
        'advanced_rate_limiting': False,
        
        # Support
        'priority_support': False,
        'sla_guarantee': False,
        
        # AI Model Optimization
        'model_routing': False,
        'response_caching': False,
        'prompt_optimization': False,
        'cost_optimization': False,
        
        # Rate Limits
        'api_calls_per_minute': 10,
        'concurrent_analyses': 1,
        'file_size_mb': 10,
    },
    
    'pro': {
        # Core Features
        'documents_per_month': 500,
        'analysis_per_month': 1000,
        'vault_storage_mb': 10000,
        
        # Multi-Modal Features
        'audio_transcription': 'whisper',  # Free Whisper + paid services
        'video_processing': True,
        'ocr_processing': 'all',  # All OCR services
        
        # Collaboration Features
        'team_vaults': 5,
        'workspace_members': 25,
        'document_sharing': True,
        
        # Analytics Features
        'advanced_analytics': True,
        'user_analytics': True,
        'admin_analytics': False,  # Pro users don't get admin access
        'ai_performance_tracking': True,
        'analytics_retention_days': 365,
        
        # AI Features
        'model_selection': 'standard',  # Standard models
        'response_caching': 'user',  # User-specific cache
        'prompt_optimization': True,
        
        # AI Model Optimization
        'model_routing': True,
        'response_caching': True,
        'prompt_optimization': True,
        'cost_optimization': True,
        
        # Security & Compliance
        'audit_logging': True,
        'compliance_frameworks': 'basic',  # Basic compliance
        'data_retention_policies': True,
        'encryption': 'advanced',  # Advanced encryption
        'advanced_rate_limiting': True,
        
        # Support
        'priority_support': True,
        'sla_guarantee': True,
        
        # Rate Limits
        'api_calls_per_minute': 100,
        'concurrent_analyses': 5,
        'file_size_mb': 100,
    },
    
    'enterprise': {
        # Core Features
        'documents_per_month': -1,  # Unlimited
        'analysis_per_month': -1,
        'vault_storage_mb': -1,
        
        # Multi-Modal Features
        'audio_transcription': 'all',  # All services available
        'video_processing': True,
        'ocr_processing': 'all',
        
        # Collaboration Features
        'team_vaults': -1,  # Unlimited
        'workspace_members': -1,
        'document_sharing': True,
        
        # Analytics Features
        'advanced_analytics': True,
        'user_analytics': True,
        'admin_analytics': True,  # Full admin access
        'ai_performance_tracking': True,
        'analytics_retention_days': 2555,  # 7 years
        
        # AI Features
        'model_selection': 'all',  # All models available
        'response_caching': 'enterprise',  # Enterprise cache with custom TTL
        'prompt_optimization': True,
        
        # AI Model Optimization
        'model_routing': True,
        'response_caching': True,
        'prompt_optimization': True,
        'cost_optimization': True,
        
        # Security & Compliance
        'audit_logging': True,
        'compliance_frameworks': 'all',  # All compliance frameworks
        'data_retention_policies': True,
        'encryption': 'enterprise',  # Enterprise-grade encryption
        'advanced_rate_limiting': True,
        
        # Support
        'priority_support': True,
        'sla_guarantee': True,
        
        # Rate Limits
        'api_calls_per_minute': -1,  # Unlimited
        'concurrent_analyses': -1,
        'file_size_mb': -1,  # Unlimited
    }
}

# ==============================================================================
# TIER MANAGEMENT FUNCTIONS
# ==============================================================================

def get_tier_limits(tier: str) -> Dict[str, Any]:
    """
    Get the limits for a specific tier.
    
    Args:
        tier: The tier name (free, pro, enterprise)
        
    Returns:
        Dict containing all limits for the tier
    """
    return TIER_LIMITS.get(tier, TIER_LIMITS['free'])


def can_use_feature(tier: str, feature: str) -> bool:
    """
    Check if a tier allows access to a specific feature.
    
    Args:
        tier: The tier name
        feature: The feature name
        
    Returns:
        True if feature is available, False otherwise
    """
    limits = get_tier_limits(tier)
    feature_value = limits.get(feature, False)
    
    # Handle different feature value types
    if isinstance(feature_value, bool):
        return feature_value
    elif isinstance(feature_value, str):
        return feature_value != 'false' and feature_value != ''
    elif isinstance(feature_value, (int, float)):
        return feature_value > 0
    else:
        return bool(feature_value)


def get_feature_limit(tier: str, feature: str) -> Any:
    """
    Get the specific limit value for a feature in a tier.
    
    Args:
        tier: The tier name
        feature: The feature name
        
    Returns:
        The limit value for the feature
    """
    limits = get_tier_limits(tier)
    return limits.get(feature, 0)


def is_unlimited(tier: str, feature: str) -> bool:
    """
    Check if a feature is unlimited for a tier.
    
    Args:
        tier: The tier name
        feature: The feature name
        
    Returns:
        True if feature is unlimited (-1), False otherwise
    """
    limit = get_feature_limit(tier, feature)
    return limit == -1


def get_available_services(tier: str, service_type: str) -> list:
    """
    Get list of available services for a tier and service type.
    
    Args:
        tier: The tier name
        service_type: Type of service (audio_transcription, ocr_processing, etc.)
        
    Returns:
        List of available service names
    """
    service_config = get_feature_limit(tier, service_type)
    
    if service_config is False:
        return []
    elif service_config is True:
        return ['all']
    elif service_config == 'all':
        return ['all']
    elif isinstance(service_config, str):
        return [service_config]
    else:
        return []


def get_upgrade_prompt(tier: str, feature: str) -> str:
    """
    Generate an upgrade prompt for a feature not available in current tier.
    
    Args:
        tier: Current tier
        feature: Feature that requires upgrade
        
    Returns:
        Upgrade prompt message
    """
    upgrade_map = {
        'free': {
            'audio_transcription': 'Upgrade to Pro to transcribe audio files with Whisper',
            'video_processing': 'Upgrade to Pro to process video files',
            'team_vaults': 'Upgrade to Pro to create collaborative workspaces',
            'advanced_analytics': 'Upgrade to Pro for advanced analytics and insights',
            'audit_logging': 'Upgrade to Pro for audit logging and compliance',
        },
        'pro': {
            'admin_analytics': 'Upgrade to Enterprise for admin analytics dashboard',
            'compliance_frameworks': 'Upgrade to Enterprise for full compliance frameworks',
            'unlimited_usage': 'Upgrade to Enterprise for unlimited usage',
        }
    }
    
    return upgrade_map.get(tier, {}).get(feature, f'Upgrade to access {feature}')


# ==============================================================================
# USAGE TRACKING HELPERS
# ==============================================================================

def get_current_period() -> str:
    """
    Get current period string in YYYY-MM format for usage tracking.
    
    Returns:
        Current period string
    """
    now = datetime.utcnow()
    return now.strftime('%Y-%m')


def get_period_start(period: str) -> datetime:
    """
    Get the start date of a period.
    
    Args:
        period: Period string in YYYY-MM format
        
    Returns:
        Start date of the period
    """
    year, month = map(int, period.split('-'))
    return datetime(year, month, 1)


def get_period_end(period: str) -> datetime:
    """
    Get the end date of a period.
    
    Args:
        period: Period string in YYYY-MM format
        
    Returns:
        End date of the period
    """
    year, month = map(int, period.split('-'))
    if month == 12:
        return datetime(year + 1, 1, 1) - timedelta(seconds=1)
    else:
        return datetime(year, month + 1, 1) - timedelta(seconds=1)


def is_period_current(period: str) -> bool:
    """
    Check if a period is the current period.
    
    Args:
        period: Period string in YYYY-MM format
        
    Returns:
        True if period is current, False otherwise
    """
    return period == get_current_period()


# ==============================================================================
# TIER COMPARISON AND RECOMMENDATIONS
# ==============================================================================

def get_tier_comparison() -> Dict[str, Dict[str, Any]]:
    """
    Get a comparison of all tiers for display purposes.
    
    Returns:
        Dict with tier comparisons
    """
    comparison = {}
    
    for tier in ['free', 'pro', 'enterprise']:
        limits = get_tier_limits(tier)
        comparison[tier] = {
            'name': tier.title(),
            'price': get_tier_price(tier),
            'features': {
                'documents_per_month': limits['documents_per_month'],
                'analysis_per_month': limits['analysis_per_month'],
                'vault_storage_mb': limits['vault_storage_mb'],
                'audio_transcription': limits['audio_transcription'],
                'video_processing': limits['video_processing'],
                'team_vaults': limits['team_vaults'],
                'advanced_analytics': limits['advanced_analytics'],
                'audit_logging': limits['audit_logging'],
                'priority_support': limits['priority_support'],
            }
        }
    
    return comparison


def get_tier_price(tier: str) -> str:
    """
    Get the price display string for a tier.
    
    Args:
        tier: The tier name
        
    Returns:
        Price string
    """
    prices = {
        'free': 'Free',
        'pro': '$29/month',
        'enterprise': 'Contact Sales'
    }
    return prices.get(tier, 'Unknown')


def recommend_tier(usage_stats: Dict[str, int]) -> str:
    """
    Recommend a tier based on usage statistics.
    
    Args:
        usage_stats: Dict with usage metrics
        
    Returns:
        Recommended tier name
    """
    documents = usage_stats.get('documents_per_month', 0)
    analyses = usage_stats.get('analysis_per_month', 0)
    storage_mb = usage_stats.get('vault_storage_mb', 0)
    
    # Simple recommendation logic
    if documents > 100 or analyses > 200 or storage_mb > 1000:
        return 'enterprise'
    elif documents > 10 or analyses > 20 or storage_mb > 100:
        return 'pro'
    else:
        return 'free'


# ==============================================================================
# FEATURE FLAGS AND EXPERIMENTAL FEATURES
# ==============================================================================

EXPERIMENTAL_FEATURES = {
    'ai_voice_analysis': ['enterprise'],  # Only for enterprise
    'real_time_collaboration': ['pro', 'enterprise'],
    'custom_model_training': ['enterprise'],
    'api_webhooks': ['pro', 'enterprise'],
    'white_label': ['enterprise'],
}

def is_experimental_feature_available(tier: str, feature: str) -> bool:
    """
    Check if an experimental feature is available for a tier.
    
    Args:
        tier: The tier name
        feature: The experimental feature name
        
    Returns:
        True if feature is available, False otherwise
    """
    available_tiers = EXPERIMENTAL_FEATURES.get(feature, [])
    return tier in available_tiers


# ==============================================================================
# VALIDATION AND ERROR HANDLING
# ==============================================================================

def validate_tier(tier: str) -> bool:
    """
    Validate that a tier name is valid.
    
    Args:
        tier: The tier name to validate
        
    Returns:
        True if valid, False otherwise
    """
    return tier in TIER_LIMITS


def get_default_tier() -> str:
    """
    Get the default tier for new users.
    
    Returns:
        Default tier name
    """
    return 'free'


def get_tier_display_name(tier: str) -> str:
    """
    Get the display name for a tier.
    
    Args:
        tier: The tier name
        
    Returns:
        Display name for the tier
    """
    display_names = {
        'free': 'Free',
        'pro': 'Professional',
        'enterprise': 'Enterprise'
    }
    return display_names.get(tier, tier.title())


# ==============================================================================
# LOGGING AND MONITORING
# ==============================================================================

def log_tier_usage(user_id: int, tier: str, feature: str, action: str):
    """
    Log tier usage for monitoring and analytics.
    
    Args:
        user_id: User ID
        tier: User's tier
        feature: Feature being used
        action: Action performed
    """
    logger.info(f"Tier usage - User: {user_id}, Tier: {tier}, Feature: {feature}, Action: {action}")


def log_tier_limit_exceeded(user_id: int, tier: str, feature: str, limit: Any, current: Any):
    """
    Log when a user exceeds their tier limits.
    
    Args:
        user_id: User ID
        tier: User's tier
        feature: Feature that exceeded limit
        limit: The limit value
        current: Current usage value
    """
    logger.warning(f"Tier limit exceeded - User: {user_id}, Tier: {tier}, Feature: {feature}, Limit: {limit}, Current: {current}")


# ==============================================================================
# INITIALIZATION AND SETUP
# ==============================================================================

def initialize_tier_system():
    """
    Initialize the tier system and validate configuration.
    """
    logger.info("Initializing tier system...")
    
    # Validate all tier configurations
    for tier, limits in TIER_LIMITS.items():
        if not isinstance(limits, dict):
            raise ValueError(f"Invalid tier configuration for {tier}")
        
        # Check for required features
        required_features = [
            'documents_per_month', 'analysis_per_month', 'vault_storage_mb',
            'audio_transcription', 'video_processing', 'team_vaults'
        ]
        
        for feature in required_features:
            if feature not in limits:
                raise ValueError(f"Missing required feature {feature} in tier {tier}")
    
    logger.info("Tier system initialized successfully")


# Initialize on import
initialize_tier_system()
