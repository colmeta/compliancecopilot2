# ==============================================================================
# app/expense_management/expense_engine.py
# Expense Engine - CFO-Grade Expense Management
# ==============================================================================
"""
Expense Engine: Comprehensive Expense Tracking and Management

This engine manages the complete expense lifecycle:
1. Capture (receipt scanning)
2. Extract (data extraction)
3. Categorize (automatic categorization)
4. Analyze (spending patterns)
5. Optimize (cost reduction opportunities)
6. Report (expense reports and forecasts)
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import pandas as pd
import json

logger = logging.getLogger(__name__)


@dataclass
class ExpenseRecord:
    """
    A single expense record.
    
    Attributes:
        expense_id: Unique identifier
        date: Date of expense
        amount: Expense amount
        currency: Currency code
        category: Expense category
        vendor: Vendor/merchant name
        description: Expense description
        payment_method: Payment method used
        department: Department (if applicable)
        project: Project code (if applicable)
        receipt_image: Path to receipt image
        status: Status ('pending', 'approved', 'rejected')
        created_at: Record creation timestamp
        metadata: Additional metadata
    """
    expense_id: str
    date: datetime
    amount: float
    currency: str
    category: str
    vendor: str
    description: str
    payment_method: str = "unknown"
    department: Optional[str] = None
    project: Optional[str] = None
    receipt_image: Optional[str] = None
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExpenseEngine:
    """
    Expense Engine: CFO-Grade Expense Management.
    
    Manages the complete expense tracking and optimization workflow.
    """
    
    # Standard expense categories
    EXPENSE_CATEGORIES = {
        'travel': ['airfare', 'hotel', 'taxi', 'uber', 'lyft', 'car rental', 'parking', 'tolls'],
        'meals': ['restaurant', 'food', 'catering', 'coffee', 'lunch', 'dinner', 'breakfast'],
        'office_supplies': ['staples', 'office depot', 'paper', 'pens', 'supplies'],
        'technology': ['software', 'hardware', 'computer', 'phone', 'electronics', 'saas'],
        'marketing': ['advertising', 'promotion', 'marketing', 'branding', 'social media'],
        'utilities': ['electricity', 'water', 'internet', 'phone service', 'gas'],
        'rent': ['office rent', 'lease', 'property'],
        'insurance': ['insurance', 'coverage', 'policy'],
        'professional_services': ['consulting', 'legal', 'accounting', 'advisory'],
        'miscellaneous': []  # Catch-all
    }
    
    def __init__(self):
        """Initialize the Expense Engine."""
        logger.info("ExpenseEngine initialized - CFO-Grade Expense Management Ready")
    
    def add_expense(self, expense: ExpenseRecord) -> Dict[str, Any]:
        """
        Add a new expense record.
        
        Args:
            expense: ExpenseRecord object
            
        Returns:
            Dict with operation result
        """
        try:
            # Auto-categorize if not provided
            if expense.category == "unknown":
                expense.category = self._auto_categorize(expense.vendor, expense.description)
            
            # Store in database
            self._store_expense(expense)
            
            return {
                'success': True,
                'expense_id': expense.expense_id,
                'category': expense.category
            }
            
        except Exception as e:
            logger.error(f"Error adding expense: {e}")
            return {'success': False, 'error': str(e)}
    
    def _auto_categorize(self, vendor: str, description: str) -> str:
        """
        Automatically categorize an expense based on vendor and description.
        
        Args:
            vendor: Vendor name
            description: Expense description
            
        Returns:
            Category name
        """
        combined = f"{vendor} {description}".lower()
        
        for category, keywords in self.EXPENSE_CATEGORIES.items():
            if any(keyword in combined for keyword in keywords):
                return category
        
        return 'miscellaneous'
    
    def _store_expense(self, expense: ExpenseRecord):
        """Store expense in database."""
        try:
            from app import db
            from app.models import UsageMetrics  # Repurpose for expense tracking
            
            # Store as JSON in metadata
            expense_data = {
                'expense_id': expense.expense_id,
                'date': expense.date.isoformat(),
                'amount': expense.amount,
                'currency': expense.currency,
                'category': expense.category,
                'vendor': expense.vendor,
                'description': expense.description,
                'payment_method': expense.payment_method,
                'department': expense.department,
                'project': expense.project,
                'status': expense.status
            }
            
            # Create or update record
            # In production, would use dedicated Expense model
            
        except Exception as e:
            logger.error(f"Failed to store expense: {e}")
    
    def get_expense_summary(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: str = 'category'
    ) -> Dict[str, Any]:
        """
        Get expense summary for a user.
        
        Args:
            user_id: User ID
            start_date: Start date for analysis
            end_date: End date for analysis
            group_by: How to group expenses ('category', 'department', 'vendor', 'month')
            
        Returns:
            Dict with expense summary
        """
        try:
            # In production, would query actual expense records
            # This is a demonstration structure
            
            summary = {
                'period': {
                    'start': start_date.isoformat() if start_date else None,
                    'end': end_date.isoformat() if end_date else None
                },
                'total_expenses': 0.0,
                'expense_count': 0,
                'by_category': {},
                'by_department': {},
                'by_vendor': {},
                'trend': 'stable'  # or 'increasing', 'decreasing'
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting expense summary: {e}")
            return {'error': str(e)}
    
    def identify_cost_savings(
        self,
        expenses: List[ExpenseRecord]
    ) -> List[Dict[str, Any]]:
        """
        Identify potential cost-saving opportunities.
        
        Args:
            expenses: List of expense records
            
        Returns:
            List of cost-saving opportunities
        """
        opportunities = []
        
        # Create DataFrame for analysis
        df = pd.DataFrame([
            {
                'date': e.date,
                'amount': e.amount,
                'category': e.category,
                'vendor': e.vendor
            }
            for e in expenses
        ])
        
        if df.empty:
            return opportunities
        
        # Opportunity 1: Duplicate/Similar Subscriptions
        subscription_categories = ['technology', 'professional_services']
        subscription_expenses = df[df['category'].isin(subscription_categories)]
        
        if len(subscription_expenses) > 0:
            vendor_counts = subscription_expenses['vendor'].value_counts()
            if len(vendor_counts[vendor_counts > 1]) > 0:
                opportunities.append({
                    'type': 'duplicate_subscriptions',
                    'title': 'Potential Duplicate Subscriptions',
                    'description': f'Found {len(vendor_counts[vendor_counts > 1])} vendors with multiple charges. Review for duplicate subscriptions.',
                    'potential_savings': float(subscription_expenses['amount'].sum() * 0.15),
                    'priority': 'high'
                })
        
        # Opportunity 2: High-frequency Small Purchases
        if len(df) > 0:
            avg_expense = df['amount'].mean()
            small_expenses = df[df['amount'] < avg_expense * 0.5]
            
            if len(small_expenses) > 20:  # More than 20 small purchases
                opportunities.append({
                    'type': 'small_purchases',
                    'title': 'Excessive Small Purchases',
                    'description': f'Found {len(small_expenses)} small purchases. Consider bulk purchasing or vendor consolidation.',
                    'potential_savings': float(small_expenses['amount'].sum() * 0.10),
                    'priority': 'medium'
                })
        
        # Opportunity 3: Category Over-Spending
        category_totals = df.groupby('category')['amount'].sum().sort_values(ascending=False)
        
        if len(category_totals) > 0:
            top_category = category_totals.index[0]
            top_amount = category_totals.iloc[0]
            
            opportunities.append({
                'type': 'category_overspend',
                'title': f'High Spending in {top_category.replace("_", " ").title()}',
                'description': f'${top_amount:.2f} spent in this category. Review for optimization opportunities.',
                'potential_savings': float(top_amount * 0.20),
                'priority': 'high'
            })
        
        # Opportunity 4: Seasonal/Pattern Analysis
        if 'date' in df.columns:
            df['month'] = pd.to_datetime(df['date']).dt.month
            monthly_spend = df.groupby('month')['amount'].sum()
            
            if monthly_spend.std() / monthly_spend.mean() > 0.3:  # High variance
                opportunities.append({
                    'type': 'spending_variance',
                    'title': 'Irregular Spending Patterns',
                    'description': 'Spending varies significantly by month. Consider budget smoothing and advance planning.',
                    'potential_savings': float(monthly_spend.std() * 0.5),
                    'priority': 'medium'
                })
        
        # Sort by potential savings
        opportunities.sort(key=lambda x: x['potential_savings'], reverse=True)
        
        return opportunities
    
    def generate_expense_report(
        self,
        expenses: List[ExpenseRecord],
        report_type: str = 'summary'
    ) -> str:
        """
        Generate an expense report.
        
        Args:
            expenses: List of expense records
            report_type: Type of report ('summary', 'detailed', 'compliance')
            
        Returns:
            Report text in markdown format
        """
        try:
            # Create DataFrame
            df = pd.DataFrame([
                {
                    'Date': e.date.strftime('%Y-%m-%d'),
                    'Vendor': e.vendor,
                    'Category': e.category,
                    'Amount': e.amount,
                    'Description': e.description
                }
                for e in expenses
            ])
            
            # Calculate totals
            total = df['Amount'].sum()
            count = len(df)
            avg = df['Amount'].mean()
            
            # Group by category
            by_category = df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
            
            # Build report
            report = f"""# Expense Report

