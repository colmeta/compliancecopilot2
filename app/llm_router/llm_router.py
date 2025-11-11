# ==============================================================================
# app/llm_router/llm_router.py
# Multi-LLM Router with Automatic Failover
# ==============================================================================
"""
LLM Router: Enterprise-Grade Multi-Provider System

This router manages multiple LLM providers and automatically fails over
when one provider has issues. Never goes down.

Priority Order (by default):
1. Groq (fastest, cheapest for simple tasks)
2. Gemini Flash (fast, cheap)
3. Gemini Pro (balanced)
4. OpenAI GPT-4 (highest quality)
5. Claude Sonnet (excellent quality)

Failover Strategy:
- Try primary provider
- On error, try next provider
- Track provider health
- Prefer healthy providers
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import os
import time

logger = logging.getLogger(__name__)


@dataclass
class LLMProvider:
    """Configuration for an LLM provider."""
    name: str
    provider_type: str  # 'google', 'openai', 'anthropic', 'groq'
    model: str
    api_key: Optional[str]
    priority: int  # Lower = higher priority
    cost_per_1k_input: float
    cost_per_1k_output: float
    speed_score: float  # 0.0-1.0, higher = faster
    quality_score: float  # 0.0-1.0, higher = better
    is_available: bool = True
    error_count: int = 0
    last_error: Optional[datetime] = None


@dataclass
class LLMResponse:
    """Response from an LLM."""
    text: str
    provider: str
    model: str
    tokens_input: int
    tokens_output: int
    cost: float
    latency: float
    success: bool


class LLMRouter:
    """
    Multi-LLM Router with Automatic Failover.
    
    Manages multiple LLM providers and routes requests intelligently.
    """
    
    def __init__(self):
        """Initialize the LLM Router with all available providers."""
        self.providers: List[LLMProvider] = []
        self._initialize_providers()
        logger.info(f"LLMRouter initialized with {len(self.providers)} providers")
    
    def _initialize_providers(self):
        """Initialize all available LLM providers."""
        
        # Groq - FASTEST (for simple tasks)
        if os.getenv('GROQ_API_KEY'):
            self.providers.append(LLMProvider(
                name='groq_llama',
                provider_type='groq',
                model='llama-3.1-70b-versatile',
                api_key=os.getenv('GROQ_API_KEY'),
                priority=1,
                cost_per_1k_input=0.0,  # Free tier
                cost_per_1k_output=0.0,
                speed_score=1.0,  # Fastest
                quality_score=0.85
            ))
            self.providers.append(LLMProvider(
                name='groq_mixtral',
                provider_type='groq',
                model='mixtral-8x7b-32768',
                api_key=os.getenv('GROQ_API_KEY'),
                priority=2,
                cost_per_1k_input=0.0,
                cost_per_1k_output=0.0,
                speed_score=0.95,
                quality_score=0.80
            ))
        
        # Google Gemini - BALANCED
        if os.getenv('GOOGLE_API_KEY'):
            self.providers.append(LLMProvider(
                name='gemini_flash',
                provider_type='google',
                model='gemini-pro',
                api_key=os.getenv('GOOGLE_API_KEY'),
                priority=3,
                cost_per_1k_input=0.000075,
                cost_per_1k_output=0.0003,
                speed_score=0.95,
                quality_score=0.75
            ))
            self.providers.append(LLMProvider(
                name='gemini_pro',
                provider_type='google',
                model='gemini-1.5-pro',
                api_key=os.getenv('GOOGLE_API_KEY'),
                priority=4,
                cost_per_1k_input=0.00125,
                cost_per_1k_output=0.005,
                speed_score=0.70,
                quality_score=0.90
            ))
        
        # OpenAI - HIGH QUALITY
        if os.getenv('OPENAI_API_KEY'):
            self.providers.append(LLMProvider(
                name='gpt4_turbo',
                provider_type='openai',
                model='gpt-4-turbo-preview',
                api_key=os.getenv('OPENAI_API_KEY'),
                priority=5,
                cost_per_1k_input=0.01,
                cost_per_1k_output=0.03,
                speed_score=0.60,
                quality_score=0.98
            ))
            self.providers.append(LLMProvider(
                name='gpt35_turbo',
                provider_type='openai',
                model='gpt-3.5-turbo',
                api_key=os.getenv('OPENAI_API_KEY'),
                priority=6,
                cost_per_1k_input=0.0005,
                cost_per_1k_output=0.0015,
                speed_score=0.85,
                quality_score=0.80
            ))
        
        # Anthropic Claude - EXCELLENT QUALITY
        if os.getenv('ANTHROPIC_API_KEY'):
            self.providers.append(LLMProvider(
                name='claude_sonnet',
                provider_type='anthropic',
                model='claude-3-5-sonnet-20241022',
                api_key=os.getenv('ANTHROPIC_API_KEY'),
                priority=7,
                cost_per_1k_input=0.003,
                cost_per_1k_output=0.015,
                speed_score=0.75,
                quality_score=0.95
            ))
            self.providers.append(LLMProvider(
                name='claude_haiku',
                provider_type='anthropic',
                model='claude-3-haiku-20240307',
                api_key=os.getenv('ANTHROPIC_API_KEY'),
                priority=8,
                cost_per_1k_input=0.00025,
                cost_per_1k_output=0.00125,
                speed_score=0.90,
                quality_score=0.85
            ))
        
        # Sort by priority
        self.providers.sort(key=lambda x: x.priority)
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        optimization_goal: str = 'balanced'  # 'speed', 'cost', 'quality', 'balanced'
    ) -> LLMResponse:
        """
        Generate text using the best available LLM with automatic failover.
        
        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            optimization_goal: What to optimize for
            
        Returns:
            LLMResponse with generated text and metadata
        """
        # Select providers based on optimization goal
        sorted_providers = self._sort_providers_by_goal(optimization_goal)
        
        # Try each provider until one succeeds
        for provider in sorted_providers:
            if not provider.is_available:
                continue
            
            try:
                logger.info(f"Trying provider: {provider.name}")
                response = self._call_provider(provider, prompt, max_tokens, temperature)
                
                if response.success:
                    # Reset error count on success
                    provider.error_count = 0
                    return response
                
            except Exception as e:
                logger.warning(f"Provider {provider.name} failed: {e}")
                self._handle_provider_error(provider, str(e))
                continue
        
        # All providers failed
        raise Exception("All LLM providers failed. Please check API keys and connectivity.")
    
    def _sort_providers_by_goal(self, goal: str) -> List[LLMProvider]:
        """Sort providers based on optimization goal."""
        available = [p for p in self.providers if p.is_available]
        
        if goal == 'speed':
            return sorted(available, key=lambda x: -x.speed_score)
        elif goal == 'cost':
            return sorted(available, key=lambda x: x.cost_per_1k_input)
        elif goal == 'quality':
            return sorted(available, key=lambda x: -x.quality_score)
        else:  # balanced
            return sorted(available, key=lambda x: x.priority)
    
    def _call_provider(
        self,
        provider: LLMProvider,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> LLMResponse:
        """Call a specific LLM provider."""
        start_time = time.time()
        
        if provider.provider_type == 'google':
            response = self._call_google(provider, prompt, max_tokens, temperature)
        elif provider.provider_type == 'openai':
            response = self._call_openai(provider, prompt, max_tokens, temperature)
        elif provider.provider_type == 'anthropic':
            response = self._call_anthropic(provider, prompt, max_tokens, temperature)
        elif provider.provider_type == 'groq':
            response = self._call_groq(provider, prompt, max_tokens, temperature)
        else:
            raise ValueError(f"Unknown provider type: {provider.provider_type}")
        
        latency = time.time() - start_time
        response.latency = latency
        
        return response
    
    def _call_google(self, provider: LLMProvider, prompt: str, max_tokens: int, temperature: float) -> LLMResponse:
        """Call Google Gemini API."""
        import google.generativeai as genai
        
        genai.configure(api_key=provider.api_key)
        model = genai.GenerativeModel(provider.model)
        
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature
            )
        )
        
        text = response.text
        
        # Estimate tokens (rough)
        tokens_input = len(prompt) // 4
        tokens_output = len(text) // 4
        
        cost = (tokens_input / 1000 * provider.cost_per_1k_input +
                tokens_output / 1000 * provider.cost_per_1k_output)
        
        return LLMResponse(
            text=text,
            provider=provider.name,
            model=provider.model,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            cost=cost,
            latency=0.0,
            success=True
        )
    
    def _call_openai(self, provider: LLMProvider, prompt: str, max_tokens: int, temperature: float) -> LLMResponse:
        """Call OpenAI API."""
        import openai
        
        client = openai.OpenAI(api_key=provider.api_key)
        
        response = client.chat.completions.create(
            model=provider.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        text = response.choices[0].message.content
        tokens_input = response.usage.prompt_tokens
        tokens_output = response.usage.completion_tokens
        
        cost = (tokens_input / 1000 * provider.cost_per_1k_input +
                tokens_output / 1000 * provider.cost_per_1k_output)
        
        return LLMResponse(
            text=text,
            provider=provider.name,
            model=provider.model,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            cost=cost,
            latency=0.0,
            success=True
        )
    
    def _call_anthropic(self, provider: LLMProvider, prompt: str, max_tokens: int, temperature: float) -> LLMResponse:
        """Call Anthropic Claude API."""
        import anthropic
        
        client = anthropic.Anthropic(api_key=provider.api_key)
        
        response = client.messages.create(
            model=provider.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        
        text = response.content[0].text
        tokens_input = response.usage.input_tokens
        tokens_output = response.usage.output_tokens
        
        cost = (tokens_input / 1000 * provider.cost_per_1k_input +
                tokens_output / 1000 * provider.cost_per_1k_output)
        
        return LLMResponse(
            text=text,
            provider=provider.name,
            model=provider.model,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            cost=cost,
            latency=0.0,
            success=True
        )
    
    def _call_groq(self, provider: LLMProvider, prompt: str, max_tokens: int, temperature: float) -> LLMResponse:
        """Call Groq API."""
        from groq import Groq
        
        client = Groq(api_key=provider.api_key)
        
        response = client.chat.completions.create(
            model=provider.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        text = response.choices[0].message.content
        tokens_input = response.usage.prompt_tokens
        tokens_output = response.usage.completion_tokens
        
        cost = (tokens_input / 1000 * provider.cost_per_1k_input +
                tokens_output / 1000 * provider.cost_per_1k_output)
        
        return LLMResponse(
            text=text,
            provider=provider.name,
            model=provider.model,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            cost=cost,
            latency=0.0,
            success=True
        )
    
    def _handle_provider_error(self, provider: LLMProvider, error: str):
        """Handle provider error and update health status."""
        provider.error_count += 1
        provider.last_error = datetime.utcnow()
        
        # Disable provider after 3 consecutive errors
        if provider.error_count >= 3:
            provider.is_available = False
            logger.error(f"Provider {provider.name} disabled after 3 errors")
        
        # Re-enable after 5 minutes
        if provider.last_error and (datetime.utcnow() - provider.last_error) > timedelta(minutes=5):
            provider.is_available = True
            provider.error_count = 0
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers."""
        return {
            'total_providers': len(self.providers),
            'available_providers': len([p for p in self.providers if p.is_available]),
            'providers': [
                {
                    'name': p.name,
                    'model': p.model,
                    'available': p.is_available,
                    'error_count': p.error_count,
                    'speed_score': p.speed_score,
                    'quality_score': p.quality_score
                }
                for p in self.providers
            ]
        }


# Global instance
_router = None


def get_llm_router() -> LLMRouter:
    """Get or create the global LLMRouter instance."""
    global _router
    
    if _router is None:
        _router = LLMRouter()
    
    return _router
