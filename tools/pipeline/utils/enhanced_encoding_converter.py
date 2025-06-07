"""
Enhanced Encoding Converter with comprehensive metadata tracking.
"""

import sys
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging

# Add the enhanced vidyut-lipi path - THIS is our enhanced version!
enhanced_vidyut_path = '/Users/skmnktl/Projects/ambuda/vidyut/bindings-python'
if enhanced_vidyut_path not in sys.path:
    sys.path.insert(0, enhanced_vidyut_path)

try:
    import vidyut.lipi as lipi
    VIDYUT_AVAILABLE = True
    logging.info(f"✅ Using enhanced vidyut-lipi from: {enhanced_vidyut_path}")
except ImportError as e:
    VIDYUT_AVAILABLE = False
    logging.warning(f"❌ Enhanced vidyut-lipi not available: {e}")

logger = logging.getLogger(__name__)

class EncodingDetector:
    """Advanced encoding detection with feature analysis."""
    
    def __init__(self):
        self.baraha_patterns = {
            'accent_markers': ['q', '#', '$', '&'],
            'nasal_annotations': [
                r'\(gm\)', r'\(gg\)', r'\(nn\)', 
                r'~M', r'~j', r'~g'
            ],
            'section_markers': ['|||', '||', '|'],
            'compound_markers': ['^^'],
            'special_chars': ['Z', 'V']  # jihvamuliya, upadhmaniya
        }
        
        # Unicode Vedic markers in Devanagari text
        self.unicode_vedic_patterns = {
            'accent_markers': [
                '\u02C6',  # ˆ circumflex (svarita)
                '\u02DC',  # ˜ tilde (anudatta)
                '\u0952',  # ॒ anudatta accent
                '\u0951',  # ॑ udatta accent  
                '\u0954',  # ॔ acute accent
                '\u1CD0',  # ᳐ tone mark
                '\u1CD1',  # ᳑ tone mark
                '\u1CD2',  # ᳒ tone mark
            ],
            'nasal_annotations': [
                '\u0901',  # ँ candrabindu
                '\u0902',  # ं anusvara
                '\u1CE2',  # ᳢ vedic sign
                '\u1CE8',  # ᳨ vedic sign
            ],
            'section_markers': ['।', '॥'],  # Devanagari danda/double danda
        }
        
        self.devanagari_ranges = [
            (0x0900, 0x097F),  # Devanagari
            (0x1CD0, 0x1CFF),  # Vedic Extensions
            (0xA8E0, 0xA8FF),  # Devanagari Extended
        ]
    
    def detect_encoding(self, text: str) -> Dict[str, Any]:
        """Comprehensive encoding detection with confidence scoring."""
        results = {
            'detected_encoding': 'unknown',
            'confidence': 0.0,
            'features': {},
            'analysis': {}
        }
        
        if not text.strip():
            return results
        
        # Try vidyut-lipi detection first
        if VIDYUT_AVAILABLE:
            try:
                detected = lipi.detect(text)
                if detected:
                    # Convert Scheme enum to string
                    detected_str = str(detected).split('.')[-1] if hasattr(detected, 'name') else str(detected)
                    results['detected_encoding'] = detected_str
                    results['confidence'] = 0.8  # Base confidence for vidyut detection
            except Exception as e:
                logger.warning(f"Vidyut detection failed: {e}")
        
        # Enhanced Baraha detection
        baraha_score = self._score_baraha_features(text)
        if baraha_score > 0.5:
            results['detected_encoding'] = 'BarahaSouth'
            results['confidence'] = max(results['confidence'], baraha_score)
        
        # Unicode Vedic detection (Devanagari with Vedic markers)
        unicode_vedic_score = self._score_unicode_vedic_features(text)
        if unicode_vedic_score > 0.3:  # Lower threshold since these are mixed
            results['detected_encoding'] = 'DevanagariVedic'
            results['confidence'] = max(results['confidence'], unicode_vedic_score)
        
        # Devanagari detection
        deva_score = self._score_devanagari_features(text)
        if deva_score > 0.8 and results['detected_encoding'] == 'unknown':
            results['detected_encoding'] = 'Devanagari'
            results['confidence'] = max(results['confidence'], deva_score)
        
        # Feature analysis
        results['features'] = self._analyze_text_features(text)
        results['analysis'] = self._analyze_text_statistics(text)
        
        return results
    
    def _score_baraha_features(self, text: str) -> float:
        """Score text for Baraha-specific features."""
        total_score = 0.0
        max_score = 0.0
        
        # Accent markers
        accent_count = sum(text.count(marker) for marker in self.baraha_patterns['accent_markers'])
        if accent_count > 0:
            total_score += min(accent_count * 0.1, 0.3)
        max_score += 0.3
        
        # Nasal annotations
        nasal_count = 0
        for pattern in self.baraha_patterns['nasal_annotations']:
            nasal_count += len(re.findall(pattern, text))
        if nasal_count > 0:
            total_score += min(nasal_count * 0.15, 0.4)
        max_score += 0.4
        
        # Section markers
        section_count = sum(text.count(marker) for marker in self.baraha_patterns['section_markers'])
        if section_count > 0:
            total_score += min(section_count * 0.05, 0.2)
        max_score += 0.2
        
        # Compound markers
        if '^^' in text:
            total_score += 0.1
        max_score += 0.1
        
        return total_score / max_score if max_score > 0 else 0.0
    
    def _score_unicode_vedic_features(self, text: str) -> float:
        """Score text for Unicode Vedic markers in Devanagari."""
        total_score = 0.0
        max_score = 0.0
        
        # Check for Devanagari base first
        deva_base_score = self._score_devanagari_features(text)
        if deva_base_score < 0.5:  # Requires significant Devanagari content
            return 0.0
        
        # Unicode accent markers
        accent_count = sum(text.count(marker) for marker in self.unicode_vedic_patterns['accent_markers'])
        if accent_count > 0:
            total_score += min(accent_count * 0.2, 0.5)
        max_score += 0.5
        
        # Unicode nasal annotations
        nasal_count = sum(text.count(marker) for marker in self.unicode_vedic_patterns['nasal_annotations'])
        if nasal_count > 0:
            total_score += min(nasal_count * 0.15, 0.3)
        max_score += 0.3
        
        # Section markers
        section_count = sum(text.count(marker) for marker in self.unicode_vedic_patterns['section_markers'])
        if section_count > 0:
            total_score += min(section_count * 0.1, 0.2)
        max_score += 0.2
        
        # Bonus for having Devanagari base
        total_score += deva_base_score * 0.3
        max_score += 0.3
        
        return total_score / max_score if max_score > 0 else 0.0
    
    def _score_devanagari_features(self, text: str) -> float:
        """Score text for Devanagari features."""
        devanagari_chars = 0
        total_chars = 0
        
        for char in text:
            if char.isalpha() or ord(char) > 127:  # Non-ASCII chars
                total_chars += 1
                for start, end in self.devanagari_ranges:
                    if start <= ord(char) <= end:
                        devanagari_chars += 1
                        break
        
        return devanagari_chars / total_chars if total_chars > 0 else 0.0
    
    def _analyze_text_features(self, text: str) -> Dict[str, Any]:
        """Analyze text features for metadata."""
        features = {
            'has_accents': False,
            'accent_types': [],
            'has_nasal_annotations': False,
            'nasal_patterns': [],
            'has_section_markers': False,
            'section_types': [],
            'has_numbers': bool(re.search(r'\d', text)),
            'special_markers': [],
            'case_patterns': [],
            'character_set': 'ascii' if text.isascii() else 'unicode',
        }
        
        # Baraha accent analysis
        for marker in self.baraha_patterns['accent_markers']:
            if marker in text:
                features['has_accents'] = True
                features['accent_types'].append(f'baraha_{marker}')
        
        # Unicode Vedic accent analysis
        for marker in self.unicode_vedic_patterns['accent_markers']:
            if marker in text:
                features['has_accents'] = True
                features['accent_types'].append(f'unicode_{ord(marker):04x}')
        
        # Baraha nasal annotation analysis
        for pattern in self.baraha_patterns['nasal_annotations']:
            if re.search(pattern, text):
                features['has_nasal_annotations'] = True
                features['nasal_patterns'].append(f'baraha_{pattern}')
        
        # Unicode Vedic nasal analysis
        for marker in self.unicode_vedic_patterns['nasal_annotations']:
            if marker in text:
                features['has_nasal_annotations'] = True
                features['nasal_patterns'].append(f'unicode_{ord(marker):04x}')
        
        # Baraha section marker analysis
        for marker in self.baraha_patterns['section_markers']:
            if marker in text:
                features['has_section_markers'] = True
                features['section_types'].append(f'baraha_{marker}')
        
        # Unicode Vedic section marker analysis
        for marker in self.unicode_vedic_patterns['section_markers']:
            if marker in text:
                features['has_section_markers'] = True
                features['section_types'].append(f'unicode_{marker}')
        
        # Special markers
        if '^^' in text:
            features['special_markers'].append('compound_separator')
        if '&' in text:
            features['special_markers'].append('avagraha')
        
        # Case pattern analysis
        if any(c.isupper() for c in text):
            features['case_patterns'].append('has_uppercase')
        if any(c.islower() for c in text):
            features['case_patterns'].append('has_lowercase')
        if text != text.lower() and text != text.upper():
            features['case_patterns'].append('mixed_case')
        
        return features
    
    def _analyze_text_statistics(self, text: str) -> Dict[str, Any]:
        """Generate text statistics for analysis."""
        lines = text.split('\n')
        words = text.split()
        
        return {
            'total_chars': len(text),
            'total_lines': len(lines),
            'total_words': len(words),
            'avg_line_length': sum(len(line) for line in lines) / len(lines) if lines else 0,
            'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'non_ascii_chars': sum(1 for c in text if ord(c) > 127),
            'ascii_ratio': sum(1 for c in text if ord(c) <= 127) / len(text) if text else 0,
        }

