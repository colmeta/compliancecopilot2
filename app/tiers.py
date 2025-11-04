# ==============================================================================
# app/tiers.py
# Multi-Tier Subscription System - Fortune 500 Grade Pricing
# ==============================================================================
"""
CLARITY Tier System: Free/Pro/Enterprise

This module defines the capabilities and limits for each subscription tier.
Built to scale from individual users to Fortune 500 enterprises.
"""

# ==============================================================================
# TIER DEFINITIONS - The Monetization Architecture
# ==============================================================================

TIER_LIMITS = {
    'free': {
        # Document Processing
        'documents_per_month': 10,
        'analysis_per_month': 20,
        'vault_storage_mb': 100,
        'max_file_size_mb': 5,
        
        # AI Capabilities
        'ai_model': 'gemini-1.5-flash',  # Fast, cost-effective model
        'context_window': 32000,
        'audio_transcription': False,
        'video_processing': False,
        'advanced_ocr': False,
        'multimodal_analysis': False,
        
        # Collaboration
        'team_vaults': False,
        'workspace_members': 0,
        'document_sharing': False,
        'real_time_collaboration': False,
        
        # Analytics & Intelligence
        'advanced_analytics': False,
        'custom_accelerators': False,
        'ai_performance_tracking': False,
        'usage_dashboard': 'basic',
        
        # Enterprise Features
        'audit_logging': False,
        'compliance_frameworks': False,
        'sso_integration': False,
        'dedicated_support': False,
        'sla_guarantee': False,
        
        # Data Entry Automation
        'keystone_engine': False,
        'planning_engine': 'basic',
        'human_touch_writer': False,
        
        # API Access
        'api_access': False,
        'api_calls_per_month': 0,
        'webhook_notifications': False,
        
        # Pricing
        'price_monthly': 0,
        'price_annually': 0,
    },
    
    'pro': {
        # Document Processing
        'documents_per_month': 500,
        'analysis_per_month': 1000,
        'vault_storage_mb': 10000,  # 10 GB
        'max_file_size_mb': 50,
        
        # AI Capabilities
        'ai_model': 'gemini-1.5-pro',  # Balanced performance
        'context_window': 128000,
        'audio_transcription': 'whisper',  # Free Whisper transcription
        'video_processing': True,
        'advanced_ocr': 'tesseract',  # Free Tesseract OCR
        'multimodal_analysis': True,
        
        # Collaboration
        'team_vaults': True,
        'workspace_members': 5,
        'document_sharing': True,
        'real_time_collaboration': True,
        
        # Analytics & Intelligence
        'advanced_analytics': True,
        'custom_accelerators': True,
        'ai_performance_tracking': True,
        'usage_dashboard': 'advanced',
        
        # Enterprise Features
        'audit_logging': True,
        'compliance_frameworks': ['GDPR'],
        'sso_integration': False,
        'dedicated_support': 'email',
        'sla_guarantee': False,
        
        # Data Entry Automation
        'keystone_engine': True,
        'planning_engine': 'advanced',
        'human_touch_writer': True,
        
        # API Access
        'api_access': True,
        'api_calls_per_month': 10000,
        'webhook_notifications': True,
        
        # Pricing
        'price_monthly': 49,
        'price_annually': 490,  # ~17% discount
    },
    
    'enterprise': {
        # Document Processing
        'documents_per_month': -1,  # Unlimited
        'analysis_per_month': -1,  # Unlimited
        'vault_storage_mb': -1,  # Unlimited
        'max_file_size_mb': 500,
        
        # AI Capabilities
        'ai_model': 'all',  # Access to all models with intelligent routing
        'context_window': 1000000,  # Gemini 1.5 Ultra context
        'audio_transcription': 'all',  # All services (Whisper, Google, AssemblyAI)
        'video_processing': True,
        'advanced_ocr': 'all',  # All services (Tesseract, Google Vision, AWS Textract)
        'multimodal_analysis': True,
        
        # Collaboration
        'team_vaults': True,
        'workspace_members': -1,  # Unlimited
        'document_sharing': True,
        'real_time_collaboration': True,
        
        # Analytics & Intelligence
        'advanced_analytics': True,
        'custom_accelerators': True,
        'ai_performance_tracking': True,
        'usage_dashboard': 'enterprise',
        
        # Enterprise Features
        'audit_logging': True,
        'compliance_frameworks': ['GDPR', 'HIPAA', 'SOC2', 'ISO27001'],
        'sso_integration': True,
        'dedicated_support': '24/7',
        'sla_guarantee': '99.9%',
        
        # Data Entry Automation
        'keystone_engine': True,
        'planning_engine': 'enterprise',
        'human_touch_writer': True,
        
        # API Access
        'api_access': True,
        'api_calls_per_month': -1,  # Unlimited
        'webhook_notifications': True,
        
        # Pricing
        'price_monthly': 499,
        'price_annually': 4990,  # ~17% discount
    }
}


# ==============================================================================
# TIER FEATURE DESCRIPTIONS - For Marketing and Sales
# ==============================================================================

