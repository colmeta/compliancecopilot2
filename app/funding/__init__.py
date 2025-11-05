# ==============================================================================
# app/funding/__init__.py
# CLARITY Funding Readiness Engine
# ==============================================================================
"""
The Funding Readiness Engine: Transform Ideas into Fundable Ventures

This module helps entrepreneurs and organizations with brilliant ideas but no
documentation become investor-ready and fundable.

Features:
- Vision/Mission statement generation
- Business plan creation
- Investor pitch deck
- Organizational structure
- Policies and procedures
- Financial projections
- Impact assessment
- Y-Combinator ready documentation
- Presidential briefing packages
"""

from .funding_engine import FundingEngine, DocumentPackage, FundingLevel
from .research_agent import DeepResearchAgent, ResearchReport, get_research_agent
from .interactive_planner import InteractivePlanner, Question, get_interactive_planner
from .document_writer import OutstandingDocumentWriter, get_outstanding_writer

__all__ = [
    'FundingEngine', 
    'DocumentPackage', 
    'FundingLevel',
    'DeepResearchAgent',
    'ResearchReport',
    'InteractivePlanner',
    'Question',
    'OutstandingDocumentWriter',
    'get_research_agent',
    'get_interactive_planner',
    'get_outstanding_writer'
]
