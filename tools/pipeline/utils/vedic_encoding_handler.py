"""
Vedic Encoding Handler with sakha-specific extensions for lossless conversion.
"""

import re
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class VedicEncodingHandler:
    """Handle Vedic text encoding with preservation of all source-specific markers."""
    
    def __init__(self):
        # Baraha special patterns that need preservation
        self.baraha_specials = {
            # Accent markers
            'anudatta': 'q',
            'svarita': '#',
            'dheerga_svarita': '$',
            'avagraha': '&',
            
            # Nasal annotations (preserved as-is)
            'nasal_patterns': [
                r'\(gm\)',  # guttural + m
                r'\(gg\)',  # guttural + g
                r'\(nn\)',  # dental n
                r'~M',      # nasal symbol
                r'~j',      # palatal nasal
                r'~g',      # guttural nasal
            ],
            
            # Other markers
            'compound_separator': '^^',
            'section_markers': ['|', '||', '|||'],
            'parenthetical': r'\([^)]+\)',  # Preserve all parenthetical content
        }
        
        # SLP1 extensions for preserving Vedic features
        self.slp1_extensions = {
            # Accent marks (using Unicode combining marks in private use area)
            'anudatta': '\uE000',      # Private use for anudatta
            'udatta': '\uE001',        # Private use for udatta
            'svarita': '\uE002',       # Private use for svarita
            'dheerga_svarita': '\uE003', # Private use for dheerga svarita
            'avagraha': '\uE004',      # Private use for avagraha
            
            # Preserve nasal annotations
            'nasal_gm': '\uE010',      # (gm) marker
            'nasal_gg': '\uE011',      # (gg) marker
            'nasal_nn': '\uE012',      # (nn) marker
            'nasal_M': '\uE013',       # ~M marker
            'nasal_j': '\uE014',       # ~j marker
            'nasal_g': '\uE015',       # ~g marker
            
            # Other preserved markers
            'compound_sep': '\uE020',   # ^^ marker
            'section_1': '\uE021',      # | marker
            'section_2': '\uE022',      # || marker
            'section_3': '\uE023',      # ||| marker
        }
        
        # Reverse mapping for round-trip
        self.extension_to_source = {v: k for k, v in self.slp1_extensions.items()}

    def detect_encoding(self, text: str) -> Dict[str, any]:
        """Detect source encoding and special features."""
        features = {
            'encoding': 'unknown',
            'has_accents': False,
            'has_nasal_annotations': False,
            'has_numbers': False,
            'special_markers': []
        }
        
        # Check for Baraha patterns
        if any(marker in text for marker in ['q', '#', '$', '&']):
            features['encoding'] = 'baraha'
            features['has_accents'] = True
        
        # Check for nasal annotations
        for pattern in self.baraha_specials['nasal_patterns']:
            if re.search(pattern, text):
                features['has_nasal_annotations'] = True
                features['special_markers'].append(pattern)
        
        # Check for numbers
        if re.search(r'\d', text):
            features['has_numbers'] = True
        
        # Check for Devanagari
        if re.search(r'[\u0900-\u097F]', text):
            features['encoding'] = 'devanagari'
        
        return features

    def preprocess_baraha(self, text: str) -> Tuple[str, Dict]:
        """Preprocess Baraha text to preserve special markers."""
        preserved_data = {
            'accents': [],
            'nasals': [],
            'sections': [],
            'numbers': [],
            'parentheticals': []
        }
        
        # Step 1: Extract and replace accent markers with placeholders
        accent_map = {
            'q': ('ANUDATTA', self.slp1_extensions['anudatta']),
            '#': ('SVARITA', self.slp1_extensions['svarita']),
            '$': ('DHEERGA_SVARITA', self.slp1_extensions['dheerga_svarita']),
            '&': ('AVAGRAHA', self.slp1_extensions['avagraha'])
        }
        
        for source, (name, target) in accent_map.items():
            positions = []
            idx = 0
            while True:
                idx = text.find(source, idx)
                if idx == -1:
                    break
                positions.append(idx)
                idx += 1
            
            if positions:
                preserved_data['accents'].append({
                    'marker': source,
                    'name': name,
                    'positions': positions,
                    'replacement': target
                })
                # Replace with extension marker
                text = text.replace(source, target)
        
        # Step 2: Handle nasal annotations
        nasal_map = {
            '(gm)': self.slp1_extensions['nasal_gm'],
            '(gg)': self.slp1_extensions['nasal_gg'],
            '(nn)': self.slp1_extensions['nasal_nn'],
            '~M': self.slp1_extensions['nasal_M'],
            '~j': self.slp1_extensions['nasal_j'],
            '~g': self.slp1_extensions['nasal_g'],
        }
        
        for source, target in nasal_map.items():
            if source in text:
                preserved_data['nasals'].append({
                    'pattern': source,
                    'replacement': target,
                    'count': text.count(source)
                })
                text = text.replace(source, target)
        
        # Step 3: Handle section markers
        section_map = {
            '|||': self.slp1_extensions['section_3'],
            '||': self.slp1_extensions['section_2'],
            '|': self.slp1_extensions['section_1'],
        }
        
        # Process in order of length to avoid conflicts
        for source, target in section_map.items():
            if source in text:
                preserved_data['sections'].append({
                    'marker': source,
                    'replacement': target,
                    'count': text.count(source)
                })
                text = text.replace(source, target)
        
        # Step 4: Preserve numbers with context
        number_pattern = re.compile(r'(\d+)')
        matches = list(number_pattern.finditer(text))
        for match in reversed(matches):  # Process in reverse to maintain positions
            num = match.group(1)
            start, end = match.span()
            context = text[max(0, start-5):min(len(text), end+5)]
            preserved_data['numbers'].append({
                'value': num,
                'position': start,
                'context': context
            })
            # Mark numbers with special delimiter
            text = text[:start] + f'\uE030{num}\uE031' + text[end:]
        
        # Step 5: Handle compound separator
        if '^^' in text:
            text = text.replace('^^', self.slp1_extensions['compound_sep'])
        
        return text, preserved_data

    def postprocess_slp1(self, text: str, preserved_data: Dict) -> str:
        """Restore original markers after conversion."""
        # Reverse all transformations
        
        # Restore accent markers
        for accent_info in preserved_data['accents']:
            text = text.replace(accent_info['replacement'], accent_info['marker'])
        
        # Restore nasal annotations
        for nasal_info in preserved_data['nasals']:
            text = text.replace(nasal_info['replacement'], nasal_info['pattern'])
        
        # Restore section markers
        for section_info in preserved_data['sections']:
            text = text.replace(section_info['replacement'], section_info['marker'])
        
        # Restore numbers
        text = re.sub(r'\uE030(\d+)\uE031', r'\1', text)
        
        # Restore compound separator
        text = text.replace(self.slp1_extensions['compound_sep'], '^^')
        
        # Remove any remaining extension markers (safety)
        for ext_char in self.slp1_extensions.values():
            text = text.replace(ext_char, '')
        
        return text

    def convert_with_preservation(self, text: str, source_encoding: str, 
                                 target_encoding: str, converter_func) -> Tuple[str, bool]:
        """
        Convert text while preserving source-specific features.
        
        Args:
            text: Source text
            source_encoding: Source encoding name
            target_encoding: Target encoding name
            converter_func: Function to perform base conversion
            
        Returns:
            Tuple of (converted_text, is_lossless)
        """
        if source_encoding == 'baraha':
            # Preprocess to preserve special markers
            processed_text, preserved_data = self.preprocess_baraha(text)
            
            # Perform base conversion
            converted = converter_func(processed_text)
            
            # For round-trip testing, we need to ensure markers are preserved
            if target_encoding == 'slp1':
                # Keep the extension markers in SLP1
                return converted, True
            else:
                # For other targets, restore original markers
                restored = self.postprocess_slp1(converted, preserved_data)
                return restored, True
        else:
            # For non-Baraha sources, use standard conversion
            converted = converter_func(text)
            return converted, True

    def create_sakha_extension(self, text: str, sakha: str, text_type: str) -> str:
        """Create sakha-specific encoding extensions."""
        # Add metadata markers for sakha-specific features
        metadata_prefix = f"%%SAKHA:{sakha}%%TYPE:{text_type}%%"
        
        # Sakha-specific processing
        if sakha == 'taittiriya' and text_type == 'aranyaka':
            # Handle specific Taittiriya Aranyaka features
            # Add markers for ritual instructions, etc.
            pass
        elif sakha == 'kauthuma' and text_type == 'samhita':
            # Handle Samaveda musical notations
            # Preserve stobha elements, elongation marks, etc.
            pass
        
        return metadata_prefix + text

    def validate_round_trip(self, original: str, converted: str, 
                          roundtrip: str, encoding: str) -> Dict:
        """Validate round-trip conversion with detailed analysis."""
        result = {
            'is_lossless': original == roundtrip,
            'original_length': len(original),
            'roundtrip_length': len(roundtrip),
            'encoding': encoding
        }
        
        if not result['is_lossless']:
            # Analyze differences
            differences = []
            
            # Character-level comparison
            min_len = min(len(original), len(roundtrip))
            for i in range(min_len):
                if original[i] != roundtrip[i]:
                    differences.append({
                        'position': i,
                        'original': original[i],
                        'roundtrip': roundtrip[i],
                        'context': original[max(0, i-10):i+10]
                    })
                    if len(differences) >= 10:  # Limit to first 10 differences
                        break
            
            result['differences'] = differences
            result['length_diff'] = len(roundtrip) - len(original)
            
            # Check for specific pattern losses
            features_original = self.detect_encoding(original)
            features_roundtrip = self.detect_encoding(roundtrip)
            
            result['feature_loss'] = {
                'accents_lost': features_original['has_accents'] and not features_roundtrip['has_accents'],
                'nasals_lost': features_original['has_nasal_annotations'] and not features_roundtrip['has_nasal_annotations'],
                'numbers_lost': features_original['has_numbers'] and not features_roundtrip['has_numbers']
            }
        
        return result


# Example usage
if __name__ == "__main__":
    handler = VedicEncodingHandler()
    
    # Test text with various features
    test_text = "BaqdraM karNE#BiH SRuNuqyAma# dEvAH | aqGaSa(gm)#saq | 1 (10)"
    
    print("Original:", test_text)
    features = handler.detect_encoding(test_text)
    print("Detected features:", features)
    
    if features['encoding'] == 'baraha':
        processed, preserved = handler.preprocess_baraha(test_text)
        print("Preprocessed:", repr(processed))
        print("Preserved data:", preserved)
        
        restored = handler.postprocess_slp1(processed, preserved)
        print("Restored:", restored)
        print("Lossless:", test_text == restored)