# ==============================================================================
# app/chunking/strategies.py
# Advanced Document Chunking Strategies - The Intelligence Processor
# ==============================================================================
"""
This module implements advanced document chunking strategies for CLARITY.
Provides semantic, hierarchical, context-aware, and dynamic chunking approaches.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

# ==============================================================================
# CHUNK DATA STRUCTURES
# ==============================================================================

@dataclass
class Chunk:
    """Represents a document chunk with metadata."""
    content: str
    start_pos: int
    end_pos: int
    chunk_id: str
    metadata: Dict[str, Any]
    parent_doc: str
    strategy: str
    confidence: float = 1.0
    context: Optional[str] = None

@dataclass
class ChunkingResult:
    """Result of chunking operation."""
    chunks: List[Chunk]
    strategy_used: str
    total_chunks: int
    avg_chunk_size: float
    metadata: Dict[str, Any]

# ==============================================================================
# BASE CHUNKER CLASS
# ==============================================================================

class BaseChunker(ABC):
    """Base class for all chunking strategies."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    def chunk(self, text: str, metadata: Dict[str, Any] = None) -> ChunkingResult:
        """
        Chunk text into smaller pieces.
        
        Args:
            text: Input text to chunk
            metadata: Additional metadata for the document
            
        Returns:
            ChunkingResult with chunks and metadata
        """
        pass
    
    def _create_chunk(self, content: str, start_pos: int, end_pos: int, 
                     chunk_id: str, metadata: Dict[str, Any], 
                     parent_doc: str, context: str = None) -> Chunk:
        """Create a chunk with standard metadata."""
        return Chunk(
            content=content,
            start_pos=start_pos,
            end_pos=end_pos,
            chunk_id=chunk_id,
            metadata=metadata,
            parent_doc=parent_doc,
            strategy=self.name,
            context=context
        )

# ==============================================================================
# SEMANTIC CHUNKER
# ==============================================================================

