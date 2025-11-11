# ==============================================================================
# app/data_entry/agent_validator.py
# Agent Validator - The Auditor (Quality Assurance & Validation)
# ==============================================================================
"""
Agent Validator: The third agent in the Data Keystone pipeline.

Mission: Guarantee accuracy, consistency, and integrity of extracted data,
flagging any ambiguities for human review.

Capabilities:
- Data type validation
- Business rule enforcement
- Confidence scoring with LLM verification
- Cross-field consistency checks
- Exception handling and quarantine logic
"""

import logging
from typing import Dict, Any, List, Optional
import re
from datetime import datetime
import json
import os
import google.generativeai as genai

logger = logging.getLogger(__name__)


class AgentValidator:
    """
    Agent Validator - Quality assurance and validation specialist.
    
    This is the most critical trust-building agent. It ensures every piece
    of data meets quality standards before proceeding.
    """
    
    def __init__(self, confidence_threshold: float = 0.85):
        """
        Initialize Agent Validator.
        
        Args:
            confidence_threshold: Minimum confidence to pass validation
        """
        self.confidence_threshold = confidence_threshold
        
        try:
            genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
            self.model = genai.GenerativeModel('gemini-pro')  # Use Pro for reliability
            self.llm_available = True
            logger.info("Agent Validator initialized successfully")
        except Exception as e:
            logger.warning(f"LLM not available for confidence scoring: {e}")
            self.llm_available = False
    
    def validate_data(
        self,
        extracted_data: Dict[str, Any],
        raw_text: str,
        schema: Dict[str, Any],
        business_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate extracted data against schema and business rules.
        
        Args:
            extracted_data: Data from Agent Extractor
            raw_text: Original text for confidence verification
            schema: Target schema
            business_rules: Optional business rules to enforce
            
        Returns:
            Dict with 'success', 'validated_data', 'confidence', 'errors', 'warnings'
        """
        errors = []
        warnings = []
        field_confidences = {}
        
        try:
            # VALIDATION STEP 1: Data Type Validation
            type_validation = self._validate_data_types(extracted_data, schema)
            errors.extend(type_validation['errors'])
            warnings.extend(type_validation['warnings'])
            
            # VALIDATION STEP 2: Required Field Check
            required_validation = self._validate_required_fields(extracted_data, schema)
            errors.extend(required_validation['errors'])
            
            # VALIDATION STEP 3: Business Rules Enforcement
            if business_rules:
                rules_validation = self._enforce_business_rules(
                    extracted_data,
                    business_rules
                )
                errors.extend(rules_validation['errors'])
                warnings.extend(rules_validation['warnings'])
            
            # VALIDATION STEP 4: Cross-Field Consistency
            consistency_validation = self._check_consistency(extracted_data, schema)
            warnings.extend(consistency_validation['warnings'])
            
            # VALIDATION STEP 5: LLM Confidence Scoring
            if self.llm_available:
                confidence_results = self._score_confidence(
                    extracted_data,
                    raw_text,
                    schema
                )
                field_confidences = confidence_results['field_confidences']
                warnings.extend(confidence_results['warnings'])
            else:
                # Fallback: use heuristic confidence
                field_confidences = self._heuristic_confidence(extracted_data)
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(
                field_confidences,
                errors,
                warnings
            )
            
            # Determine validation success
            success = (
                len(errors) == 0 and
                overall_confidence >= self.confidence_threshold
            )
            
            return {
                'success': success,
                'validated_data': extracted_data,
                'confidence': overall_confidence,
                'field_confidences': field_confidences,
                'errors': errors,
                'warnings': warnings
            }
            
        except Exception as e:
            logger.error(f"Agent Validator error: {e}", exc_info=True)
            return {
                'success': False,
                'validated_data': extracted_data,
                'confidence': 0.0,
                'field_confidences': {},
                'errors': [f"Validation error: {str(e)}"],
                'warnings': []
            }
    
    def _validate_data_types(
        self,
        data: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Validate data types match schema.
        
        Args:
            data: Extracted data
            schema: Target schema
            
        Returns:
            Dict with 'errors' and 'warnings'
        """
        errors = []
        warnings = []
        
        for field_name, field_spec in schema.items():
            value = data.get(field_name)
            
            if value is None:
                continue  # Null values handled separately
            
            # Get expected type
            if isinstance(field_spec, dict):
                expected_type = field_spec.get('type', 'string')
            else:
                expected_type = field_spec
            
            # Validate type
            validation_result = self._validate_field_type(value, expected_type)
            
            if not validation_result['valid']:
                errors.append(
                    f"Field '{field_name}': {validation_result['error']}"
                )
        
        return {'errors': errors, 'warnings': warnings}
    
    def _validate_field_type(self, value: Any, expected_type: str) -> Dict[str, Any]:
        """
        Validate a single field's type.
        
        Args:
            value: Field value
            expected_type: Expected type as string
            
        Returns:
            Dict with 'valid' and 'error'
        """
        if expected_type.lower() in ['string', 'str']:
            if not isinstance(value, str):
                return {
                    'valid': False,
                    'error': f"Expected string, got {type(value).__name__}"
                }
        
        elif expected_type.lower() in ['integer', 'int']:
            if not isinstance(value, int) or isinstance(value, bool):
                return {
                    'valid': False,
                    'error': f"Expected integer, got {type(value).__name__}"
                }
        
        elif expected_type.lower() in ['float', 'number']:
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                return {
                    'valid': False,
                    'error': f"Expected number, got {type(value).__name__}"
                }
        
        elif expected_type.lower() in ['boolean', 'bool']:
            if not isinstance(value, bool):
                return {
                    'valid': False,
                    'error': f"Expected boolean, got {type(value).__name__}"
                }
        
        elif expected_type.lower() == 'date':
            # Validate date format
            if not self._is_valid_date(value):
                return {
                    'valid': False,
                    'error': f"Invalid date format: {value}"
                }
        
        return {'valid': True, 'error': None}
    
    def _is_valid_date(self, value: str) -> bool:
        """
        Check if value is a valid date.
        
        Args:
            value: String value to check
            
        Returns:
            True if valid date
        """
        if not isinstance(value, str):
            return False
        
        date_formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y/%m/%d',
            '%m-%d-%Y',
            '%d-%m-%Y'
        ]
        
        for fmt in date_formats:
            try:
                datetime.strptime(value, fmt)
                return True
            except ValueError:
                continue
        
        return False
    
    def _validate_required_fields(
        self,
        data: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Validate required fields are present and non-null.
        
        Args:
            data: Extracted data
            schema: Target schema
            
        Returns:
            Dict with 'errors'
        """
        errors = []
        
        for field_name, field_spec in schema.items():
            if isinstance(field_spec, dict) and field_spec.get('required', False):
                value = data.get(field_name)
                
                if value is None or value == '':
                    errors.append(f"Required field '{field_name}' is missing or empty")
        
        return {'errors': errors}
    
    def _enforce_business_rules(
        self,
        data: Dict[str, Any],
        business_rules: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Enforce custom business rules.
        
        Args:
            data: Extracted data
            business_rules: Business rules to enforce
            
        Returns:
            Dict with 'errors' and 'warnings'
        """
        errors = []
        warnings = []
        
        for rule_name, rule_spec in business_rules.items():
            rule_type = rule_spec.get('type')
            field = rule_spec.get('field')
            
            if rule_type == 'date_not_future':
                # Date cannot be in the future
                value = data.get(field)
                if value and self._is_valid_date(value):
                    try:
                        date_value = datetime.strptime(value, '%Y-%m-%d')
                        if date_value > datetime.now():
                            errors.append(
                                f"Field '{field}' cannot be in the future"
                            )
                    except ValueError:
                        pass
            
            elif rule_type == 'sum_equals':
                # Sum of fields must equal another field
                sum_fields = rule_spec.get('sum_fields', [])
                target_field = rule_spec.get('target_field')
                
                total = sum(data.get(f, 0) for f in sum_fields)
                target_value = data.get(target_field, 0)
                
                if abs(total - target_value) > 0.01:  # Allow small rounding errors
                    errors.append(
                        f"Sum of {sum_fields} ({total}) does not equal "
                        f"{target_field} ({target_value})"
                    )
            
            elif rule_type == 'regex':
                # Field must match regex pattern
                pattern = rule_spec.get('pattern')
                value = data.get(field, '')
                
                if value and not re.match(pattern, str(value)):
                    errors.append(
                        f"Field '{field}' does not match required pattern"
                    )
            
            elif rule_type == 'range':
                # Field value must be in range
                min_value = rule_spec.get('min')
                max_value = rule_spec.get('max')
                value = data.get(field)
                
                if value is not None:
                    if min_value is not None and value < min_value:
                        errors.append(
                            f"Field '{field}' value {value} is below minimum {min_value}"
                        )
                    if max_value is not None and value > max_value:
                        errors.append(
                            f"Field '{field}' value {value} exceeds maximum {max_value}"
                        )
        
        return {'errors': errors, 'warnings': warnings}
    
    def _check_consistency(
        self,
        data: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Check cross-field consistency.
        
        Args:
            data: Extracted data
            schema: Target schema
            
        Returns:
            Dict with 'warnings'
        """
        warnings = []
        
        # Check for suspicious patterns
        # Example: All numeric fields are zero
        numeric_fields = [
            k for k, v in data.items()
            if isinstance(v, (int, float)) and k != 'id'
        ]
        
        if numeric_fields and all(data.get(f) == 0 for f in numeric_fields):
            warnings.append("All numeric fields are zero - please verify")
        
        # Check for duplicate values in fields that should be unique
        # (This would require schema metadata about uniqueness)
        
        return {'warnings': warnings}
    
    def _score_confidence(
        self,
        data: Dict[str, Any],
        raw_text: str,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use LLM to score confidence for each field.
        
        Args:
            data: Extracted data
            raw_text: Original text
            schema: Target schema
            
        Returns:
            Dict with 'field_confidences' and 'warnings'
        """
        field_confidences = {}
        warnings = []
        
        try:
            # Create prompt for confidence scoring
            prompt = f"""You are a data quality expert. Review the following data extraction and provide a confidence score (0.0 to 1.0) for each field.

ORIGINAL TEXT:
{raw_text[:2000]}  # Limit to first 2000 chars

EXTRACTED DATA:
{json.dumps(data, indent=2)}

For each field, consider:
1. Is the value clearly stated in the original text?
2. Is there any ambiguity or potential for misreading?
3. Does the value make logical sense?

Respond with ONLY a JSON object:
{{
    "field_confidences": {{
        "field_name": 0.95,
        ...
    }},
    "warnings": ["warning 1", "warning 2"]
}}"""
            
            response = self.model.generate_content(prompt)
            
            # Parse response
            cleaned = response.text.strip().replace('```json', '').replace('```', '').strip()
            parsed = json.loads(cleaned)
            
            field_confidences = parsed.get('field_confidences', {})
            warnings = parsed.get('warnings', [])
            
        except Exception as e:
            logger.warning(f"LLM confidence scoring failed: {e}")
            # Fallback to heuristic
            field_confidences = self._heuristic_confidence(data)
        
        return {
            'field_confidences': field_confidences,
            'warnings': warnings
        }
    
    def _heuristic_confidence(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate heuristic confidence scores.
        
        Args:
            data: Extracted data
            
        Returns:
            Dict mapping field names to confidence scores
        """
        confidences = {}
        
        for field_name, value in data.items():
            if value is None:
                confidences[field_name] = 0.0
            elif isinstance(value, str) and len(value) == 0:
                confidences[field_name] = 0.0
            elif isinstance(value, str) and len(value) < 3:
                confidences[field_name] = 0.7  # Short strings might be correct
            else:
                confidences[field_name] = 0.85  # Default reasonable confidence
        
        return confidences
    
    def _calculate_overall_confidence(
        self,
        field_confidences: Dict[str, float],
        errors: List[str],
        warnings: List[str]
    ) -> float:
        """
        Calculate overall confidence score.
        
        Args:
            field_confidences: Per-field confidence scores
            errors: List of errors
            warnings: List of warnings
            
        Returns:
            Overall confidence score (0.0 to 1.0)
        """
        if errors:
            return 0.0  # Any errors = zero confidence
        
        if not field_confidences:
            return 0.5  # No data = low confidence
        
        # Average field confidences
        avg_confidence = sum(field_confidences.values()) / len(field_confidences)
        
        # Penalize for warnings
        warning_penalty = len(warnings) * 0.05
        
        final_confidence = max(0.0, avg_confidence - warning_penalty)
        
        return round(final_confidence, 3)
