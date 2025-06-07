"""
Stage 3: Encoding Conversion
Converts all texts to SLP1 encoding with round-trip validation.
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional
import logging
from datetime import datetime
import hashlib

# Add project root and vidyut path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append('/Users/skmnktl/Projects/ambuda/vidyut/bindings-python')

try:
    import vidyut.lipi as lipi
except ImportError:
    print("vidyut-lipi not found. Check PYTHONPATH.")
    sys.exit(1)

from utils.round_trip_testing import RoundTripTester
from utils.vedic_encoding_handler import VedicEncodingHandler
from utils.slp1_extended import SLP1Extended

logger = logging.getLogger(__name__)

class EncodingConverter:
    """Stage 3: Convert text to SLP1 encoding with validation."""
    
    def __init__(self):
        self.target_scheme = 'slp1'
        self.round_trip_tester = RoundTripTester()
        self.encoding_handler = VedicEncodingHandler()
        self.slp1_extended = SLP1Extended()
        
        # Mapping of source encodings to vidyut-lipi schemes
        self.encoding_map = {
            'baraha': 'BarahaSouth', 
            'devanagari': 'Devanagari',
            'iast': 'Iast',
            'harvard_kyoto': 'HarvardKyoto',
            'itrans': 'Itrans',
            'slp1': 'Slp1'
        }
        
        # Get vidyut-lipi scheme objects
        self.vidyut_schemes = {}
        for encoding, scheme_name in self.encoding_map.items():
            try:
                self.vidyut_schemes[encoding] = getattr(lipi.Scheme, scheme_name)
            except AttributeError:
                logger.warning(f"Scheme {scheme_name} not available in vidyut-lipi")
    
    def convert_text(self, text: str, source_encoding: str, metadata: Dict) -> Dict:
        """
        Convert text to SLP1 encoding with round-trip validation.
        
        Args:
            text: Normalized text to convert
            source_encoding: Source encoding scheme
            metadata: Text metadata
            
        Returns:
            Dict with conversion results and validation info
        """
        logger.info(f"Converting text from {source_encoding} to SLP1: {len(text)} characters")
        
        if source_encoding not in self.vidyut_schemes:
            raise ValueError(f"Unsupported source encoding: {source_encoding}")
        
        original_checksum = self._calculate_checksum(text)
        
        try:
            # Detect encoding features
            features = self.encoding_handler.detect_encoding(text)
            logger.info(f"Detected features: {features}")
            
            # Use special handling for Baraha texts with accents/special markers
            if source_encoding == 'baraha' and (features['has_accents'] or features['has_nasal_annotations']):
                # First convert to SLP1-Extended to preserve markers
                encoded_result = self.slp1_extended.create_round_trip_safe_encoding(text, source_encoding)
                slp1_extended_text = encoded_result['encoded']
                
                # Now convert the base text (without markers) through vidyut-lipi
                # Strip markers temporarily for vidyut conversion
                pure_text = self.slp1_extended.strip_extensions(slp1_extended_text)
                
                # For Baraha, we need to handle the base text conversion
                # First decode back to get Baraha without special markers
                temp_baraha = self.slp1_extended.decode_slp1_ext_to_baraha(slp1_extended_text)
                # Remove the special markers we know about
                # Process in order to avoid conflicts with bar markers
                for marker in ['q', '#', '$', '&', '(gm)', '(gg)', '~M', '~j', '~g', '|||', '||', '|']:
                    temp_baraha = temp_baraha.replace(marker, '')
                
                # Convert clean Baraha to SLP1
                source_scheme = self.vidyut_schemes[source_encoding]
                target_scheme = self.vidyut_schemes['slp1']
                slp1_base = lipi.transliterate(temp_baraha, source_scheme, target_scheme)
                
                # Merge: Use SLP1-Extended format as final result
                slp1_text = slp1_extended_text
                
                # For round-trip, validate using our extended encoding
                round_trip_result = {
                    'is_lossless': encoded_result['is_lossless'],
                    'original_text': text,
                    'converted_text': slp1_text,
                    'round_trip_text': encoded_result['decoded'],
                    'was_preprocessed': True,
                    'encoding_method': 'slp1_extended'
                }
                
            else:
                # Standard conversion for non-Baraha or simple texts
                source_scheme = self.vidyut_schemes[source_encoding]
                target_scheme = self.vidyut_schemes['slp1']
                
                slp1_text = lipi.transliterate(text, source_scheme, target_scheme)
                
                # Perform standard round-trip testing
                round_trip_result = self.round_trip_tester.test_round_trip(
                    text, source_encoding, 'slp1'
                )
                round_trip_result['was_preprocessed'] = False
                round_trip_result['encoding_method'] = 'standard'
            
            slp1_checksum = self._calculate_checksum(slp1_text)
            
            # Validate conversion
            validation_result = self._validate_conversion(
                text, slp1_text, source_encoding, round_trip_result, metadata
            )
            
            result = {
                'original_text': text,
                'slp1_text': slp1_text,
                'source_encoding': source_encoding,
                'target_encoding': 'slp1',
                'original_length': len(text),
                'slp1_length': len(slp1_text),
                'original_checksum': original_checksum,
                'slp1_checksum': slp1_checksum,
                'round_trip_result': round_trip_result,
                'validation_result': validation_result,
                'stage': 'encoding_conversion',
                'stage_timestamp': datetime.now().isoformat(),
                'vidyut_version': self._get_vidyut_version()
            }
            
            logger.info(f"Conversion complete: {source_encoding} -> SLP1, "
                       f"lossless: {round_trip_result.get('is_lossless', False)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Conversion failed for {source_encoding} -> SLP1: {e}")
            return {
                'original_text': text,
                'slp1_text': None,
                'source_encoding': source_encoding,
                'target_encoding': 'slp1',
                'conversion_error': str(e),
                'round_trip_result': {'is_lossless': False, 'error': str(e)},
                'validation_result': {'is_valid': False, 'errors': [str(e)]},
                'stage': 'encoding_conversion',
                'stage_timestamp': datetime.now().isoformat()
            }
    
    def _validate_conversion(self, original: str, converted: str, source_encoding: str, 
                           round_trip_result: Dict, metadata: Dict) -> Dict:
        """Validate the encoding conversion."""
        validation = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'stats': {}
        }
        
        # Check for conversion failure
        if not converted:
            validation['errors'].append("Conversion produced empty result")
            validation['is_valid'] = False
            return validation
        
        # Check round-trip test result
        if not round_trip_result.get('is_lossless', False):
            if round_trip_result.get('error'):
                validation['errors'].append(f"Round-trip test failed: {round_trip_result['error']}")
                validation['is_valid'] = False
            else:
                validation['warnings'].append("Round-trip test detected lossy conversion")
                validation['warnings'].append(f"Differences: {round_trip_result.get('diff_details', 'unknown')}")
        
        # Check for dramatic length changes (might indicate encoding issues)
        length_ratio = len(converted) / len(original) if original else 0
        if length_ratio > 2.0:
            validation['warnings'].append(f"Converted text much longer than original: {length_ratio:.1f}x")
        elif length_ratio < 0.5:
            validation['warnings'].append(f"Converted text much shorter than original: {length_ratio:.1f}x")
        
        # Check for valid SLP1 characters
        invalid_chars = self._find_invalid_slp1_chars(converted)
        if invalid_chars:
            validation['warnings'].append(f"Non-SLP1 characters found: {invalid_chars}")
        
        # Statistics
        validation['stats'] = {
            'original_length': len(original),
            'converted_length': len(converted),
            'length_ratio': length_ratio,
            'round_trip_lossless': round_trip_result.get('is_lossless', False)
        }
        
        if validation['errors']:
            logger.error(f"Conversion validation failed: {validation['errors']}")
        elif validation['warnings']:
            logger.warning(f"Conversion warnings: {validation['warnings']}")
        
        return validation
    
    def _find_invalid_slp1_chars(self, text: str) -> List[str]:
        """Find characters that are not valid in SLP1 or SLP1-Extended."""
        # SLP1 valid characters (basic set)
        valid_chars = set('aAiIuUfFxXeEoOMHkKgGNcCjJYwWqQRtTdDnpPbBmyrlvSs')
        valid_chars.update(' \n\t.,;:!?()[]|-+=123456789')  # Common punctuation and numbers
        
        # For SLP1-Extended, also allow our extension markers
        # Check if this is SLP1-Extended format
        if '{' in text and '}' in text:
            # This appears to be SLP1-Extended, so validate differently
            # Remove all valid extension markers first
            temp_text = text
            import re
            ext_pattern = re.compile(r'\{[^}]+\}')
            temp_text = ext_pattern.sub('', temp_text)
            
            # Now check remaining text
            invalid = set()
            for char in temp_text:
                if char not in valid_chars:
                    invalid.add(char)
        else:
            # Standard SLP1 validation
            invalid = set()
            for char in text:
                if char not in valid_chars:
                    invalid.add(char)
        
        return sorted(list(invalid))
    
    def _calculate_checksum(self, text: str) -> str:
        """Calculate MD5 checksum of text."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _get_vidyut_version(self) -> str:
        """Get vidyut-lipi version info."""
        try:
            # Try to get version info if available
            return "vidyut-lipi-python"
        except:
            return "unknown"
    
    def batch_convert(self, normalized_data: List[Dict]) -> List[Dict]:
        """Convert a batch of normalized texts to SLP1."""
        converted_data = []
        
        for item in normalized_data:
            try:
                # Use normalized text if available, otherwise fall back to raw text
                text_to_convert = item.get('normalized_text', item.get('raw_text', ''))
                source_encoding = item.get('encoding', 'unknown')
                
                if not text_to_convert:
                    logger.warning(f"No text to convert for {item.get('source_file', 'unknown')}")
                    continue
                
                conversion_result = self.convert_text(
                    text_to_convert,
                    source_encoding,
                    item.get('metadata', {})
                )
                
                # Combine with previous stage data
                result = item.copy()
                result.update(conversion_result)
                converted_data.append(result)
                
            except Exception as e:
                logger.error(f"Failed to convert {item.get('source_file', 'unknown')}: {e}")
                # Add failed item with error info
                result = item.copy()
                result.update({
                    'slp1_text': item.get('normalized_text', item.get('raw_text', '')),
                    'conversion_error': str(e),
                    'stage': 'encoding_conversion',
                    'stage_timestamp': datetime.now().isoformat()
                })
                converted_data.append(result)
        
        return converted_data
    
    def get_conversion_stats(self, converted_data: List[Dict]) -> Dict:
        """Generate statistics about the conversion results."""
        stats = {
            'total_conversions': len(converted_data),
            'successful_conversions': 0,
            'lossless_conversions': 0,
            'failed_conversions': 0,
            'by_source_encoding': {},
            'total_original_chars': 0,
            'total_slp1_chars': 0
        }
        
        for item in converted_data:
            source_encoding = item.get('source_encoding', 'unknown')
            
            # Count by encoding
            stats['by_source_encoding'][source_encoding] = \
                stats['by_source_encoding'].get(source_encoding, 0) + 1
            
            # Count success/failure
            if item.get('conversion_error'):
                stats['failed_conversions'] += 1
            else:
                stats['successful_conversions'] += 1
                
                # Count lossless conversions
                if item.get('round_trip_result', {}).get('is_lossless', False):
                    stats['lossless_conversions'] += 1
            
            # Character counts
            stats['total_original_chars'] += item.get('original_length', 0)
            stats['total_slp1_chars'] += item.get('slp1_length', 0)
        
        # Calculate rates
        if stats['total_conversions'] > 0:
            stats['success_rate'] = stats['successful_conversions'] / stats['total_conversions']
            stats['lossless_rate'] = stats['lossless_conversions'] / stats['total_conversions']
        
        return stats


