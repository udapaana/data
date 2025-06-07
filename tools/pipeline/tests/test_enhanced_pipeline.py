#!/usr/bin/env python3
"""
Test suite for enhanced udapaana pipeline.
"""

import unittest
import tempfile
import json
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch

# Import pipeline modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from enhanced_udapaana_pipeline import EnhancedUdapaanaPipeline
from analyze_pipeline_results import UdapaanaPipelineAnalyzer


class TestEnhancedPipeline(unittest.TestCase):
    """Test cases for enhanced udapaana pipeline."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_db = str(Path(self.test_dir) / "test.sqlite")
        self.test_config = str(Path(self.test_dir) / "test_config.yaml")
        
        # Create test configuration
        test_config_content = """
version: "1.0"
scheme_extensions:
  TestScheme:
    base_scheme: "BarahaSouth"
    description: "Test scheme"
    unknown_strategy: "CreatePlaceholders"
    validation:
      enabled: true
      tolerance: "Exact"
      on_failure: "Error"
    patterns:
      - name: "test_accent"
        pattern: "q"
        pattern_type: "Accent"
        target_mapping:
          Fixed: "{A}"
        confidence: 0.9
    sources:
      test_source:
        source_id: "test_source"
        patterns: []
        known_mappings:
          "q": "{A}"
        processing_rules: []
defaults:
  unknown_strategy: "CreatePlaceholders"
  validation:
    enabled: true
    tolerance: "Exact"
    on_failure: "Error"
  confidence_threshold: 0.7
  max_pattern_length: 8
