# ==============================================================================
# app/data_entry/agent_extractor.py
# Agent Extractor - The Brain (Intelligent Data Extraction)
# ==============================================================================
"""
Agent Extractor: The second agent in the Data Keystone pipeline.

Mission: Understand document structure and extract specific data points
into a predefined schema with high accuracy.

Capabilities:
- LLM-powered intelligent field extraction
- Schema-driven data mapping
- Multi-field extraction with context awareness
- Confidence scoring per field
- Null handling for missing data
"""

import logging
from typing import Dict, Any, List
import json
import os
import google.generativeai as genai

logger = logging.getLogger(__name__)


class AgentExtractor:
    """
    Agent Extractor - Intelligent data extraction specialist.
    
    This agent uses LLMs to understand document structure and extract
    data according to a user-defined schema.
    """
    
    def __init__(self):
        """Initialize Agent Extractor with AI model."""
        try:
            genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            self.initialized = True
            logger.info("Agent Extractor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Agent Extractor: {e}")
            self.initialized = False
    
    def extract_data(self, raw_text: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from raw text according to schema.
        
        Args:
            raw_text: Raw text from Agent Visionary
            schema: Target data schema (field_name: field_type pairs)
            
        Returns:
            Dict with 'success', 'data', 'confidence', 'field_confidences'
        """
        if not self.initialized:
            return {
                'success': False,
                'error': 'Agent Extractor not initialized',
                'data': {},
                'confidence': 0.0
            }
        
        try:
            # Build extraction prompt
            prompt = self._build_extraction_prompt(raw_text, schema)
            
            # Call LLM for extraction
            response = self.model.generate_content(prompt)
            
            # Parse response
            result = self._parse_extraction_response(response.text, schema)
            
            return result
            
        except Exception as e:
            logger.error(f"Agent Extractor error: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'data': {},
                'confidence': 0.0
            }
    
    def _build_extraction_prompt(self, raw_text: str, schema: Dict[str, Any]) -> str:
        """
        Build a prompt for the LLM to extract data according to schema.
        
        Args:
            raw_text: Raw text to extract from
            schema: Target schema
            
        Returns:
            Prompt string
        """
        # Convert schema to readable format
        schema_description = self._format_schema(schema)
        
        prompt = f"""You are an expert data entry professional with perfect accuracy.

MISSION: Extract data from the following document text and structure it according to the provided JSON schema.

CRITICAL RULES:
1. Extract ONLY the information explicitly present in the document
2. If a field is not found in the document, return null for that field
3. Prioritize accuracy above all else - do not guess or infer
4. Return ONLY valid JSON, no markdown formatting or explanations
5. Include a confidence score (0.0 to 1.0) for each extracted field

TARGET SCHEMA:
{schema_description}

DOCUMENT TEXT:
{raw_text}

Your response must be a valid JSON object with this exact structure:
{{
    "extracted_data": {{
        "field_name": "extracted_value or null",
        ...
    }},
    "field_confidences": {{
        "field_name": 0.95,
        ...
    }},
    "overall_confidence": 0.90
}}

BEGIN EXTRACTION NOW:"""
        
        return prompt
    
    def _format_schema(self, schema: Dict[str, Any]) -> str:
        """
        Format schema for the LLM prompt.
        
        Args:
            schema: Data schema
            
        Returns:
            Formatted schema description
        """
        schema_lines = []
        
        for field_name, field_type in schema.items():
            if isinstance(field_type, dict):
                # Nested schema
                description = field_type.get('description', '')
                data_type = field_type.get('type', 'string')
                required = field_type.get('required', False)
                
                schema_lines.append(
                    f"  - {field_name} ({data_type}): {description}"
                    f"{' [REQUIRED]' if required else ''}"
                )
            else:
                # Simple type
                schema_lines.append(f"  - {field_name} ({field_type})")
        
        return "\n".join(schema_lines)
    
    def _parse_extraction_response(
        self,
        response_text: str,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse LLM response and extract data.
        
        Args:
            response_text: LLM response text
            schema: Target schema
            
        Returns:
            Dict with extraction result
        """
        try:
            # Clean response (remove markdown formatting if present)
            cleaned_text = response_text.strip()
            cleaned_text = cleaned_text.replace('```json', '').replace('```', '').strip()
            
            # Parse JSON
            parsed = json.loads(cleaned_text)
            
            # Extract components
            extracted_data = parsed.get('extracted_data', {})
            field_confidences = parsed.get('field_confidences', {})
            overall_confidence = parsed.get('overall_confidence', 0.8)
            
            # Validate against schema
            validated_data = self._validate_against_schema(extracted_data, schema)
            
            # Calculate overall confidence if not provided
            if not overall_confidence and field_confidences:
                overall_confidence = sum(field_confidences.values()) / len(field_confidences)
            
            return {
                'success': True,
                'data': validated_data,
                'confidence': overall_confidence,
                'field_confidences': field_confidences
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response text: {response_text}")
            
            return {
                'success': False,
                'error': f'Invalid JSON response: {str(e)}',
                'data': {},
                'confidence': 0.0
            }
        
        except Exception as e:
            logger.error(f"Failed to parse extraction response: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'data': {},
                'confidence': 0.0
            }
    
    def _validate_against_schema(
        self,
        data: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate extracted data against schema and fill missing fields.
        
        Args:
            data: Extracted data
            schema: Target schema
            
        Returns:
            Validated data with all schema fields
        """
        validated = {}
        
        for field_name, field_spec in schema.items():
            value = data.get(field_name)
            
            # Handle missing fields
            if value is None:
                validated[field_name] = None
                continue
            
            # Type coercion based on schema
            if isinstance(field_spec, dict):
                field_type = field_spec.get('type', 'string')
            else:
                field_type = field_spec
            
            try:
                validated[field_name] = self._coerce_type(value, field_type)
            except Exception as e:
                logger.warning(f"Type coercion failed for {field_name}: {e}")
                validated[field_name] = value  # Keep original value
        
        return validated
    
    def _coerce_type(self, value: Any, target_type: str) -> Any:
        """
        Coerce value to target type.
        
        Args:
            value: Input value
            target_type: Target type as string
            
        Returns:
            Coerced value
        """
        if value is None:
            return None
        
        type_map = {
            'string': str,
            'str': str,
            'integer': int,
            'int': int,
            'float': float,
            'number': float,
            'boolean': bool,
            'bool': bool,
            'date': str,  # Keep as string for now
            'datetime': str
        }
        
        converter = type_map.get(target_type.lower(), str)
        
        try:
            return converter(value)
        except (ValueError, TypeError):
            return value  # Return original if conversion fails
