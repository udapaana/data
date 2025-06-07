"""
Stage 2: Text Normalization
Cleans and standardizes text while preserving content integrity.
"""

import re
import unicodedata
from typing import Dict, List, Tuple
import logging
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class TextNormalizer:
    """Stage 2: Normalize and clean text content."""
    
    def __init__(self):
        self.normalization_rules = {
            'vedavms': self._get_vedavms_rules(),
            'vedanidhi': self._get_vedanidhi_rules(),
            'common': self._get_common_rules()
        }
    
    def normalize_text(self, text: str, source_name: str, metadata: Dict) -> Dict:
        """
        Normalize text content based on source type.
        
        Args:
            text: Raw text to normalize
            source_name: Source type (vedavms, vedanidhi, etc.)
            metadata: Metadata from Stage 1
            
        Returns:
            Dict with normalized text and processing info
        """
        logger.info(f"Normalizing text from {source_name}: {len(text)} characters")
        
        original_checksum = self._calculate_checksum(text)
        normalized_text = text
        applied_rules = []
        
        # Apply source-specific rules
        if source_name in self.normalization_rules:
            for rule_name, rule_func in self.normalization_rules[source_name].items():
                before = normalized_text
                normalized_text = rule_func(normalized_text)
                if before != normalized_text:
                    applied_rules.append(rule_name)
                    logger.debug(f"Applied rule: {rule_name}")
        
        # Apply common rules
        for rule_name, rule_func in self.normalization_rules['common'].items():
            before = normalized_text
            normalized_text = rule_func(normalized_text)
            if before != normalized_text:
                applied_rules.append(f"common_{rule_name}")
                logger.debug(f"Applied common rule: {rule_name}")
        
        # Calculate final checksum
        normalized_checksum = self._calculate_checksum(normalized_text)
        
        # Validate normalization
        validation_result = self._validate_normalization(text, normalized_text, metadata)
        
        result = {
            'original_text': text,
            'normalized_text': normalized_text,
            'original_length': len(text),
            'normalized_length': len(normalized_text),
            'original_checksum': original_checksum,
            'normalized_checksum': normalized_checksum,
            'applied_rules': applied_rules,
            'character_reduction': len(text) - len(normalized_text),
            'stage': 'text_normalization',
            'stage_timestamp': datetime.now().isoformat(),
            'validation_result': validation_result
        }
        
        logger.info(f"Normalization complete: {len(applied_rules)} rules applied, "
                   f"{result['character_reduction']} characters removed")
        
        return result
    
    def _get_vedavms_rules(self) -> Dict:
        """Normalization rules specific to VedaVMS (Baraha) sources."""
        return {
            'remove_word_wrapping': self._remove_word_wrapping,
            'clean_baraha_artifacts': self._clean_baraha_artifacts,
            'normalize_punctuation': self._normalize_punctuation,
            'fix_line_breaks': self._fix_line_breaks
        }
    
    def _get_vedanidhi_rules(self) -> Dict:
        """Normalization rules specific to Vedanidhi (Devanagari) sources."""
        return {
            'normalize_unicode': self._normalize_unicode_devanagari,
            'clean_json_artifacts': self._clean_json_artifacts,
            'normalize_diacritics': self._normalize_diacritics,
            'fix_spacing': self._fix_spacing
        }
    
    def _get_common_rules(self) -> Dict:
        """Common normalization rules for all sources."""
        return {
            'normalize_whitespace': self._normalize_whitespace,
            'remove_empty_lines': self._remove_empty_lines,
            'standardize_markers': self._standardize_section_markers,
            'trim_content': self._trim_content
        }
    
    # VedaVMS-specific rules
    def _remove_word_wrapping(self, text: str) -> str:
        """Remove artificial word wrapping from DOCX conversion."""
        # Join lines that end with lowercase and start with lowercase (likely wrapped words)
        lines = text.split('\n')
        result_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                result_lines.append('')
                continue
                
            # Check if this line should be joined with the next
            if (i < len(lines) - 1 and 
                line and lines[i + 1].strip() and
                line[-1].islower() and lines[i + 1].strip()[0].islower()):
                # Don't add this line yet, it will be joined
                continue
            else:
                # Check if previous line should be joined with this one
                if (result_lines and result_lines[-1] and 
                    result_lines[-1][-1].islower() and line[0].islower()):
                    result_lines[-1] += ' ' + line
                else:
                    result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def _clean_baraha_artifacts(self, text: str) -> str:
        """Clean artifacts specific to Baraha encoding conversion."""
        # Remove common artifacts from DOCX->text conversion
        text = re.sub(r'\u00A0', ' ', text)  # Non-breaking space
        text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)  # Zero-width characters
        return text
    
    def _normalize_punctuation(self, text: str) -> str:
        """Normalize punctuation marks."""
        # Standardize quotes
        text = re.sub(r'[""''`]', '"', text)
        # Standardize dashes
        text = re.sub(r'[–—]', '-', text)
        return text
    
    def _fix_line_breaks(self, text: str) -> str:
        """Fix inconsistent line breaks."""
        # Convert multiple consecutive line breaks to double line breaks
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text
    
    # Vedanidhi-specific rules
    def _normalize_unicode_devanagari(self, text: str) -> str:
        """Normalize Devanagari Unicode characters."""
        # Apply Unicode normalization (NFC - composed form)
        text = unicodedata.normalize('NFC', text)
        return text
    
    def _clean_json_artifacts(self, text: str) -> str:
        """Remove artifacts from JSON parsing."""
        # Remove escape sequences that might have leaked through
        text = re.sub(r'\\[ntr]', ' ', text)
        text = re.sub(r'\\["\'/]', '', text)
        return text
    
    def _normalize_diacritics(self, text: str) -> str:
        """Normalize Devanagari diacritics and accents."""
        # This would include specific Devanagari normalization
        # For now, just basic Unicode normalization
        return unicodedata.normalize('NFC', text)
    
    def _fix_spacing(self, text: str) -> str:
        """Fix spacing issues in Devanagari text."""
        # Remove extra spaces around Devanagari punctuation
        text = re.sub(r'\s*([।॥])\s*', r'\1 ', text)
        return text
    
    # Common rules
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize all whitespace to standard spaces."""
        # Replace tabs, non-breaking spaces, etc. with regular spaces
        text = re.sub(r'[\t\r\f\v\u00A0\u2000-\u200B]+', ' ', text)
        # Collapse multiple spaces
        text = re.sub(r' {2,}', ' ', text)
        return text
    
    def _remove_empty_lines(self, text: str) -> str:
        """Remove completely empty lines but preserve intentional line breaks."""
        lines = text.split('\n')
        result_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped or (result_lines and result_lines[-1].strip()):
                # Keep non-empty lines and single empty lines after content
                result_lines.append(line.rstrip())  # Remove trailing whitespace
        
        return '\n'.join(result_lines)
    
    def _standardize_section_markers(self, text: str) -> str:
        """Standardize section markers and numbering."""
        # Standardize various forms of section markers
        text = re.sub(r'(\d+)[\.\):]', r'\1.', text)  # Standardize numbering
        text = re.sub(r'[।॥]{2,}', '॥', text)  # Standardize double danda
        return text
    
    def _trim_content(self, text: str) -> str:
        """Trim leading and trailing whitespace."""
        return text.strip()
    
    def _calculate_checksum(self, text: str) -> str:
        """Calculate MD5 checksum of text."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _validate_normalization(self, original: str, normalized: str, metadata: Dict) -> Dict:
        """Validate that normalization didn't lose important content."""
        validation = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'stats': {}
        }
        
        # Check for excessive content loss
        reduction_ratio = (len(original) - len(normalized)) / len(original) if original else 0
        if reduction_ratio > 0.1:  # More than 10% reduction
            validation['warnings'].append(f"High content reduction: {reduction_ratio:.1%}")
        
        # Check for complete content loss
        if not normalized.strip():
            validation['errors'].append("All content was removed during normalization")
            validation['is_valid'] = False
        
        # Check for character encoding issues
        try:
            normalized.encode('utf-8')
        except UnicodeEncodeError as e:
            validation['errors'].append(f"Unicode encoding error: {e}")
            validation['is_valid'] = False
        
        # Statistics
        validation['stats'] = {
            'original_length': len(original),
            'normalized_length': len(normalized),
            'lines_original': original.count('\n') + 1,
            'lines_normalized': normalized.count('\n') + 1,
            'reduction_ratio': reduction_ratio
        }
        
        if validation['errors']:
            logger.error(f"Normalization validation failed: {validation['errors']}")
        elif validation['warnings']:
            logger.warning(f"Normalization warnings: {validation['warnings']}")
        
        return validation
    
    def batch_normalize(self, extracted_data: List[Dict]) -> List[Dict]:
        """Normalize a batch of extracted texts."""
        normalized_data = []
        
        for item in extracted_data:
            try:
                normalization_result = self.normalize_text(
                    item['raw_text'],
                    item['source_name'], 
                    item['metadata']
                )
                
                # Combine with original data
                result = item.copy()
                result.update(normalization_result)
                normalized_data.append(result)
                
            except Exception as e:
                logger.error(f"Failed to normalize {item.get('source_file', 'unknown')}: {e}")
                # Add failed item with error info
                result = item.copy()
                result.update({
                    'normalized_text': item['raw_text'],  # Use original as fallback
                    'normalization_error': str(e),
                    'stage': 'text_normalization',
                    'stage_timestamp': datetime.now().isoformat()
                })
                normalized_data.append(result)
        
        return normalized_data