class SemanticChunker(BaseChunker):
    """
    Chunks documents based on semantic similarity using embeddings.
    Groups semantically similar content together.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("semantic", config)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.similarity_threshold = self.config.get('similarity_threshold', 0.7)
        self.min_chunk_size = self.config.get('min_chunk_size', 100)
        self.max_chunk_size = self.config.get('max_chunk_size', 1000)
    
    def chunk(self, text: str, metadata: Dict[str, Any] = None) -> ChunkingResult:
        """Chunk text based on semantic similarity."""
        metadata = metadata or {}
        
        # Split into sentences first
        sentences = self._split_into_sentences(text)
        if len(sentences) < 2:
            # Single sentence or very short text
            return self._create_single_chunk(text, metadata)
        
        # Generate embeddings for sentences
        embeddings = self.embedding_model.encode(sentences)
        
        # Cluster sentences based on semantic similarity
        clusters = self._cluster_sentences(sentences, embeddings)
        
        # Create chunks from clusters
        chunks = []
        chunk_id = 0
        
        for cluster in clusters:
            if not cluster:
                continue
                
            # Combine sentences in cluster
            chunk_content = ' '.join(cluster)
            
            # Ensure chunk size is within limits
            if len(chunk_content) < self.min_chunk_size:
                continue
            elif len(chunk_content) > self.max_chunk_size:
                # Split large clusters further
                sub_chunks = self._split_large_cluster(chunk_content)
                chunks.extend(sub_chunks)
            else:
                # Create chunk from cluster
                chunk = self._create_chunk(
                    content=chunk_content,
                    start_pos=0,  # Will be updated
                    end_pos=len(chunk_content),
                    chunk_id=f"semantic_{chunk_id}",
                    metadata=metadata,
                    parent_doc=metadata.get('filename', 'unknown')
                )
                chunks.append(chunk)
                chunk_id += 1
        
        return ChunkingResult(
            chunks=chunks,
            strategy_used=self.name,
            total_chunks=len(chunks),
            avg_chunk_size=sum(len(c.content) for c in chunks) / len(chunks) if chunks else 0,
            metadata={'similarity_threshold': self.similarity_threshold}
        )
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting - can be enhanced with spaCy
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _cluster_sentences(self, sentences: List[str], embeddings: np.ndarray) -> List[List[str]]:
        """Cluster sentences based on semantic similarity."""
        if len(sentences) <= 2:
            return [sentences]
        
        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(embeddings)
        
        # Use hierarchical clustering or simple threshold-based grouping
        clusters = []
        used = set()
        
        for i, sentence in enumerate(sentences):
            if i in used:
                continue
                
            cluster = [sentence]
            used.add(i)
            
            # Find similar sentences
            for j, other_sentence in enumerate(sentences):
                if j in used or i == j:
                    continue
                    
                if similarity_matrix[i][j] > self.similarity_threshold:
                    cluster.append(other_sentence)
                    used.add(j)
            
            clusters.append(cluster)
        
        return clusters
    
    def _split_large_cluster(self, content: str) -> List[Chunk]:
        """Split large clusters into smaller chunks."""
        # Simple splitting by sentences
        sentences = self._split_into_sentences(content)
        chunks = []
        
        current_chunk = ""
        chunk_id = 0
        
        for sentence in sentences:
            if len(current_chunk + sentence) > self.max_chunk_size and current_chunk:
                # Create chunk
                chunk = self._create_chunk(
                    content=current_chunk.strip(),
                    start_pos=0,
                    end_pos=len(current_chunk),
                    chunk_id=f"semantic_split_{chunk_id}",
                    metadata={},
                    parent_doc="unknown"
                )
                chunks.append(chunk)
                current_chunk = sentence
                chunk_id += 1
            else:
                current_chunk += " " + sentence
        
        # Add remaining content
        if current_chunk.strip():
            chunk = self._create_chunk(
                content=current_chunk.strip(),
                start_pos=0,
                end_pos=len(current_chunk),
                chunk_id=f"semantic_split_{chunk_id}",
                metadata={},
                parent_doc="unknown"
            )
            chunks.append(chunk)
        
        return chunks
    
    def _create_single_chunk(self, text: str, metadata: Dict[str, Any]) -> ChunkingResult:
        """Create a single chunk for short text."""
        chunk = self._create_chunk(
            content=text,
            start_pos=0,
            end_pos=len(text),
            chunk_id="semantic_single",
            metadata=metadata,
            parent_doc=metadata.get('filename', 'unknown')
        )
        
        return ChunkingResult(
            chunks=[chunk],
            strategy_used=self.name,
            total_chunks=1,
            avg_chunk_size=len(text),
            metadata={'single_chunk': True}
        )

# ==============================================================================
# HIERARCHICAL CHUNKER
# ==============================================================================

class HierarchicalChunker(BaseChunker):
    """
    Chunks documents based on their hierarchical structure (headings, sections, paragraphs).
    Preserves document organization and context.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("hierarchical", config)
        self.max_chunk_size = self.config.get('max_chunk_size', 1000)
        self.min_chunk_size = self.config.get('min_chunk_size', 100)
        self.preserve_structure = self.config.get('preserve_structure', True)
    
    def chunk(self, text: str, metadata: Dict[str, Any] = None) -> ChunkingResult:
        """Chunk text based on hierarchical structure."""
        metadata = metadata or {}
        
        # Detect document structure
        structure = self._detect_structure(text)
        
        # Create chunks based on structure
        chunks = []
        chunk_id = 0
        
        for section in structure:
            if len(section['content']) < self.min_chunk_size:
                continue
            elif len(section['content']) <= self.max_chunk_size:
                # Single chunk for section
                chunk = self._create_chunk(
                    content=section['content'],
                    start_pos=section['start'],
                    end_pos=section['end'],
                    chunk_id=f"hierarchical_{chunk_id}",
                    metadata={
                        **metadata,
                        'section_type': section['type'],
                        'section_level': section['level'],
                        'section_title': section.get('title', '')
                    },
                    parent_doc=metadata.get('filename', 'unknown'),
                    context=section.get('context', '')
                )
                chunks.append(chunk)
                chunk_id += 1
            else:
                # Split large sections
                sub_chunks = self._split_section(section, chunk_id, metadata)
                chunks.extend(sub_chunks)
                chunk_id += len(sub_chunks)
        
        return ChunkingResult(
            chunks=chunks,
            strategy_used=self.name,
            total_chunks=len(chunks),
            avg_chunk_size=sum(len(c.content) for c in chunks) / len(chunks) if chunks else 0,
            metadata={'structure_preserved': self.preserve_structure}
        )
    
    def _detect_structure(self, text: str) -> List[Dict[str, Any]]:
        """Detect hierarchical structure in text."""
        structure = []
        
        # Patterns for different document structures
        patterns = {
            'markdown_heading': r'^(#{1,6})\s+(.+)$',
            'html_heading': r'<h([1-6])[^>]*>(.*?)</h[1-6]>',
            'numbered_section': r'^(\d+\.?\s+[A-Z][^.]*\.?)$',
            'lettered_section': r'^([A-Z]\.?\s+[A-Z][^.]*\.?)$',
            'paragraph_break': r'\n\s*\n',
        }
        
        lines = text.split('\n')
        current_section = None
        current_content = []
        current_start = 0
        
        for i, line in enumerate(lines):
            line_start = current_start
            
            # Check for heading patterns
            heading_match = None
            for pattern_name, pattern in patterns.items():
                if pattern_name.endswith('_heading'):
                    match = re.match(pattern, line.strip())
                    if match:
                        heading_match = (pattern_name, match)
                        break
            
            if heading_match:
                # Save previous section
                if current_section and current_content:
                    structure.append({
                        'type': current_section['type'],
                        'level': current_section['level'],
                        'title': current_section['title'],
                        'content': '\n'.join(current_content),
                        'start': current_section['start'],
                        'end': line_start,
                        'context': self._get_section_context(current_section)
                    })
                
                # Start new section
                pattern_name, match = heading_match
                level = len(match.group(1)) if pattern_name == 'markdown_heading' else int(match.group(1))
                title = match.group(2).strip()
                
                current_section = {
                    'type': pattern_name,
                    'level': level,
                    'title': title,
                    'start': line_start
                }
                current_content = [line]
            else:
                # Add to current section
                if current_section:
                    current_content.append(line)
                else:
                    # No section detected yet, create default
                    current_section = {
                        'type': 'paragraph',
                        'level': 0,
                        'title': 'Introduction',
                        'start': 0
                    }
                    current_content = [line]
            
            current_start += len(line) + 1  # +1 for newline
        
        # Add final section
        if current_section and current_content:
            structure.append({
                'type': current_section['type'],
                'level': current_section['level'],
                'title': current_section['title'],
                'content': '\n'.join(current_content),
                'start': current_section['start'],
                'end': current_start,
                'context': self._get_section_context(current_section)
            })
        
        return structure
    
    def _get_section_context(self, section: Dict[str, Any]) -> str:
        """Get context information for a section."""
        return f"{section['type']} level {section['level']}: {section['title']}"
    
    def _split_section(self, section: Dict[str, Any], start_chunk_id: int, 
                      metadata: Dict[str, Any]) -> List[Chunk]:
        """Split a large section into smaller chunks."""
        content = section['content']
        chunks = []
        
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        current_chunk = ""
        chunk_id = start_chunk_id
        
        for paragraph in paragraphs:
            if len(current_chunk + paragraph) > self.max_chunk_size and current_chunk:
                # Create chunk
                chunk = self._create_chunk(
                    content=current_chunk.strip(),
                    start_pos=section['start'],
                    end_pos=section['start'] + len(current_chunk),
                    chunk_id=f"hierarchical_split_{chunk_id}",
                    metadata={
                        **metadata,
                        'section_type': section['type'],
                        'section_level': section['level'],
                        'section_title': section['title'],
                        'is_split': True
                    },
                    parent_doc=metadata.get('filename', 'unknown'),
                    context=section.get('context', '')
                )
                chunks.append(chunk)
                current_chunk = paragraph
                chunk_id += 1
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
        
        # Add remaining content
        if current_chunk.strip():
            chunk = self._create_chunk(
                content=current_chunk.strip(),
                start_pos=section['start'],
                end_pos=section['end'],
                chunk_id=f"hierarchical_split_{chunk_id}",
                metadata={
                    **metadata,
                    'section_type': section['type'],
                    'section_level': section['level'],
                    'section_title': section['title'],
                    'is_split': True
                },
                parent_doc=metadata.get('filename', 'unknown'),
                context=section.get('context', '')
            )
            chunks.append(chunk)
        
        return chunks

