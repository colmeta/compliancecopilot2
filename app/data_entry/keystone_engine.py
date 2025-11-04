# ==============================================================================
# app/data_entry/keystone_engine.py
# The Orchestrator - Coordinates the 4-Agent Data Entry Pipeline
# ==============================================================================
"""
KeystoneEngine: The central orchestrator for automated data entry.

This class coordinates the 4-agent pipeline:
1. Visionary extracts text from images/scans
2. Extractor identifies and extracts structured data
3. Validator ensures accuracy and flags issues
4. Loader inserts data into target systems

Fortune 500-Grade Features:
- Configurable confidence thresholds
- Human-in-the-loop for low-confidence records
- Batch processing with progress tracking
- Detailed audit trails
- Multi-format output support
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

# Import agents
from .agent_visionary import AgentVisionary
from .agent_extractor import AgentExtractor
from .agent_validator import AgentValidator
from .agent_loader import AgentLoader

logger = logging.getLogger(__name__)


@dataclass
class DataEntryResult:
    """
    Result of a data entry operation.
    
    Attributes:
        success: Whether the operation completed successfully
        extracted_data: The extracted and validated data
        confidence_score: Overall confidence (0.0 to 1.0)
        validation_status: Status from validator
        quarantined: Whether the record was quarantined for review
        errors: List of errors encountered
        warnings: List of warnings
        processing_time: Time taken in seconds
        metadata: Additional metadata
    """
    success: bool
    extracted_data: Dict[str, Any]
    confidence_score: float
    validation_status: str
    quarantined: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'success': self.success,
            'extracted_data': self.extracted_data,
            'confidence_score': self.confidence_score,
            'validation_status': self.validation_status,
            'quarantined': self.quarantined,
            'errors': self.errors,
            'warnings': self.warnings,
            'processing_time': self.processing_time,
            'metadata': self.metadata
        }


class KeystoneEngine:
    """
    The Data Keystone Engine Orchestrator.
    
    This class manages the entire data entry pipeline, coordinating
    all four agents to transform documents into validated data.
    """
    
    def __init__(
        self,
        confidence_threshold: float = 0.85,
        enable_human_review: bool = True,
        enable_audit_log: bool = True
    ):
        """
        Initialize the Keystone Engine.
        
        Args:
            confidence_threshold: Minimum confidence to auto-approve (0.0-1.0)
            enable_human_review: Whether to quarantine low-confidence records
            enable_audit_log: Whether to log all operations for compliance
        """
        self.confidence_threshold = confidence_threshold
        self.enable_human_review = enable_human_review
        self.enable_audit_log = enable_audit_log
        
        # Initialize agents
        self.visionary = AgentVisionary()
        self.extractor = AgentExtractor()
        self.validator = AgentValidator(confidence_threshold=confidence_threshold)
        self.loader = AgentLoader()
        
        logger.info(
            f"KeystoneEngine initialized with confidence threshold: {confidence_threshold}"
        )
    
    def process_document(
        self,
        document: Dict[str, Any],
        schema: Dict[str, Any],
        output_config: Optional[Dict[str, Any]] = None
    ) -> DataEntryResult:
        """
        Process a single document through the 4-agent pipeline.
        
        Args:
            document: Document data (filename, content, content_type)
            schema: Target data schema
            output_config: Optional output configuration
            
        Returns:
            DataEntryResult with processing outcome
        """
        start_time = datetime.now()
        
        try:
            # STAGE 1: Agent Visionary - Extract text from document
            logger.info(f"STAGE 1: Agent Visionary processing {document.get('filename', 'unknown')}")
            vision_result = self.visionary.extract_text(document)
            
            if not vision_result['success']:
                return DataEntryResult(
                    success=False,
                    extracted_data={},
                    confidence_score=0.0,
                    validation_status='failed',
                    errors=[f"Vision extraction failed: {vision_result.get('error', 'Unknown error')}"],
                    processing_time=(datetime.now() - start_time).total_seconds()
                )
            
            raw_text = vision_result['text']
            vision_confidence = vision_result.get('confidence', 1.0)
            
            # STAGE 2: Agent Extractor - Extract structured data
            logger.info("STAGE 2: Agent Extractor extracting structured data")
            extraction_result = self.extractor.extract_data(raw_text, schema)
            
            if not extraction_result['success']:
                return DataEntryResult(
                    success=False,
                    extracted_data={},
                    confidence_score=vision_confidence,
                    validation_status='extraction_failed',
                    errors=[f"Data extraction failed: {extraction_result.get('error', 'Unknown error')}"],
                    processing_time=(datetime.now() - start_time).total_seconds()
                )
            
            extracted_data = extraction_result['data']
            extraction_confidence = extraction_result.get('confidence', 0.8)
            
            # STAGE 3: Agent Validator - Validate extracted data
            logger.info("STAGE 3: Agent Validator validating data")
            validation_result = self.validator.validate_data(
                extracted_data=extracted_data,
                raw_text=raw_text,
                schema=schema
            )
            
            if not validation_result['success']:
                # Validation failed - quarantine if enabled
                quarantined = self.enable_human_review
                
                return DataEntryResult(
                    success=False,
                    extracted_data=extracted_data,
                    confidence_score=validation_result.get('confidence', 0.0),
                    validation_status='validation_failed',
                    quarantined=quarantined,
                    errors=validation_result.get('errors', []),
                    warnings=validation_result.get('warnings', []),
                    processing_time=(datetime.now() - start_time).total_seconds(),
                    metadata={
                        'vision_confidence': vision_confidence,
                        'extraction_confidence': extraction_confidence,
                        'quarantine_reason': 'Validation failed'
                    }
                )
            
            validated_data = validation_result['validated_data']
            validation_confidence = validation_result['confidence']
            
            # Calculate overall confidence
            overall_confidence = (
                vision_confidence * 0.2 +
                extraction_confidence * 0.4 +
                validation_confidence * 0.4
            )
            
            # Check if confidence meets threshold
            if overall_confidence < self.confidence_threshold and self.enable_human_review:
                logger.warning(
                    f"Low confidence ({overall_confidence:.2f}), quarantining for human review"
                )
                
                return DataEntryResult(
                    success=True,
                    extracted_data=validated_data,
                    confidence_score=overall_confidence,
                    validation_status='quarantined_low_confidence',
                    quarantined=True,
                    warnings=[f"Confidence {overall_confidence:.2f} below threshold {self.confidence_threshold}"],
                    processing_time=(datetime.now() - start_time).total_seconds(),
                    metadata={
                        'vision_confidence': vision_confidence,
                        'extraction_confidence': extraction_confidence,
                        'validation_confidence': validation_confidence,
                        'quarantine_reason': 'Low confidence score'
                    }
                )
            
            # STAGE 4: Agent Loader - Load data into target system
            if output_config:
                logger.info("STAGE 4: Agent Loader loading data")
                load_result = self.loader.load_data(validated_data, output_config)
                
                if not load_result['success']:
                    return DataEntryResult(
                        success=False,
                        extracted_data=validated_data,
                        confidence_score=overall_confidence,
                        validation_status='load_failed',
                        errors=[f"Data loading failed: {load_result.get('error', 'Unknown error')}"],
                        processing_time=(datetime.now() - start_time).total_seconds()
                    )
            
            # Success!
            return DataEntryResult(
                success=True,
                extracted_data=validated_data,
                confidence_score=overall_confidence,
                validation_status='success',
                quarantined=False,
                processing_time=(datetime.now() - start_time).total_seconds(),
                metadata={
                    'vision_confidence': vision_confidence,
                    'extraction_confidence': extraction_confidence,
                    'validation_confidence': validation_confidence,
                    'loaded': output_config is not None
                }
            )
            
        except Exception as e:
            logger.error(f"KeystoneEngine fatal error: {e}", exc_info=True)
            
            return DataEntryResult(
                success=False,
                extracted_data={},
                confidence_score=0.0,
                validation_status='error',
                errors=[f"Fatal error: {str(e)}"],
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    def process_batch(
        self,
        documents: List[Dict[str, Any]],
        schema: Dict[str, Any],
        output_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a batch of documents.
        
        Args:
            documents: List of document data dictionaries
            schema: Target data schema
            output_config: Optional output configuration
            
        Returns:
            Dict with batch processing results
        """
        results = []
        successful = 0
        quarantined = 0
        failed = 0
        
        for i, doc in enumerate(documents):
            logger.info(f"Processing document {i+1}/{len(documents)}")
            
            result = self.process_document(doc, schema, output_config)
            results.append(result.to_dict())
            
            if result.success:
                successful += 1
                if result.quarantined:
                    quarantined += 1
            else:
                failed += 1
        
        return {
            'total': len(documents),
            'successful': successful,
            'quarantined': quarantined,
            'failed': failed,
            'success_rate': (successful / len(documents)) * 100 if documents else 0,
            'results': results
        }
    
    def get_quarantined_records(self, results: List[DataEntryResult]) -> List[Dict[str, Any]]:
        """
        Get all records that were quarantined for human review.
        
        Args:
            results: List of DataEntryResult objects
            
        Returns:
            List of quarantined records with metadata
        """
        quarantined = []
        
        for result in results:
            if result.quarantined:
                quarantined.append({
                    'data': result.extracted_data,
                    'confidence': result.confidence_score,
                    'reason': result.metadata.get('quarantine_reason', 'Unknown'),
                    'warnings': result.warnings,
                    'errors': result.errors
                })
        
        return quarantined