if __name__ == "__main__":
    # Test the normalizer
    import json
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Load sample data from Stage 1
    try:
        # Create test data if Stage 1 output doesn't exist
        test_data = [
            {
                'source_file': 'test.txt',
                'source_name': 'vedavms',
                'raw_text': 'agniM  parame\nSTI  yaja\nmAnaH   || 1 ||',
                'metadata': {'veda': 'yajurveda', 'text_type': 'samhita'}
            },
            {
                'source_file': 'test2.json', 
                'source_name': 'vedanidhi',
                'raw_text': 'अग्निमीळे  पुरोहितं\n\n\nयज्ञस्य  देवम् ॥',
                'metadata': {'veda': 'rigveda', 'text_type': 'samhita'}
            }
        ]
        
        normalizer = TextNormalizer()
        normalized_data = normalizer.batch_normalize(test_data)
        
        print("Normalization Test Results:")
        for item in normalized_data:
            print(f"\nSource: {item['source_name']}")
            print(f"Original length: {item.get('original_length', 'unknown')}")
            print(f"Normalized length: {item.get('normalized_length', 'unknown')}")
            print(f"Rules applied: {item.get('applied_rules', [])}")
            if item.get('validation_result', {}).get('warnings'):
                print(f"Warnings: {item['validation_result']['warnings']}")
        
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()