# ==============================================================================
# CONTEXT-AWARE CHUNKER
# ==============================================================================

class ContextAwareChunker(BaseChunker):
    """
    Chunks documents while maintaining context across boundaries.
    Uses overlap and summary techniques to preserve meaning.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("context_aware", config)
        self.chunk_size = self.config.get('chunk_size', 500)
        self.overlap_size = self.config.get('overlap_size', 100)
        self.context_window = self.config.get('context_window', 2)
        self.use_summaries = self.config.get('use_summaries', True)
    
    def chunk(self, text: str, metadata: Dict[str, Any] = None) -> ChunkingResult:
        """Chunk text with context preservation."""
        metadata = metadata or {}
        
        # First, create basic chunks with overlap
        basic_chunks = self._create_overlapping_chunks(text)
        
        # Enhance chunks with context
        enhanced_chunks = []
        chunk_id = 0
        
        for i, chunk_content in enumerate(basic_chunks):
            # Get context from surrounding chunks
            context = self._get_context_for_chunk(basic_chunks, i)
            
            # Create summary if enabled
            summary = None
            if self.use_summaries and len(chunk_content) > 200:
                summary = self._create_chunk_summary(chunk_content)
            
            # Create enhanced chunk
            chunk = self._create_chunk(
                content=chunk_content,
                start_pos=i * (self.chunk_size - self.overlap_size),
                end_pos=min((i + 1) * (self.chunk_size - self.overlap_size) + self.overlap_size, len(text)),
                chunk_id=f"context_aware_{chunk_id}",
                metadata={
                    **metadata,
                    'chunk_index': i,
                    'has_summary': summary is not None,
                    'context_chunks': len(context)
                },
                parent_doc=metadata.get('filename', 'unknown'),
                context=context
            )
            
            if summary:
                chunk.metadata['summary'] = summary
            
            enhanced_chunks.append(chunk)
            chunk_id += 1
        
        return ChunkingResult(
            chunks=enhanced_chunks,
            strategy_used=self.name,
            total_chunks=len(enhanced_chunks),
            avg_chunk_size=sum(len(c.content) for c in enhanced_chunks) / len(enhanced_chunks) if enhanced_chunks else 0,
            metadata={
                'overlap_size': self.overlap_size,
                'context_window': self.context_window,
                'use_summaries': self.use_summaries
            }
        )
    
    def _create_overlapping_chunks(self, text: str) -> List[str]:
        """Create chunks with overlap."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - self.overlap_size
        
        return chunks
    
    def _get_context_for_chunk(self, chunks: List[str], chunk_index: int) -> str:
        """Get context information for a chunk."""
        context_parts = []
        
        # Get previous chunks
        start_idx = max(0, chunk_index - self.context_window)
        for i in range(start_idx, chunk_index):
            if i < len(chunks):
                context_parts.append(f"[Previous {chunk_index - i}]: {chunks[i][:100]}...")
        
        # Get next chunks
        end_idx = min(len(chunks), chunk_index + self.context_window + 1)
        for i in range(chunk_index + 1, end_idx):
            if i < len(chunks):
                context_parts.append(f"[Next {i - chunk_index}]: {chunks[i][:100]}...")
        
        return " | ".join(context_parts)
    
    def _create_chunk_summary(self, content: str) -> str:
        """Create a summary of chunk content."""
        # Simple extractive summary - can be enhanced with AI
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= 3:
            return content
        
        # Take first and last sentences as summary
        summary_sentences = [sentences[0]]
        if len(sentences) > 1:
            summary_sentences.append(sentences[-1])
        
        return ". ".join(summary_sentences) + "."

