# ==============================================================================
# app/planning/__init__.py
# Planning Engine - Cursor-style Plan-First-Then-Execute Workflow
# ==============================================================================
"""
The CLARITY Planning Engine: Revolutionary Plan-First Workflow

This module implements a Cursor-style planning system where CLARITY:
1. Analyzes the task
2. Creates a detailed plan
3. Presents the plan to the user
4. Waits for approval
5. Executes the approved plan step-by-step

This approach ensures transparency, builds trust, and allows users to
guide the AI before significant work begins.
"""

from .planning_engine import PlanningEngine, ExecutionPlan, PlanStep

__all__ = ['PlanningEngine', 'ExecutionPlan', 'PlanStep']