"""
        with open(self.test_config, 'w') as f:
            f.write(test_config_content)
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        pipeline = EnhancedUdapaanaPipeline(
            db_path=self.test_db,
            config_path=self.test_config
        )
        
        self.assertIsNotNone(pipeline.conn)
        self.assertIsNotNone(pipeline.run_id)
        self.assertIsInstance(pipeline.stats, dict)
    
    def test_database_initialization(self):
        """Test database schema creation."""
        pipeline = EnhancedUdapaanaPipeline(db_path=self.test_db)
        
        # Check that core tables exist
        cursor = pipeline.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            'vedas', 'sakhas', 'text_types', 'sources', 'texts',
            'text_lines', 'discovered_patterns', 'round_trip_tests'
        ]
        
        for table in expected_tables:
            self.assertIn(table, tables)
    
    def test_source_detection(self):
        """Test source detection functionality."""
        pipeline = EnhancedUdapaanaPipeline(db_path=self.test_db)
        
        # Mock detection result
        mock_detection = {
            'scheme_name': 'TestScheme',
            'confidence': 0.9,
            'matched_rule': 'test_rule',
            'metadata': {
                'veda': 'rigveda',
                'sakha': 'shakala',
                'source': 'vedanidhi',
                'text_type': 'samhita',
                'has_pua': False,
                'accent_patterns': ['q', '#'],
                'section_markers': ['||']
            }
        }
        
        test_path = Path("test/path.json")
        pipeline._store_source_detection(test_path, mock_detection)
        
        # Verify storage
        cursor = pipeline.conn.execute(
            "SELECT * FROM source_detections WHERE file_path = ?",
            (str(test_path),)
        )
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row['detected_scheme'], 'TestScheme')
    
    def test_text_extraction(self):
        """Test text extraction from JSON."""
        pipeline = EnhancedUdapaanaPipeline(db_path=self.test_db)
        
        # Test single text extraction
        test_data = {
            'content': 'agni mILe purohitam',
            'title': 'Test Text',
            'metadata': {'text_type': 'samhita'}
        }
        
        texts = pipeline._extract_texts_from_json(test_data, Path("test.json"))
        self.assertEqual(len(texts), 1)
        self.assertEqual(texts[0]['content'], 'agni mILe purohitam')
    
    @patch('enhanced_udapaana_pipeline.vidyut_lipi')
    def test_translation_with_extension(self, mock_vidyut):
        """Test translation with extensible mappings."""
        # Mock vidyut-lipi results
        mock_result = Mock()
        mock_result.result = "agni mILe purohitam"
        mock_result.discovered_patterns = []
        mock_result.round_trip_valid = True
        mock_result.warnings = []
        
        mock_vidyut.ExtensibleLipika.return_value.transliterate_extensible.return_value = mock_result
        
        pipeline = EnhancedUdapaanaPipeline(db_path=self.test_db)
        
        detection = {'scheme_name': 'TestScheme'}
        result = pipeline._translate_with_extension("test content", detection, "test_source")
        
        self.assertEqual(result['result'], "agni mILe purohitam")
        self.assertTrue(result['round_trip_valid'])
    
    def test_round_trip_testing(self):
        """Test round-trip validation logic."""
        pipeline = EnhancedUdapaanaPipeline(db_path=self.test_db)
        
        # Test exact match
        original = "agni mILe"
        translation_result = {'result': 'agni mILe'}
        detection = {'scheme_name': 'TestScheme'}
        
        round_trip_result = pipeline._test_line_round_trip(
            original, translation_result, detection, "test_source"
        )
        
        # Should be lossless for identical content
        self.assertTrue(round_trip_result.get('exact_match', False))
    
    def test_similarity_calculation(self):
        """Test similarity calculation methods."""
        pipeline = EnhancedUdapaanaPipeline(db_path=self.test_db)
        
        # Test exact match
        similarity = pipeline._calculate_similarity("test", "test")
        self.assertEqual(similarity, 1.0)
        
        # Test no match
        similarity = pipeline._calculate_similarity("", "test")
        self.assertEqual(similarity, 0.0)
        
        # Test Levenshtein distance
        distance = pipeline._levenshtein_distance("test", "text")
        self.assertEqual(distance, 1)
    
    def test_statistics_tracking(self):
        """Test pipeline statistics tracking."""
        pipeline = EnhancedUdapaanaPipeline(db_path=self.test_db)
        
        # Check initial stats
        self.assertEqual(pipeline.stats['total_files_processed'], 0)
        self.assertEqual(pipeline.stats['total_lines_processed'], 0)
        
        # Update stats
        pipeline.stats['total_files_processed'] += 1
        pipeline.stats['total_lines_processed'] += 10
        
        self.assertEqual(pipeline.stats['total_files_processed'], 1)
        self.assertEqual(pipeline.stats['total_lines_processed'], 10)


class TestPipelineAnalyzer(unittest.TestCase):
    """Test cases for pipeline result analyzer."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_db = str(Path(self.test_dir) / "test_analysis.sqlite")
        
        # Create test database with sample data
        self._create_test_database()
    
    def _create_test_database(self):
        """Create test database with sample data."""
        conn = sqlite3.connect(self.test_db)
        
        # Create minimal schema for testing
        conn.executescript("""
        CREATE TABLE texts (
            id INTEGER PRIMARY KEY,
            quality_score REAL,
            round_trip_valid BOOLEAN
        );
        
        CREATE TABLE text_lines (
            id INTEGER PRIMARY KEY,
            text_id INTEGER,
            round_trip_valid BOOLEAN,
            confidence_score REAL
        );
        
        CREATE TABLE discovered_patterns (
            id INTEGER PRIMARY KEY,
            pattern_type TEXT,
            frequency_count INTEGER,
            confidence_score REAL
        );
        
        CREATE TABLE round_trip_tests (
            id INTEGER PRIMARY KEY,
            is_lossless BOOLEAN,
            exact_match BOOLEAN,
            similarity_score REAL
        );
        
        -- Insert sample data
        INSERT INTO texts (quality_score, round_trip_valid) VALUES 
        (0.95, 1), (0.87, 1), (0.73, 0);
        
        INSERT INTO text_lines (text_id, round_trip_valid, confidence_score) VALUES
        (1, 1, 0.95), (1, 1, 0.90), (2, 0, 0.75);
        
        INSERT INTO discovered_patterns (pattern_type, frequency_count, confidence_score) VALUES
        ('accent', 10, 0.9), ('nasal', 5, 0.8);
        
        INSERT INTO round_trip_tests (is_lossless, exact_match, similarity_score) VALUES
        (1, 1, 1.0), (1, 0, 0.95), (0, 0, 0.6);
        """)
        
        conn.commit()
        conn.close()
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        analyzer = UdapaanaPipelineAnalyzer(self.test_db)
        self.assertIsNotNone(analyzer.conn)
    
    def test_overall_statistics(self):
        """Test overall statistics calculation."""
        analyzer = UdapaanaPipelineAnalyzer(self.test_db)
        stats = analyzer.get_overall_statistics()
        
        self.assertIn('total_texts', stats)
        self.assertIn('total_lines', stats)
        self.assertIn('round_trip_success_rate', stats)
    
    def test_round_trip_analysis(self):
        """Test round-trip analysis."""
        analyzer = UdapaanaPipelineAnalyzer(self.test_db)
        analysis = analyzer.analyze_round_trip_results()
        
        self.assertIn('overall', analysis)
        self.assertIn('failed_examples', analysis)
    
    def test_pattern_analysis(self):
        """Test pattern discovery analysis."""
        analyzer = UdapaanaPipelineAnalyzer(self.test_db)
        analysis = analyzer.analyze_discovered_patterns()
        
        self.assertIn('by_type', analysis)
        self.assertIn('most_frequent', analysis)


class TestConfigurationHandling(unittest.TestCase):
    """Test configuration handling and validation."""
    
    def test_yaml_configuration_loading(self):
        """Test YAML configuration loading."""
        test_config = """
version: "1.0"
scheme_extensions:
  TestScheme:
    base_scheme: "BarahaSouth"
    description: "Test scheme"
    patterns: []
    sources: {}
defaults:
  unknown_strategy: "CreatePlaceholders"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(test_config)
            config_path = f.name
        
        try:
            # Test that configuration can be loaded
            with open(config_path, 'r') as f:
                import yaml
                config = yaml.safe_load(f)
            
            self.assertEqual(config['version'], "1.0")
            self.assertIn('TestScheme', config['scheme_extensions'])
        finally:
            Path(config_path).unlink()


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)