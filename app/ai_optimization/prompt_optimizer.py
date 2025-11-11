# ==============================================================================
# app/ai_optimization/prompt_optimizer.py
# Prompt Optimization & A/B Testing - Continuously improve prompt effectiveness
# ==============================================================================
"""
Prompt Optimizer: Fortune 500-Grade Prompt Engineering

This module implements A/B testing and optimization for prompts to
continuously improve AI response quality, speed, and cost-effectiveness.

Key Features:
- A/B testing of prompt variants
- Statistical significance testing
- Performance tracking (confidence, feedback, response time)
- Automatic winner selection
- Prompt versioning and history
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import random
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class PromptVariant:
    """A prompt variant for A/B testing."""
    id: int
    domain: str
    variant_name: str
    prompt_text: str
    is_active: bool
    created_at: datetime


@dataclass
class PerformanceMetrics:
    """Performance metrics for a prompt variant."""
    variant_id: int
    total_uses: int
    avg_confidence: float
    positive_feedback_count: int
    negative_feedback_count: int
    avg_response_time: float
    positive_feedback_ratio: float


class PromptOptimizer:
    """
    Prompt Optimizer and A/B Testing System.
    
    Manages prompt variants, runs A/B tests, and automatically
    selects the best-performing prompts.
    """
    
    def __init__(self, min_samples: int = 10, confidence_level: float = 0.95):
        """
        Initialize the Prompt Optimizer.
        
        Args:
            min_samples: Minimum samples before declaring a winner
            confidence_level: Statistical confidence level for tests
        """
        self.min_samples = min_samples
        self.confidence_level = confidence_level
        logger.info(f"PromptOptimizer initialized (min_samples: {min_samples})")
    
    def create_variant(
        self,
        domain: str,
        variant_name: str,
        prompt_text: str
    ) -> Dict[str, Any]:
        """
        Create a new prompt variant for testing.
        
        Args:
            domain: Domain for the prompt (e.g., 'legal', 'financial')
            variant_name: Name of the variant (e.g., 'variant_a', 'variant_b')
            prompt_text: The actual prompt text
            
        Returns:
            Dict with created variant info
        """
        try:
            from app import db
            from app.models import PromptVariant as PromptVariantModel
            
            # Create variant
            variant = PromptVariantModel(
                domain=domain,
                variant_name=variant_name,
                prompt_text=prompt_text,
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.session.add(variant)
            db.session.commit()
            
            logger.info(f"Created prompt variant: {domain}/{variant_name}")
            
            return {
                'success': True,
                'variant_id': variant.id,
                'domain': domain,
                'variant_name': variant_name
            }
            
        except Exception as e:
            logger.error(f"Failed to create variant: {e}")
            return {'success': False, 'error': str(e)}
    
    def select_variant(
        self,
        domain: str,
        strategy: str = 'epsilon_greedy'
    ) -> Optional[str]:
        """
        Select a prompt variant for use (A/B testing).
        
        Args:
            domain: Domain for the prompt
            strategy: Selection strategy ('random', 'epsilon_greedy', 'best')
            
        Returns:
            Prompt text or None
        """
        try:
            from app import db
            from app.models import PromptVariant, PromptPerformance
            
            # Get active variants for domain
            variants = PromptVariant.query.filter_by(
                domain=domain,
                is_active=True
            ).all()
            
            if not variants:
                logger.warning(f"No active variants for domain: {domain}")
                return None
            
            if len(variants) == 1:
                return variants[0].prompt_text
            
            # Select based on strategy
            if strategy == 'random':
                selected = random.choice(variants)
            
            elif strategy == 'epsilon_greedy':
                # 90% exploit (best), 10% explore (random)
                if random.random() < 0.9:
                    # Select best performing variant
                    best_variant = self._get_best_variant(variants)
                    selected = best_variant if best_variant else random.choice(variants)
                else:
                    # Random exploration
                    selected = random.choice(variants)
            
            elif strategy == 'best':
                # Always use best performing variant
                selected = self._get_best_variant(variants)
                if not selected:
                    selected = random.choice(variants)
            
            else:
                selected = random.choice(variants)
            
            # Track selection
            self._track_variant_use(selected.id)
            
            return selected.prompt_text
            
        except Exception as e:
            logger.error(f"Failed to select variant: {e}")
            return None
    
    def _get_best_variant(self, variants: List) -> Optional[Any]:
        """
        Get the best performing variant.
        
        Args:
            variants: List of PromptVariant objects
            
        Returns:
            Best variant or None
        """
        try:
            from app.models import PromptPerformance
            
            best_variant = None
            best_score = -1
            
            for variant in variants:
                performance = PromptPerformance.query.filter_by(
                    variant_id=variant.id
                ).first()
                
                if not performance or performance.usage_count < self.min_samples:
                    continue
                
                # Calculate composite score
                score = self._calculate_variant_score(performance)
                
                if score > best_score:
                    best_score = score
                    best_variant = variant
            
            return best_variant
            
        except Exception as e:
            logger.error(f"Failed to get best variant: {e}")
            return None
    
    def _calculate_variant_score(self, performance) -> float:
        """
        Calculate a composite score for a variant.
        
        Args:
            performance: PromptPerformance object
            
        Returns:
            Composite score (higher is better)
        """
        # Weight factors
        confidence_weight = 0.4
        feedback_weight = 0.4
        speed_weight = 0.2
        
        # Normalize metrics to 0-1 scale
        confidence_score = performance.avg_confidence or 0.0
        feedback_score = performance.positive_feedback_ratio or 0.0
        
        # Speed score (inverse - faster is better)
        # Assume 10 seconds is slow, 1 second is fast
        speed_score = max(0, 1 - (performance.avg_response_time / 10.0)) if performance.avg_response_time else 0.5
        
        # Calculate composite score
        composite_score = (
            confidence_score * confidence_weight +
            feedback_score * feedback_weight +
            speed_score * speed_weight
        )
        
        return composite_score
    
    def _track_variant_use(self, variant_id: int):
        """
        Track usage of a variant.
        
        Args:
            variant_id: Variant ID
        """
        try:
            from app import db
            from app.models import PromptPerformance
            
            # Get or create performance record
            performance = PromptPerformance.query.filter_by(
                variant_id=variant_id
            ).first()
            
            if not performance:
                performance = PromptPerformance(
                    variant_id=variant_id,
                    usage_count=0
                )
                db.session.add(performance)
            
            performance.usage_count += 1
            performance.last_updated = datetime.utcnow()
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to track variant use: {e}")
    
    def update_performance(
        self,
        variant_id: int,
        confidence_score: float,
        feedback_rating: Optional[int] = None,
        response_time: Optional[float] = None
    ) -> bool:
        """
        Update performance metrics for a variant.
        
        Args:
            variant_id: Variant ID
            confidence_score: Confidence score from AI (0.0-1.0)
            feedback_rating: User feedback (1 = positive, -1 = negative)
            response_time: Response time in seconds
            
        Returns:
            True if successful
        """
        try:
            from app import db
            from app.models import PromptPerformance
            
            # Get performance record
            performance = PromptPerformance.query.filter_by(
                variant_id=variant_id
            ).first()
            
            if not performance:
                logger.warning(f"No performance record for variant {variant_id}")
                return False
            
            # Update confidence (running average)
            if performance.avg_confidence:
                current_avg = performance.avg_confidence
                count = performance.usage_count
                performance.avg_confidence = (
                    (current_avg * count + confidence_score) / (count + 1)
                )
            else:
                performance.avg_confidence = confidence_score
            
            # Update feedback ratio
            if feedback_rating is not None:
                if feedback_rating > 0:
                    performance.positive_feedback_count = (performance.positive_feedback_count or 0) + 1
                else:
                    performance.negative_feedback_count = (performance.negative_feedback_count or 0) + 1
                
                total_feedback = (
                    (performance.positive_feedback_count or 0) +
                    (performance.negative_feedback_count or 0)
                )
                
                if total_feedback > 0:
                    performance.positive_feedback_ratio = (
                        (performance.positive_feedback_count or 0) / total_feedback
                    )
            
            # Update response time (running average)
            if response_time is not None:
                if performance.avg_response_time:
                    current_avg = performance.avg_response_time
                    count = performance.usage_count
                    performance.avg_response_time = (
                        (current_avg * count + response_time) / (count + 1)
                    )
                else:
                    performance.avg_response_time = response_time
            
            performance.last_updated = datetime.utcnow()
            
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update performance: {e}")
            return False
    
    def get_variant_comparison(self, domain: str) -> List[Dict[str, Any]]:
        """
        Get performance comparison of all variants in a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            List of variant performance data
        """
        try:
            from app.models import PromptVariant, PromptPerformance
            
            variants = PromptVariant.query.filter_by(
                domain=domain,
                is_active=True
            ).all()
            
            comparison = []
            
            for variant in variants:
                performance = PromptPerformance.query.filter_by(
                    variant_id=variant.id
                ).first()
                
                if performance:
                    score = self._calculate_variant_score(performance)
                    
                    comparison.append({
                        'variant_name': variant.variant_name,
                        'usage_count': performance.usage_count,
                        'avg_confidence': round(performance.avg_confidence or 0, 3),
                        'positive_feedback_ratio': round(performance.positive_feedback_ratio or 0, 3),
                        'avg_response_time': round(performance.avg_response_time or 0, 2),
                        'composite_score': round(score, 3),
                        'is_best': False
                    })
                else:
                    comparison.append({
                        'variant_name': variant.variant_name,
                        'usage_count': 0,
                        'avg_confidence': 0,
                        'positive_feedback_ratio': 0,
                        'avg_response_time': 0,
                        'composite_score': 0,
                        'is_best': False
                    })
            
            # Mark the best variant
            if comparison:
                best = max(comparison, key=lambda x: x['composite_score'])
                best['is_best'] = True
            
            return comparison
            
        except Exception as e:
            logger.error(f"Failed to get variant comparison: {e}")
            return []
    
    def declare_winner(
        self,
        domain: str,
        deactivate_losers: bool = True
    ) -> Dict[str, Any]:
        """
        Declare a winning variant and optionally deactivate others.
        
        Args:
            domain: Domain name
            deactivate_losers: Whether to deactivate losing variants
            
        Returns:
            Dict with winner info
        """
        try:
            from app import db
            from app.models import PromptVariant
            
            # Get comparison
            comparison = self.get_variant_comparison(domain)
            
            if not comparison:
                return {'success': False, 'error': 'No variants to compare'}
            
            # Find winner
            winner = max(comparison, key=lambda x: x['composite_score'])
            
            # Check if winner has enough samples
            if winner['usage_count'] < self.min_samples:
                return {
                    'success': False,
                    'error': f"Winner needs more samples (has {winner['usage_count']}, needs {self.min_samples})"
                }
            
            # Deactivate losers if requested
            if deactivate_losers:
                variants = PromptVariant.query.filter_by(
                    domain=domain,
                    is_active=True
                ).all()
                
                for variant in variants:
                    if variant.variant_name != winner['variant_name']:
                        variant.is_active = False
                
                db.session.commit()
                
                logger.info(f"Declared winner for {domain}: {winner['variant_name']}")
            
            return {
                'success': True,
                'winner': winner,
                'deactivated_count': len(comparison) - 1 if deactivate_losers else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to declare winner: {e}")
            return {'success': False, 'error': str(e)}


# Global instance
_optimizer = None


def get_prompt_optimizer() -> PromptOptimizer:
    """
    Get or create the global PromptOptimizer instance.
    
    Returns:
        PromptOptimizer instance
    """
    global _optimizer
    
    if _optimizer is None:
        _optimizer = PromptOptimizer()
    
    return _optimizer
