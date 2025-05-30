#!/usr/bin/env python3

import re
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from enum import Enum

class AccentType(Enum):
    UDATTA = "udatta"
    ANUDATTA = "anudatta"
    SVARITA = "svarita"
    ELONGATION_1 = "elongation_1"
    ELONGATION_2 = "elongation_2"
    ELONGATION_3 = "elongation_3"
    PAUSE_SHORT = "pause_short"
    PAUSE_LONG = "pause_long"
    GLIDE_UP = "glide_up"
    GLIDE_DOWN = "glide_down"
    STOBHA = "stobha"
    KAMPANA = "kampana"
    PLUTA = "pluta"

@dataclass
class UVTSAccent:
    """UVTS accent information"""
    position: int
    accent_type: AccentType
    character: str
    uvts_marker: str
    original_unicode: str = ""

@dataclass
class UVTSConversion:
    """Result of UVTS conversion"""
    uvts_text: str
    accents: List[UVTSAccent]
    regional_variant: Optional[str] = None
    manuscript_tradition: Optional[str] = None
    patha_type: Optional[str] = None
    conversion_notes: List[str] = None

class UVTSConverter:
    """Unified Vedic Transliteration Scheme converter"""
    
    def __init__(self):
        # Base character mappings (Unicode Devanagari to ASCII)
        self.consonant_map = {
            # Gutturals
            'क': 'k', 'ख': 'K', 'ग': 'g', 'घ': 'G', 'ङ': 'f',
            # Palatals  
            'च': 'c', 'छ': 'C', 'ज': 'j', 'झ': 'J', 'ञ': 'F',
            # Retroflexes
            'ट': 'w', 'ठ': 'W', 'ड': 'x', 'ढ': 'X', 'ण': 'N',
            # Dentals
            'त': 't', 'थ': 'T', 'द': 'd', 'ध': 'D', 'न': 'n',
            # Labials
            'प': 'p', 'फ': 'P', 'ब': 'b', 'भ': 'B', 'म': 'm',
            # Semivowels
            'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v',
            # Sibilants
            'श': 'S', 'ष': 'z', 'स': 's', 'ह': 'h',
            # Vedic/Regional variants
            'ळ': 'L',  # Vedic ळ (retroflex l)
            'ऴ': 'Z',  # Tamil/Malayalam ऴ
            # Conjunct consonants
            'क्ष': 'kz', 'त्र': 'tr', 'ज्ञ': 'jF'
        }
        
        self.vowel_map = {
            # Independent vowels
            'अ': 'a', 'आ': 'A', 'इ': 'i', 'ई': 'I', 'उ': 'u', 'ऊ': 'U',
            'ऋ': 'R', 'ॠ': 'q', 'ऌ': 'L', 'ॡ': 'Q',
            'ए': 'e', 'ऐ': 'E', 'ओ': 'o', 'औ': 'O',
            # Dependent vowels (mātrās)
            'ा': 'A', 'ि': 'i', 'ी': 'I', 'ु': 'u', 'ू': 'U',
            'ृ': 'R', 'ॄ': 'q', 'ॢ': 'L', 'ॣ': 'Q',
            'े': 'e', 'ै': 'E', 'ो': 'o', 'ौ': 'O',
            # Special
            'ं': 'M', 'ः': 'H', '्': ''  # Virama removes inherent 'a'
        }
        
        # Vedic accent mappings (Unicode to UVTS)
        self.accent_map = {
            '॑': ('\\', AccentType.UDATTA),      # Udātta
            '॒': ('/', AccentType.ANUDATTA),     # Anudātta  
            '॓': ('=', AccentType.SVARITA),      # Svarita
            '॔': ('`', AccentType.GLIDE_DOWN),   # Grave accent
            '᳚': ('~', AccentType.GLIDE_UP),     # Vedic tone mark
            '᳛': ('|', AccentType.KAMPANA),      # Vedic tone mark
        }
        
        # Special characters
        self.special_chars = {
            '।': '|',    # Daṇḍa
            '॥': '||',   # Double daṇḍa  
            'ॐ': 'OM',   # Om
            '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
            '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
        }
        
        # Regional variant patterns
        self.regional_patterns = {
            r'\(A1?\)': '[andhra]',
            r'\(A2\)': '[andhra]',
            r'\(D\)': '[dravida]',
            r'\(M\)': '[maharastra]',
            r'\(G\)': '[gujarat]',
            r'\(K\)': '[kashmir]',
            r'\(Ke\)': '[kerala]',
            r'\(Ka\)': '[karnataka]',
            r'\(B\)': '[bengal]'
        }
    
    def extract_regional_variants(self, text: str) -> Tuple[str, List[str]]:
        """Extract regional variant markers from text"""
        variants = []
        cleaned_text = text
        
        for pattern, variant in self.regional_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                variants.extend([variant] * len(matches))
                cleaned_text = re.sub(pattern, '', cleaned_text)
        
        return cleaned_text, variants
    
    def transliterate_character(self, char: str) -> str:
        """Transliterate a single character to UVTS"""
        # Check consonants first
        if char in self.consonant_map:
            return self.consonant_map[char]
        
        # Check vowels
        if char in self.vowel_map:
            return self.vowel_map[char]
        
        # Check special characters
        if char in self.special_chars:
            return self.special_chars[char]
        
        # Check if it's an accent mark
        if char in self.accent_map:
            return self.accent_map[char][0]
        
        # If ASCII already, keep as-is
        if ord(char) >= 32 and ord(char) <= 126:
            return char
        
        # Unknown character - mark for review
        return f'[?{char}?]'
    
    def process_conjunct_consonants(self, text: str) -> str:
        """Handle conjunct consonants properly"""
        # Common conjunct patterns
        conjuncts = {
            'क्ष': 'kz',
            'त्र': 'tr', 
            'ज्ञ': 'jF',
            'श्र': 'Sr',
            'द्व': 'dv',
            'द्य': 'dy',
            'त्व': 'tv',
            'स्व': 'sv',
            'स्य': 'sy',
            'न्य': 'ny',
            'र्य': 'ry',
            'ल्य': 'ly'
        }
        
        result = text
        for devanagari, uvts in conjuncts.items():
            result = result.replace(devanagari, uvts)
        
        return result
    
    def extract_accents(self, text: str) -> Tuple[str, List[UVTSAccent]]:
        """Extract accent information and convert to UVTS markers"""
        accents = []
        result = ""
        position = 0
        
        i = 0
        while i < len(text):
            char = text[i]
            
            # Check if this is an accent mark
            if char in self.accent_map:
                uvts_marker, accent_type = self.accent_map[char]
                
                # Find the character this accent applies to
                target_char = result[-1] if result else ''
                
                accent = UVTSAccent(
                    position=position,
                    accent_type=accent_type,
                    character=target_char,
                    uvts_marker=uvts_marker,
                    original_unicode=char
                )
                accents.append(accent)
                
                # Add accent marker after the character
                result += uvts_marker
                position += len(uvts_marker)
            else:
                # Regular character - transliterate it
                transliterated = self.transliterate_character(char)
                result += transliterated
                position += len(transliterated)
            
            i += 1
        
        return result, accents
    
    def detect_patha_type(self, text: str) -> Optional[str]:
        """Detect pāṭha type from text patterns"""
        # Look for pada markers
        if '•' in text or re.search(r'\s+[a-zA-Z]+-[a-zA-Z]+\s+', text):
            return 'pada'
        
        # Look for krama patterns (repeated words)
        words = re.findall(r'[a-zA-Z\\\/=]+', text)
        word_counts = {}
        for word in words:
            clean_word = re.sub(r'[\\\/=]', '', word)
            word_counts[clean_word] = word_counts.get(clean_word, 0) + 1
        
        # If many words repeat, likely krama
        repeated_words = sum(1 for count in word_counts.values() if count > 1)
        if repeated_words > len(words) * 0.3:
            return 'krama'
        
        # Default to samhita
        return 'samhita'
    
    def convert_to_uvts(self, text: str, sakha: str = None, 
                       region: str = None, manuscript: str = None) -> UVTSConversion:
        """Convert Unicode Devanagari text with accents to UVTS format"""
        conversion_notes = []
        
        # Extract regional variants
        cleaned_text, detected_variants = self.extract_regional_variants(text)
        if detected_variants:
            conversion_notes.append(f"Detected regional variants: {detected_variants}")
        
        # Handle conjunct consonants first
        processed_text = self.process_conjunct_consonants(cleaned_text)
        
        # Extract accents and convert to UVTS
        uvts_text, accents = self.extract_accents(processed_text)
        
        # Detect pāṭha type
        patha_type = self.detect_patha_type(uvts_text)
        
        # Clean up extra spaces
        uvts_text = re.sub(r'\s+', ' ', uvts_text).strip()
        
        # Use provided region or detected variants
        final_region = region
        if not final_region and detected_variants:
            final_region = detected_variants[0].strip('[]')
        
        return UVTSConversion(
            uvts_text=uvts_text,
            accents=accents,
            regional_variant=final_region,
            manuscript_tradition=manuscript,
            patha_type=patha_type,
            conversion_notes=conversion_notes or []
        )
    
    def generate_uvts_header(self, sakha: str, region: str = None, 
                            manuscript: str = None, patha: str = None,
                            accent_coverage: str = "full") -> str:
        """Generate UVTS file header"""
        header = "#UVTS-1.0\n"
        header += f"#SAKHA: {sakha}\n"
        
        if region:
            header += f"#REGION: {region}\n"
        if manuscript:
            header += f"#SOURCE: {manuscript}\n"
        if patha:
            header += f"#PATHA: {patha}\n"
            
        header += f"#ACCENT: {accent_coverage}\n"
        header += "\n"
        
        return header
    
    def validate_uvts(self, uvts_text: str) -> Tuple[bool, List[str]]:
        """Validate UVTS text for correctness"""
        errors = []
        
        # Check for unknown characters
        unknown_chars = re.findall(r'\[?\?.*?\?\]?', uvts_text)
        if unknown_chars:
            errors.append(f"Unknown characters found: {unknown_chars}")
        
        # Check for malformed accent patterns
        malformed_accents = re.findall(r'[\\\/=]{2,}', uvts_text)
        if malformed_accents:
            errors.append(f"Malformed accent sequences: {malformed_accents}")
        
        # Check for orphaned accent marks (accents not following characters)
        if re.search(r'^[\\\/=]', uvts_text) or re.search(r'\s[\\\/=]', uvts_text):
            errors.append("Orphaned accent marks found")
        
        # Check ASCII range
        non_ascii = [char for char in uvts_text if ord(char) > 126]
        if non_ascii:
            errors.append(f"Non-ASCII characters found: {set(non_ascii)}")
        
        return len(errors) == 0, errors