# ==============================================================================
# DYNAMIC CHUNKER
# ==============================================================================

class DynamicChunker(BaseChunker):
    """
    Dynamically adjusts chunking strategy based on content type and characteristics.
    Optimizes chunk size and strategy for different document types.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("dynamic", config)
        self.content_type_detector = ContentTypeDetector()
        self.strategy_selector = StrategySelector()
    
    def chunk(self, text: str, metadata: Dict[str, Any] = None) -> ChunkingResult:
        """Dynamically chunk text based on content analysis."""
        metadata = metadata or {}
        
        # Analyze content type and characteristics
        content_analysis = self.content_type_detector.analyze(text, metadata)
        
        # Select optimal chunking strategy
        strategy = self.strategy_selector.select_strategy(content_analysis)
        
        # Apply selected strategy
        chunker = self._get_chunker_for_strategy(strategy, content_analysis)
        result = chunker.chunk(text, metadata)
        
        # Add dynamic analysis metadata
        result.metadata.update({
            'content_type': content_analysis['type'],
            'complexity': content_analysis['complexity'],
            'selected_strategy': strategy,
            'dynamic_optimization': True
        })
        
        return result
    
    def _get_chunker_for_strategy(self, strategy: str, analysis: Dict[str, Any]) -> BaseChunker:
        """Get chunker instance for selected strategy."""
        if strategy == 'semantic':
            return SemanticChunker({
                'similarity_threshold': 0.7,
                'min_chunk_size': analysis.get('optimal_min_size', 100),
                'max_chunk_size': analysis.get('optimal_max_size', 1000)
            })
        elif strategy == 'hierarchical':
            return HierarchicalChunker({
                'max_chunk_size': analysis.get('optimal_max_size', 1000),
                'min_chunk_size': analysis.get('optimal_min_size', 100)
            })
        elif strategy == 'context_aware':
            return ContextAwareChunker({
                'chunk_size': analysis.get('optimal_chunk_size', 500),
                'overlap_size': analysis.get('optimal_overlap', 100)
            })
        else:
            # Default to context-aware
            return ContextAwareChunker()

# ==============================================================================
# CONTENT TYPE DETECTOR
# ==============================================================================

class ContentTypeDetector:
    """Detects content type and characteristics for dynamic chunking."""
    
    def analyze(self, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze text to determine optimal chunking parameters."""
        metadata = metadata or {}
        
        # Detect content type
        content_type = self._detect_content_type(text, metadata)
        
        # Analyze complexity
        complexity = self._analyze_complexity(text)
        
        # Calculate optimal parameters
        optimal_params = self._calculate_optimal_parameters(text, content_type, complexity)
        
        return {
            'type': content_type,
            'complexity': complexity,
            'length': len(text),
            'sentence_count': len(re.split(r'[.!?]+', text)),
            'paragraph_count': len(text.split('\n\n')),
            **optimal_params
        }
    
    def _detect_content_type(self, text: str, metadata: Dict[str, Any]) -> str:
        """Detect the type of content."""
        filename = metadata.get('filename', '').lower()
        
        # File extension hints
        if filename.endswith('.pdf'):
            return 'document'
        elif filename.endswith(('.doc', '.docx')):
            return 'document'
        elif filename.endswith('.txt'):
            return 'text'
        elif filename.endswith('.md'):
            return 'markdown'
        
        # Content analysis
        if re.search(r'#{1,6}\s+', text):
            return 'markdown'
        elif re.search(r'<h[1-6][^>]*>', text):
            return 'html'
        elif re.search(r'\d+\.\s+[A-Z]', text):
            return 'structured'
        elif len(text.split('\n\n')) > 10:
            return 'document'
        else:
            return 'text'
    
    def _analyze_complexity(self, text: str) -> str:
        """Analyze text complexity."""
        # Simple complexity metrics
        avg_sentence_length = len(text.split()) / len(re.split(r'[.!?]+', text))
        unique_words = len(set(text.lower().split()))
        total_words = len(text.split())
        vocabulary_richness = unique_words / total_words if total_words > 0 else 0
        
        if avg_sentence_length > 20 and vocabulary_richness > 0.7:
            return 'high'
        elif avg_sentence_length > 15 and vocabulary_richness > 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_optimal_parameters(self, text: str, content_type: str, complexity: str) -> Dict[str, Any]:
        """Calculate optimal chunking parameters."""
        base_size = 500
        
        # Adjust based on content type
        type_multipliers = {
            'document': 1.2,
            'markdown': 1.0,
            'html': 1.1,
            'structured': 0.8,
            'text': 1.0
        }
        
        # Adjust based on complexity
        complexity_multipliers = {
            'high': 0.8,
            'medium': 1.0,
            'low': 1.2
        }
        
        multiplier = type_multipliers.get(content_type, 1.0) * complexity_multipliers.get(complexity, 1.0)
        optimal_size = int(base_size * multiplier)
        
        return {
            'optimal_chunk_size': optimal_size,
            'optimal_min_size': int(optimal_size * 0.3),
            'optimal_max_size': int(optimal_size * 2),
            'optimal_overlap': int(optimal_size * 0.2)
        }