TIER_FEATURES_DESCRIPTION = {
    'free': {
        'title': 'Free - Get Started',
        'tagline': 'Perfect for individuals exploring AI-powered document analysis',
        'best_for': 'Students, researchers, and individual professionals',
        'key_features': [
            '10 documents/month',
            '20 AI analyses/month',
            '100 MB storage',
            'Basic Intelligence Vault',
            'All 11 domain accelerators',
            'Community support'
        ],
        'cta': 'Start Free'
    },
    
    'pro': {
        'title': 'Pro - Scale Your Intelligence',
        'tagline': 'Advanced features for professionals and small teams',
        'best_for': 'Consultants, small businesses, and professional teams',
        'key_features': [
            '500 documents/month',
            '1,000 AI analyses/month',
            '10 GB storage',
            'Team workspaces (5 members)',
            'Audio & video processing',
            'Data Keystone Engine',
            'Planning Engine',
            'Human Touch Writer',
            'Advanced analytics',
            'API access (10k calls/month)',
            'Email support'
        ],
        'cta': 'Upgrade to Pro'
    },
    
    'enterprise': {
        'title': 'Enterprise - Unstoppable Intelligence',
        'tagline': 'Fortune 500-grade platform with unlimited capabilities',
        'best_for': 'Large organizations, government agencies, and enterprises',
        'key_features': [
            'Unlimited documents & analyses',
            'Unlimited storage',
            'Unlimited team members',
            'All AI models with intelligent routing',
            'All transcription & OCR services',
            'Full Data Keystone Engine',
            'Enterprise Planning Engine',
            'SOC2, HIPAA, GDPR compliance',
            'SSO integration',
            '99.9% SLA',
            '24/7 dedicated support',
            'Unlimited API access',
            'Custom accelerators',
            'White-label options'
        ],
        'cta': 'Contact Sales'
    }
}


# ==============================================================================
# TIER UTILITY FUNCTIONS
# ==============================================================================

def get_tier_limit(tier: str, feature: str) -> any:
    """
    Get the limit for a specific feature in a tier.
    
    Args:
        tier: Tier name ('free', 'pro', 'enterprise')
        feature: Feature name (e.g., 'documents_per_month')
        
    Returns:
        The limit value, or None if feature doesn't exist
    """
    return TIER_LIMITS.get(tier, {}).get(feature, None)


def can_use_feature(tier: str, feature: str) -> bool:
    """
    Check if a tier has access to a specific feature.
    
    Args:
        tier: Tier name ('free', 'pro', 'enterprise')
        feature: Feature name
        
    Returns:
        True if feature is available, False otherwise
    """
    limit = get_tier_limit(tier, feature)
    
    # Handle different types of limits
    if limit is None:
        return False
    elif isinstance(limit, bool):
        return limit
    elif isinstance(limit, int) and limit == -1:
        return True  # -1 means unlimited
    elif isinstance(limit, int) and limit > 0:
        return True
    elif isinstance(limit, list):
        return len(limit) > 0
    elif isinstance(limit, str) and limit != 'false':
        return True
    
    return False


def get_usage_limit(tier: str, metric_type: str) -> int:
    """
    Get the usage limit for a metric type.
    
    Args:
        tier: Tier name ('free', 'pro', 'enterprise')
        metric_type: Type of metric (e.g., 'documents', 'analysis')
        
    Returns:
        The limit value, -1 for unlimited, 0 for not allowed
    """
    metric_map = {
        'documents': 'documents_per_month',
        'analysis': 'analysis_per_month',
        'storage': 'vault_storage_mb',
        'api_calls': 'api_calls_per_month'
    }
    
    feature_key = metric_map.get(metric_type, metric_type)
    limit = get_tier_limit(tier, feature_key)
    
    if limit is None or limit is False:
        return 0
    elif limit is True:
        return -1  # Unlimited
    elif isinstance(limit, int):
        return limit
    
    return 0


def get_tier_comparison() -> dict:
    """
    Get a comparison table of all tier features.
    
    Returns:
        Dict with feature comparison across all tiers
    """
    features = list(TIER_LIMITS['free'].keys())
    
    comparison = {}
    for feature in features:
        comparison[feature] = {
            'free': TIER_LIMITS['free'].get(feature),
            'pro': TIER_LIMITS['pro'].get(feature),
            'enterprise': TIER_LIMITS['enterprise'].get(feature)
        }
    
    return comparison


def get_tier_pricing(tier: str) -> dict:
    """
    Get pricing information for a tier.
    
    Args:
        tier: Tier name
        
    Returns:
        Dict with pricing information
    """
    tier_info = TIER_LIMITS.get(tier, {})
    
    return {
        'tier': tier,
        'price_monthly': tier_info.get('price_monthly', 0),
        'price_annually': tier_info.get('price_annually', 0),
        'savings_annually': tier_info.get('price_monthly', 0) * 12 - tier_info.get('price_annually', 0),
        'description': TIER_FEATURES_DESCRIPTION.get(tier, {})
    }


