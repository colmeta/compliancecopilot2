# ==============================================================================
# app/expense_management/receipt_processor.py
# Receipt Processor - Automated Receipt Scanning and Extraction
# ==============================================================================
"""
Receipt Processor: Hardcopy → Digital → Data

This processor handles the complete receipt processing workflow:
1. Scan/upload receipt image
2. OCR to extract text
3. Parse receipt structure
4. Extract key fields (date, amount, vendor, items)
5. Create expense record

Handles:
- Hardcopy receipts (scanned)
- Digital receipts (PDF, images)
- Email receipts
- Multiple currencies
- Various receipt formats
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class ReceiptProcessor:
    """
    Receipt Processor: Automated Receipt Intelligence.
    
    Transforms receipt images into structured expense data.
    """
    
    def __init__(self):
        """Initialize the Receipt Processor."""
        logger.info("ReceiptProcessor initialized - Automated Receipt Processing Ready")
    
    def process_receipt(
        self,
        receipt_image: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a receipt image and extract expense data.
        
        Args:
            receipt_image: Dict with image data (filename, content_base64, content_type)
            
        Returns:
            Dict with extracted expense data
        """
        try:
            # STEP 1: OCR - Extract text from image
            from app.data_entry.agent_visionary import AgentVisionary
            
            visionary = AgentVisionary()
            ocr_result = visionary.extract_text(receipt_image)
            
            if not ocr_result['success']:
                return {
                    'success': False,
                    'error': 'OCR failed'
                }
            
            raw_text = ocr_result['text']
            
            # STEP 2: Parse receipt structure
            parsed_data = self._parse_receipt_text(raw_text)
            
            # STEP 3: Extract key fields
            expense_data = self._extract_expense_fields(parsed_data, raw_text)
            
            # STEP 4: Validate data
            validation = self._validate_expense_data(expense_data)
            
            if not validation['valid']:
                expense_data['warnings'] = validation['warnings']
            
            return {
                'success': True,
                'expense_data': expense_data,
                'confidence': ocr_result.get('confidence', 0.8),
                'raw_text': raw_text
            }
            
        except Exception as e:
            logger.error(f"Receipt processing error: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_receipt_text(self, text: str) -> Dict[str, Any]:
        """
        Parse receipt text into structured components.
        
        Args:
            text: Raw OCR text
            
        Returns:
            Dict with parsed components
        """
        lines = text.split('\n')
        
        parsed = {
            'header': [],
            'items': [],
            'footer': [],
            'all_lines': lines
        }
        
        # Simple heuristic: first 5 lines are header, last 5 are footer
        if len(lines) > 10:
            parsed['header'] = lines[:5]
            parsed['footer'] = lines[-5:]
            parsed['items'] = lines[5:-5]
        else:
            parsed['header'] = lines[:2] if len(lines) > 2 else lines
            parsed['footer'] = lines[-2:] if len(lines) > 2 else lines
        
        return parsed
    
    def _extract_expense_fields(self, parsed_data: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
        """
        Extract key expense fields from parsed receipt.
        
        Args:
            parsed_data: Parsed receipt structure
            raw_text: Raw text for backup parsing
            
        Returns:
            Dict with expense fields
        """
        expense_data = {
            'vendor': None,
            'date': None,
            'total_amount': None,
            'currency': 'USD',
            'items': [],
            'tax': None,
            'tip': None
        }
        
        # Extract vendor (usually first non-empty line)
        for line in parsed_data['header']:
            if line.strip():
                expense_data['vendor'] = line.strip()
                break
        
        # Extract date
        expense_data['date'] = self._extract_date(raw_text)
        
        # Extract total amount
        expense_data['total_amount'] = self._extract_total(raw_text)
        
        # Extract currency
        currency = self._extract_currency(raw_text)
        if currency:
            expense_data['currency'] = currency
        
        # Extract tax
        expense_data['tax'] = self._extract_tax(raw_text)
        
        # Extract tip
        expense_data['tip'] = self._extract_tip(raw_text)
        
        return expense_data
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from receipt text."""
        # Common date patterns
        patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',  # MM/DD/YYYY
            r'\d{1,2}-\d{1,2}-\d{4}',  # MM-DD-YYYY
            r'\d{4}-\d{1,2}-\d{1,2}',  # YYYY-MM-DD
            r'\w+ \d{1,2}, \d{4}'       # Month DD, YYYY
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_total(self, text: str) -> Optional[float]:
        """Extract total amount from receipt text."""
        # Look for patterns like "Total: $XX.XX" or "Amount: $XX.XX"
        patterns = [
            r'(?:total|amount|sum)[:\s]*\$?(\d+\.?\d*)',
            r'\$(\d+\.\d{2})\s*(?:total|amount)?',
            r'grand\s+total[:\s]*\$?(\d+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        
        # Fallback: find largest dollar amount
        amounts = re.findall(r'\$(\d+\.\d{2})', text)
        if amounts:
            return max(float(amt) for amt in amounts)
        
        return None
    
    def _extract_currency(self, text: str) -> Optional[str]:
        """Extract currency from receipt text."""
        currency_symbols = {
            '$': 'USD',
            '€': 'EUR',
            '£': 'GBP',
            '¥': 'JPY',
            '₹': 'INR'
        }
        
        for symbol, code in currency_symbols.items():
            if symbol in text:
                return code
        
        # Look for currency codes
        currency_codes = ['USD', 'EUR', 'GBP', 'JPY', 'INR', 'CAD', 'AUD']
        for code in currency_codes:
            if code in text.upper():
                return code
        
        return None
    
    def _extract_tax(self, text: str) -> Optional[float]:
        """Extract tax amount from receipt text."""
        patterns = [
            r'tax[:\s]*\$?(\d+\.?\d*)',
            r'vat[:\s]*\$?(\d+\.?\d*)',
            r'gst[:\s]*\$?(\d+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        
        return None
    
    def _extract_tip(self, text: str) -> Optional[float]:
        """Extract tip amount from receipt text."""
        patterns = [
            r'tip[:\s]*\$?(\d+\.?\d*)',
            r'gratuity[:\s]*\$?(\d+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        
        return None
    
    def _validate_expense_data(self, expense_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extracted expense data.
        
        Args:
            expense_data: Extracted expense fields
            
        Returns:
            Dict with validation results
        """
        warnings = []
        
        if not expense_data.get('vendor'):
            warnings.append("Vendor name not found")
        
        if not expense_data.get('date'):
            warnings.append("Date not found")
        
        if not expense_data.get('total_amount'):
            warnings.append("Total amount not found")
        
        return {
            'valid': len(warnings) == 0,
            'warnings': warnings
        }
    
    def batch_process_receipts(
        self,
        receipt_images: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process multiple receipts in batch.
        
        Args:
            receipt_images: List of receipt image data
            
        Returns:
            Dict with batch processing results
        """
        results = []
        successful = 0
        failed = 0
        
        for receipt in receipt_images:
            result = self.process_receipt(receipt)
            results.append(result)
            
            if result['success']:
                successful += 1
            else:
                failed += 1
        
        return {
            'total': len(receipt_images),
            'successful': successful,
            'failed': failed,
            'results': results
        }


# Global instance
_processor = None


def get_receipt_processor() -> ReceiptProcessor:
    """Get or create the global ReceiptProcessor instance."""
    global _processor
    
    if _processor is None:
        _processor = ReceiptProcessor()
    
    return _processor