# ==============================================================================
# STRATEGY SELECTOR
# ==============================================================================

class StrategySelector:
    """Selects optimal chunking strategy based on content analysis."""
    
    def select_strategy(self, analysis: Dict[str, Any]) -> str:
        """Select the best chunking strategy for the content."""
        content_type = analysis['type']
        complexity = analysis['complexity']
        length = analysis['length']
        
        # Strategy selection logic
        if content_type in ['markdown', 'html'] and analysis.get('paragraph_count', 0) > 5:
            return 'hierarchical'
        elif complexity == 'high' and length > 2000:
            return 'semantic'
        elif length > 1000:
            return 'context_aware'
        else:
            return 'context_aware'  # Default

# ==============================================================================
# CHUNKING ORCHESTRATOR
# ==============================================================================

class ChunkingOrchestrator:
    """
    Orchestrates different chunking strategies and provides a unified interface.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize chunkers
        self.chunkers = {
            'semantic': SemanticChunker(self.config.get('semantic', {})),
            'hierarchical': HierarchicalChunker(self.config.get('hierarchical', {})),
            'context_aware': ContextAwareChunker(self.config.get('context_aware', {})),
            'dynamic': DynamicChunker(self.config.get('dynamic', {}))
        }
    
    def chunk(self, text: str, strategy: str = 'dynamic', 
              metadata: Dict[str, Any] = None) -> ChunkingResult:
        """
        Chunk text using specified strategy.
        
        Args:
            text: Text to chunk
            strategy: Chunking strategy to use
            metadata: Additional metadata
            
        Returns:
            ChunkingResult
        """
        if strategy not in self.chunkers:
            self.logger.warning(f"Unknown strategy {strategy}, using dynamic")
            strategy = 'dynamic'
        
        chunker = self.chunkers[strategy]
        return chunker.chunk(text, metadata)
    
    def get_available_strategies(self) -> List[str]:
        """Get list of available chunking strategies."""
        return list(self.chunkers.keys())
    
    def get_strategy_info(self, strategy: str) -> Dict[str, Any]:
        """Get information about a chunking strategy."""
        if strategy not in self.chunkers:
            return {}
        
        chunker = self.chunkers[strategy]
        return {
            'name': chunker.name,
            'description': self._get_strategy_description(strategy),
            'config': chunker.config
        }
    
    def _get_strategy_description(self, strategy: str) -> str:
        """Get description for a strategy."""
        descriptions = {
            'semantic': 'Groups semantically similar content together using embeddings',
            'hierarchical': 'Preserves document structure (headings, sections, paragraphs)',
            'context_aware': 'Maintains context across chunk boundaries with overlap',
            'dynamic': 'Automatically selects optimal strategy based on content analysis'
        }
        return descriptions.get(strategy, 'Unknown strategy')

