# ==============================================================================
# app/ai_optimization/prompt_optimizer.py
# A/B Testing Framework for Prompt Optimization - The Prompt Lab
# ==============================================================================
"""
This module provides prompt optimization through A/B testing for CLARITY.
Tests different prompt variants and optimizes for effectiveness.
"""

import logging
import json
import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import desc, and_, or_
from app.models import User, PromptVariant, PromptPerformance, AuditLog
from app import db

logger = logging.getLogger(__name__)

# ==============================================================================
# PROMPT OPTIMIZER
# ==============================================================================

class PromptOptimizer:
    """
    A/B testing framework for prompt optimization.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def optimize_prompt(self, user_id: int, domain: str, base_prompt: str,
                       optimization_goal: str = 'effectiveness') -> Dict[str, Any]:
        """
        Optimize a prompt using A/B testing.
        
        Args:
            user_id: ID of the user
            domain: Domain of the prompt (e.g., 'legal', 'financial', 'security')
            base_prompt: Base prompt to optimize
            optimization_goal: Goal for optimization ('effectiveness', 'speed', 'cost')
            
        Returns:
            Dict with optimization result
        """
        try:
            # Get existing variants for the domain
            existing_variants = PromptVariant.query.filter_by(
                domain=domain,
                is_active=True
            ).all()
            
            # Create new variants if needed
            if len(existing_variants) < 3:  # Need at least 3 variants for A/B testing
                new_variants = self._generate_prompt_variants(base_prompt, domain)
                
                for i, variant_text in enumerate(new_variants):
                    variant = PromptVariant(
                        domain=domain,
                        variant_name=f'variant_{len(existing_variants) + i + 1}',
                        prompt_text=variant_text,
                        created_by=user_id
                    )
                    db.session.add(variant)
                
                db.session.commit()
                
                # Refresh variants list
                existing_variants = PromptVariant.query.filter_by(
                    domain=domain,
                    is_active=True
                ).all()
            
            # Select variant for testing
            selected_variant = self._select_variant_for_testing(existing_variants, user_id)
            
            # Log optimization attempt
            from app.security.audit_logger import log_user_action
            log_user_action(
                user_id=user_id,
                action='prompt_optimization',
                resource_type='prompt',
                details={
                    'domain': domain,
                    'selected_variant': selected_variant.variant_name,
                    'optimization_goal': optimization_goal
                }
            )
            
            return {
                'success': True,
                'domain': domain,
                'selected_variant': {
                    'id': selected_variant.id,
                    'name': selected_variant.variant_name,
                    'text': selected_variant.prompt_text
                },
                'total_variants': len(existing_variants),
                'optimization_goal': optimization_goal,
                'testing_strategy': self._get_testing_strategy(selected_variant)
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to optimize prompt: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_prompt_variants(self, user_id: int, domain: str, test_duration_days: int = 7) -> Dict[str, Any]:
        """
        Run A/B testing for prompt variants.
        
        Args:
            user_id: ID of the user running the test
            domain: Domain to test
            test_duration_days: Duration of the test in days
            
        Returns:
            Dict with testing result
        """
        try:
            # Get active variants for the domain
            variants = PromptVariant.query.filter_by(
                domain=domain,
                is_active=True
            ).all()
            
            if len(variants) < 2:
                return {
                    'success': False,
                    'error': 'Need at least 2 variants for A/B testing'
                }
            
            # Get performance data for variants
            variant_performance = {}
            for variant in variants:
                performance = PromptPerformance.query.filter_by(variant_id=variant.id).first()
                variant_performance[variant.id] = {
                    'variant_name': variant.variant_name,
                    'prompt_text': variant.prompt_text,
                    'performance': performance
                }
            
            # Calculate test statistics
            test_stats = self._calculate_test_statistics(variant_performance)
            
            # Determine winner
            winner = self._determine_winner(variant_performance)
            
            # Generate recommendations
            recommendations = self._generate_optimization_recommendations(
                variant_performance, winner, test_stats
            )
            
            # Log testing completion
            from app.security.audit_logger import log_user_action
            log_user_action(
                user_id=user_id,
                action='prompt_testing_completed',
                resource_type='prompt',
                details={
                    'domain': domain,
                    'test_duration_days': test_duration_days,
                    'winner': winner['variant_name'] if winner else None,
                    'total_variants': len(variants)
                }
            )
            
            return {
                'success': True,
                'domain': domain,
                'test_duration_days': test_duration_days,
                'variants_tested': len(variants),
                'test_statistics': test_stats,
                'winner': winner,
                'recommendations': recommendations,
                'completed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to test prompt variants: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_prompt_performance(self, domain: str = None, variant_id: int = None) -> Dict[str, Any]:
        """
        Get performance metrics for prompts.
        
        Args:
            domain: Filter by domain (optional)
            variant_id: Filter by specific variant (optional)
            
        Returns:
            Dict with performance metrics
        """
        try:
            # Build query
            query = PromptVariant.query.filter_by(is_active=True)
            
            if domain:
                query = query.filter_by(domain=domain)
            
            if variant_id:
                query = query.filter_by(id=variant_id)
            
            variants = query.all()
            
            if not variants:
                return {
                    'success': True,
                    'performance_metrics': [],
                    'message': 'No variants found'
                }
            
            # Get performance data
            performance_metrics = []
            for variant in variants:
                performance = PromptPerformance.query.filter_by(variant_id=variant.id).first()
                
                metrics = {
                    'variant_id': variant.id,
                    'variant_name': variant.variant_name,
                    'domain': variant.domain,
                    'prompt_text': variant.prompt_text,
                    'created_at': variant.created_at.isoformat(),
                    'performance': {
                        'usage_count': performance.usage_count if performance else 0,
                        'avg_confidence': performance.avg_confidence if performance else 0,
                        'positive_feedback_ratio': performance.positive_feedback_ratio if performance else 0,
                        'avg_response_time': performance.avg_response_time if performance else 0,
                        'last_updated': performance.last_updated.isoformat() if performance else None
                    }
                }
                
                # Calculate effectiveness score
                metrics['effectiveness_score'] = self._calculate_effectiveness_score(performance)
                
                performance_metrics.append(metrics)
            
            # Sort by effectiveness score
            performance_metrics.sort(key=lambda x: x['effectiveness_score'], reverse=True)
            
            return {
                'success': True,
                'performance_metrics': performance_metrics,
                'total_variants': len(performance_metrics)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get prompt performance: {e}")
            return {'success': False, 'error': str(e)}
    
    def deploy_optimal_prompt(self, user_id: int, domain: str, variant_id: int) -> Dict[str, Any]:
        """
        Deploy the optimal prompt variant.
        
        Args:
            user_id: ID of the user deploying the prompt
            domain: Domain of the prompt
            variant_id: ID of the variant to deploy
            
        Returns:
            Dict with deployment result
        """
        try:
            # Get the variant to deploy
            variant = PromptVariant.query.get(variant_id)
            if not variant:
                return {'success': False, 'error': 'Variant not found'}
            
            if variant.domain != domain:
                return {'success': False, 'error': 'Variant domain mismatch'}
            
            # Deactivate other variants in the same domain
            other_variants = PromptVariant.query.filter(
                and_(
                    PromptVariant.domain == domain,
                    PromptVariant.id != variant_id,
                    PromptVariant.is_active == True
                )
            ).all()
            
            for other_variant in other_variants:
                other_variant.is_active = False
            
            # Mark the selected variant as the primary one
            variant.is_active = True
            
            db.session.commit()
            
            # Log deployment
            from app.security.audit_logger import log_user_action
            log_user_action(
                user_id=user_id,
                action='prompt_deployed',
                resource_type='prompt',
                details={
                    'domain': domain,
                    'variant_id': variant_id,
                    'variant_name': variant.variant_name,
                    'deactivated_variants': len(other_variants)
                }
            )
            
            self.logger.info(f"Optimal prompt deployed for domain {domain}: {variant.variant_name}")
            
            return {
                'success': True,
                'domain': domain,
                'deployed_variant': {
                    'id': variant.id,
                    'name': variant.variant_name,
                    'text': variant.prompt_text
                },
                'deactivated_variants': len(other_variants),
                'deployed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to deploy optimal prompt: {e}")
            return {'success': False, 'error': str(e)}
    
    # ==============================================================================
    # HELPER METHODS
    # ==============================================================================
    
    def _generate_prompt_variants(self, base_prompt: str, domain: str) -> List[str]:
        """Generate optimized variants of a base prompt."""
        variants = []
        
        # Domain-specific optimizations
        domain_optimizations = {
            'legal': {
                'precision': "Please provide a precise legal analysis with specific references to relevant laws and precedents.",
                'clarity': "Please provide a clear and concise legal explanation that a non-lawyer can understand.",
                'comprehensive': "Please provide a comprehensive legal analysis covering all relevant aspects and potential implications."
            },
            'financial': {
                'accuracy': "Please provide accurate financial analysis with specific numbers and calculations.",
                'risk_assessment': "Please include a detailed risk assessment and mitigation strategies.",
                'compliance': "Please ensure compliance with financial regulations and standards."
            },
            'security': {
                'threat_analysis': "Please provide a detailed threat analysis with specific security recommendations.",
                'vulnerability_assessment': "Please identify potential vulnerabilities and provide remediation steps.",
                'incident_response': "Please provide incident response procedures and best practices."
            }
        }
        
        # Get domain-specific templates
        domain_templates = domain_optimizations.get(domain, {})
        
        # Generate variants
        for template_name, template_text in domain_templates.items():
            variant = f"{base_prompt}\n\n{template_text}"
            variants.append(variant)
        
        # Add general optimization variants
        general_variants = [
            f"{base_prompt}\n\nPlease provide a detailed and comprehensive response.",
            f"{base_prompt}\n\nPlease provide a concise and actionable response.",
            f"{base_prompt}\n\nPlease provide a response with specific examples and evidence."
        ]
        
        variants.extend(general_variants)
        
        return variants[:5]  # Limit to 5 variants
    
    def _select_variant_for_testing(self, variants: List[PromptVariant], user_id: int) -> PromptVariant:
        """Select a variant for testing using weighted random selection."""
        if not variants:
            return None
        
        # Calculate weights based on current performance
        weights = []
        for variant in variants:
            performance = PromptPerformance.query.filter_by(variant_id=variant.id).first()
            
            if performance and performance.usage_count > 0:
                # Weight inversely proportional to usage (explore less used variants)
                weight = 1.0 / (performance.usage_count + 1)
            else:
                # Higher weight for untested variants
                weight = 1.0
            
            weights.append(weight)
        
        # Normalize weights
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        # Select variant based on weights
        selected_variant = random.choices(variants, weights=normalized_weights)[0]
        
        return selected_variant
    
    def _get_testing_strategy(self, variant: PromptVariant) -> Dict[str, Any]:
        """Get testing strategy for a variant."""
        performance = PromptPerformance.query.filter_by(variant_id=variant.id).first()
        
        if not performance or performance.usage_count < 10:
            return {
                'phase': 'exploration',
                'target_samples': 50,
                'description': 'Initial testing phase to gather baseline performance data'
            }
        elif performance.usage_count < 100:
            return {
                'phase': 'validation',
                'target_samples': 200,
                'description': 'Validation phase to confirm performance improvements'
            }
        else:
            return {
                'phase': 'optimization',
                'target_samples': 500,
                'description': 'Optimization phase to fine-tune performance'
            }
    
    def _calculate_test_statistics(self, variant_performance: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate A/B testing statistics."""
        stats = {
            'total_variants': len(variant_performance),
            'total_usage': 0,
            'avg_confidence': 0,
            'avg_response_time': 0,
            'confidence_interval': 0.95
        }
        
        total_usage = 0
        total_confidence = 0
        total_response_time = 0
        valid_variants = 0
        
        for variant_data in variant_performance.values():
            performance = variant_data['performance']
            if performance:
                total_usage += performance.usage_count
                total_confidence += performance.avg_confidence or 0
                total_response_time += performance.avg_response_time or 0
                valid_variants += 1
        
        if valid_variants > 0:
            stats['total_usage'] = total_usage
            stats['avg_confidence'] = total_confidence / valid_variants
            stats['avg_response_time'] = total_response_time / valid_variants
        
        return stats
    
    def _determine_winner(self, variant_performance: Dict[int, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Determine the winning variant based on performance metrics."""
        if not variant_performance:
            return None
        
        best_variant = None
        best_score = -1
        
        for variant_id, variant_data in variant_performance.items():
            performance = variant_data['performance']
            
            if performance and performance.usage_count >= 10:  # Minimum sample size
                # Calculate composite score
                score = self._calculate_effectiveness_score(performance)
                
                if score > best_score:
                    best_score = score
                    best_variant = {
                        'variant_id': variant_id,
                        'variant_name': variant_data['variant_name'],
                        'effectiveness_score': score,
                        'usage_count': performance.usage_count,
                        'avg_confidence': performance.avg_confidence,
                        'avg_response_time': performance.avg_response_time
                    }
        
        return best_variant
    
    def _calculate_effectiveness_score(self, performance: PromptPerformance) -> float:
        """Calculate effectiveness score for a prompt variant."""
        if not performance or performance.usage_count == 0:
            return 0.0
        
        # Weighted combination of metrics
        confidence_score = (performance.avg_confidence or 0) * 0.4
        feedback_score = (performance.positive_feedback_ratio or 0) * 0.3
        speed_score = max(0, 1 - (performance.avg_response_time or 0) / 10) * 0.2
        usage_score = min(performance.usage_count / 100, 1.0) * 0.1
        
        return confidence_score + feedback_score + speed_score + usage_score
    
    def _generate_optimization_recommendations(self, variant_performance: Dict[int, Dict[str, Any]],
                                            winner: Optional[Dict[str, Any]],
                                            test_stats: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate optimization recommendations based on test results."""
        recommendations = []
        
        if winner:
            recommendations.append({
                'type': 'deployment',
                'title': 'Deploy Winning Variant',
                'description': f"Deploy '{winner['variant_name']}' as the primary prompt for this domain",
                'priority': 'high'
            })
        
        # Analyze performance gaps
        for variant_id, variant_data in variant_performance.items():
            performance = variant_data['performance']
            if performance and performance.usage_count < 10:
                recommendations.append({
                    'type': 'testing',
                    'title': 'Increase Sample Size',
                    'description': f"Increase testing for '{variant_data['variant_name']}' to reach statistical significance",
                    'priority': 'medium'
                })
        
        # Performance improvement suggestions
        if test_stats['avg_confidence'] < 0.8:
            recommendations.append({
                'type': 'optimization',
                'title': 'Improve Prompt Clarity',
                'description': 'Consider refining prompts to improve confidence scores',
                'priority': 'medium'
            })
        
        if test_stats['avg_response_time'] > 3.0:
            recommendations.append({
                'type': 'optimization',
                'title': 'Optimize for Speed',
                'description': 'Consider shorter, more direct prompts to improve response times',
                'priority': 'low'
            })
        
        return recommendations

# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

def optimize_prompt(user_id: int, domain: str, base_prompt: str,
                   optimization_goal: str = 'effectiveness') -> Dict[str, Any]:
    """Optimize a prompt using A/B testing."""
    optimizer = PromptOptimizer()
    return optimizer.optimize_prompt(user_id, domain, base_prompt, optimization_goal)

def test_prompt_variants(user_id: int, domain: str, test_duration_days: int = 7) -> Dict[str, Any]:
    """Run A/B testing for prompt variants."""
    optimizer = PromptOptimizer()
    return optimizer.test_prompt_variants(user_id, domain, test_duration_days)

def get_prompt_performance(domain: str = None, variant_id: int = None) -> Dict[str, Any]:
    """Get performance metrics for prompts."""
    optimizer = PromptOptimizer()
    return optimizer.get_prompt_performance(domain, variant_id)

def deploy_optimal_prompt(user_id: int, domain: str, variant_id: int) -> Dict[str, Any]:
    """Deploy the optimal prompt variant."""
    optimizer = PromptOptimizer()
    return optimizer.deploy_optimal_prompt(user_id, domain, variant_id)

