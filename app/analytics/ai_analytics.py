"""
app/analytics/ai_analytics.py

Lightweight AI performance logging and analysis helpers used by Phase 4.

Provides:
- log_model_performance: records model choice, latency, confidence, and metadata
- summarize_recent_performance: small helper to compute averages from PromptPerformance and AnalyticsSnapshot

This module intentionally keeps DB access simple and non-blocking.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from app import db
from app.models import PromptPerformance, AnalyticsSnapshot

logger = logging.getLogger(__name__)


def log_model_performance(variant_id: Optional[int], model_name: str, latency_s: float,
						  confidence: Optional[float], user_id: Optional[int] = None,
						  additional: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
	"""Record a quick prompt/model performance snapshot into PromptPerformance.

	Args:
		variant_id: optional PromptVariant id this run used
		model_name: model identifier
		latency_s: response time in seconds
		confidence: model confidence score (0-1)
		user_id: optional user id
		additional: optional metadata

	Returns:
		dict with success and record id when applicable
	"""
	try:
		# Create or update a PromptPerformance summary row
		if variant_id:
			perf = PromptPerformance.query.filter_by(variant_id=variant_id).first()
			if not perf:
				perf = PromptPerformance(variant_id=variant_id, usage_count=1,
										 avg_confidence=confidence or 0.0,
										 avg_response_time=latency_s)
				db.session.add(perf)
			else:
				# Running average updates
				prev_count = perf.usage_count or 0
				new_count = prev_count + 1
				perf.avg_confidence = ((perf.avg_confidence or 0.0) * prev_count + (confidence or 0.0)) / new_count
				perf.avg_response_time = ((perf.avg_response_time or 0.0) * prev_count + latency_s) / new_count
				perf.usage_count = new_count
			perf.last_updated = datetime.utcnow()
			db.session.commit()

		# Also write an AnalyticsSnapshot for time-series storage
		snapshot = AnalyticsSnapshot(
			user_id=user_id,
			date=datetime.utcnow().date(),
			metric_name=f'model_latency_{model_name}',
			value=latency_s,
			metadata=json.dumps(additional) if additional else None
		)
		db.session.add(snapshot)
		db.session.commit()

		return {'success': True}
	except Exception as e:
		logger.exception(f"Failed to log model performance: {e}")
		try:
			db.session.rollback()
		except Exception:
			pass
		return {'success': False, 'error': str(e)}


def summarize_recent_performance(days: int = 7):
	"""Return simple aggregates for the last N days from AnalyticsSnapshot."""
	cutoff = datetime.utcnow().date() - timedelta(days=days)
	rows = AnalyticsSnapshot.query.filter(AnalyticsSnapshot.date >= cutoff).all()
	summary = {}
	for r in rows:
		summary.setdefault(r.metric_name, {'count': 0, 'sum': 0.0})
		summary[r.metric_name]['count'] += 1
		summary[r.metric_name]['sum'] += float(r.value or 0.0)

	# Compute averages
	for k, v in summary.items():
		v['avg'] = v['sum'] / v['count'] if v['count'] else 0.0

	return summary

