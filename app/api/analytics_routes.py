# ==============================================================================
# app/api/analytics_routes.py
# Analytics API Routes - The Intelligence Dashboard Gateway
# ==============================================================================
"""
This module provides API endpoints for analytics and insights.
Includes user analytics, admin analytics, AI performance tracking, and business intelligence.
"""

from flask import Blueprint, request, jsonify, current_app, g
from functools import wraps
import logging
from app.api.routes import api_key_required
from app.middleware.tier_check import check_tier_limit, require_tier
from app.analytics.user_analytics import UserAnalyticsManager
from app.analytics.admin_analytics import AdminAnalyticsManager
from app.analytics.ai_performance import AIPerformanceTracker
from app.models import User, Subscription

# Configure logging
logger = logging.getLogger(__name__)

# Create analytics blueprint
analytics = Blueprint('analytics', __name__)

# ==============================================================================
# USER ANALYTICS ENDPOINTS
# ==============================================================================

@analytics.route('/user/usage', methods=['GET'])
@api_key_required
def get_user_usage_analytics():
    """
    Get user usage analytics and statistics.
    
    Available for all tiers with different detail levels.
    
    Query Parameters:
        - days: Number of days to analyze (default: 30, max: 365)
    
    Response:
        - statistics: User usage statistics
        - period_days: Analysis period
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get query parameters
        days = min(int(request.args.get('days', 30)), 365)  # Cap at 365 days
        
        # Get user's subscription tier
        subscription = Subscription.query.filter_by(user_id=user.id, status='active').first()
        user_tier = subscription.tier if subscription else 'free'
        
        # Check tier limits for analytics detail
        if user_tier == 'free' and days > 30:
            days = 30  # Free tier limited to 30 days
        
        # Get usage analytics
        manager = UserAnalyticsManager()
        result = manager.get_user_usage_stats(user.id, days)
        
        if result['success']:
            return jsonify({
                'success': True,
                'user_id': user.id,
                'user_tier': user_tier,
                'period_days': days,
                'analytics': result['statistics']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get user usage analytics endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics.route('/user/documents', methods=['GET'])
@api_key_required
def get_user_document_analytics():
    """
    Get user document analytics.
    
    Available for all tiers.
    
    Query Parameters:
        - days: Number of days to analyze (default: 30)
    
    Response:
        - analytics: Document analytics data
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get query parameters
        days = int(request.args.get('days', 30))
        
        # Get document analytics
        manager = UserAnalyticsManager()
        result = manager.get_user_document_analytics(user.id, days)
        
        if result['success']:
            return jsonify({
                'success': True,
                'user_id': user.id,
                'analytics': result['analytics']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get user document analytics endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics.route('/user/workspaces', methods=['GET'])
@api_key_required
def get_user_workspace_analytics():
    """
    Get user workspace analytics.
    
    Available for all tiers.
    
    Response:
        - analytics: Workspace analytics data
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get workspace analytics
        manager = UserAnalyticsManager()
        result = manager.get_user_workspace_analytics(user.id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'user_id': user.id,
                'analytics': result['analytics']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get user workspace analytics endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics.route('/user/insights', methods=['GET'])
@api_key_required
def get_user_performance_insights():
    """
    Get user performance insights and recommendations.
    
    Available for all tiers.
    
    Query Parameters:
        - days: Number of days to analyze (default: 30)
    
    Response:
        - performance: Performance insights and recommendations
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get query parameters
        days = int(request.args.get('days', 30))
        
        # Get performance insights
        manager = UserAnalyticsManager()
        result = manager.get_user_performance_insights(user.id, days)
        
        if result['success']:
            return jsonify({
                'success': True,
                'user_id': user.id,
                'user_tier': result['user_tier'],
                'period_days': days,
                'performance': result['performance']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get user performance insights endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==============================================================================
# ADMIN ANALYTICS ENDPOINTS (Require Admin Access)
# ==============================================================================

@analytics.route('/admin/system', methods=['GET'])
@api_key_required
@require_tier('enterprise')  # Only enterprise users can access admin analytics
def get_admin_system_metrics():
    """
    Get system-wide metrics for administrators.
    
    Available for Enterprise tier only.
    
    Query Parameters:
        - days: Number of days to analyze (default: 30)
    
    Response:
        - metrics: System-wide metrics
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get query parameters
        days = int(request.args.get('days', 30))
        
        # Get system metrics
        manager = AdminAnalyticsManager()
        result = manager.get_system_metrics(days)
        
        if result['success']:
            return jsonify({
                'success': True,
                'period_days': days,
                'metrics': result['metrics']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get admin system metrics endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics.route('/admin/engagement', methods=['GET'])
@api_key_required
@require_tier('enterprise')
def get_admin_engagement_metrics():
    """
    Get user engagement metrics for administrators.
    
    Available for Enterprise tier only.
    
    Query Parameters:
        - days: Number of days to analyze (default: 30)
    
    Response:
        - engagement: User engagement metrics
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get query parameters
        days = int(request.args.get('days', 30))
        
        # Get engagement metrics
        manager = AdminAnalyticsManager()
        result = manager.get_user_engagement_metrics(days)
        
        if result['success']:
            return jsonify({
                'success': True,
                'period_days': days,
                'engagement': result['engagement']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get admin engagement metrics endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics.route('/admin/business', methods=['GET'])
@api_key_required
@require_tier('enterprise')
def get_admin_business_metrics():
    """
    Get business metrics for administrators.
    
    Available for Enterprise tier only.
    
    Query Parameters:
        - days: Number of days to analyze (default: 30)
    
    Response:
        - business: Business metrics
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get query parameters
        days = int(request.args.get('days', 30))
        
        # Get business metrics
        manager = AdminAnalyticsManager()
        result = manager.get_business_metrics(days)
        
        if result['success']:
            return jsonify({
                'success': True,
                'period_days': days,
                'business': result['business']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get admin business metrics endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics.route('/admin/compliance', methods=['GET'])
@api_key_required
@require_tier('enterprise')
def get_admin_compliance_metrics():
    """
    Get compliance metrics for administrators.
    
    Available for Enterprise tier only.
    
    Query Parameters:
        - days: Number of days to analyze (default: 30)
    
    Response:
        - compliance: Compliance metrics
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get query parameters
        days = int(request.args.get('days', 30))
        
        # Get compliance metrics
        manager = AdminAnalyticsManager()
        result = manager.get_compliance_metrics(days)
        
        if result['success']:
            return jsonify({
                'success': True,
                'period_days': days,
                'compliance': result['compliance']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get admin compliance metrics endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==============================================================================
# AI PERFORMANCE ENDPOINTS
# ==============================================================================

@analytics.route('/ai/performance', methods=['GET'])
@api_key_required
@check_tier_limit('ai_performance_tracking', 1)
def get_ai_performance_metrics():
    """
    Get AI performance metrics.
    
    Available for Pro and Enterprise tiers.
    
    Query Parameters:
        - days: Number of days to analyze (default: 30)
    
    Response:
        - ai_performance: AI performance metrics
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get query parameters
        days = int(request.args.get('days', 30))
        
        # Get AI performance metrics
        manager = AdminAnalyticsManager()
        result = manager.get_ai_performance_metrics(days)
        
        if result['success']:
            return jsonify({
                'success': True,
                'period_days': days,
                'ai_performance': result['ai_performance']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get AI performance metrics endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics.route('/ai/models', methods=['GET'])
@api_key_required
@check_tier_limit('ai_performance_tracking', 1)
def get_model_performance_stats():
    """
    Get AI model performance statistics.
    
    Available for Pro and Enterprise tiers.
    
    Query Parameters:
        - days: Number of days to analyze (default: 30)
    
    Response:
        - model_performance: Model performance statistics
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get query parameters
        days = int(request.args.get('days', 30))
        
        # Get model performance stats
        tracker = AIPerformanceTracker()
        result = tracker.get_model_performance_stats(days)
        
        if result['success']:
            return jsonify({
                'success': True,
                'period_days': days,
                'model_performance': result['model_performance']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get model performance stats endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics.route('/ai/prompts', methods=['GET'])
@api_key_required
@check_tier_limit('ai_performance_tracking', 1)
def get_prompt_effectiveness_metrics():
    """
    Get prompt effectiveness metrics for A/B testing.
    
    Available for Pro and Enterprise tiers.
    
    Query Parameters:
        - domain: Specific domain to analyze (optional)
    
    Response:
        - prompt_metrics: Prompt effectiveness metrics
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get query parameters
        domain = request.args.get('domain')
        
        # Get prompt effectiveness metrics
        tracker = AIPerformanceTracker()
        result = tracker.get_prompt_effectiveness_metrics(domain)
        
        if result['success']:
            return jsonify({
                'success': True,
                'domain': domain,
                'prompt_metrics': result['prompt_metrics'],
                'effectiveness_ranking': result['effectiveness_ranking']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get prompt effectiveness metrics endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics.route('/ai/quality', methods=['GET'])
@api_key_required
@check_tier_limit('ai_performance_tracking', 1)
def get_ai_quality_metrics():
    """
    Get AI response quality metrics.
    
    Available for Pro and Enterprise tiers.
    
    Query Parameters:
        - days: Number of days to analyze (default: 30)
    
    Response:
        - quality_metrics: AI quality metrics
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get query parameters
        days = int(request.args.get('days', 30))
        
        # Get quality metrics
        tracker = AIPerformanceTracker()
        result = tracker.get_quality_metrics(days)
        
        if result['success']:
            return jsonify({
                'success': True,
                'period_days': days,
                'quality_metrics': result['quality_metrics']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get AI quality metrics endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics.route('/ai/cost-optimization', methods=['GET'])
@api_key_required
@require_tier('enterprise')  # Only enterprise users can access cost optimization
def get_cost_optimization_metrics():
    """
    Get cost optimization metrics.
    
    Available for Enterprise tier only.
    
    Query Parameters:
        - days: Number of days to analyze (default: 30)
    
    Response:
        - cost_optimization: Cost optimization metrics
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get query parameters
        days = int(request.args.get('days', 30))
        
        # Get cost optimization metrics
        tracker = AIPerformanceTracker()
        result = tracker.get_cost_optimization_metrics(days)
        
        if result['success']:
            return jsonify({
                'success': True,
                'period_days': days,
                'cost_optimization': result['cost_optimization']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"Get cost optimization metrics endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==============================================================================
# ANALYTICS SNAPSHOT ENDPOINTS
# ==============================================================================

@analytics.route('/user/snapshot', methods=['POST'])
@api_key_required
def create_user_analytics_snapshot():
    """
    Create a daily analytics snapshot for the current user.
    
    Available for all tiers.
    
    Request:
        - date: Date for snapshot (ISO format, optional, defaults to today)
    
    Response:
        - snapshot: Created snapshot information
    """
    try:
        # Get current user
        user = g.current_user
        
        # Get request data
        data = request.get_json() or {}
        date_str = data.get('date')
        
        # Parse date if provided
        date = None
        if date_str:
            from datetime import datetime
            try:
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
            except ValueError:
                return jsonify({'error': 'Invalid date format'}), 400
        
        # Create snapshot
        manager = UserAnalyticsManager()
        result = manager.create_analytics_snapshot(user.id, date)
        
        if result['success']:
            return jsonify({
                'success': True,
                'snapshot': result['snapshot']
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
    except Exception as e:
        logger.error(f"Create user analytics snapshot endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==============================================================================
# ERROR HANDLERS
# ==============================================================================

@analytics.errorhandler(404)
def not_found(e):
    """Handle not found errors."""
    return jsonify({
        'error': 'Resource not found',
        'message': 'The requested analytics resource could not be found'
    }), 404

@analytics.errorhandler(403)
def forbidden(e):
    """Handle forbidden errors."""
    return jsonify({
        'error': 'Access forbidden',
        'message': 'You do not have permission to access this analytics resource'
    }), 403

