# ==============================================================================
# app/outstanding_system/__init__.py
# Universal Outstanding Writing System for ALL CLARITY Domains
# ==============================================================================
"""
Universal Outstanding Writing System

This system applies presidential-grade quality to ALL CLARITY domains:
- Security Intelligence
- Legal Intelligence
- Financial Intelligence
- Corporate Intelligence
- Healthcare Intelligence
- Proposal Intelligence
- Engineering Intelligence
- Grant Proposal Intelligence
- Market Analysis Intelligence
- Pitch Deck Intelligence
- Investor Diligence Intelligence
- Education Intelligence

Every domain gets:
✅ Deep Research
✅ Human Touch
✅ Interactive Planning
✅ Multi-Pass Writing
✅ Refinement Loops
"""

from .universal_writer import UniversalOutstandingWriter, get_universal_writer
from .domain_researcher import DomainResearcher, get_domain_researcher
from .universal_planner import UniversalPlanner, get_universal_planner

__all__ = [
    'UniversalOutstandingWriter',
    'DomainResearcher',
    'UniversalPlanner',
    'get_universal_writer',
    'get_domain_researcher',
    'get_universal_planner'
]
