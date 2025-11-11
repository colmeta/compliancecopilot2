"""
CLARITY Expense Management System
Scan receipts → Extract data → Categorize → Track spending → Optimize costs

Features:
- OCR receipt scanning
- Automatic categorization
- Spending analytics
- Budget tracking
- Cost optimization recommendations
- Export to accounting software
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import re
import json

logger = logging.getLogger(__name__)


class ExpenseManager:
    """
    Manage expenses with OCR receipt scanning and AI categorization
    
    Perfect for:
    - Small businesses tracking expenses
    - Lawyers tracking billable expenses
    - Freelancers managing receipts
    - Startups optimizing costs
    """
    
    # Expense categories (can be customized per business)
    CATEGORIES = {
        'office_supplies': {
            'name': 'Office Supplies',
            'keywords': ['staples', 'office', 'depot', 'paper', 'pen', 'folder', 'printer'],
            'tax_deductible': True,
            'budget_percentage': 5
        },
        'software': {
            'name': 'Software & Subscriptions',
            'keywords': ['software', 'saas', 'subscription', 'license', 'cloud', 'hosting'],
            'tax_deductible': True,
            'budget_percentage': 10
        },
        'meals_entertainment': {
            'name': 'Meals & Entertainment',
            'keywords': ['restaurant', 'cafe', 'coffee', 'lunch', 'dinner', 'catering'],
            'tax_deductible': True,
            'deductible_percentage': 50,
            'budget_percentage': 8
        },
        'travel': {
            'name': 'Travel',
            'keywords': ['hotel', 'airbnb', 'airline', 'uber', 'lyft', 'taxi', 'parking', 'gas'],
            'tax_deductible': True,
            'budget_percentage': 15
        },
        'utilities': {
            'name': 'Utilities',
            'keywords': ['electric', 'water', 'internet', 'phone', 'mobile', 'telecom'],
            'tax_deductible': True,
            'budget_percentage': 5
        },
        'marketing': {
            'name': 'Marketing & Advertising',
            'keywords': ['ads', 'advertising', 'marketing', 'facebook', 'google ads', 'linkedin'],
            'tax_deductible': True,
            'budget_percentage': 12
        },
        'legal_professional': {
            'name': 'Legal & Professional Fees',
            'keywords': ['attorney', 'lawyer', 'consultant', 'accountant', 'professional'],
            'tax_deductible': True,
            'budget_percentage': 5
        },
        'insurance': {
            'name': 'Insurance',
            'keywords': ['insurance', 'premium', 'policy'],
            'tax_deductible': True,
            'budget_percentage': 3
        },
        'equipment': {
            'name': 'Equipment',
            'keywords': ['laptop', 'computer', 'desk', 'chair', 'monitor', 'equipment'],
            'tax_deductible': True,
            'depreciation': True,
            'budget_percentage': 10
        },
        'miscellaneous': {
            'name': 'Miscellaneous',
            'keywords': [],
            'tax_deductible': False,
            'budget_percentage': 2
        }
    }
    
    def __init__(self):
        self.expenses = []  # In production, would use database
    
    def process_receipt(self, ocr_result: Dict, user_id: str = None) -> Dict:
        """
        Process scanned receipt and extract expense data
        
        Args:
            ocr_result: OCR extraction result from OCR engine
            user_id: User/company ID for tracking
        
        Returns:
            {
                'success': bool,
                'expense': {
                    'id': str,
                    'merchant': str,
                    'amount': Decimal,
                    'date': datetime,
                    'category': str,
                    'tax_deductible': bool,
                    'receipt_text': str,
                    'line_items': [...],
                    'payment_method': str
                },
                'recommendations': [...]
            }
        """
        try:
            if not ocr_result.get('success'):
                return {
                    'success': False,
                    'error': 'OCR failed',
                    'message': ocr_result.get('error', 'Could not extract text from receipt')
                }
            
            receipt_text = ocr_result['text']
            
            # Extract key information
            merchant = self._extract_merchant(receipt_text)
            amount = self._extract_amount(receipt_text)
            date = self._extract_date(receipt_text)
            line_items = self._extract_line_items(receipt_text)
            payment_method = self._extract_payment_method(receipt_text)
            
            # Categorize expense
            category = self._categorize_expense(merchant, receipt_text, line_items)
            category_info = self.CATEGORIES.get(category, self.CATEGORIES['miscellaneous'])
            
            # Create expense record
            expense = {
                'id': f"exp_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'user_id': user_id,
                'merchant': merchant,
                'amount': float(amount),
                'date': date.isoformat() if date else datetime.now().isoformat(),
                'category': category,
                'category_name': category_info['name'],
                'tax_deductible': category_info.get('tax_deductible', False),
                'deductible_percentage': category_info.get('deductible_percentage', 100),
                'receipt_text': receipt_text,
                'line_items': line_items,
                'payment_method': payment_method,
                'ocr_confidence': ocr_result.get('confidence', 0),
                'created_at': datetime.now().isoformat()
            }
            
            # Add to tracking (in production, save to database)
            self.expenses.append(expense)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(expense)
            
            return {
                'success': True,
                'expense': expense,
                'recommendations': recommendations,
                'message': f'Expense recorded: ${amount:.2f} at {merchant}'
            }
            
        except Exception as e:
            logger.error(f"Receipt processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to process receipt'
            }
    
    def _extract_merchant(self, text: str) -> str:
        """Extract merchant name from receipt"""
        # Usually merchant is in first few lines
        lines = text.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 3 and len(line) < 50 and not re.match(r'^[\d\s\-\.]+$', line):
                return line
        return "Unknown Merchant"
    
    def _extract_amount(self, text: str) -> Decimal:
        """Extract total amount from receipt"""
        # Look for "Total", "Amount", "Balance Due", etc.
        patterns = [
            r'total[:\s]+\$?([\d,]+\.?\d{0,2})',
            r'amount[:\s]+\$?([\d,]+\.?\d{0,2})',
            r'balance[:\s]+\$?([\d,]+\.?\d{0,2})',
            r'\$\s*([\d,]+\.\d{2})'
        ]
        
        amounts = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    amount_str = match.group(1).replace(',', '')
                    amount = Decimal(amount_str)
                    amounts.append(amount)
                except:
                    continue
        
        # Return largest amount found (usually the total)
        return max(amounts) if amounts else Decimal('0.00')
    
    def _extract_date(self, text: str) -> Optional[datetime]:
        """Extract date from receipt"""
        # Common date patterns
        patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
            r'(\d{2,4})[/-](\d{1,2})[/-](\d{1,2})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    parts = [int(p) for p in match.groups()]
                    # Try different date formats
                    if parts[0] > 31:  # Year first
                        return datetime(parts[0], parts[1], parts[2])
                    elif parts[2] > 31:  # Year last
                        return datetime(parts[2], parts[0], parts[1])
                    else:  # Ambiguous, assume MM/DD/YY
                        year = parts[2] if parts[2] > 100 else 2000 + parts[2]
                        return datetime(year, parts[0], parts[1])
                except:
                    continue
        
        return None
    
    def _extract_line_items(self, text: str) -> List[Dict]:
        """Extract individual line items from receipt"""
        items = []
        lines = text.split('\n')
        
        for line in lines:
            # Look for lines with prices
            match = re.search(r'(.+?)\s+\$?([\d,]+\.?\d{0,2})$', line)
            if match:
                item_name = match.group(1).strip()
                try:
                    price = float(match.group(2).replace(',', ''))
                    if len(item_name) > 2 and price > 0:
                        items.append({
                            'name': item_name,
                            'price': price
                        })
                except:
                    continue
        
        return items
    
    def _extract_payment_method(self, text: str) -> str:
        """Extract payment method from receipt"""
        text_lower = text.lower()
        
        if 'visa' in text_lower:
            return 'Visa'
        elif 'mastercard' in text_lower or 'master card' in text_lower:
            return 'Mastercard'
        elif 'amex' in text_lower or 'american express' in text_lower:
            return 'American Express'
        elif 'cash' in text_lower:
            return 'Cash'
        elif 'check' in text_lower:
            return 'Check'
        elif 'debit' in text_lower:
            return 'Debit Card'
        else:
            return 'Unknown'
    
    def _categorize_expense(self, merchant: str, text: str, line_items: List[Dict]) -> str:
        """Automatically categorize expense using AI/keywords"""
        merchant_lower = merchant.lower()
        text_lower = text.lower()
        
        # Score each category
        scores = {}
        for category_id, category_info in self.CATEGORIES.items():
            score = 0
            keywords = category_info.get('keywords', [])
            
            for keyword in keywords:
                if keyword in merchant_lower:
                    score += 3  # Merchant name is strong signal
                if keyword in text_lower:
                    score += 1  # Keyword in receipt text
            
            scores[category_id] = score
        
        # Return category with highest score
        if scores:
            best_category = max(scores, key=scores.get)
            if scores[best_category] > 0:
                return best_category
        
        return 'miscellaneous'
    
    def _generate_recommendations(self, expense: Dict) -> List[str]:
        """Generate cost optimization recommendations"""
        recommendations = []
        
        amount = expense['amount']
        category = expense['category']
        merchant = expense['merchant']
        
        # High-cost alerts
        if amount > 500:
            recommendations.append({
                'type': 'alert',
                'message': f'High expense: ${amount:.2f} - Consider if this is necessary',
                'severity': 'medium'
            })
        
        # Category-specific recommendations
        if category == 'software' and amount > 100:
            recommendations.append({
                'type': 'optimization',
                'message': 'Check for annual billing discounts (typically 20% off)',
                'potential_savings': amount * 0.2
            })
        
        if category == 'meals_entertainment':
            deductible = amount * 0.5  # 50% deductible
            recommendations.append({
                'type': 'tax',
                'message': f'50% tax deductible: ${deductible:.2f}',
                'tax_benefit': deductible * 0.25  # Assuming 25% tax rate
            })
        
        if category == 'office_supplies' and amount > 50:
            recommendations.append({
                'type': 'optimization',
                'message': 'Consider bulk purchasing to save 15-30%',
                'potential_savings': amount * 0.2
            })
        
        return recommendations
    
    def get_spending_summary(self, user_id: str = None, days: int = 30) -> Dict:
        """Get spending summary and analytics"""
        # Filter expenses for user and time period
        cutoff_date = datetime.now() - timedelta(days=days)
        
        user_expenses = [
            e for e in self.expenses
            if (not user_id or e.get('user_id') == user_id) and
               datetime.fromisoformat(e['created_at']) > cutoff_date
        ]
        
        if not user_expenses:
            return {
                'total_expenses': 0,
                'expense_count': 0,
                'average_expense': 0,
                'by_category': {},
                'recommendations': []
            }
        
        # Calculate totals
        total_amount = sum(e['amount'] for e in user_expenses)
        expense_count = len(user_expenses)
        average_expense = total_amount / expense_count if expense_count > 0 else 0
        
        # Group by category
        by_category = {}
        for expense in user_expenses:
            category = expense['category_name']
            if category not in by_category:
                by_category[category] = {
                    'count': 0,
                    'total': 0,
                    'percentage': 0
                }
            by_category[category]['count'] += 1
            by_category[category]['total'] += expense['amount']
        
        # Calculate percentages
        for category in by_category.values():
            category['percentage'] = (category['total'] / total_amount * 100) if total_amount > 0 else 0
        
        # Generate optimization recommendations
        recommendations = self._generate_budget_recommendations(user_expenses, total_amount)
        
        return {
            'total_expenses': round(total_amount, 2),
            'expense_count': expense_count,
            'average_expense': round(average_expense, 2),
            'by_category': by_category,
            'tax_deductible_total': sum(
                e['amount'] * (e.get('deductible_percentage', 100) / 100)
                for e in user_expenses if e.get('tax_deductible')
            ),
            'period_days': days,
            'recommendations': recommendations
        }
    
    def _generate_budget_recommendations(self, expenses: List[Dict], total: float) -> List[Dict]:
        """Generate budget optimization recommendations"""
        recommendations = []
        
        # Calculate spending by category
        category_spending = {}
        for expense in expenses:
            category = expense['category']
            category_spending[category] = category_spending.get(category, 0) + expense['amount']
        
        # Check against recommended budget percentages
        for category_id, amount in category_spending.items():
            category_info = self.CATEGORIES.get(category_id, {})
            recommended_pct = category_info.get('budget_percentage', 0)
            actual_pct = (amount / total * 100) if total > 0 else 0
            
            if actual_pct > recommended_pct * 1.5:  # 50% over recommended
                recommendations.append({
                    'type': 'budget_alert',
                    'category': category_info.get('name', category_id),
                    'message': f"Spending {actual_pct:.1f}% on {category_info.get('name')} (recommended: {recommended_pct}%)",
                    'overspend': amount - (total * recommended_pct / 100),
                    'severity': 'high'
                })
        
        return recommendations


# Singleton
_expense_manager = None

def get_expense_manager():
    """Get singleton expense manager instance"""
    global _expense_manager
    if _expense_manager is None:
        _expense_manager = ExpenseManager()
    return _expense_manager
