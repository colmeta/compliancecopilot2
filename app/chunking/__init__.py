# ==============================================================================
# app/chunking/__init__.py
# Advanced Chunking System - The Intelligence Processor
# ==============================================================================
"""
This package contains advanced document chunking strategies for CLARITY.
Implements semantic, hierarchical, context-aware, and dynamic chunking.
"""

from .strategies import (
    SemanticChunker,
    HierarchicalChunker,
    ContextAwareChunker,
    DynamicChunker,
    ChunkingOrchestrator
)

__all__ = [
    'SemanticChunker',
    'HierarchicalChunker', 
    'ContextAwareChunker',
    'DynamicChunker',
    'ChunkingOrchestrator'
]