if __name__ == "__main__":
    # Test the converter
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Create test data
    test_data = [
        {
            'source_file': 'test_baraha.txt',
            'encoding': 'baraha', 
            'normalized_text': 'agniM parameSTI yajamAnaH',
            'metadata': {'veda': 'yajurveda', 'text_type': 'samhita'}
        },
        {
            'source_file': 'test_devanagari.json',
            'encoding': 'devanagari',
            'normalized_text': 'अग्निमीळे पुरोहितं यज्ञस्य देवम्',
            'metadata': {'veda': 'rigveda', 'text_type': 'samhita'}
        }
    ]
    
    converter = EncodingConverter()
    converted_data = converter.batch_convert(test_data)
    
    print("Encoding Conversion Test Results:")
    for item in converted_data:
        print(f"\nSource: {item.get('source_encoding', 'unknown')}")
        print(f"Original: {item.get('original_text', 'N/A')}")
        print(f"SLP1: {item.get('slp1_text', 'N/A')}")
        print(f"Lossless: {item.get('round_trip_result', {}).get('is_lossless', False)}")
        
        validation = item.get('validation_result', {})
        if validation.get('warnings'):
            print(f"Warnings: {validation['warnings']}")
        if validation.get('errors'):
            print(f"Errors: {validation['errors']}")
    
    # Show statistics
    stats = converter.get_conversion_stats(converted_data)
    print(f"\nConversion Statistics:")
    print(f"Total: {stats['total_conversions']}")
    print(f"Successful: {stats['successful_conversions']}")
    print(f"Lossless: {stats['lossless_conversions']}")
    print(f"Success rate: {stats.get('success_rate', 0):.1%}")
    print(f"Lossless rate: {stats.get('lossless_rate', 0):.1%}")