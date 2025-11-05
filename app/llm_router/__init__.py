# ==============================================================================
# app/llm_router/__init__.py
# Multi-LLM Failover Router - Never Goes Down
# ==============================================================================
"""
The CLARITY Multi-LLM Router: Enterprise-Grade Reliability

This module provides automatic failover across multiple LLM providers:
- Google Gemini (Flash, Pro, Ultra)
- OpenAI (GPT-4, GPT-3.5-turbo)
- Anthropic Claude (Opus, Sonnet, Haiku)
- Groq (Llama, Mixtral - super fast)

Features:
- Automatic failover on errors
- Load balancing
- Cost optimization
- Speed prioritization
- Quality prioritization
- Provider health monitoring
"""

from .llm_router import LLMRouter, LLMProvider, LLMResponse

__all__ = ['LLMRouter', 'LLMProvider', 'LLMResponse']
