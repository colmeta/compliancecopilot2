"""
CLARITY ENGINE - MULTI-PROVIDER AI SYSTEM
Automatic fallback across Anthropic, Groq, OpenAI, and Gemini
"""

import os
import time
import logging
from typing import Optional, Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

class MultiProviderAI:
    """
    AI provider router with automatic fallback
    
    Priority order:
    1. Anthropic Claude (best quality)
    2. Groq (fastest, generous free tier)
    3. OpenAI GPT-4 (most versatile)
    4. Google Gemini (backup)
    """
    
    def __init__(self):
        self.providers = self._initialize_providers()
        self.provider_stats = {
            'anthropic': {'calls': 0, 'failures': 0, 'total_time': 0},
            'groq': {'calls': 0, 'failures': 0, 'total_time': 0},
            'openai': {'calls': 0, 'failures': 0, 'total_time': 0},
            'gemini': {'calls': 0, 'failures': 0, 'total_time': 0}
        }
    
    def _initialize_providers(self) -> List[Dict[str, Any]]:
        """Initialize all available AI providers"""
        providers = []
        
        # 1. Anthropic Claude (BEST QUALITY)
        if os.getenv('ANTHROPIC_API_KEY'):
            try:
                import anthropic
                providers.append({
                    'name': 'anthropic',
                    'client': anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY')),
                    'model': 'claude-3-5-sonnet-20241022',
                    'priority': 1,
                    'description': 'Claude 3.5 Sonnet - Best quality',
                    'cost_per_1k': 0.003  # $3 per million input tokens
                })
                logger.info("✅ Anthropic Claude initialized")
            except Exception as e:
                logger.warning(f"⚠️  Anthropic unavailable: {e}")
        
        # 2. Groq (FASTEST + GENEROUS FREE TIER)
        if os.getenv('GROQ_API_KEY'):
            try:
                import groq
                providers.append({
                    'name': 'groq',
                    'client': groq.Groq(api_key=os.getenv('GROQ_API_KEY')),
                    'model': 'llama-3.1-70b-versatile',
                    'priority': 2,
                    'description': 'Llama 3.1 70B - Fastest',
                    'cost_per_1k': 0.0005  # Very cheap
                })
                logger.info("✅ Groq initialized")
            except Exception as e:
                logger.warning(f"⚠️  Groq unavailable: {e}")
        
        # 3. OpenAI (MOST VERSATILE)
        if os.getenv('OPENAI_API_KEY'):
            try:
                import openai
                providers.append({
                    'name': 'openai',
                    'client': openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY')),
                    'model': 'gpt-4o',  # GPT-4 Optimized
                    'priority': 3,
                    'description': 'GPT-4o - Most versatile',
                    'cost_per_1k': 0.0025  # $2.50 per million input tokens
                })
                logger.info("✅ OpenAI initialized")
            except Exception as e:
                logger.warning(f"⚠️  OpenAI unavailable: {e}")
        
        # 4. Google Gemini (BACKUP)
        if os.getenv('GOOGLE_API_KEY'):
            try:
                import google.generativeai as genai
                genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
                providers.append({
                    'name': 'gemini',
                    'client': genai.GenerativeModel('gemini-pro'),
                    'model': 'gemini-pro',
                    'priority': 4,
                    'description': 'Gemini Pro - Backup',
                    'cost_per_1k': 0.0005
                })
                logger.info("✅ Google Gemini initialized")
            except Exception as e:
                logger.warning(f"⚠️  Gemini unavailable: {e}")
        
        # Sort by priority
        providers.sort(key=lambda x: x['priority'])
        
        if not providers:
            logger.error("🚨 NO AI PROVIDERS AVAILABLE!")
        else:
            logger.info(f"🎯 {len(providers)} AI providers ready: {[p['name'] for p in providers]}")
        
        return providers
    
    def generate(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7,
                 preferred_provider: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Generate text with automatic fallback
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum response length
            temperature: Creativity (0-1)
            preferred_provider: Try this provider first (optional)
        
        Returns:
            (generated_text, metadata)
        """
        if not self.providers:
            raise Exception("No AI providers available. Please set API keys.")
        
        # Reorder if preferred provider specified
        providers_to_try = self.providers.copy()
        if preferred_provider:
            providers_to_try.sort(key=lambda x: (
                0 if x['name'] == preferred_provider else x['priority']
            ))
        
        last_error = None
        
        for provider in providers_to_try:
            try:
                start_time = time.time()
                
                logger.info(f"🤖 Trying {provider['name']} ({provider['description']})...")
                
                # Generate based on provider
                result = self._generate_with_provider(
                    provider, prompt, max_tokens, temperature
                )
                
                elapsed = time.time() - start_time
                
                # Update stats
                self.provider_stats[provider['name']]['calls'] += 1
                self.provider_stats[provider['name']]['total_time'] += elapsed
                
                metadata = {
                    'provider': provider['name'],
                    'model': provider['model'],
                    'time_taken': round(elapsed, 2),
                    'cost_estimate': self._estimate_cost(prompt, result, provider),
                    'success': True
                }
                
                logger.info(f"✅ {provider['name']} succeeded in {elapsed:.2f}s")
                
                return result, metadata
                
            except Exception as e:
                self.provider_stats[provider['name']]['failures'] += 1
                last_error = str(e)
                logger.warning(f"❌ {provider['name']} failed: {e}")
                continue
        
        # All providers failed
        raise Exception(
            f"All AI providers failed. Last error: {last_error}. "
            f"Tried: {[p['name'] for p in providers_to_try]}"
        )
    
    def _generate_with_provider(self, provider: Dict, prompt: str, 
                                max_tokens: int, temperature: float) -> str:
        """Generate text with specific provider"""
        
        if provider['name'] == 'anthropic':
            response = provider['client'].messages.create(
                model=provider['model'],
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        
        elif provider['name'] == 'groq':
            response = provider['client'].chat.completions.create(
                model=provider['model'],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        
        elif provider['name'] == 'openai':
            response = provider['client'].chat.completions.create(
                model=provider['model'],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        
        elif provider['name'] == 'gemini':
            response = provider['client'].generate_content(
                prompt,
                generation_config={
                    'max_output_tokens': max_tokens,
                    'temperature': temperature
                }
            )
            return response.text
        
        else:
            raise ValueError(f"Unknown provider: {provider['name']}")
    
    def _estimate_cost(self, prompt: str, response: str, provider: Dict) -> float:
        """Estimate API cost for this call"""
        # Rough estimation: 1 token ≈ 4 characters
        input_tokens = len(prompt) / 4
        output_tokens = len(response) / 4
        total_tokens = input_tokens + output_tokens
        
        cost_per_token = provider['cost_per_1k'] / 1000
        return round(total_tokens * cost_per_token, 6)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get provider usage statistics"""
        stats = {
            'total_calls': sum(p['calls'] for p in self.provider_stats.values()),
            'total_failures': sum(p['failures'] for p in self.provider_stats.values()),
            'providers': {}
        }
        
        for name, data in self.provider_stats.items():
            if data['calls'] > 0:
                stats['providers'][name] = {
                    'calls': data['calls'],
                    'failures': data['failures'],
                    'success_rate': round((1 - data['failures'] / max(data['calls'], 1)) * 100, 2),
                    'avg_time': round(data['total_time'] / data['calls'], 2)
                }
        
        return stats
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        return [p['name'] for p in self.providers]
    
    def get_provider_info(self) -> List[Dict[str, Any]]:
        """Get detailed info about all providers"""
        return [{
            'name': p['name'],
            'model': p['model'],
            'description': p['description'],
            'priority': p['priority'],
            'available': True
        } for p in self.providers]


# Global instance
_multi_provider_instance = None

def get_multi_provider() -> MultiProviderAI:
    """Get or create global multi-provider instance"""
    global _multi_provider_instance
    if _multi_provider_instance is None:
        _multi_provider_instance = MultiProviderAI()
    return _multi_provider_instance
