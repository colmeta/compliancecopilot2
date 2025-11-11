# ==============================================================================
# app/expense_management/cost_optimizer.py
# Cost Optimizer - AI-Powered Cost Reduction Intelligence
# ==============================================================================
"""
Cost Optimizer: CFO-Grade Cost Reduction Intelligence

This system analyzes spending patterns and provides actionable cost-cutting
recommendations using AI-powered analysis.

Capabilities:
- Identify duplicate/unnecessary spending
- Vendor consolidation opportunities
- Contract renegotiation recommendations
- Budget optimization suggestions
- Seasonal spending analysis
- Category-specific cost reduction strategies
"""

import logging
from typing import Dict, Any, List
import pandas as pd
import os
import google.generativeai as genai
import json

logger = logging.getLogger(__name__)


class CostOptimizer:
    """
    Cost Optimizer: AI-Powered Cost Reduction.
    
    Analyzes expense patterns and generates cost-cutting strategies.
    """
    
    def __init__(self):
        """Initialize the Cost Optimizer."""
        try:
            genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            self.initialized = True
            logger.info("CostOptimizer initialized - AI-Powered Cost Reduction Ready")
        except Exception as e:
            logger.error(f"Failed to initialize CostOptimizer: {e}")
            self.initialized = False
    
    def analyze_and_optimize(
        self,
        expense_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Analyze expenses and generate optimization recommendations.
        
        Args:
            expense_data: DataFrame with expense records
            
        Returns:
            Dict with optimization recommendations
        """
        if not self.initialized:
            return {'error': 'Cost Optimizer not initialized'}
        
        try:
            # Prepare expense summary
            summary = self._create_expense_summary(expense_data)
            
            # Generate AI-powered recommendations
            recommendations = self._generate_ai_recommendations(summary)
            
            # Calculate potential savings
            total_savings = sum(rec.get('estimated_savings', 0) for rec in recommendations)
            
            return {
                'success': True,
                'current_monthly_spend': summary.get('total_monthly', 0),
                'potential_monthly_savings': total_savings,
                'savings_percentage': (total_savings / summary.get('total_monthly', 1)) * 100,
                'recommendations': recommendations,
                'summary': summary
            }
            
        except Exception as e:
            logger.error(f"Optimization error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_expense_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create a summary of expense patterns."""
        summary = {
            'total_monthly': float(df['amount'].sum()),
            'transaction_count': len(df),
            'avg_transaction': float(df['amount'].mean()),
            'by_category': {},
            'top_vendors': {}
        }
        
        # By category
        if 'category' in df.columns:
            category_totals = df.groupby('category')['amount'].sum().to_dict()
            summary['by_category'] = {k: float(v) for k, v in category_totals.items()}
        
        # Top vendors
        if 'vendor' in df.columns:
            top_vendors = df.groupby('vendor')['amount'].sum().nlargest(10).to_dict()
            summary['top_vendors'] = {k: float(v) for k, v in top_vendors.items()}
        
        return summary
    
    def _generate_ai_recommendations(self, summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate AI-powered cost optimization recommendations."""
        if not self.initialized:
            return []
        
        try:
            prompt = f"""You are a CFO and cost optimization expert. Analyze the following expense data and provide specific, actionable cost-cutting recommendations.

EXPENSE SUMMARY:
- Total Monthly Spend: ${summary.get('total_monthly', 0):.2f}
- Number of Transactions: {summary.get('transaction_count', 0)}
- Average Transaction: ${summary.get('avg_transaction', 0):.2f}

SPENDING BY CATEGORY:
{json.dumps(summary.get('by_category', {}), indent=2)}

TOP VENDORS:
{json.dumps(summary.get('top_vendors', {}), indent=2)}

YOUR MISSION: Provide 5-7 specific, actionable cost-cutting recommendations. For each recommendation:
1. Identify the opportunity
2. Explain the strategy
3. Estimate potential savings (in dollars per month)
4. Assign priority (high/medium/low)
5. Provide implementation steps

Return your analysis as valid JSON with this structure:
{{
    "recommendations": [
        {{
            "title": "Recommendation title",
            "description": "Detailed explanation of the opportunity",
            "strategy": "How to implement this",
            "estimated_savings": 500.00,
            "priority": "high",
            "implementation_steps": ["Step 1", "Step 2", "Step 3"],
            "timeframe": "immediate" or "short-term" or "long-term"
        }},
        ...
    ]
}}

CRITICAL: Return ONLY valid JSON, no markdown formatting or explanations.

BEGIN ANALYSIS:"""
            
            response = self.model.generate_content(prompt)
            
            # Parse response
            cleaned = response.text.strip().replace('```json', '').replace('```', '').strip()
            parsed = json.loads(cleaned)
            
            return parsed.get('recommendations', [])
            
        except Exception as e:
            logger.error(f"AI recommendation error: {e}")
            return []


# Global instance
_optimizer = None


def get_cost_optimizer() -> CostOptimizer:
    """Get or create the global CostOptimizer instance."""
    global _optimizer
    
    if _optimizer is None:
        _optimizer = CostOptimizer()
    
    return _optimizer