# Example usage and testing
def test_uvts_converter():
    """Test the UVTS converter with sample texts"""
    converter = UVTSConverter()
    
    # Test cases
    test_texts = [
        # Basic Rigveda with accents
        "अग्नि॑म् ई॒ळे पु॒रोहि॑तं य॒ज्ञस्य॑ दे॒वम् ऋ॒त्विज॑म्",
        
        # Taittiriya with regional variants  
        "इषे॒ त्वोर्जे॒ त्वा॒ वायु॑र्व॒ आयु॑ः पवमान॒स् सुवी॑र्यम् (A1)",
        
        # Complex text with multiple accents
        "ओ॒म् भू॒र्भुव॒स्स्व॒रि॑ति ता॒नि सप्त॑ छ॒न्दाम्सि॑"
    ]
    
    print("Testing UVTS Converter")
    print("=" * 50)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}: {text}")
        
        result = converter.convert_to_uvts(text, sakha="test")
        
        print(f"UVTS: {result.uvts_text}")
        print(f"Accents: {len(result.accents)}")
        print(f"Patha: {result.patha_type}")
        if result.regional_variant:
            print(f"Region: {result.regional_variant}")
        
        # Validate
        is_valid, errors = converter.validate_uvts(result.uvts_text)
        print(f"Valid: {is_valid}")
        if errors:
            print(f"Errors: {errors}")

if __name__ == "__main__":
    test_uvts_converter()