class EnhancedEncodingConverter:
    """Enhanced encoding converter with comprehensive metadata tracking."""
    
    def __init__(self):
        self.detector = EncodingDetector()
        self.conversion_stats = {
            'total_conversions': 0,
            'successful_conversions': 0,
            'lossless_conversions': 0,
            'failed_conversions': 0
        }
    
    def convert_with_metadata(self, text: str, source_file_path: str, 
                            sakha_info: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Convert text with comprehensive metadata tracking.
        
        Args:
            text: Source text to convert
            source_file_path: Path to source file
            sakha_info: Dict with veda, sakha, text_type information
            
        Returns:
            Complete conversion result with metadata
        """
        conversion_start = datetime.now()
        result = {
            'text_id': self._generate_text_id(source_file_path),
            'source_file_path': source_file_path,
            'conversion_timestamp': conversion_start.isoformat(),
            'conversion_method': 'enhanced_vidyut_lipi' if VIDYUT_AVAILABLE else 'fallback',
            'conversion_version': self._get_version_info(),
        }
        
        try:
            # Step 1: Detection and analysis
            detection_result = self.detector.detect_encoding(text)
            result.update({
                'source_encoding_detected': detection_result['detected_encoding'],
                'source_encoding_confidence': detection_result['confidence'],
                'source_encoding_final': detection_result['detected_encoding'],
                'source_features': json.dumps(detection_result['features']),
                'analysis_stats': detection_result['analysis'],
            })
            
            # Step 2: Preprocessing
            preprocessing_steps = []
            processed_text = self._preprocess_text(text, detection_result, preprocessing_steps)
            result['preprocessing_applied'] = json.dumps(preprocessing_steps)
            
            # Step 3: Conversion
            conversion_result = self._convert_text(
                processed_text, 
                detection_result['detected_encoding']
            )
            
            # Step 4: Round-trip validation
            round_trip_result = self._validate_round_trip(
                text, 
                conversion_result['converted_text'],
                detection_result['detected_encoding']
            )
            
            # Step 5: Quality assessment
            quality_metrics = self._assess_quality(
                text, 
                conversion_result, 
                round_trip_result,
                detection_result['features']
            )
            
            # Compile final result
            result.update({
                'target_encoding': 'slp1_extended',
                'converted_text': conversion_result['converted_text'],
                'conversion_lossless': round_trip_result['is_lossless'],
                'round_trip_checksum_original': self._calculate_checksum(text),
                'round_trip_checksum_converted': self._calculate_checksum(
                    round_trip_result.get('round_trip_text', '')
                ),
                'quality_score': quality_metrics['overall_score'],
                'features_preserved': json.dumps(quality_metrics['preservation']),
                'original_sample': text[:500],
                'validation_errors': json.dumps(quality_metrics.get('errors', [])),
                'conversion_notes': quality_metrics.get('notes', ''),
            })
            
            # Add śākhā information if provided
            if sakha_info:
                result.update({
                    'veda': sakha_info.get('veda'),
                    'sakha': sakha_info.get('sakha'),
                    'text_type': sakha_info.get('text_type'),
                    'regional_variant': sakha_info.get('regional_variant'),
                })
            
            self.conversion_stats['successful_conversions'] += 1
            if round_trip_result['is_lossless']:
                self.conversion_stats['lossless_conversions'] += 1
                
        except Exception as e:
            logger.error(f"Conversion failed for {source_file_path}: {e}")
            result.update({
                'conversion_error': str(e),
                'conversion_lossless': False,
                'quality_score': 0.0,
                'validation_errors': json.dumps([{'type': 'conversion_error', 'message': str(e)}])
            })
            self.conversion_stats['failed_conversions'] += 1
        
        self.conversion_stats['total_conversions'] += 1
        return result
    
    def _preprocess_text(self, text: str, detection_result: Dict, 
                        preprocessing_steps: List) -> str:
        """Apply preprocessing based on detected encoding."""
        processed = text
        
        # Normalize case for Baraha annotations
        if detection_result['detected_encoding'] == 'BarahaSouth':
            if '(GM)' in processed:
                processed = processed.replace('(GM)', '(gm)')
                preprocessing_steps.append({
                    'step': 'normalize_case',
                    'description': '(GM) → (gm)'
                })
            
            if '(GG)' in processed:
                processed = processed.replace('(GG)', '(gg)')
                preprocessing_steps.append({
                    'step': 'normalize_case', 
                    'description': '(GG) → (gg)'
                })
        
        # Clean extra whitespace
        if re.search(r'\s{2,}', processed):
            processed = re.sub(r'\s+', ' ', processed)
            preprocessing_steps.append({
                'step': 'clean_whitespace',
                'description': 'Remove extra spaces'
            })
        
        return processed
    
    def _convert_text(self, text: str, source_encoding: str) -> Dict[str, Any]:
        """Perform the actual text conversion."""
        if not VIDYUT_AVAILABLE:
            # Fallback: basic conversion
            return {
                'converted_text': text,  # Identity conversion as fallback
                'conversion_method': 'identity_fallback',
                'warnings': ['vidyut-lipi not available, using identity conversion']
            }
        
        try:
            # Map our encoding names to vidyut scheme names
            scheme_map = {
                'BarahaSouth': lipi.Scheme.BarahaSouth,
                'Devanagari': lipi.Scheme.Devanagari,
                'DevanagariVedic': lipi.Scheme.Devanagari,  # Treat as Devanagari for now
                'Slp1': lipi.Scheme.Slp1,
                'Iast': lipi.Scheme.Iast,
                'HarvardKyoto': lipi.Scheme.HarvardKyoto,
            }
            
            source_scheme = scheme_map.get(source_encoding, lipi.Scheme.Devanagari)
            target_scheme = lipi.Scheme.Slp1
            
            # Perform conversion
            converted = lipi.transliterate(text, source_scheme, target_scheme)
            
            return {
                'converted_text': converted,
                'conversion_method': 'vidyut_lipi',
                'source_scheme': source_encoding,
                'target_scheme': 'Slp1'
            }
            
        except Exception as e:
            logger.error(f"Vidyut conversion failed: {e}")
            return {
                'converted_text': text,
                'conversion_method': 'error_fallback',
                'error': str(e)
            }
    
    def _validate_round_trip(self, original: str, converted: str, 
                           source_encoding: str) -> Dict[str, Any]:
        """Validate round-trip conversion."""
        if not VIDYUT_AVAILABLE:
            return {
                'is_lossless': False,
                'round_trip_text': original,
                'validation_method': 'no_validation_available'
            }
        
        try:
            # Map encoding for round-trip
            scheme_map = {
                'BarahaSouth': lipi.Scheme.BarahaSouth,
                'Devanagari': lipi.Scheme.Devanagari,
                'DevanagariVedic': lipi.Scheme.Devanagari,  # Treat as Devanagari for now
                'Slp1': lipi.Scheme.Slp1,
                'Iast': lipi.Scheme.Iast,
                'HarvardKyoto': lipi.Scheme.HarvardKyoto,
            }
            
            target_scheme = scheme_map.get(source_encoding, lipi.Scheme.Devanagari)
            source_scheme = lipi.Scheme.Slp1
            
            # Convert back
            round_trip = lipi.transliterate(converted, source_scheme, target_scheme)
            
            # Compare
            is_lossless = original == round_trip
            
            return {
                'is_lossless': is_lossless,
                'round_trip_text': round_trip,
                'original_length': len(original),
                'round_trip_length': len(round_trip),
                'validation_method': 'vidyut_round_trip'
            }
            
        except Exception as e:
            logger.error(f"Round-trip validation failed: {e}")
            return {
                'is_lossless': False,
                'round_trip_text': original,
                'validation_method': 'validation_error',
                'error': str(e)
            }
    
    def _assess_quality(self, original: str, conversion_result: Dict,
                       round_trip_result: Dict, features: Dict) -> Dict[str, Any]:
        """Assess overall conversion quality."""
        quality_score = 0.0
        preservation = {}
        errors = []
        notes = []
        
        # Base score from round-trip success
        if round_trip_result['is_lossless']:
            quality_score += 0.5
            preservation['round_trip_perfect'] = True
        else:
            preservation['round_trip_perfect'] = False
            errors.append({
                'type': 'round_trip_failure',
                'message': 'Round-trip conversion not lossless'
            })
        
        # Feature preservation assessment
        if features.get('has_accents'):
            # Check if accents are preserved (simplified check)
            converted = conversion_result['converted_text']
            if any(marker in converted for marker in ['\\', '^', "'"]):
                quality_score += 0.2
                preservation['accents_preserved'] = True
            else:
                preservation['accents_preserved'] = False
                errors.append({
                    'type': 'feature_loss',
                    'message': 'Accent markers may have been lost'
                })
        
        if features.get('has_nasal_annotations'):
            converted = conversion_result['converted_text']
            if any(pattern in converted for pattern in ['{gm}', '{gg}', '(gm)', '(gg)']):
                quality_score += 0.2
                preservation['nasal_annotations_preserved'] = True
            else:
                preservation['nasal_annotations_preserved'] = False
        
        # Length preservation (rough check)
        original_len = len(original)
        converted_len = len(conversion_result['converted_text'])
        length_ratio = converted_len / original_len if original_len > 0 else 0
        
        if 0.8 <= length_ratio <= 1.2:  # Reasonable length range
            quality_score += 0.1
        else:
            errors.append({
                'type': 'length_anomaly',
                'message': f'Significant length change: {length_ratio:.2f}x'
            })
        
        # Method bonus
        if conversion_result.get('conversion_method') == 'vidyut_lipi':
            quality_score += 0.1
        
        # Calculate preservation rate
        total_features = sum(1 for key in features.keys() if key.startswith('has_') and features[key])
        preserved_features = sum(1 for key in preservation.keys() if preservation[key])
        preservation['preservation_rate'] = preserved_features / total_features if total_features > 0 else 1.0
        
        # Final quality score (0.0 to 1.0)
        quality_score = min(quality_score, 1.0)
        
        if quality_score >= 0.9:
            notes.append("Excellent conversion quality")
        elif quality_score >= 0.7:
            notes.append("Good conversion quality")
        elif quality_score >= 0.5:
            notes.append("Acceptable conversion quality")
        else:
            notes.append("Poor conversion quality - manual review recommended")
        
        return {
            'overall_score': quality_score,
            'preservation': preservation,
            'errors': errors,
            'notes': '; '.join(notes)
        }
    
    def _generate_text_id(self, source_file_path: str) -> str:
        """Generate unique text ID from file path."""
        return hashlib.md5(source_file_path.encode()).hexdigest()[:16]
    
    def _calculate_checksum(self, text: str) -> str:
        """Calculate MD5 checksum of text."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _get_version_info(self) -> str:
        """Get version information for conversion tools."""
        if VIDYUT_AVAILABLE:
            return "enhanced_vidyut_lipi_v1.0"
        else:
            return "fallback_converter_v1.0"
    
    def get_conversion_statistics(self) -> Dict[str, Any]:
        """Get conversion statistics."""
        stats = self.conversion_stats.copy()
        if stats['total_conversions'] > 0:
            stats['success_rate'] = stats['successful_conversions'] / stats['total_conversions']
            stats['lossless_rate'] = stats['lossless_conversions'] / stats['total_conversions']
        else:
            stats['success_rate'] = 0.0
            stats['lossless_rate'] = 0.0
        
        return stats


# Example usage
if __name__ == "__main__":
    converter = EnhancedEncodingConverter()
    
    # Test with sample Baraha text
    test_text = "aqgni#mI$Le puroqhitaM yaqj~jasyaq dEvamRuqtvijam"
    sakha_info = {
        'veda': 'rigveda',
        'sakha': 'shakala', 
        'text_type': 'samhita'
    }
    
    result = converter.convert_with_metadata(
        test_text, 
        "test/sample_baraha.txt",
        sakha_info
    )
    
    print("Conversion Result:")
    print(f"Source encoding: {result['source_encoding_detected']}")
    print(f"Converted text: {result['converted_text']}")
    print(f"Lossless: {result['conversion_lossless']}")
    print(f"Quality score: {result['quality_score']}")
    print(f"Features: {result['source_features']}")
    
    print("\nStatistics:")
    print(converter.get_conversion_statistics())