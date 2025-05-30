#!/usr/bin/env python3

import json
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
from datetime import datetime

from transformation_logger import TransformationLogger
from uvts_converter import UVTSConverter, UVTSAccent, AccentType, UVTSConversion

@dataclass
class StandardizedText:
    """Stage 3 output: Text with UVTS standardized accent notation"""
    source_id: str
    text_type: str  # samhita, brahmana, aranyaka
    sakha: str
    hierarchy: Dict[str, any]
    
    uvts_text: str  # Text in Unified Vedic Transliteration Scheme format
    original_normalized_text: str
    
    # Accent standardization metrics
    accents_converted: int
    uvts_udatta_count: int
    uvts_anudatta_count: int
    uvts_svarita_count: int
    unicode_accents_preserved: int
    
    # Detailed accent info
    accent_positions: List[Dict[str, any]]  # Serializable version of UVTSAccent
    accent_pattern_analysis: Dict[str, any]
    
    # UVTS specific metadata
    regional_variant: Optional[str]
    manuscript_tradition: Optional[str]
    patha_type: str
    
    # Quality metrics
    text_length: int
    accent_density: float  # accents per 100 characters
    conversion_confidence: float
    validation_errors: List[str]
    
    # Metadata
    processing_timestamp: str
    stage: str = "03_accent_standardization"
    quality_score: float = 0.0