def get_upgrade_path(current_tier: str) -> dict:
    """
    Get upgrade options for a tier.
    
    Args:
        current_tier: Current tier name
        
    Returns:
        Dict with upgrade options and benefits
    """
    tier_hierarchy = ['free', 'pro', 'enterprise']
    
    if current_tier not in tier_hierarchy:
        return {'available': False}
    
    current_index = tier_hierarchy.index(current_tier)
    
    if current_index >= len(tier_hierarchy) - 1:
        return {'available': False, 'message': 'You are on the highest tier'}
    
    next_tier = tier_hierarchy[current_index + 1]
    next_tier_info = TIER_LIMITS[next_tier]
    current_tier_info = TIER_LIMITS[current_tier]
    
    # Calculate additional benefits
    benefits = []
    for key, value in next_tier_info.items():
        current_value = current_tier_info.get(key)
        
        if current_value != value:
            if isinstance(value, int) and value == -1:
                benefits.append(f"Unlimited {key.replace('_', ' ')}")
            elif isinstance(value, bool) and value and not current_value:
                benefits.append(f"Access to {key.replace('_', ' ')}")
            elif isinstance(value, int) and isinstance(current_value, int) and value > current_value:
                benefits.append(f"{key.replace('_', ' ')}: {current_value} → {value}")
    
    return {
        'available': True,
        'next_tier': next_tier,
        'price_monthly': next_tier_info['price_monthly'],
        'price_annually': next_tier_info['price_annually'],
        'additional_benefits': benefits[:10],  # Top 10 benefits
        'description': TIER_FEATURES_DESCRIPTION[next_tier]
    }


def check_usage_against_limit(tier: str, metric_type: str, current_usage: int) -> dict:
    """
    Check if current usage is within tier limits.
    
    Args:
        tier: Tier name
        metric_type: Type of metric
        current_usage: Current usage count
        
    Returns:
        Dict with usage status and recommendations
    """
    limit = get_usage_limit(tier, metric_type)
    
    if limit == -1:
        return {
            'within_limit': True,
            'usage': current_usage,
            'limit': 'unlimited',
            'percentage': 0,
            'status': 'unlimited'
        }
    
    if limit == 0:
        return {
            'within_limit': False,
            'usage': current_usage,
            'limit': 0,
            'percentage': 100,
            'status': 'not_available',
            'message': f'{metric_type} is not available in your current tier'
        }
    
    percentage = (current_usage / limit) * 100 if limit > 0 else 0
    within_limit = current_usage < limit
    
    status = 'ok'
    message = None
    
    if percentage >= 100:
        status = 'exceeded'
        message = f'You have exceeded your {metric_type} limit. Please upgrade to continue.'
    elif percentage >= 90:
        status = 'warning'
        message = f'You have used {percentage:.0f}% of your {metric_type} limit.'
    elif percentage >= 75:
        status = 'approaching'
        message = f'You are approaching your {metric_type} limit.'
    
    return {
        'within_limit': within_limit,
        'usage': current_usage,
        'limit': limit,
        'percentage': round(percentage, 1),
        'status': status,
        'message': message
    }


# ==============================================================================
# TIER VALIDATION AND ENFORCEMENT
# ==============================================================================

class TierViolationError(Exception):
    """Raised when a tier limit is violated."""
    pass


def enforce_tier_limit(tier: str, feature: str, raise_error: bool = True) -> bool:
    """
    Enforce tier limits for a feature.
    
    Args:
        tier: Tier name
        feature: Feature name
        raise_error: If True, raises exception on violation
        
    Returns:
        True if allowed, False if not allowed
        
    Raises:
        TierViolationError: If feature is not allowed and raise_error is True
    """
    allowed = can_use_feature(tier, feature)
    
    if not allowed and raise_error:
        upgrade_info = get_upgrade_path(tier)
        next_tier = upgrade_info.get('next_tier', 'pro')
        
        raise TierViolationError(
            f"'{feature}' is not available in your current '{tier}' tier. "
            f"Upgrade to '{next_tier}' to unlock this feature."
        )
    
    return allowed


# ==============================================================================
# PRICING CALCULATOR
# ==============================================================================

def calculate_cost_savings(tier: str, billing_cycle: str = 'annually') -> dict:
    """
    Calculate cost savings for a tier.
    
    Args:
        tier: Tier name
        billing_cycle: 'monthly' or 'annually'
        
    Returns:
        Dict with cost analysis
    """
    tier_info = TIER_LIMITS.get(tier, {})
    monthly_price = tier_info.get('price_monthly', 0)
    annual_price = tier_info.get('price_annually', 0)
    
    if billing_cycle == 'annually':
        total_cost = annual_price
        monthly_equivalent = annual_price / 12
        savings = (monthly_price * 12) - annual_price
        savings_percentage = (savings / (monthly_price * 12)) * 100 if monthly_price > 0 else 0
    else:
        total_cost = monthly_price * 12
        monthly_equivalent = monthly_price
        savings = 0
        savings_percentage = 0
    
    return {
        'tier': tier,
        'billing_cycle': billing_cycle,
        'monthly_price': monthly_price,
        'annual_price': annual_price,
        'total_annual_cost': total_cost,
        'monthly_equivalent': round(monthly_equivalent, 2),
        'annual_savings': round(savings, 2),
        'savings_percentage': round(savings_percentage, 1)
    }
