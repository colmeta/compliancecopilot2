"""
app/middleware/rate_limiter.py

Simple per-user rate limiter middleware. Uses Redis if available, otherwise
falls back to an in-memory token bucket (not suitable for multi-process).

Provides a decorator `rate_limit` to protect endpoints.
"""

import functools
import logging
import time
from typing import Callable, Optional

from flask import jsonify, g

logger = logging.getLogger(__name__)

_redis_client = None
try:
    import redis
    _redis_client = redis.StrictRedis.from_url('redis://localhost:6379/0')
except Exception:
    _redis_client = None

# In-memory fallback store: {key: (tokens, last_ts)}
_memory_store = {}


def _get_redis_key(user_id: int, endpoint: str) -> str:
    return f"rate:{user_id}:{endpoint}"


def rate_limit(calls: int = 60, period: int = 60, by_user: bool = True):
    """Decorator to rate limit endpoint.

    Args:
        calls: number of allowed calls
        period: period in seconds
        by_user: if True, rate limit per user (uses g.current_user.id)
    """
    def decorator(f: Callable):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            user = getattr(g, 'current_user', None)
            if by_user and not user:
                return jsonify({'error': 'Authentication required for rate-limited endpoint'}), 401

            key = _get_redis_key(user.id if user else 'anon', f.__name__)

            # Try Redis first
            if _redis_client:
                try:
                    # Use INCR with EXPIRE for simple rate limiting
                    count = _redis_client.incr(key)
                    if count == 1:
                        _redis_client.expire(key, period)
                    if int(count) > calls:
                        ttl = _redis_client.ttl(key)
                        return jsonify({'error': 'Rate limit exceeded', 'retry_after': ttl}), 429
                except Exception as e:
                    logger.exception(f"Redis rate limiter error: {e}")

            else:
                # In-memory token bucket fallback
                now = time.time()
                entry = _memory_store.get(key)
                if not entry:
                    _memory_store[key] = {'count': 1, 'ts': now}
                else:
                    if now - entry['ts'] > period:
                        # reset
                        _memory_store[key] = {'count': 1, 'ts': now}
                    else:
                        entry['count'] += 1
                        if entry['count'] > calls:
                            retry_after = int(period - (now - entry['ts']))
                            return jsonify({'error': 'Rate limit exceeded', 'retry_after': retry_after}), 429

            return f(*args, **kwargs)

        return wrapped
    return decorator
