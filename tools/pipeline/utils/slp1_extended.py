"""
Extended SLP1 encoding for preserving Vedic text features using ASCII-safe markers.
"""

import re
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class SLP1Extended:
    """
    SLP1 encoding with ASCII-safe extensions for Vedic texts.
    
    Uses inline markers to preserve source-specific features:
    - Accents: {U}, {A}, {S} for udatta, anudatta, svarita
    - Nasals: {GM}, {GG}, {NM} etc.
    - Sections: {|}, {||}, {|||}
    - Numbers: preserved as-is
    """
    
    def __init__(self):
        # Baraha to SLP1-Extended mappings
        self.baraha_to_slp1_ext = {
            # Accent markers (using inline notation)
            'q': '{A}',     # anudatta
            '#': '{S}',     # svarita
            '$': '{DS}',    # dheerga svarita
            '&': '{AV}',    # avagraha
            
            # Nasal annotations (preserved with clear markers)
            '(gm)': '{GM}',  # guttural + m
            '(gg)': '{GG}',  # guttural + g
            '(nn)': '{NN}',  # dental n
            '~M': '{NM}',    # nasal M
            '~j': '{NJ}',    # palatal nasal
            '~g': '{NG}',    # guttural nasal
            
            # Other markers
            '^^': '{CS}',    # compound separator
            '|||': '{3BAR}', # triple bar
            '||': '{2BAR}',   # double bar
            '|': '{1BAR}',    # single bar
        }
        
        # Reverse mapping for restoration
        self.slp1_ext_to_baraha = {v: k for k, v in self.baraha_to_slp1_ext.items()}
        
        # Pattern to identify SLP1-Extended markers
        self.ext_pattern = re.compile(r'\{[^}]+\}')
        
        # Pattern to identify numbers with context
        self.number_pattern = re.compile(r'(\d+)')

    def encode_baraha_to_slp1_ext(self, text: str) -> Tuple[str, Dict]:
        """
        Encode Baraha text to SLP1-Extended format.
        
        Returns:
            Tuple of (encoded_text, metadata)
        """
        metadata = {
            'source_encoding': 'baraha',
            'markers_found': [],
            'numbers_preserved': []
        }
        
        # Process in specific order to avoid conflicts
        # 1. First handle multi-character patterns
        for baraha_pattern, slp1_marker in sorted(self.baraha_to_slp1_ext.items(), 
                                                  key=lambda x: len(x[0]), reverse=True):
            if baraha_pattern in text:
                count = text.count(baraha_pattern)
                metadata['markers_found'].append({
                    'pattern': baraha_pattern,
                    'marker': slp1_marker,
                    'count': count
                })
                text = text.replace(baraha_pattern, slp1_marker)
        
        # 2. Preserve numbers with context markers
        matches = list(self.number_pattern.finditer(text))
        for match in reversed(matches):  # Process in reverse to maintain positions
            num = match.group(1)
            start, end = match.span()
            metadata['numbers_preserved'].append({
                'value': num,
                'position': start
            })
            # Numbers are preserved as-is in SLP1
        
        return text, metadata

    def decode_slp1_ext_to_baraha(self, text: str, metadata: Dict = None) -> str:
        """
        Decode SLP1-Extended format back to Baraha.
        """
        # Restore all extended markers
        for slp1_marker, baraha_pattern in self.slp1_ext_to_baraha.items():
            text = text.replace(slp1_marker, baraha_pattern)
        
        return text

    def strip_extensions(self, text: str) -> str:
        """
        Remove all extension markers to get pure SLP1.
        """
        return self.ext_pattern.sub('', text)

    def validate_extended_slp1(self, text: str) -> Dict:
        """
        Validate SLP1-Extended text format.
        """
        result = {
            'is_valid': True,
            'markers': [],
            'issues': []
        }
        
        # Find all markers
        markers = self.ext_pattern.findall(text)
        result['markers'] = markers
        
        # Check for unbalanced braces
        open_braces = text.count('{')
        close_braces = text.count('}')
        if open_braces != close_braces:
            result['is_valid'] = False
            result['issues'].append(f"Unbalanced braces: {open_braces} open, {close_braces} close")
        
        # Check for unknown markers
        known_markers = set(self.baraha_to_slp1_ext.values())
        for marker in markers:
            if marker not in known_markers:
                result['issues'].append(f"Unknown marker: {marker}")
        
        return result

    def convert_to_display_format(self, text: str, target_format: str = 'unicode') -> str:
        """
        Convert SLP1-Extended to display format with proper accent marks.
        """
        if target_format == 'unicode':
            # Map to Unicode combining marks
            unicode_map = {
                '{U}': '\u0951',    # Vedic udatta
                '{A}': '\u0952',    # Vedic anudatta
                '{S}': '\u0951',    # Svarita (same as udatta in many fonts)
                '{DS}': '\u0951\u0951',  # Double udatta for dheerga
                '{AV}': '\u093D',   # Avagraha
                '{GM}': 'ṅ',        # IAST guttural nasal
                '{GG}': 'ṅ',        
                '{NN}': 'ñ',        # IAST palatal nasal
                '{NM}': 'ṁ',        # IAST anusvara
                '{NJ}': 'ñ',
                '{NG}': 'ṅ',
                '{CS}': '·',        # Middle dot for compound separator
                '{1BAR}': '|',
                '{2BAR}': '||',
                '{3BAR}': '|||'
            }
            
            for marker, unicode_char in unicode_map.items():
                text = text.replace(marker, unicode_char)
        
        return text

    def create_round_trip_safe_encoding(self, text: str, source_encoding: str) -> Dict:
        """
        Create a round-trip safe encoding with full metadata.
        """
        if source_encoding == 'baraha':
            encoded, metadata = self.encode_baraha_to_slp1_ext(text)
            
            # Validate
            validation = self.validate_extended_slp1(encoded)
            
            # Test round-trip
            decoded = self.decode_slp1_ext_to_baraha(encoded, metadata)
            is_lossless = (text == decoded)
            
            return {
                'original': text,
                'encoded': encoded,
                'metadata': metadata,
                'validation': validation,
                'is_lossless': is_lossless,
                'decoded': decoded
            }
        else:
            # For non-Baraha sources, return as-is
            return {
                'original': text,
                'encoded': text,
                'metadata': {'source_encoding': source_encoding},
                'validation': {'is_valid': True},
                'is_lossless': True,
                'decoded': text
            }


