# ==============================================================================
# app/data_entry/__init__.py
# Data Keystone Engine - Automated Data Entry System
# ==============================================================================
"""
The CLARITY Data Keystone Engine: A 4-Agent Autonomous Data Entry System

This module implements a revolutionary approach to data entry automation,
replacing entire teams of human data entry specialists with an AI-powered pipeline.

The Four-Agent Squad:
1. Agent Visionary (The Eye) - OCR and vision processing
2. Agent Extractor (The Brain) - Intelligent data extraction
3. Agent Validator (The Auditor) - Quality assurance and validation
4. Agent Loader (The Hand) - Database integration and loading

Mission: Transform unstructured documents into structured, validated data
with enterprise-grade accuracy and speed.
"""

from .keystone_engine import KeystoneEngine, DataEntryResult
from .agent_visionary import AgentVisionary
from .agent_extractor import AgentExtractor
from .agent_validator import AgentValidator
from .agent_loader import AgentLoader

__all__ = [
    'KeystoneEngine',
    'DataEntryResult',
    'AgentVisionary',
    'AgentExtractor',
    'AgentValidator',
    'AgentLoader'
]