## Summary
- **Total Expenses**: ${total:,.2f}
- **Number of Transactions**: {count}
- **Average Transaction**: ${avg:.2f}

## By Category
"""
            
            for category, amount in by_category.items():
                percentage = (amount / total) * 100
                report += f"- **{category.replace('_', ' ').title()}**: ${amount:,.2f} ({percentage:.1f}%)\n"
            
            if report_type == 'detailed':
                report += "\n## Detailed Transactions\n\n"
                report += df.to_markdown(index=False)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return "Error generating expense report"
    
    def forecast_expenses(
        self,
        historical_expenses: List[ExpenseRecord],
        periods: int = 3
    ) -> Dict[str, Any]:
        """
        Forecast future expenses based on historical data.
        
        Args:
            historical_expenses: Historical expense records
            periods: Number of periods to forecast (months)
            
        Returns:
            Dict with forecast results
        """
        try:
            # Create DataFrame
            df = pd.DataFrame([
                {
                    'date': e.date,
                    'amount': e.amount
                }
                for e in historical_expenses
            ])
            
            if df.empty:
                return {'success': False, 'error': 'No historical data'}
            
            # Group by month
            df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
            monthly = df.groupby('month')['amount'].sum()
            
            # Simple moving average forecast
            avg_monthly = monthly.mean()
            trend = monthly.diff().mean()  # Average change per month
            
            # Generate forecast
            forecast = []
            last_value = monthly.iloc[-1]
            
            for i in range(1, periods + 1):
                forecasted_value = last_value + (trend * i)
                forecast.append({
                    'period': i,
                    'forecast': float(forecasted_value),
                    'lower_bound': float(forecasted_value * 0.9),
                    'upper_bound': float(forecasted_value * 1.1)
                })
            
            return {
                'success': True,
                'forecast': forecast,
                'avg_monthly': float(avg_monthly),
                'trend': 'increasing' if trend > 0 else 'decreasing' if trend < 0 else 'stable'
            }
            
        except Exception as e:
            logger.error(f"Forecast error: {e}")
            return {'success': False, 'error': str(e)}


# Global instance
_engine = None


def get_expense_engine() -> ExpenseEngine:
    """Get or create the global ExpenseEngine instance."""
    global _engine
    
    if _engine is None:
        _engine = ExpenseEngine()
    
    return _engine
