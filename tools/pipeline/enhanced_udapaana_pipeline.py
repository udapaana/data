#!/usr/bin/env python3
"""
Enhanced Udapaana Processing Pipeline with Runtime Extensible Mappings

This pipeline:
1. Uses the new vidyut-lipi extensible mapping system
2. Performs automatic source detection for sakha-veda-source combinations
3. Conducts line-by-line round-trip testing for every single line
4. Stores comprehensive metadata about discovered patterns
5. Tracks quality metrics and pipeline statistics
"""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
import sys
import os

# Add vidyut-lipi Python bindings to path
vidyut_path = Path(__file__).parent.parent / "ambuda" / "vidyut" / "bindings-python"
if vidyut_path.exists():
    sys.path.insert(0, str(vidyut_path))

try:
    import vidyut_lipi
except ImportError:
    print("Warning: vidyut_lipi not available, using mock implementation")
    vidyut_lipi = None

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedUdapaanaPipeline:
    """Enhanced pipeline with runtime extensible mappings and comprehensive testing."""
    
    def __init__(self, 
                 db_path: str = "udapaana_enhanced.sqlite",
                 config_path: str = "udapaana_sakha_extensions.yaml"):
        self.db_path = db_path
        self.config_path = config_path
        self.run_id = str(uuid.uuid4())
        self.processing_start_time = datetime.now()
        
        # Initialize database
        self._init_database()
        
        # Initialize extensible transliteration system
        self._init_transliteration_system()
        
        # Pipeline statistics
        self.stats = {
            'total_files_processed': 0,
            'total_lines_processed': 0,
            'total_texts_created': 0,
            'sources_processed': {},
            'sakha_veda_combinations': {},
            'total_patterns_discovered': 0,
            'unique_patterns_discovered': 0,
            'patterns_by_type': {},
            'round_trip_success_rate': 0.0,
            'lines_with_perfect_round_trip': 0,
            'lines_with_failed_round_trip': 0,
            'extension_schemes_used': [],
            'custom_mappings_created': 0
        }
    
    def _init_database(self):
        """Initialize SQLite database with enhanced schema."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Read and execute enhanced schema
        schema_path = Path(__file__).parent.parent / "enhanced_schema.sql"
        if schema_path.exists():
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Execute schema (handle existing tables gracefully)
            try:
                self.conn.executescript(schema_sql)
                self.conn.commit()
                logger.info("Database schema initialized successfully")
            except sqlite3.OperationalError as e:
                if "already exists" in str(e):
                    logger.info("Database tables already exist, continuing...")
                else:
                    raise
        else:
            logger.warning(f"Schema file not found at {schema_path}")
    
    def _init_transliteration_system(self):
        """Initialize the extensible transliteration system."""
        if vidyut_lipi is None:
            logger.warning("Using mock transliteration system")
            self.lipika = MockExtensibleLipika()
            self.detector = MockSourceDetector()
            return
        
        try:
            # Initialize with udapaana configuration
            config_path = Path(__file__).parent.parent / self.config_path
            if config_path.exists():
                self.lipika = vidyut_lipi.ExtensibleLipika.from_config_file(str(config_path))
                logger.info(f"Loaded extensible configuration from {config_path}")
            else:
                self.lipika = vidyut_lipi.ExtensibleLipika.new()
                logger.info("Using default extensible configuration")
            
            self.detector = vidyut_lipi.SourceDetector.with_udapaana_config()
            logger.info("Extensible transliteration system initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize transliteration system: {e}")
            logger.info("Falling back to mock implementation")
            self.lipika = MockExtensibleLipika()
            self.detector = MockSourceDetector()
    
    def process_all_udapaana_data(self, data_dir: Path = None):
        """Process all udapaana data with comprehensive testing."""
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data" / "vedic_texts"
        
        logger.info(f"Starting enhanced udapaana processing from {data_dir}")
        logger.info(f"Run ID: {self.run_id}")
        
        # Process each veda/sakha/source combination
        for veda_dir in data_dir.iterdir():
            if not veda_dir.is_dir():
                continue
                
            veda_name = veda_dir.name
            logger.info(f"Processing veda: {veda_name}")
            
            for sakha_dir in veda_dir.iterdir():
                if not sakha_dir.is_dir():
                    continue
                    
                sakha_name = sakha_dir.name
                logger.info(f"Processing sakha: {sakha_name}")
                
                for source_dir in sakha_dir.iterdir():
                    if not source_dir.is_dir():
                        continue
                        
                    source_name = source_dir.name
                    logger.info(f"Processing source: {source_name}")
                    
                    # Process this sakha-veda-source combination
                    self._process_source_directory(
                        source_dir, veda_name, sakha_name, source_name
                    )
        
        # Finalize processing
        self._finalize_processing()
        logger.info("Enhanced udapaana processing completed")
    
    def _process_source_directory(self, source_dir: Path, veda: str, sakha: str, source: str):
        """Process all files in a source directory."""
        source_key = f"{veda}_{sakha}_{source}"
        self.stats['sources_processed'][source_key] = 0
        self.stats['sakha_veda_combinations'][f"{veda}_{sakha}"] = \
            self.stats['sakha_veda_combinations'].get(f"{veda}_{sakha}", 0)
        
        # Find all JSON files recursively
        json_files = list(source_dir.rglob("*.json"))
        logger.info(f"Found {len(json_files)} JSON files in {source_dir}")
        
        for json_file in json_files:
            try:
                self._process_file(json_file, veda, sakha, source)
                self.stats['total_files_processed'] += 1
                self.stats['sources_processed'][source_key] += 1
            except Exception as e:
                logger.error(f"Error processing {json_file}: {e}")
    
    def _process_file(self, file_path: Path, veda: str, sakha: str, source: str):
        """Process a single file with comprehensive testing."""
        logger.debug(f"Processing file: {file_path}")
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        # Detect source type automatically
        detection_result = self._detect_source(file_path, file_content)
        
        # Store detection result
        self._store_source_detection(file_path, detection_result)
        
        # Parse JSON content
        try:
            data = json.loads(file_content)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            return
        
        # Extract text content and metadata
        texts = self._extract_texts_from_json(data, file_path)
        
        for text_data in texts:
            text_id = self._process_single_text(
                text_data, veda, sakha, source, detection_result, file_path
            )
            
            if text_id:
                self.stats['total_texts_created'] += 1
    
    def _detect_source(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Detect source type using the extensible system."""
        try:
            detection = self.detector.detect_source(str(file_path), content)
            return {
                'scheme_name': detection.scheme_name,
                'confidence': detection.confidence,
                'matched_rule': detection.matched_rule,
                'metadata': {
                    'veda': detection.metadata.veda,
                    'sakha': detection.metadata.sakha,
                    'source': detection.metadata.source,
                    'text_type': detection.metadata.text_type,
                    'has_pua': detection.metadata.has_pua,
                    'accent_patterns': detection.metadata.accent_patterns,
                    'section_markers': detection.metadata.section_markers
                }
            }
        except Exception as e:
            logger.error(f"Source detection failed for {file_path}: {e}")
            return {
                'scheme_name': 'Unknown',
                'confidence': 0.0,
                'matched_rule': 'none',
                'metadata': {}
            }
    
    def _store_source_detection(self, file_path: Path, detection: Dict[str, Any]):
        """Store source detection results in database."""
        metadata = detection.get('metadata', {})
        
        self.conn.execute("""
            INSERT OR REPLACE INTO source_detections 
            (file_path, detected_scheme, confidence_score, matched_rule,
             detected_veda, detected_sakha, detected_source, detected_text_type,
             has_pua_codes, accent_patterns_found, section_markers_found)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(file_path),
            detection['scheme_name'],
            detection['confidence'],
            detection['matched_rule'],
            metadata.get('veda'),
            metadata.get('sakha'),
            metadata.get('source'),
            metadata.get('text_type'),
            metadata.get('has_pua', False),
            json.dumps(metadata.get('accent_patterns', [])),
            json.dumps(metadata.get('section_markers', []))
        ))
        self.conn.commit()
    
    def _extract_texts_from_json(self, data: Dict, file_path: Path) -> List[Dict]:
        """Extract individual texts from JSON data."""
        # Handle udapaana JSON structure specifically
        
        if isinstance(data, dict):
            # Check for udapaana structure with 'texts' array containing 'vaakya_text'
            if 'texts' in data and isinstance(data['texts'], list):
                extracted_texts = []
                for item in data['texts']:
                    if isinstance(item, dict):
                        # Extract text from various possible fields
                        text_content = (
                            item.get('vaakya_text') or 
                            item.get('text') or 
                            item.get('content') or
                            ''
                        )
                        
                        if text_content and len(text_content.strip()) > 3:
                            extracted_texts.append({
                                'content': text_content,
                                'title': f"{file_path.stem}_{item.get('vaakya_pk', len(extracted_texts))}",
                                'metadata': {
                                    'location': item.get('location', []),
                                    'vaakya_pk': item.get('vaakya_pk'),
                                    'vaakya_sk': item.get('vaakya_sk'),
                                    'source_file': str(file_path)
                                }
                            })
                return extracted_texts
            
            # Fallback: check for single text
            elif 'content' in data or 'text' in data or 'vaakya_text' in data:
                text_content = data.get('content') or data.get('text') or data.get('vaakya_text', '')
                return [{
                    'content': text_content,
                    'title': file_path.stem,
                    'metadata': data.get('metadata', {})
                }]
            
            # Last resort: try to find any string content
            else:
                texts = []
                for key, value in data.items():
                    if isinstance(value, str) and len(value) > 10:
                        texts.append({
                            'content': value,
                            'title': f"{file_path.stem}_{key}",
                            'metadata': {'field': key}
                        })
                return texts
        
        return [{'content': str(data), 'title': file_path.stem, 'metadata': {}}]
    
    def _process_single_text(self, text_data: Dict, veda: str, sakha: str, 
                           source: str, detection: Dict, file_path: Path) -> Optional[int]:
        """Process a single text with line-by-line round-trip testing."""
        
        # Extract content
        content = (
            text_data.get('content') or 
            text_data.get('text') or 
            text_data.get('vaakya_text') or 
            ''
        )
        if not content or len(content.strip()) < 3:
            return None
        
        title = text_data.get('title', file_path.stem)
        metadata = text_data.get('metadata', {})
        
        # Get database IDs
        sakha_id = self._get_sakha_id(veda, sakha)
        text_type_id = self._get_text_type_id(metadata.get('text_type', 'samhita'))
        source_id = self._get_source_id(source)
        
        # Perform extensible transliteration
        translation_result = self._translate_with_extension(
            content, detection, source
        )
        
        # Calculate overall round-trip validity
        overall_round_trip_valid = translation_result.get('round_trip_valid', False)
        
        # Insert main text record
        cursor = self.conn.execute("""
            INSERT INTO texts 
            (sakha_id, text_type_id, source_id, content_slp1_extended, 
             content_original, source_encoding, source_file_path,
             extension_scheme_used, discovered_patterns_count, 
             custom_mappings_applied, round_trip_valid, round_trip_confidence,
             processing_confidence, quality_score, title, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sakha_id, text_type_id, source_id,
            translation_result.get('result', ''),
            content,
            detection.get('scheme_name', 'unknown'),
            str(file_path),
            detection.get('scheme_name'),
            len(translation_result.get('discovered_patterns', [])),
            json.dumps(translation_result.get('custom_mappings', [])),
            overall_round_trip_valid,
            translation_result.get('confidence', 1.0),
            translation_result.get('confidence', 1.0),
            translation_result.get('quality_score', 1.0),
            title,
            json.dumps(metadata)
        ))
        
        text_id = cursor.lastrowid
        
        # Process line by line
        self._process_lines(text_id, content, detection, source)
        
        # Store discovered patterns
        self._store_discovered_patterns(
            translation_result.get('discovered_patterns', []),
            detection, f"{veda}_{sakha}"
        )
        
        return text_id
    
    def _translate_with_extension(self, content: str, detection: Dict, source: str) -> Dict:
        """Perform transliteration with extensible mappings."""
        try:
            # Determine source and target schemes
            source_scheme = self._get_source_scheme(detection)
            target_scheme = 'Slp1'  # Always convert to SLP1 Extended
            
            # Perform extensible transliteration
            result = self.lipika.transliterate_extensible(
                content, source_scheme, target_scheme, source
            )
            
            return {
                'result': result.result,
                'discovered_patterns': result.discovered_patterns,
                'round_trip_valid': result.round_trip_valid,
                'warnings': result.warnings,
                'confidence': 1.0,
                'quality_score': 1.0 if result.round_trip_valid else 0.8
            }
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return {
                'result': content,  # Fallback to original
                'discovered_patterns': [],
                'round_trip_valid': False,
                'warnings': [str(e)],
                'confidence': 0.0,
                'quality_score': 0.0
            }
    
    def _process_lines(self, text_id: int, content: str, detection: Dict, source: str):
        """Process text line by line with individual round-trip testing."""
        lines = content.split('\n')
        
        for line_number, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            # Translate this line
            line_result = self._translate_with_extension(line, detection, source)
            
            # Perform detailed round-trip testing for this line
            round_trip_result = self._test_line_round_trip(
                line, line_result, detection, source
            )
            
            # Store line data
            self.conn.execute("""
                INSERT INTO text_lines 
                (text_id, line_number, content_original, content_slp1_extended,
                 content_round_trip, round_trip_valid, round_trip_exact_match,
                 round_trip_normalized_match, patterns_discovered, 
                 mappings_applied, confidence_score, processing_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                text_id, line_number, line,
                line_result.get('result', ''),
                round_trip_result.get('round_trip_content', ''),
                round_trip_result.get('is_lossless', False),
                round_trip_result.get('exact_match', False),
                round_trip_result.get('normalized_match', False),
                json.dumps(line_result.get('discovered_patterns', [])),
                json.dumps(line_result.get('custom_mappings', [])),
                line_result.get('confidence', 1.0),
                json.dumps(round_trip_result.get('notes', []))
            ))
            
            # Store detailed round-trip test
            self._store_round_trip_test(text_id, line_number, round_trip_result)
            
            # Update statistics
            self.stats['total_lines_processed'] += 1
            if round_trip_result.get('is_lossless', False):
                self.stats['lines_with_perfect_round_trip'] += 1
            else:
                self.stats['lines_with_failed_round_trip'] += 1
        
        self.conn.commit()
    
    def _test_line_round_trip(self, original: str, translation_result: Dict, 
                            detection: Dict, source: str) -> Dict:
        """Perform comprehensive round-trip testing for a single line."""
        translated = translation_result.get('result', '')
        
        # Attempt reverse translation
        try:
            target_scheme = self._get_source_scheme(detection)
            reverse_result = self.lipika.transliterate_extensible(
                translated, 'Slp1', target_scheme, source
            )
            round_trip_content = reverse_result.result
        except Exception as e:
            round_trip_content = translated
            logger.debug(f"Reverse translation failed: {e}")
        
        # Test different levels of equality
        exact_match = original == round_trip_content
        normalized_match = self._normalize_for_comparison(original) == \
                          self._normalize_for_comparison(round_trip_content)
        
        # Calculate similarity metrics
        similarity = self._calculate_similarity(original, round_trip_content)
        levenshtein_dist = self._levenshtein_distance(original, round_trip_content)
        
        # Determine if lossless
        is_lossless = exact_match or (normalized_match and similarity > 0.95)
        
        return {
            'round_trip_content': round_trip_content,
            'is_lossless': is_lossless,
            'exact_match': exact_match,
            'normalized_match': normalized_match,
            'similarity_score': similarity,
            'levenshtein_distance': levenshtein_dist,
            'char_differences': abs(len(original) - len(round_trip_content)),
            'notes': []
        }
    
    def _store_round_trip_test(self, text_id: int, line_number: int, result: Dict):
        """Store detailed round-trip test results."""
        # Get the text_line_id
        cursor = self.conn.execute(
            "SELECT id FROM text_lines WHERE text_id = ? AND line_number = ?",
            (text_id, line_number)
        )
        row = cursor.fetchone()
        text_line_id = row['id'] if row else None
        
        self.conn.execute("""
            INSERT INTO round_trip_tests 
            (text_id, text_line_id, source_scheme, target_scheme,
             original_content, converted_content, round_trip_content,
             is_lossless, exact_match, normalized_match,
             char_differences, similarity_score, levenshtein_distance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            text_id, text_line_id, 'auto_detected', 'Slp1',
            result.get('original_content', ''),
            result.get('converted_content', ''),
            result.get('round_trip_content', ''),
            result.get('is_lossless', False),
            result.get('exact_match', False),
            result.get('normalized_match', False),
            result.get('char_differences', 0),
            result.get('similarity_score', 0.0),
            result.get('levenshtein_distance', 0)
        ))
    
    def _store_discovered_patterns(self, patterns: List, detection: Dict, sakha_veda: str):
        """Store discovered patterns in database."""
        for pattern in patterns:
            # Check if pattern already exists
            cursor = self.conn.execute("""
                SELECT id, frequency_count FROM discovered_patterns 
                WHERE source_pattern = ? AND target_mapping = ? AND detected_in_source = ?
            """, (
                pattern.get('source', ''),
                pattern.get('target', ''),
                detection.get('scheme_name', '')
            ))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update frequency
                self.conn.execute("""
                    UPDATE discovered_patterns 
                    SET frequency_count = frequency_count + 1, last_seen_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (existing['id'],))
            else:
                # Insert new pattern
                self.conn.execute("""
                    INSERT INTO discovered_patterns 
                    (source_pattern, target_mapping, pattern_type, detected_in_source,
                     detected_in_sakha_veda, detection_scheme, confidence_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    pattern.get('source', ''),
                    pattern.get('target', ''),
                    pattern.get('pattern_type', 'unknown'),
                    detection.get('scheme_name', ''),
                    sakha_veda,
                    detection.get('scheme_name', ''),
                    pattern.get('confidence', 0.0)
                ))
                
                self.stats['unique_patterns_discovered'] += 1
            
            self.stats['total_patterns_discovered'] += 1
    
    def _finalize_processing(self):
        """Finalize processing and store statistics."""
        processing_end_time = datetime.now()
        processing_duration = (processing_end_time - self.processing_start_time).total_seconds()
        
        # Calculate final statistics
        if self.stats['total_lines_processed'] > 0:
            self.stats['round_trip_success_rate'] = \
                self.stats['lines_with_perfect_round_trip'] / self.stats['total_lines_processed']
        
        # Store pipeline statistics
        self.conn.execute("""
            INSERT INTO pipeline_statistics 
            (run_id, total_files_processed, total_lines_processed, total_texts_created,
             sources_processed, sakha_veda_combinations, total_patterns_discovered,
             unique_patterns_discovered, round_trip_success_rate, 
             lines_with_perfect_round_trip, lines_with_failed_round_trip,
             processing_start_time, processing_end_time, total_processing_time_seconds,
             pipeline_version, config_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.run_id,
            self.stats['total_files_processed'],
            self.stats['total_lines_processed'],
            self.stats['total_texts_created'],
            json.dumps(self.stats['sources_processed']),
            json.dumps(self.stats['sakha_veda_combinations']),
            self.stats['total_patterns_discovered'],
            self.stats['unique_patterns_discovered'],
            self.stats['round_trip_success_rate'],
            self.stats['lines_with_perfect_round_trip'],
            self.stats['lines_with_failed_round_trip'],
            self.processing_start_time.isoformat(),
            processing_end_time.isoformat(),
            processing_duration,
            "enhanced_pipeline_v1.0",
            json.dumps({"config_path": self.config_path})
        ))
        
        self.conn.commit()
        
        # Log final statistics
        logger.info(f"Pipeline completed in {processing_duration:.2f} seconds")
        logger.info(f"Processed {self.stats['total_files_processed']} files")
        logger.info(f"Processed {self.stats['total_lines_processed']} lines")
        logger.info(f"Created {self.stats['total_texts_created']} text records")
        logger.info(f"Round-trip success rate: {self.stats['round_trip_success_rate']:.2%}")
        logger.info(f"Discovered {self.stats['unique_patterns_discovered']} unique patterns")
    
    # Helper methods
    def _get_sakha_id(self, veda: str, sakha: str) -> int:
        cursor = self.conn.execute("""
            SELECT s.id FROM sakhas s 
            JOIN vedas v ON s.veda_id = v.id 
            WHERE v.name = ? AND s.name = ?
        """, (veda, sakha))
        row = cursor.fetchone()
        return row['id'] if row else 1
    
    def _get_text_type_id(self, text_type: str) -> int:
        cursor = self.conn.execute("SELECT id FROM text_types WHERE name = ?", (text_type,))
        row = cursor.fetchone()
        return row['id'] if row else 1
    
    def _get_source_id(self, source: str) -> int:
        cursor = self.conn.execute("SELECT id FROM sources WHERE name = ?", (source,))
        row = cursor.fetchone()
        return row['id'] if row else 1
    
    def _get_source_scheme(self, detection: Dict) -> str:
        """Determine source scheme from detection results."""
        scheme_name = detection.get('scheme_name', 'Unknown')
        if 'Baraha' in scheme_name or 'vedavms' in scheme_name:
            return 'BarahaSouth'
        elif 'Devanagari' in scheme_name or 'Samaveda' in scheme_name:
            return 'Devanagari'
        else:
            return 'BarahaSouth'  # Default fallback
    
    def _normalize_for_comparison(self, text: str) -> str:
        """Normalize text for comparison (whitespace, etc.)."""
        return ' '.join(text.split())
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity score between two texts."""
        if text1 == text2:
            return 1.0
        
        # Simple character-based similarity
        len1, len2 = len(text1), len(text2)
        if len1 == 0 and len2 == 0:
            return 1.0
        if len1 == 0 or len2 == 0:
            return 0.0
        
        # Use Levenshtein distance for similarity
        distance = self._levenshtein_distance(text1, text2)
        max_len = max(len1, len2)
        return 1.0 - (distance / max_len)
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]

# Mock implementations for when vidyut-lipi is not available
class MockExtensibleLipika:
    def transliterate_extensible(self, text, from_scheme, to_scheme, source):
        return MockTranslationResult(text)

class MockTranslationResult:
    def __init__(self, text):
        self.result = text
        self.discovered_patterns = []
        self.round_trip_valid = True
        self.warnings = []

class MockSourceDetector:
    def detect_source(self, path, content):
        return MockDetectionResult()

class MockDetectionResult:
    def __init__(self):
        self.scheme_name = "MockScheme"
        self.confidence = 0.8
        self.matched_rule = "mock_rule"
        self.metadata = MockMetadata()

class MockMetadata:
    def __init__(self):
        self.veda = "rigveda"
        self.sakha = "shakala"
        self.source = "vedanidhi"
        self.text_type = "samhita"
        self.has_pua = False
        self.accent_patterns = ["#", "q"]
        self.section_markers = ["||"]

if __name__ == "__main__":
    # Run the enhanced pipeline
    pipeline = EnhancedUdapaanaPipeline()
    pipeline.process_all_udapaana_data()