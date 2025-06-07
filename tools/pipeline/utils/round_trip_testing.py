"""
Round-trip testing utilities for encoding conversions.
Ensures data integrity when converting between different encoding schemes.
"""

import sys
import os
sys.path.append('/Users/skmnktl/Projects/ambuda/vidyut/bindings-python')

import vidyut.lipi as lipi
from typing import Tuple, Dict, List
import hashlib
import logging

logger = logging.getLogger(__name__)

class RoundTripTester:
    """Tests encoding conversions for data loss."""
    
    def __init__(self):
        self.supported_schemes = {
            'baraha': lipi.Scheme.BarahaSouth,
            'devanagari': lipi.Scheme.Devanagari,
            'iast': lipi.Scheme.Iast,
            'slp1': lipi.Scheme.Slp1,
            'harvard_kyoto': lipi.Scheme.HarvardKyoto,
            'itrans': lipi.Scheme.Itrans,
            'velthuis': lipi.Scheme.Velthuis
        }
    
    def test_round_trip(self, text: str, source_scheme: str, target_scheme: str = 'slp1') -> Dict:
        """
        Test round-trip conversion: source -> target -> source
        
        Args:
            text: Original text to test
            source_scheme: Source encoding scheme name
            target_scheme: Target encoding scheme name (default: slp1)
            
        Returns:
            Dict with test results including is_lossless, differences, etc.
        """
        if source_scheme not in self.supported_schemes:
            raise ValueError(f"Unsupported source scheme: {source_scheme}")
        if target_scheme not in self.supported_schemes:
            raise ValueError(f"Unsupported target scheme: {target_scheme}")
        
        source_enum = self.supported_schemes[source_scheme]
        target_enum = self.supported_schemes[target_scheme]
        
        try:
            # Forward conversion: source -> target
            converted = lipi.transliterate(text, source_enum, target_enum)
            
            # Backward conversion: target -> source  
            round_trip = lipi.transliterate(converted, target_enum, source_enum)
            
            # Compare original with round-trip result
            is_lossless = text == round_trip
            
            result = {
                'original_text': text,
                'converted_text': converted,
                'round_trip_text': round_trip,
                'source_scheme': source_scheme,
                'target_scheme': target_scheme,
                'is_lossless': is_lossless,
                'original_checksum': hashlib.md5(text.encode()).hexdigest(),
                'converted_checksum': hashlib.md5(converted.encode()).hexdigest(),
                'round_trip_checksum': hashlib.md5(round_trip.encode()).hexdigest(),
                'diff_details': None
            }
            
            if not is_lossless:
                result['diff_details'] = self._find_differences(text, round_trip)
                logger.warning(f"Lossy conversion detected: {source_scheme} -> {target_scheme}")
                logger.warning(f"Original: {text}")
                logger.warning(f"Round-trip: {round_trip}")
            
            return result
            
        except Exception as e:
            logger.error(f"Round-trip test failed: {e}")
            return {
                'original_text': text,
                'converted_text': None,
                'round_trip_text': None,
                'source_scheme': source_scheme,
                'target_scheme': target_scheme,
                'is_lossless': False,
                'error': str(e),
                'diff_details': f"Conversion failed: {e}"
            }
    
    def _find_differences(self, text1: str, text2: str) -> str:
        """Find character-level differences between two texts."""
        if len(text1) != len(text2):
            return f"Length mismatch: {len(text1)} vs {len(text2)}"
        
        differences = []
        for i, (c1, c2) in enumerate(zip(text1, text2)):
            if c1 != c2:
                differences.append(f"Position {i}: '{c1}' != '{c2}'")
        
        return "; ".join(differences) if differences else "No character differences found"
    
    def batch_test(self, texts: List[str], source_scheme: str, target_scheme: str = 'slp1') -> List[Dict]:
        """Test multiple texts for round-trip conversion."""
        results = []
        for text in texts:
            result = self.test_round_trip(text, source_scheme, target_scheme)
            results.append(result)
        return results
    
    def get_lossless_rate(self, results: List[Dict]) -> float:
        """Calculate the percentage of lossless conversions."""
        if not results:
            return 0.0
        lossless_count = sum(1 for r in results if r.get('is_lossless', False))
        return lossless_count / len(results)


def validate_encoding_conversion(text: str, source_scheme: str, target_scheme: str = 'slp1') -> bool:
    """
    Quick validation function for encoding conversion.
    Returns True if conversion is lossless, False otherwise.
    """
    tester = RoundTripTester()
    result = tester.test_round_trip(text, source_scheme, target_scheme)
    return result.get('is_lossless', False)


if __name__ == "__main__":
    # Example usage and testing
    tester = RoundTripTester()
    
    # Test with Sanskrit text
    test_texts = [
        "नमस्ते",
        "अग्निमीळे पुरोहितं यज्ञस्य देवमृत्विजम्",
        "ॐ भूर्भुवः स्वः"
    ]
    
    for text in test_texts:
        print(f"\nTesting: {text}")
        result = tester.test_round_trip(text, 'devanagari', 'slp1')
        print(f"Lossless: {result['is_lossless']}")
        print(f"SLP1: {result['converted_text']}")
        if not result['is_lossless']:
            print(f"Differences: {result['diff_details']}")