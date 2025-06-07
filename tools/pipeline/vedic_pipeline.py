"""
Udapaana Vedic Text Processing Pipeline
End-to-end pipeline for processing raw Vedic texts into SQLite database.
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional
import json
import sqlite3
import logging
from datetime import datetime

# Add project paths
sys.path.append(str(Path(__file__).parent))
sys.path.append('/Users/skmnktl/Projects/ambuda/vidyut/bindings-python')

from stages.stage_01_source_extraction import SourceExtractor
from stages.stage_02_text_normalization import TextNormalizer
from stages.stage_03_encoding_conversion import EncodingConverter

logger = logging.getLogger(__name__)

class VedicPipeline:
    """Complete pipeline for processing Vedic texts."""
    
    def __init__(self, 
                 database_path: str = "udapaana_corpus.sqlite",
                 base_data_path: str = "data/vedic_texts",
                 output_dir: str = "output"):
        self.database_path = database_path
        self.base_data_path = Path(base_data_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize pipeline stages
        self.extractor = SourceExtractor(database_path)
        self.normalizer = TextNormalizer()
        self.converter = EncodingConverter()
        
        # Database connection
        self.db_conn = None
        
        # Pipeline statistics
        self.stats = {
            'files_processed': 0,
            'files_failed': 0,
            'stage_stats': {}
        }
    
    def run_complete_pipeline(self, sample_mode: bool = False, max_files_per_source: int = 5) -> Dict:
        """
        Run the complete pipeline from raw sources to database.
        
        Args:
            sample_mode: If True, process only a sample of files for testing
            max_files_per_source: Maximum files per source in sample mode
            
        Returns:
            Dict with pipeline results and statistics
        """
        logger.info("Starting Udapaana Vedic Text Processing Pipeline")
        start_time = datetime.now()
        
        try:
            # Stage 1: Source Extraction
            logger.info("=" * 60)
            logger.info("STAGE 1: SOURCE EXTRACTION")
            logger.info("=" * 60)
            
            if sample_mode:
                extracted_data = self.extractor.extract_sample_files(
                    str(self.base_data_path), max_files_per_source
                )
            else:
                extracted_data = self.extractor.extract_all_sources(str(self.base_data_path))
            
            self.stats['stage_stats']['extraction'] = self.extractor.get_extraction_stats(extracted_data)
            
            # Save Stage 1 results
            stage1_output = self.output_dir / "stage1_extraction_results.json"
            self.extractor.save_extracted_data(extracted_data, stage1_output)
            
            logger.info(f"Stage 1 complete: {len(extracted_data)} files extracted")
            
            # Stage 2: Text Normalization
            logger.info("=" * 60)
            logger.info("STAGE 2: TEXT NORMALIZATION")
            logger.info("=" * 60)
            
            normalized_data = self.normalizer.batch_normalize(extracted_data)
            
            # Save Stage 2 results
            stage2_output = self.output_dir / "stage2_normalization_results.json"
            self._save_pipeline_data(normalized_data, stage2_output, include_full_text=False)
            
            logger.info(f"Stage 2 complete: {len(normalized_data)} files normalized")
            
            # Stage 3: Encoding Conversion
            logger.info("=" * 60)
            logger.info("STAGE 3: ENCODING CONVERSION")
            logger.info("=" * 60)
            
            converted_data = self.converter.batch_convert(normalized_data)
            
            self.stats['stage_stats']['conversion'] = self.converter.get_conversion_stats(converted_data)
            
            # Save Stage 3 results
            stage3_output = self.output_dir / "stage3_conversion_results.json"
            self._save_pipeline_data(converted_data, stage3_output, include_full_text=False)
            
            logger.info(f"Stage 3 complete: {len(converted_data)} files converted")
            
            # Stage 4 & 5: Database Loading (to be implemented)
            logger.info("=" * 60)
            logger.info("STAGES 4-5: DATABASE LOADING (Placeholder)")
            logger.info("=" * 60)
            
            # For now, just save the final processed data
            final_output = self.output_dir / "final_processed_data.json"
            self._save_pipeline_data(converted_data, final_output, include_full_text=True)
            
            # Calculate final statistics
            end_time = datetime.now()
            self.stats.update({
                'files_processed': len(converted_data),
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': (end_time - start_time).total_seconds(),
                'sample_mode': sample_mode
            })
            
            # Save pipeline statistics
            stats_output = self.output_dir / "pipeline_statistics.json"
            with open(stats_output, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
            
            logger.info("=" * 60)
            logger.info("PIPELINE COMPLETE")
            logger.info("=" * 60)
            logger.info(f"Total files processed: {self.stats['files_processed']}")
            logger.info(f"Total duration: {self.stats['duration_seconds']:.1f} seconds")
            logger.info(f"Results saved to: {self.output_dir}")
            
            return {
                'success': True,
                'processed_data': converted_data,
                'statistics': self.stats,
                'output_files': {
                    'stage1': str(stage1_output),
                    'stage2': str(stage2_output),
                    'stage3': str(stage3_output),
                    'final': str(final_output),
                    'stats': str(stats_output)
                }
            }
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'error': str(e),
                'statistics': self.stats
            }
    
    def process_single_file(self, file_path: str, source_type: str) -> Dict:
        """Process a single file through the complete pipeline."""
        logger.info(f"Processing single file: {file_path}")
        
        try:
            # Stage 1: Extract
            result = self.extractor.extract_file(file_path, source_type)
            
            # Stage 2: Normalize
            normalization = self.normalizer.normalize_text(
                result['raw_text'], 
                result['source_name'], 
                result['metadata']
            )
            result.update(normalization)
            
            # Stage 3: Convert
            conversion = self.converter.convert_text(
                result['normalized_text'],
                result['encoding'],
                result['metadata']
            )
            result.update(conversion)
            
            logger.info(f"Single file processing complete: {Path(file_path).name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")
            raise
    
    def _save_pipeline_data(self, data: List[Dict], output_path: Path, include_full_text: bool = False) -> None:
        """Save pipeline data to JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if include_full_text:
            # Save complete data
            save_data = data
        else:
            # Save summary without full text content
            save_data = []
            for item in data:
                summary = {k: v for k, v in item.items() 
                          if k not in ['raw_text', 'normalized_text', 'original_text', 'json_data']}
                # Keep text length info
                summary.update({
                    'raw_text_length': len(item.get('raw_text', '')),
                    'normalized_text_length': len(item.get('normalized_text', '')),
                    'slp1_text_length': len(item.get('slp1_text', ''))
                })
                save_data.append(summary)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved pipeline data to {output_path}")
    
    def generate_report(self) -> str:
        """Generate a human-readable pipeline report."""
        if not self.stats:
            return "No pipeline statistics available."
        
        report = []
        report.append("UDAPAANA PIPELINE REPORT")
        report.append("=" * 50)
        report.append(f"Files processed: {self.stats['files_processed']}")
        report.append(f"Duration: {self.stats.get('duration_seconds', 0):.1f} seconds")
        report.append(f"Sample mode: {self.stats.get('sample_mode', False)}")
        report.append("")
        
        # Extraction statistics
        if 'extraction' in self.stats['stage_stats']:
            ext_stats = self.stats['stage_stats']['extraction']
            report.append("EXTRACTION STAGE:")
            report.append(f"  Total files: {ext_stats['total_files']}")
            report.append(f"  Total characters: {ext_stats['total_characters']:,}")
            report.append(f"  By source: {ext_stats['by_source']}")
            report.append(f"  By veda: {ext_stats['by_veda']}")
            report.append(f"  By text type: {ext_stats['by_text_type']}")
            report.append("")
        
        # Conversion statistics  
        if 'conversion' in self.stats['stage_stats']:
            conv_stats = self.stats['stage_stats']['conversion']
            report.append("CONVERSION STAGE:")
            report.append(f"  Total conversions: {conv_stats['total_conversions']}")
            report.append(f"  Successful: {conv_stats['successful_conversions']}")
            report.append(f"  Lossless: {conv_stats['lossless_conversions']}")
            if 'success_rate' in conv_stats:
                report.append(f"  Success rate: {conv_stats['success_rate']:.1%}")
                report.append(f"  Lossless rate: {conv_stats['lossless_rate']:.1%}")
            report.append(f"  By encoding: {conv_stats['by_source_encoding']}")
            report.append("")
        
        return "\n".join(report)


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run pipeline
    pipeline = VedicPipeline()
    
    # Run in sample mode for testing
    result = pipeline.run_complete_pipeline(sample_mode=True, max_files_per_source=2)
    
    if result['success']:
        print("\n" + pipeline.generate_report())
        print(f"\nOutput files saved to: {pipeline.output_dir}")
    else:
        print(f"Pipeline failed: {result['error']}")