# Example usage and tests
if __name__ == "__main__":
    slp1_ext = SLP1Extended()
    
    # Test cases
    test_texts = [
        "BaqdraM karNE#BiH SRuNuqyAma# dEvAH",
        "aqGaSa(gm)#saq | dRu(gm)ha#sva",
        "tasyaiqShA Bava#ti || 1 (10)",
        "sam~MvathsarE tAH prati#tiShThaqnti | vaqqrq.ShABya# ityaqrthaH || 11 (16."
    ]
    
    print("SLP1-Extended Encoding Tests")
    print("=" * 60)
    
    for text in test_texts:
        print(f"\nOriginal: {text}")
        
        result = slp1_ext.create_round_trip_safe_encoding(text, 'baraha')
        
        print(f"Encoded:  {result['encoded']}")
        print(f"Lossless: {'✓' if result['is_lossless'] else '✗'}")
        
        if result['metadata']['markers_found']:
            print(f"Markers:  {[m['marker'] for m in result['metadata']['markers_found']]}")
        
        if not result['is_lossless']:
            print(f"Decoded:  {result['decoded']}")
            print("MISMATCH!")
        
        # Show pure SLP1
        pure_slp1 = slp1_ext.strip_extensions(result['encoded'])
        print(f"Pure SLP1: {pure_slp1}")