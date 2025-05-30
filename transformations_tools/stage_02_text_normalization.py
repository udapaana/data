#!/usr/bin/env python3

import json
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
from datetime import datetime

from transformation_logger import TransformationLogger

@dataclass
class NormalizedText:
    """Stage 2 output: Normalized text with quality metrics"""
    source_id: str
    text_type: str  # samhita, brahmana, aranyaka
    sakha: str
    hierarchy: Dict[str, any]
    
    normalized_text: str
    original_text: str
    
    # Normalization metrics
    characters_removed: int
    whitespace_normalized: bool
    encoding_issues_fixed: int
    baraha_marks_preserved: int
    
    # Quality metrics
    text_length: int
    accent_coverage_percent: float
    suspicious_patterns: List[str]
    
    # Metadata
    processing_timestamp: str
    stage: str = "02_normalization"
    quality_score: float = 0.0

class TextNormalizer:
    """Stage 2: Text normalization and cleaning"""
    
    def __init__(self, input_dir: Path, output_dir: Path, logger: TransformationLogger):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.logger = logger
        
        # Unicode normalization patterns
        self.unicode_fixes = {
            # Fix common encoding issues
            'â€™': "'",  # Smart quote
            'â€œ': '"',  # Smart quote
            'â€': '"',   # Smart quote
            'â€¦': '...',  # Ellipsis
            'â€"': '--',  # Em dash
            'â€"': '-',   # En dash
            
            # Normalize various apostrophes
            ''': "'",
            ''': "'",
            '"': '"',
            '"': '"',
            
            # Fix zero-width characters
            '\u200b': '',  # Zero-width space
            '\u200c': '',  # Zero-width non-joiner
            '\u200d': '',  # Zero-width joiner
            '\ufeff': '',  # BOM
        }
        
        # Baraha accent preservation patterns
        self.baraha_accents = [
            '॑',  # Udātta
            '॒',  # Anudātta
            '॓',  # Grave accent (svarita)
            '॔',  # Acute accent
            '᳚',  # Vedic tone mark
            '᳛',  # Vedic tone mark
        ]
        
        # Suspicious patterns that might indicate corruption
        self.suspicious_patterns = [
            r'[^\u0900-\u097F\u1CD0-\u1CFF\u200C\u200D\u0020-\u007F]',  # Non-Devanagari/ASCII
            r'\?\?\?',  # Question marks (encoding failure)
            r'###',     # Hash marks
            r'XXX',     # Placeholder text
            r'\[\?\]',  # Bracketed question marks
            r'<.*?>',   # HTML/XML tags
        ]
    
    def normalize_text(self, text: str) -> Tuple[str, Dict[str, any]]:
        """Normalize text while preserving Vedic accents"""
        original_length = len(text)
        normalized = text
        metrics = {
            'characters_removed': 0,
            'encoding_issues_fixed': 0,
            'baraha_marks_preserved': 0,
            'suspicious_patterns': []
        }
        
        # Count original Baraha marks
        original_baraha_count = sum(normalized.count(mark) for mark in self.baraha_accents)
        
        # Fix Unicode encoding issues
        for bad, good in self.unicode_fixes.items():
            if bad in normalized:
                normalized = normalized.replace(bad, good)
                metrics['encoding_issues_fixed'] += 1
        
        # Normalize whitespace but preserve structure
        # Replace multiple spaces with single space
        normalized = re.sub(r' {2,}', ' ', normalized)
        
        # Normalize line endings
        normalized = re.sub(r'\r\n|\r', '\n', normalized)
        
        # Remove trailing whitespace from lines
        lines = normalized.split('\n')
        normalized_lines = []
        for line in lines:
            cleaned_line = line.rstrip()
            normalized_lines.append(cleaned_line)
        normalized = '\n'.join(normalized_lines)
        
        # Remove excessive blank lines (more than 2 consecutive)
        normalized = re.sub(r'\n{3,}', '\n\n', normalized)
        
        # Count preserved Baraha marks
        preserved_baraha_count = sum(normalized.count(mark) for mark in self.baraha_accents)
        metrics['baraha_marks_preserved'] = preserved_baraha_count
        
        # Check for suspicious patterns
        for pattern in self.suspicious_patterns:
            matches = re.findall(pattern, normalized)
            if matches:
                metrics['suspicious_patterns'].append(f"{pattern}: {len(matches)} matches")
        
        # Calculate metrics
        metrics['characters_removed'] = original_length - len(normalized)
        
        return normalized, metrics
    
    def calculate_accent_coverage(self, text: str) -> float:
        """Calculate percentage of characters that have accent marks"""
        if not text:
            return 0.0
        
        # Count Devanagari characters that could have accents
        devanagari_chars = re.findall(r'[\u0900-\u097F]', text)
        if not devanagari_chars:
            return 0.0
        
        # Count accent marks
        accent_count = sum(text.count(mark) for mark in self.baraha_accents)
        
        # Rough estimate: each accent typically applies to 1-2 characters
        estimated_accented_chars = accent_count * 1.5
        
        coverage = min(100.0, (estimated_accented_chars / len(devanagari_chars)) * 100)
        return round(coverage, 2)
    
    def calculate_quality_score(self, normalized: NormalizedText) -> float:
        """Calculate quality score based on multiple factors"""
        score = 100.0
        
        # Penalize if too many characters were removed (might indicate corruption)
        if normalized.characters_removed > normalized.text_length * 0.1:
            score -= 20
        
        # Penalize encoding issues
        score -= normalized.encoding_issues_fixed * 5
        
        # Penalize suspicious patterns
        score -= len(normalized.suspicious_patterns) * 10
        
        # Bonus for good accent coverage
        if normalized.accent_coverage_percent > 50:
            score += 10
        elif normalized.accent_coverage_percent > 20:
            score += 5
        
        # Penalize very short texts (might be incomplete)
        if normalized.text_length < 100:
            score -= 15
        
        # Ensure score is between 0 and 100
        return max(0.0, min(100.0, score))
    
    def process_stage1_file(self, stage1_file: Path) -> Optional[NormalizedText]:
        """Process a single Stage 1 output file"""
        try:
            with open(stage1_file, 'r', encoding='utf-8') as f:
                stage1_data = json.load(f)
            
            # Extract Stage 1 data
            source_id = stage1_data['source_id']
            text_type = stage1_data['text_type']
            sakha = stage1_data['sakha']
            hierarchy = stage1_data['hierarchy']
            extracted_text = stage1_data['extracted_text']
            
            # Normalize the text
            normalized_text, norm_metrics = self.normalize_text(extracted_text)
            
            # Calculate quality metrics
            accent_coverage = self.calculate_accent_coverage(normalized_text)
            
            # Create normalized text object
            normalized = NormalizedText(
                source_id=source_id,
                text_type=text_type,
                sakha=sakha,
                hierarchy=hierarchy,
                normalized_text=normalized_text,
                original_text=extracted_text,
                characters_removed=norm_metrics['characters_removed'],
                whitespace_normalized=True,
                encoding_issues_fixed=norm_metrics['encoding_issues_fixed'],
                baraha_marks_preserved=norm_metrics['baraha_marks_preserved'],
                text_length=len(normalized_text),
                accent_coverage_percent=accent_coverage,
                suspicious_patterns=norm_metrics['suspicious_patterns'],
                processing_timestamp=datetime.now().isoformat()
            )
            
            # Calculate quality score
            normalized.quality_score = self.calculate_quality_score(normalized)
            
            # Log the processing
            self.logger.log_stage_completion(
                stage="02_normalization",
                source_id=source_id,
                input_file=str(stage1_file),
                output_data={
                    "normalized_length": len(normalized_text),
                    "characters_removed": norm_metrics['characters_removed'],
                    "encoding_fixes": norm_metrics['encoding_issues_fixed'],
                    "accent_coverage": accent_coverage,
                    "quality_score": normalized.quality_score
                },
                success=True
            )
            
            return normalized
            
        except Exception as e:
            self.logger.log_stage_completion(
                stage="02_normalization",
                source_id=stage1_file.stem,
                input_file=str(stage1_file),
                output_data={},
                success=False,
                error_message=str(e)
            )
            return None
    
    def process_all_files(self) -> Dict[str, List[str]]:
        """Process all Stage 1 output files"""
        stage1_files = list(self.input_dir.glob("*.json"))
        
        if not stage1_files:
            print(f"No Stage 1 files found in {self.input_dir}")
            return {"processed": [], "failed": []}
        
        processed = []
        failed = []
        
        print(f"\nProcessing {len(stage1_files)} Stage 1 files...")
        
        for stage1_file in stage1_files:
            print(f"Processing: {stage1_file.name}")
            
            normalized = self.process_stage1_file(stage1_file)
            
            if normalized:
                # Save Stage 2 output
                output_file = self.output_dir / stage1_file.name
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(asdict(normalized), f, indent=2, ensure_ascii=False)
                
                processed.append(stage1_file.name)
                print(f"  ✓ Quality score: {normalized.quality_score:.1f}")
                print(f"  ✓ Accent coverage: {normalized.accent_coverage_percent:.1f}%")
                
                if normalized.suspicious_patterns:
                    print(f"  ⚠ Suspicious patterns: {len(normalized.suspicious_patterns)}")
            else:
                failed.append(stage1_file.name)
                print(f"  ✗ Failed to process")
        
        return {"processed": processed, "failed": failed}

def main():
    """Run Stage 2: Text Normalization"""
    base_dir = Path(__file__).parent.parent
    
    # Setup paths
    stage1_dir = base_dir / "transformations" / "stage_01_extraction"
    stage2_dir = base_dir / "transformations" / "stage_02_normalization"
    stage2_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize logger
    logger = TransformationLogger(base_dir / "transformations" / "transformation_log.json")
    
    # Initialize normalizer
    normalizer = TextNormalizer(stage1_dir, stage2_dir, logger)
    
    print("=" * 60)
    print("STAGE 2: TEXT NORMALIZATION")
    print("=" * 60)
    
    # Process all files
    results = normalizer.process_all_files()
    
    print(f"\nStage 2 Complete:")
    print(f"  ✓ Processed: {len(results['processed'])} files")
    print(f"  ✗ Failed: {len(results['failed'])} files")
    
    if results['failed']:
        print(f"\nFailed files:")
        for failed_file in results['failed']:
            print(f"  - {failed_file}")

if __name__ == "__main__":
    main()