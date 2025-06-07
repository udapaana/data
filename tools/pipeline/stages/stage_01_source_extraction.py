"""
Stage 1: Source Extraction
Extracts text content from various source formats with metadata preservation.
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional
import hashlib
import json
import logging
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from parsers.vedavms_parser import VedavmsParser
from parsers.vedanidhi_parser import VedanidhiParser

logger = logging.getLogger(__name__)

class SourceExtractor:
    """Stage 1: Extract text content from raw source files."""
    
    def __init__(self, database_path: str = "udapaana_corpus.sqlite"):
        self.database_path = database_path
        self.parsers = {
            'vedavms': VedavmsParser(),
            'vedanidhi': VedanidhiParser()
        }
        
    def extract_all_sources(self, base_path: str) -> List[Dict]:
        """Extract text from all available source files."""
        base_path = Path(base_path)
        extracted_data = []
        
        logger.info("Starting Stage 1: Source Extraction")
        
        # Process VedaVMS DOCX files
        logger.info("Processing VedaVMS DOCX files...")
        vedavms_files = self.parsers['vedavms'].get_file_list(str(base_path))
        for file_path in vedavms_files:
            try:
                result = self.extract_file(file_path, 'vedavms')
                extracted_data.append(result)
                logger.info(f"✓ Extracted: {Path(file_path).name}")
            except Exception as e:
                logger.error(f"✗ Failed to extract {file_path}: {e}")
        
        # Process Vedanidhi JSON files
        logger.info("Processing Vedanidhi JSON files...")
        vedanidhi_files = self.parsers['vedanidhi'].get_file_list(str(base_path))
        for file_path in vedanidhi_files:
            try:
                result = self.extract_file(file_path, 'vedanidhi')
                extracted_data.append(result)
                logger.info(f"✓ Extracted: {Path(file_path).name}")
            except Exception as e:
                logger.error(f"✗ Failed to extract {file_path}: {e}")
        
        logger.info(f"Stage 1 complete: Extracted {len(extracted_data)} files")
        return extracted_data
    
    def extract_file(self, file_path: str, source_type: str) -> Dict:
        """Extract content from a single file."""
        if source_type not in self.parsers:
            raise ValueError(f"Unknown source type: {source_type}")
        
        parser = self.parsers[source_type]
        
        # Validate file
        if not parser.validate_file(file_path):
            raise ValueError(f"File validation failed: {file_path}")
        
        # Parse the file
        result = parser.parse_file(file_path)
        
        # Add Stage 1 metadata
        result.update({
            'stage': 'source_extraction',
            'stage_timestamp': datetime.now().isoformat(),
            'input_checksum': self._calculate_file_checksum(file_path),
            'output_checksum': self._calculate_text_checksum(result['raw_text']),
            'processing_notes': []
        })
        
        # Validate extraction
        self._validate_extraction(result)
        
        return result
    
    def extract_sample_files(self, base_path: str, max_files_per_source: int = 3) -> List[Dict]:
        """Extract a sample of files for testing purposes."""
        base_path = Path(base_path)
        extracted_data = []
        
        logger.info(f"Extracting sample files (max {max_files_per_source} per source)")
        
        # Sample VedaVMS files
        vedavms_files = self.parsers['vedavms'].get_file_list(str(base_path))
        for file_path in vedavms_files[:max_files_per_source]:
            try:
                result = self.extract_file(file_path, 'vedavms')
                extracted_data.append(result)
                logger.info(f"✓ Sample extracted: {Path(file_path).name}")
            except Exception as e:
                logger.error(f"✗ Failed to extract {file_path}: {e}")
        
        # Sample Vedanidhi files  
        vedanidhi_files = self.parsers['vedanidhi'].get_file_list(str(base_path))
        for file_path in vedanidhi_files[:max_files_per_source]:
            try:
                result = self.extract_file(file_path, 'vedanidhi')
                extracted_data.append(result)
                logger.info(f"✓ Sample extracted: {Path(file_path).name}")
            except Exception as e:
                logger.error(f"✗ Failed to extract {file_path}: {e}")
        
        return extracted_data
    
    def _calculate_file_checksum(self, file_path: str) -> str:
        """Calculate MD5 checksum of source file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _calculate_text_checksum(self, text: str) -> str:
        """Calculate MD5 checksum of extracted text."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _validate_extraction(self, result: Dict) -> None:
        """Validate the extraction result."""
        errors = []
        warnings = []
        
        # Check required fields
        required_fields = ['source_file', 'source_name', 'encoding', 'raw_text', 'metadata']
        for field in required_fields:
            if field not in result:
                errors.append(f"Missing required field: {field}")
        
        # Check text content
        if result.get('raw_text'):
            text_length = len(result['raw_text'])
            if text_length == 0:
                errors.append("No text content extracted")
            elif text_length < 100:
                warnings.append(f"Very short text content: {text_length} characters")
        
        # Check metadata
        metadata = result.get('metadata', {})
        if not metadata.get('veda'):
            warnings.append("Veda not identified in metadata")
        if not metadata.get('text_type'):
            warnings.append("Text type not identified in metadata")
        
        # Record validation results
        result['validation_errors'] = errors
        result['validation_warnings'] = warnings
        
        if errors:
            logger.error(f"Validation errors in {result.get('source_file', 'unknown')}: {errors}")
            raise ValueError(f"Extraction validation failed: {errors}")
        
        if warnings:
            logger.warning(f"Validation warnings in {result.get('source_file', 'unknown')}: {warnings}")
            result['processing_notes'].extend(warnings)
    
    def save_extracted_data(self, extracted_data: List[Dict], output_path: str) -> None:
        """Save extracted data to JSON file for inspection."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create summary data (without full content for readability)
        summary_data = []
        for item in extracted_data:
            summary = {
                'source_file': item['source_file'],
                'source_name': item['source_name'],
                'encoding': item['encoding'],
                'text_length': len(item['raw_text']),
                'metadata': item['metadata'],
                'input_checksum': item['input_checksum'],
                'output_checksum': item['output_checksum'],
                'validation_errors': item.get('validation_errors', []),
                'validation_warnings': item.get('validation_warnings', []),
                'stage_timestamp': item['stage_timestamp']
            }
            summary_data.append(summary)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved extraction summary to {output_path}")
    
    def get_extraction_stats(self, extracted_data: List[Dict]) -> Dict:
        """Generate statistics about the extracted data."""
        stats = {
            'total_files': len(extracted_data),
            'by_source': {},
            'by_veda': {},
            'by_text_type': {},
            'total_characters': 0,
            'errors': 0,
            'warnings': 0
        }
        
        for item in extracted_data:
            source = item['source_name']
            veda = item['metadata'].get('veda', 'unknown')
            text_type = item['metadata'].get('text_type', 'unknown')
            
            # Count by source
            stats['by_source'][source] = stats['by_source'].get(source, 0) + 1
            
            # Count by veda
            stats['by_veda'][veda] = stats['by_veda'].get(veda, 0) + 1
            
            # Count by text type
            stats['by_text_type'][text_type] = stats['by_text_type'].get(text_type, 0) + 1
            
            # Total characters
            stats['total_characters'] += len(item['raw_text'])
            
            # Count errors and warnings
            stats['errors'] += len(item.get('validation_errors', []))
            stats['warnings'] += len(item.get('validation_warnings', []))
        
        return stats


if __name__ == "__main__":
    # Test the source extractor
    import logging
    logging.basicConfig(level=logging.INFO)
    
    extractor = SourceExtractor()
    
    # Extract sample files
    base_path = "/Users/skmnktl/Projects/udapaana/data/vedic_texts"
    extracted_data = extractor.extract_sample_files(base_path, max_files_per_source=2)
    
    # Generate statistics
    stats = extractor.get_extraction_stats(extracted_data)
    print("\nExtraction Statistics:")
    print(f"Total files: {stats['total_files']}")
    print(f"Total characters: {stats['total_characters']:,}")
    print(f"By source: {stats['by_source']}")
    print(f"By veda: {stats['by_veda']}")
    print(f"By text type: {stats['by_text_type']}")
    print(f"Errors: {stats['errors']}, Warnings: {stats['warnings']}")
    
    # Save summary
    extractor.save_extracted_data(extracted_data, "output/stage1_sample_results.json")