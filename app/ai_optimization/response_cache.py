# ==============================================================================
# app/ai_optimization/response_cache.py
# Redis Response Caching System - The Speed Demon
# ==============================================================================
"""
This module provides intelligent response caching for CLARITY.
Uses Redis with semantic similarity matching to cache and retrieve AI responses.
"""

import logging
import json
import hashlib
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from app.models import User, Subscription
from app import db
import redis
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from config import Config

logger = logging.getLogger(__name__)

# ==============================================================================
# RESPONSE CACHE
# ==============================================================================

class ResponseCache:
    """
    Intelligent response caching system with semantic similarity matching.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize Redis connection
        try:
            self.redis_client = redis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                db=Config.REDIS_DB,
                decode_responses=True
            )
            self.redis_client.ping()
            self.logger.info("Redis connection established for response caching")
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis for caching: {e}")
            self.redis_client = None
        
        # Initialize embedding model for semantic similarity
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.logger.info("Embedding model loaded for semantic caching")
        except Exception as e:
            self.logger.error(f"Failed to load embedding model: {e}")
            self.embedding_model = None
        
        # Cache configuration
        self.cache_config = {
            'default_ttl': 3600,  # 1 hour
            'similarity_threshold': 0.85,  # 85% similarity threshold
            'max_cache_size': 10000,  # Maximum number of cached responses
            'embedding_dimension': 384  # Dimension of embeddings
        }
    
    def cache_response(self, user_id: int, prompt: str, response: str, model_id: str,
                      task_type: str, metadata: Dict[str, Any] = None,
                      ttl: int = None) -> Dict[str, Any]:
        """
        Cache an AI response with semantic indexing.
        
        Args:
            user_id: ID of the user
            prompt: The prompt that generated the response
            response: The AI response to cache
            model_id: Model that generated the response
            task_type: Type of task performed
            metadata: Additional metadata (optional)
            ttl: Time to live in seconds (optional)
            
        Returns:
            Dict with caching result
        """
        try:
            if not self.redis_client:
                return {'success': False, 'error': 'Redis not available'}
            
            # Generate cache key
            cache_key = self._generate_cache_key(user_id, prompt, model_id, task_type)
            
            # Prepare cache data
            cache_data = {
                'prompt': prompt,
                'response': response,
                'model_id': model_id,
                'task_type': task_type,
                'user_id': user_id,
                'cached_at': datetime.utcnow().isoformat(),
                'metadata': json.dumps(metadata) if metadata else None
            }
            
            # Store in Redis
            ttl = ttl or self.cache_config['default_ttl']
            self.redis_client.hset(cache_key, mapping=cache_data)
            self.redis_client.expire(cache_key, ttl)
            
            # Generate and store semantic embedding
            if self.embedding_model:
                embedding = self._generate_embedding(prompt)
                embedding_key = f"embedding:{cache_key}"
                self.redis_client.set(embedding_key, json.dumps(embedding.tolist()))
                self.redis_client.expire(embedding_key, ttl)
            
            # Update cache statistics
            self._update_cache_stats(user_id, 'cache_hit' if False else 'cache_miss')
            
            # Log caching event
            from app.security.audit_logger import log_user_action
            log_user_action(
                user_id=user_id,
                action='response_cached',
                resource_type='cache',
                details={
                    'model_id': model_id,
                    'task_type': task_type,
                    'prompt_length': len(prompt),
                    'response_length': len(response)
                }
            )
            
            self.logger.info(f"Response cached for user {user_id}: {cache_key}")
            
            return {
                'success': True,
                'cache_key': cache_key,
                'cached_at': cache_data['cached_at'],
                'ttl': ttl
            }
            
        except Exception as e:
            self.logger.error(f"Failed to cache response: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_cached_response(self, user_id: int, prompt: str, model_id: str,
                          task_type: str, similarity_threshold: float = None) -> Dict[str, Any]:
        """
        Retrieve a cached response using semantic similarity.
        
        Args:
            user_id: ID of the user
            prompt: The prompt to find a response for
            model_id: Model that should have generated the response
            task_type: Type of task
            similarity_threshold: Minimum similarity threshold (optional)
            
        Returns:
            Dict with cached response or None if not found
        """
        try:
            if not self.redis_client:
                return {'success': False, 'error': 'Redis not available'}
            
            similarity_threshold = similarity_threshold or self.cache_config['similarity_threshold']
            
            # First, try exact match
            exact_key = self._generate_cache_key(user_id, prompt, model_id, task_type)
            exact_match = self.redis_client.hgetall(exact_key)
            
            if exact_match:
                self._update_cache_stats(user_id, 'exact_hit')
                return {
                    'success': True,
                    'cached': True,
                    'response': exact_match['response'],
                    'model_id': exact_match['model_id'],
                    'cached_at': exact_match['cached_at'],
                    'match_type': 'exact',
                    'similarity': 1.0
                }
            
            # If no exact match, try semantic similarity
            if self.embedding_model:
                semantic_match = self._find_semantic_match(
                    user_id, prompt, model_id, task_type, similarity_threshold
                )
                
                if semantic_match:
                    self._update_cache_stats(user_id, 'semantic_hit')
                    return semantic_match
            
            # No match found
            self._update_cache_stats(user_id, 'cache_miss')
            return {
                'success': True,
                'cached': False,
                'message': 'No cached response found'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get cached response: {e}")
            return {'success': False, 'error': str(e)}
    
    def invalidate_cache(self, user_id: int = None, model_id: str = None,
                        task_type: str = None, pattern: str = None) -> Dict[str, Any]:
        """
        Invalidate cached responses based on criteria.
        
        Args:
            user_id: Invalidate for specific user (optional)
            model_id: Invalidate for specific model (optional)
            task_type: Invalidate for specific task type (optional)
            pattern: Custom pattern to match (optional)
            
        Returns:
            Dict with invalidation result
        """
        try:
            if not self.redis_client:
                return {'success': False, 'error': 'Redis not available'}
            
            # Build pattern for key matching
            if pattern:
                key_pattern = pattern
            else:
                key_parts = ['cache']
                if user_id:
                    key_parts.append(f"user:{user_id}")
                if model_id:
                    key_parts.append(f"model:{model_id}")
                if task_type:
                    key_parts.append(f"task:{task_type}")
                
                key_pattern = ":".join(key_parts) + ":*"
            
            # Find matching keys
            matching_keys = self.redis_client.keys(key_pattern)
            
            if not matching_keys:
                return {
                    'success': True,
                    'invalidated_count': 0,
                    'message': 'No matching cache entries found'
                }
            
            # Delete matching keys and their embeddings
            deleted_count = 0
            for key in matching_keys:
                # Delete main cache entry
                if self.redis_client.delete(key):
                    deleted_count += 1
                
                # Delete associated embedding
                embedding_key = f"embedding:{key}"
                self.redis_client.delete(embedding_key)
            
            # Log invalidation
            if user_id:
                from app.security.audit_logger import log_user_action
                log_user_action(
                    user_id=user_id,
                    action='cache_invalidated',
                    resource_type='cache',
                    details={
                        'pattern': key_pattern,
                        'deleted_count': deleted_count
                    }
                )
            
            self.logger.info(f"Cache invalidated: {deleted_count} entries deleted")
            
            return {
                'success': True,
                'invalidated_count': deleted_count,
                'pattern': key_pattern
            }
            
        except Exception as e:
            self.logger.error(f"Failed to invalidate cache: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_cache_stats(self, user_id: int = None) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Args:
            user_id: Get stats for specific user (optional)
            
        Returns:
            Dict with cache statistics
        """
        try:
            if not self.redis_client:
                return {'success': False, 'error': 'Redis not available'}
            
            # Get cache keys
            if user_id:
                key_pattern = f"cache:user:{user_id}:*"
            else:
                key_pattern = "cache:*"
            
            cache_keys = self.redis_client.keys(key_pattern)
            
            # Calculate statistics
            total_entries = len(cache_keys)
            total_size = 0
            
            # Get size of each cache entry
            for key in cache_keys:
                size = self.redis_client.memory_usage(key)
                if size:
                    total_size += size
            
            # Get hit/miss statistics
            hit_stats = self._get_hit_miss_stats(user_id)
            
            # Get model distribution
            model_distribution = self._get_model_distribution(cache_keys)
            
            # Get task type distribution
            task_distribution = self._get_task_distribution(cache_keys)
            
            return {
                'success': True,
                'user_id': user_id,
                'statistics': {
                    'total_entries': total_entries,
                    'total_size_bytes': total_size,
                    'total_size_mb': round(total_size / (1024 * 1024), 2),
                    'hit_miss_ratio': hit_stats,
                    'model_distribution': model_distribution,
                    'task_distribution': task_distribution
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get cache stats: {e}")
            return {'success': False, 'error': str(e)}
    
    # ==============================================================================
    # HELPER METHODS
    # ==============================================================================
    
    def _generate_cache_key(self, user_id: int, prompt: str, model_id: str, task_type: str) -> str:
        """Generate a unique cache key."""
        # Create a hash of the prompt for consistent keys
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:16]
        return f"cache:user:{user_id}:model:{model_id}:task:{task_type}:{prompt_hash}"
    
    def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text."""
        if not self.embedding_model:
            return np.zeros(self.cache_config['embedding_dimension'])
        
        try:
            embedding = self.embedding_model.encode(text)
            return embedding
        except Exception as e:
            self.logger.error(f"Failed to generate embedding: {e}")
            return np.zeros(self.cache_config['embedding_dimension'])
    
    def _find_semantic_match(self, user_id: int, prompt: str, model_id: str,
                           task_type: str, similarity_threshold: float) -> Optional[Dict[str, Any]]:
        """Find semantically similar cached responses."""
        try:
            # Generate embedding for the prompt
            prompt_embedding = self._generate_embedding(prompt)
            
            # Get all cache keys for the user and model
            key_pattern = f"cache:user:{user_id}:model:{model_id}:task:{task_type}:*"
            cache_keys = self.redis_client.keys(key_pattern)
            
            best_match = None
            best_similarity = 0.0
            
            for cache_key in cache_keys:
                # Get embedding for this cache entry
                embedding_key = f"embedding:{cache_key}"
                embedding_data = self.redis_client.get(embedding_key)
                
                if embedding_data:
                    cached_embedding = np.array(json.loads(embedding_data))
                    
                    # Calculate cosine similarity
                    similarity = cosine_similarity(
                        prompt_embedding.reshape(1, -1),
                        cached_embedding.reshape(1, -1)
                    )[0][0]
                    
                    if similarity > similarity_threshold and similarity > best_similarity:
                        # Get the cached response
                        cache_data = self.redis_client.hgetall(cache_key)
                        if cache_data:
                            best_match = {
                                'success': True,
                                'cached': True,
                                'response': cache_data['response'],
                                'model_id': cache_data['model_id'],
                                'cached_at': cache_data['cached_at'],
                                'match_type': 'semantic',
                                'similarity': float(similarity),
                                'original_prompt': cache_data['prompt']
                            }
                            best_similarity = similarity
            
            return best_match
            
        except Exception as e:
            self.logger.error(f"Failed to find semantic match: {e}")
            return None
    
    def _update_cache_stats(self, user_id: int, stat_type: str):
        """Update cache hit/miss statistics."""
        try:
            if not self.redis_client:
                return
            
            # Update user-specific stats
            user_stats_key = f"cache_stats:user:{user_id}"
            self.redis_client.hincrby(user_stats_key, stat_type, 1)
            self.redis_client.expire(user_stats_key, 7 * 24 * 60 * 60)  # 7 days
            
            # Update global stats
            global_stats_key = "cache_stats:global"
            self.redis_client.hincrby(global_stats_key, stat_type, 1)
            self.redis_client.expire(global_stats_key, 7 * 24 * 60 * 60)  # 7 days
            
        except Exception as e:
            self.logger.error(f"Failed to update cache stats: {e}")
    
    def _get_hit_miss_stats(self, user_id: int = None) -> Dict[str, int]:
        """Get hit/miss statistics."""
        try:
            if not self.redis_client:
                return {}
            
            if user_id:
                stats_key = f"cache_stats:user:{user_id}"
            else:
                stats_key = "cache_stats:global"
            
            stats = self.redis_client.hgetall(stats_key)
            
            return {
                'exact_hits': int(stats.get('exact_hit', 0)),
                'semantic_hits': int(stats.get('semantic_hit', 0)),
                'cache_misses': int(stats.get('cache_miss', 0))
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get hit/miss stats: {e}")
            return {}
    
    def _get_model_distribution(self, cache_keys: List[str]) -> Dict[str, int]:
        """Get distribution of cached responses by model."""
        distribution = {}
        
        for key in cache_keys:
            try:
                cache_data = self.redis_client.hgetall(key)
                model_id = cache_data.get('model_id')
                if model_id:
                    distribution[model_id] = distribution.get(model_id, 0) + 1
            except Exception:
                continue
        
        return distribution
    
    def _get_task_distribution(self, cache_keys: List[str]) -> Dict[str, int]:
        """Get distribution of cached responses by task type."""
        distribution = {}
        
        for key in cache_keys:
            try:
                cache_data = self.redis_client.hgetall(key)
                task_type = cache_data.get('task_type')
                if task_type:
                    distribution[task_type] = distribution.get(task_type, 0) + 1
            except Exception:
                continue
        
        return distribution

# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

def cache_response(user_id: int, prompt: str, response: str, model_id: str,
                  task_type: str, metadata: Dict[str, Any] = None,
                  ttl: int = None) -> Dict[str, Any]:
    """Cache an AI response."""
    cache = ResponseCache()
    return cache.cache_response(user_id, prompt, response, model_id, task_type, metadata, ttl)

def get_cached_response(user_id: int, prompt: str, model_id: str,
                       task_type: str, similarity_threshold: float = None) -> Dict[str, Any]:
    """Get a cached response."""
    cache = ResponseCache()
    return cache.get_cached_response(user_id, prompt, model_id, task_type, similarity_threshold)

def invalidate_cache(user_id: int = None, model_id: str = None,
                    task_type: str = None, pattern: str = None) -> Dict[str, Any]:
    """Invalidate cached responses."""
    cache = ResponseCache()
    return cache.invalidate_cache(user_id, model_id, task_type, pattern)

def get_cache_stats(user_id: int = None) -> Dict[str, Any]:
    """Get cache statistics."""
    cache = ResponseCache()
    return cache.get_cache_stats(user_id)

