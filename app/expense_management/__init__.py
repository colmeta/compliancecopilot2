# ==============================================================================
# app/expense_management/__init__.py
# Expense Management System - Fortune 50-Grade Financial Control
# ==============================================================================
"""
The CLARITY Expense Management System: CFO-Grade Expense Intelligence

This module provides comprehensive expense tracking, management, and optimization
for companies struggling with expense management. It:

1. Scans receipts (hardcopy → digital)
2. Extracts expense data automatically
3. Organizes expenses by category, department, project
4. Tracks spending patterns and trends
5. Identifies cost-cutting opportunities
6. Generates expense reports
7. Forecasts future spending
8. Provides budget alerts

Built for:
- CFOs and finance teams
- Small businesses struggling with receipts
- Large enterprises needing expense control
- Government agencies with budget constraints
"""

from .expense_engine import ExpenseEngine, ExpenseRecord
from .receipt_processor import ReceiptProcessor
from .cost_optimizer import CostOptimizer

__all__ = ['ExpenseEngine', 'ExpenseRecord', 'ReceiptProcessor', 'CostOptimizer']