class AccentStandardizer:
    """Stage 3: Accent standardization using UVTS"""
    
    def __init__(self, input_dir: Path, output_dir: Path, logger: TransformationLogger):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.logger = logger
        self.uvts_converter = UVTSConverter()
        
        # Vedic accent patterns for validation
        self.vedic_patterns = {
            'udatta_sequences': [
                r'[a-zA-Z]\\+',  # UVTS udātta
            ],
            'anudatta_sequences': [
                r'[a-zA-Z]/+',  # UVTS anudātta
            ],
            'svarita_patterns': [
                r'[a-zA-Z]=',  # UVTS svarita
                r'\\[a-zA-Z]/',  # Implied svarita
            ]
        }
        
        # Śākhā-specific accent rules for quality assessment
        self.sakha_rules = {
            'taittiriya': {
                'expected_accent_density': 5.0,  # High accent marking
                'common_patterns': [
                    r'agni\\m',  # Common Agni invocation in UVTS
                    r'indr\\',   # Indra
                    r'som\\',    # Soma
                ],
            },
            'sakala': {
                'expected_accent_density': 5.0,
                'common_patterns': [
                    r'agni\\m',
                    r'mI\\Lhuz\\',
                ],
            },
            'madhyandina': {
                'expected_accent_density': 3.0,
            },
            'kauthuma': {
                'expected_accent_density': 7.0,  # Sāmaveda has more musical notation
            }
        }
    
    def analyze_uvts_patterns(self, uvts_text: str, sakha: str) -> Dict[str, any]:
        """Analyze accent patterns in UVTS text"""
        analysis = {
            'total_accents': 0,
            'udatta_count': 0,
            'anudatta_count': 0,
            'svarita_count': 0,
            'pattern_matches': {},
            'accent_distribution': {},
            'quality_indicators': []
        }
        
        # Count UVTS accent marks
        analysis['udatta_count'] = uvts_text.count('\\')
        analysis['anudatta_count'] = uvts_text.count('/')
        analysis['svarita_count'] = uvts_text.count('=')
        analysis['total_accents'] = (analysis['udatta_count'] + 
                                   analysis['anudatta_count'] + 
                                   analysis['svarita_count'])
        
        # Check for known Vedic patterns in UVTS format
        for pattern_type, patterns in self.vedic_patterns.items():
            matches = 0
            for pattern in patterns:
                matches += len(re.findall(pattern, uvts_text))
            analysis['pattern_matches'][pattern_type] = matches
        
        # Check śākhā-specific patterns
        if sakha in self.sakha_rules:
            sakha_patterns = self.sakha_rules[sakha].get('common_patterns', [])
            sakha_matches = 0
            for pattern in sakha_patterns:
                sakha_matches += len(re.findall(pattern, uvts_text))
            analysis['pattern_matches'][f'{sakha}_specific'] = sakha_matches
        
        # Analyze distribution
        words = re.findall(r'[a-zA-Z\\\/=]+', uvts_text)
        if words:
            accented_words = [word for word in words if any(mark in word for mark in ['\\', '/', '='])]
            analysis['accent_distribution'] = {
                'total_words': len(words),
                'accented_words': len(accented_words),
                'accent_percentage': (len(accented_words) / len(words)) * 100
            }
        
        # Quality indicators
        if analysis['total_accents'] > 0:
            analysis['quality_indicators'].append('accents_present')
        
        if analysis['udatta_count'] > 0 and analysis['anudatta_count'] > 0:
            analysis['quality_indicators'].append('balanced_accents')
        
        if analysis.get('accent_distribution', {}).get('accent_percentage', 0) > 50:
            analysis['quality_indicators'].append('high_accent_coverage')
        
        return analysis
    
    def calculate_conversion_confidence(self, original_text: str, conversion: UVTSConversion,
                                      validation_errors: List[str]) -> float:
        """Calculate confidence in the UVTS conversion"""
        confidence = 100.0
        
        # Penalize validation errors heavily
        confidence -= len(validation_errors) * 15
        
        # Check if conversion preserved accent information
        original_accent_count = sum(original_text.count(mark) for mark in ['॑', '॒', '॓'])
        converted_accent_count = len(conversion.accents)
        
        if original_accent_count > 0:
            preservation_ratio = converted_accent_count / original_accent_count
            if preservation_ratio < 0.9:
                confidence -= 20
            elif preservation_ratio < 1.0:
                confidence -= 10
        
        # Bonus for detected metadata
        if conversion.regional_variant:
            confidence += 5
        if conversion.patha_type and conversion.patha_type != 'samhita':
            confidence += 5
        
        # Check for suspicious patterns in UVTS
        if re.search(r'[\\\/=]{2,}', conversion.uvts_text):
            confidence -= 10  # Consecutive accent marks
        
        return max(0.0, min(100.0, confidence))
    
    def calculate_quality_score(self, standardized: StandardizedText) -> float:
        """Calculate quality score for UVTS standardization"""
        score = 100.0
        
        # Get expected accent density for śākhā
        expected_density = self.sakha_rules.get(
            standardized.sakha, {}
        ).get('expected_accent_density', 3.0)
        
        # Score based on accent density compared to expected
        density_ratio = standardized.accent_density / expected_density
        if density_ratio >= 0.8:
            score += 15
        elif density_ratio >= 0.5:
            score += 10
        elif density_ratio < 0.2:
            score -= 20
        
        # Penalize validation errors
        score -= len(standardized.validation_errors) * 10
        
        # Penalize low conversion confidence
        if standardized.conversion_confidence < 80:
            score -= 20
        elif standardized.conversion_confidence < 90:
            score -= 10
        
        # Bonus for proper accent distribution
        if standardized.uvts_udatta_count > 0 and standardized.uvts_anudatta_count > 0:
            score += 10
        
        # Penalize if no accents found
        if standardized.accents_converted == 0:
            score -= 30
        
        # Bonus for regional/manuscript metadata
        if standardized.regional_variant:
            score += 5
        if standardized.manuscript_tradition:
            score += 5
        
        return max(0.0, min(100.0, score))
    
    def process_stage2_file(self, stage2_file: Path) -> Optional[StandardizedText]:
        """Process a single Stage 2 output file"""
        try:
            with open(stage2_file, 'r', encoding='utf-8') as f:
                stage2_data = json.load(f)
            
            # Extract Stage 2 data
            source_id = stage2_data['source_id']
            text_type = stage2_data['text_type']
            sakha = stage2_data['sakha']
            hierarchy = stage2_data['hierarchy']
            normalized_text = stage2_data['normalized_text']
            
            # Convert to UVTS format
            conversion = self.uvts_converter.convert_to_uvts(
                normalized_text,
                sakha=sakha,
                region=hierarchy.get('region'),
                manuscript=hierarchy.get('manuscript')
            )
            
            # Validate UVTS
            is_valid, validation_errors = self.uvts_converter.validate_uvts(conversion.uvts_text)
            
            # Analyze accent patterns
            pattern_analysis = self.analyze_uvts_patterns(conversion.uvts_text, sakha)
            
            # Count UVTS accent types
            uvts_udatta_count = conversion.uvts_text.count('\\')
            uvts_anudatta_count = conversion.uvts_text.count('/')
            uvts_svarita_count = conversion.uvts_text.count('=')
            
            # Calculate metrics
            accent_density = (len(conversion.accents) / len(conversion.uvts_text)) * 100 if conversion.uvts_text else 0
            conversion_confidence = self.calculate_conversion_confidence(
                normalized_text, conversion, validation_errors
            )
            
            # Convert UVTSAccent objects to serializable dicts
            accent_positions = [
                {
                    'position': accent.position,
                    'accent_type': accent.accent_type.value,
                    'character': accent.character,
                    'uvts_marker': accent.uvts_marker,
                    'original_unicode': accent.original_unicode
                } for accent in conversion.accents
            ]
            
            # Create standardized text object
            standardized = StandardizedText(
                source_id=source_id,
                text_type=text_type,
                sakha=sakha,
                hierarchy=hierarchy,
                uvts_text=conversion.uvts_text,
                original_normalized_text=normalized_text,
                accents_converted=len(conversion.accents),
                uvts_udatta_count=uvts_udatta_count,
                uvts_anudatta_count=uvts_anudatta_count,
                uvts_svarita_count=uvts_svarita_count,
                unicode_accents_preserved=pattern_analysis['total_accents'],
                accent_positions=accent_positions,
                accent_pattern_analysis=pattern_analysis,
                regional_variant=conversion.regional_variant,
                manuscript_tradition=conversion.manuscript_tradition,
                patha_type=conversion.patha_type,
                text_length=len(conversion.uvts_text),
                accent_density=accent_density,
                conversion_confidence=conversion_confidence,
                validation_errors=validation_errors,
                processing_timestamp=datetime.now().isoformat()
            )
            
            # Calculate quality score
            standardized.quality_score = self.calculate_quality_score(standardized)
            
            # Log the processing
            self.logger.log_stage_completion(
                stage="03_accent_standardization",
                source_id=source_id,
                input_file=str(stage2_file),
                output_data={
                    "uvts_length": len(conversion.uvts_text),
                    "accents_converted": len(conversion.accents),
                    "accent_density": accent_density,
                    "conversion_confidence": conversion_confidence,
                    "quality_score": standardized.quality_score,
                    "is_valid": is_valid,
                    "patha_type": conversion.patha_type
                },
                success=True
            )
            
            return standardized
            
        except Exception as e:
            self.logger.log_stage_completion(
                stage="03_accent_standardization",
                source_id=stage2_file.stem,
                input_file=str(stage2_file),
                output_data={},
                success=False,
                error_message=str(e)
            )
            return None
    
    def process_all_files(self) -> Dict[str, List[str]]:
        """Process all Stage 2 output files"""
        stage2_files = list(self.input_dir.glob("*.json"))
        
        if not stage2_files:
            print(f"No Stage 2 files found in {self.input_dir}")
            return {"processed": [], "failed": []}
        
        processed = []
        failed = []
        
        print(f"\nProcessing {len(stage2_files)} Stage 2 files...")
        
        for stage2_file in stage2_files:
            print(f"Processing: {stage2_file.name}")
            
            standardized = self.process_stage2_file(stage2_file)
            
            if standardized:
                # Save Stage 3 output
                output_file = self.output_dir / stage2_file.name
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(asdict(standardized), f, indent=2, ensure_ascii=False)
                
                processed.append(stage2_file.name)
                print(f"  ✓ Quality score: {standardized.quality_score:.1f}")
                print(f"  ✓ Accents converted: {standardized.accents_converted}")
                print(f"  ✓ Accent density: {standardized.accent_density:.2f}/100 chars")
                print(f"  ✓ Conversion confidence: {standardized.conversion_confidence:.1f}%")
                print(f"  ✓ Pāṭha type: {standardized.patha_type}")
                
                if standardized.validation_errors:
                    print(f"  ⚠ Validation errors: {len(standardized.validation_errors)}")
                if standardized.regional_variant:
                    print(f"  ✓ Regional variant: {standardized.regional_variant}")
            else:
                failed.append(stage2_file.name)
                print(f"  ✗ Failed to process")
        
        return {"processed": processed, "failed": failed}

def main():
    """Run Stage 3: Accent Standardization (UVTS)"""
    base_dir = Path(__file__).parent.parent
    
    # Setup paths
    stage2_dir = base_dir / "transformations" / "stage_02_normalization"
    stage3_dir = base_dir / "transformations" / "stage_03_accent_standardization"
    stage3_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize logger
    logger = TransformationLogger(base_dir / "transformations" / "transformation_log.json")
    
    # Initialize standardizer
    standardizer = AccentStandardizer(stage2_dir, stage3_dir, logger)
    
    print("=" * 60)
    print("STAGE 3: ACCENT STANDARDIZATION (UVTS)")
    print("=" * 60)
    
    # Process all files
    results = standardizer.process_all_files()
    
    print(f"\nStage 3 Complete:")
    print(f"  ✓ Processed: {len(results['processed'])} files")
    print(f"  ✗ Failed: {len(results['failed'])} files")
    
    if results['failed']:
        print(f"\nFailed files:")
        for failed_file in results['failed']:
            print(f"  - {failed_file}")

if __name__ == "__main__":
    main()