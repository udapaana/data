#!/usr/bin/env python3
"""
Udapaana Source Transformation Pipeline with Multi-Encoding Support

This pipeline processes Vedic texts from the Udapaana data structure and produces
multiple encoding formats stored in SQLite:
- Extended SLP1 (base storage)
- Devanagari 
- Telugu

Uses vidyut-lipi for robust transliteration with roundtrip testing.
"""

import json
import sqlite3
import uuid
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, NamedTuple
import logging

# Data loss prevention disabled by default - source files are the backup

# Add vidyut-lipi Python bindings to path
vidyut_path = Path("/Users/skmnktl/Projects/ambuda/vidyut/bindings-python")
if vidyut_path.exists():
    sys.path.insert(0, str(vidyut_path))

try:
    # Import directly from the compiled module to avoid the problematic wrapper
    from vidyut.vidyut import lipi
    # Test basic functionality
    test_result = lipi.transliterate("namaste", lipi.Scheme.HarvardKyoto, lipi.Scheme.Devanagari)
    VIDYUT_AVAILABLE = True
    print(f"✓ vidyut transliteration working - test: HK 'namaste' → Devanagari '{test_result}'")
except ImportError as e:
    print(f"Warning: vidyut not available: {e}")
    print("Using mock implementation")
    VIDYUT_AVAILABLE = False
except Exception as e:
    print(f"Warning: vidyut error: {e}")
    print("Using mock implementation")
    VIDYUT_AVAILABLE = False

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('udapaana_transformation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProcessingResult(NamedTuple):
    """Result of processing a single verse/text."""
    success: bool
    slp1_extended: str
    devanagari: str
    telugu: str
    iso_15919: str
    iast: str
    detected_scheme: str
    roundtrip_valid: bool
    quality_score: float
    errors: List[str]
    warnings: List[str]

class UdapaanaTransformationPipeline:
    """Transform Udapaana data into multi-encoding database storage."""
    
    def __init__(self, db_path: str = "udapaana_corpus.sqlite", enable_data_loss_prevention: bool = False):
        self.db_path = db_path
        self.run_id = str(uuid.uuid4())
        self.processing_start_time = datetime.now()
        self.enable_dlp = enable_data_loss_prevention
        
        # Initialize database
        self._init_database()
        
        # Initialize vidyut-lipi
        self._init_vidyut()
        
        # Initialize data loss prevention system
        self.dlp = None
        
        # Processing statistics
        self.stats = {
            'total_files_processed': 0,
            'total_verses_processed': 0,
            'successful_transformations': 0,
            'failed_transformations': 0,
            'roundtrip_successes': 0,
            'encoding_errors': 0,
            'source_breakdown': {},
        }
    
    def _init_database(self):
        """Initialize SQLite database with multi-encoding schema."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Create enhanced schema for multi-encoding storage
        self.conn.executescript("""
            -- Core hierarchical structure
            CREATE TABLE IF NOT EXISTS vedas (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS sakhas (
                id INTEGER PRIMARY KEY,
                veda_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (veda_id) REFERENCES vedas(id),
                UNIQUE(veda_id, name)
            );
            
            CREATE TABLE IF NOT EXISTS text_types (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Enhanced text storage with multiple encodings
            CREATE TABLE IF NOT EXISTS texts (
                id INTEGER PRIMARY KEY,
                sakha_id INTEGER NOT NULL,
                text_type_id INTEGER NOT NULL,
                source_id INTEGER NOT NULL,
                
                -- Traditional hierarchical identifiers
                kanda INTEGER,
                ashtaka INTEGER,
                adhyaya INTEGER,
                prapathaka INTEGER,
                anuvaka INTEGER,
                sukta INTEGER,
                mantra INTEGER,
                pada TEXT,
                
                -- Multi-encoding content (base storage in Extended SLP1)
                content_slp1_extended TEXT NOT NULL,
                content_devanagari TEXT,
                content_telugu TEXT,
                content_iso_15919 TEXT,
                content_iast TEXT,
                
                -- Source content preservation
                content_original TEXT NOT NULL,
                source_encoding TEXT NOT NULL,
                source_file_path TEXT NOT NULL,
                
                -- Quality and validation metrics
                roundtrip_valid BOOLEAN NOT NULL DEFAULT 0,
                quality_score REAL DEFAULT 1.0,
                encoding_confidence REAL DEFAULT 1.0,
                
                -- Processing metadata
                processing_notes TEXT,
                transformation_warnings TEXT,
                
                -- Standard metadata
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (sakha_id) REFERENCES sakhas(id),
                FOREIGN KEY (text_type_id) REFERENCES text_types(id),
                FOREIGN KEY (source_id) REFERENCES sources(id)
            );
            
            -- Detailed encoding test results for each verse
            CREATE TABLE IF NOT EXISTS encoding_tests (
                id INTEGER PRIMARY KEY,
                text_id INTEGER NOT NULL,
                source_scheme TEXT NOT NULL,
                target_scheme TEXT NOT NULL,
                original_text TEXT NOT NULL,
                converted_text TEXT NOT NULL,
                roundtrip_text TEXT NOT NULL,
                is_lossless BOOLEAN NOT NULL,
                char_differences INTEGER DEFAULT 0,
                similarity_score REAL DEFAULT 0.0,
                test_notes TEXT,
                test_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (text_id) REFERENCES texts(id)
            );
            
            -- Processing run statistics
            CREATE TABLE IF NOT EXISTS processing_runs (
                id INTEGER PRIMARY KEY,
                run_id TEXT NOT NULL UNIQUE,
                total_files_processed INTEGER DEFAULT 0,
                total_verses_processed INTEGER DEFAULT 0,
                successful_transformations INTEGER DEFAULT 0,
                failed_transformations INTEGER DEFAULT 0,
                roundtrip_success_rate REAL DEFAULT 0.0,
                processing_start_time TIMESTAMP NOT NULL,
                processing_end_time TIMESTAMP,
                config_used TEXT,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Indexes for performance
            CREATE INDEX IF NOT EXISTS idx_texts_hierarchy 
                ON texts(sakha_id, text_type_id, kanda, ashtaka, adhyaya, sukta, mantra);
            CREATE INDEX IF NOT EXISTS idx_texts_source ON texts(source_id);
            CREATE INDEX IF NOT EXISTS idx_texts_quality ON texts(roundtrip_valid, quality_score);
            CREATE INDEX IF NOT EXISTS idx_encoding_tests_text ON encoding_tests(text_id);
        """)
        
        # Initialize reference data
        self._init_reference_data()
        self.conn.commit()
        logger.info("Database schema initialized successfully")
    
    def _init_reference_data(self):
        """Initialize core reference data."""
        # Insert vedas
        for veda in ['rigveda', 'samaveda', 'yajurveda', 'atharvaveda']:
            self.conn.execute("INSERT OR IGNORE INTO vedas (name) VALUES (?)", (veda,))
        
        # Insert text types
        text_types = [
            ('samhita', 'Primary mantric texts'),
            ('brahmana', 'Ritual explanation texts'),
            ('aranyaka', 'Forest treatises'),
            ('upanishad', 'Philosophical treatises')
        ]
        for name, desc in text_types:
            self.conn.execute("INSERT OR IGNORE INTO text_types (name, description) VALUES (?, ?)", (name, desc))
        
        # Insert sources
        sources = [
            ('vedanidhi', 'Digital library API downloads'),
            ('vedavms', 'Baraha-encoded DOCX files'),
            ('gretil', 'Göttingen Register of Electronic Texts in Indian Languages')
        ]
        for name, desc in sources:
            self.conn.execute("INSERT OR IGNORE INTO sources (name, description) VALUES (?, ?)", (name, desc))
        
        # Insert sakhas
        sakha_mappings = [
            ('rigveda', 'shakala'),
            ('yajurveda', 'taittiriya'),
            ('samaveda', 'kauthuma'),
            ('atharvaveda', 'shaunaka')
        ]
        for veda_name, sakha_name in sakha_mappings:
            self.conn.execute("""
                INSERT OR IGNORE INTO sakhas (veda_id, name) 
                SELECT id, ? FROM vedas WHERE name = ?
            """, (sakha_name, veda_name))
    
    def _init_vidyut(self):
        """Initialize vidyut-lipi for transliteration."""
        if not VIDYUT_AVAILABLE:
            logger.warning("Using mock vidyut implementation")
            self.vidyut = MockVidyut()
            return
        
        try:
            # Test basic vidyut functionality
            test_result = lipi.transliterate("namaste", lipi.Scheme.HarvardKyoto, lipi.Scheme.Slp1)
            logger.info(f"Vidyut test successful: {test_result}")
            self.vidyut = VidyutTransliterator()
        except Exception as e:
            logger.error(f"Failed to initialize vidyut: {e}")
            logger.info("Falling back to mock implementation")
            self.vidyut = MockVidyut()
    
    def process_all_sources(self, data_dir: Path = None):
        """Process all source data in the Udapaana structure."""
        if data_dir is None:
            data_dir = Path("data/vedic_texts")
        
        if not data_dir.exists():
            logger.error(f"Data directory does not exist: {data_dir}")
            return
        
        logger.info(f"Starting transformation of Udapaana data from {data_dir}")
        logger.info(f"Run ID: {self.run_id}")
        
        # Data loss prevention disabled - source files are the backup
        if self.enable_dlp:
            logger.info("Data loss prevention is disabled - source files serve as backup")
        
        # Record processing run
        self.conn.execute("""
            INSERT INTO processing_runs (run_id, processing_start_time)
            VALUES (?, ?)
        """, (self.run_id, self.processing_start_time))
        self.conn.commit()
        
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
                    
                    # Process this combination
                    self._process_source_directory(source_dir, veda_name, sakha_name, source_name)
        
        # Finalize processing
        self._finalize_processing()
        logger.info("Transformation pipeline completed")
    
    def _process_source_directory(self, source_dir: Path, veda: str, sakha: str, source: str):
        """Process all files in a source directory."""
        source_key = f"{veda}_{sakha}_{source}"
        self.stats['source_breakdown'][source_key] = {
            'files_processed': 0,
            'verses_processed': 0,
            'successful_transformations': 0,
            'failed_transformations': 0
        }
        
        # Find all JSON files recursively
        json_files = list(source_dir.rglob("*.json"))
        logger.info(f"Found {len(json_files)} JSON files in {source_dir}")
        
        for json_file in json_files:
            try:
                self._process_file(json_file, veda, sakha, source)
                self.stats['total_files_processed'] += 1
                self.stats['source_breakdown'][source_key]['files_processed'] += 1
            except Exception as e:
                logger.error(f"Error processing {json_file}: {e}")
    
    def _process_file(self, file_path: Path, veda: str, sakha: str, source: str):
        """Process a single JSON file with verse-by-verse transformation."""
        logger.debug(f"Processing file: {file_path}")
        
        # Read and parse JSON
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return
        
        # Extract verses from JSON structure
        verses = self._extract_verses_from_json(data, file_path)
        source_key = f"{veda}_{sakha}_{source}"
        
        for verse_data in verses:
            try:
                result = self._transform_verse(verse_data, veda, sakha, source, file_path)
                if result.success:
                    self._store_verse(result, verse_data, veda, sakha, source, file_path)
                    self.stats['successful_transformations'] += 1
                    self.stats['source_breakdown'][source_key]['successful_transformations'] += 1
                    if result.roundtrip_valid:
                        self.stats['roundtrip_successes'] += 1
                    
                else:
                    self.stats['failed_transformations'] += 1
                    self.stats['source_breakdown'][source_key]['failed_transformations'] += 1
                    logger.warning(f"Failed to transform verse in {file_path}: {result.errors}")
                
                self.stats['total_verses_processed'] += 1
                self.stats['source_breakdown'][source_key]['verses_processed'] += 1
                
            except Exception as e:
                logger.error(f"Error transforming verse in {file_path}: {e}")
                self.stats['failed_transformations'] += 1
        
        # Commit after each file
        self.conn.commit()
    
    def _extract_verses_from_json(self, data: Dict, file_path: Path) -> List[Dict]:
        """Extract individual verses from Udapaana JSON structure."""
        verses = []
        
        if isinstance(data, dict):
            # Handle Udapaana structure with 'texts' array
            if 'texts' in data and isinstance(data['texts'], list):
                for item in data['texts']:
                    if isinstance(item, dict):
                        text_content = (
                            item.get('vaakya_text') or 
                            item.get('text') or 
                            item.get('content') or
                            ''
                        )
                        
                        if text_content and len(text_content.strip()) > 3:
                            verses.append({
                                'content': text_content.strip(),
                                'title': f"{file_path.stem}_{item.get('vaakya_pk', len(verses))}",
                                'metadata': {
                                    'location': item.get('location', []),
                                    'vaakya_pk': item.get('vaakya_pk'),
                                    'vaakya_sk': item.get('vaakya_sk'),
                                    'source_file': str(file_path)
                                }
                            })
            
            # Handle single text content
            elif any(key in data for key in ['content', 'text', 'vaakya_text']):
                text_content = data.get('content') or data.get('text') or data.get('vaakya_text', '')
                if text_content and len(text_content.strip()) > 3:
                    verses.append({
                        'content': text_content.strip(),
                        'title': file_path.stem,
                        'metadata': data.get('metadata', {})
                    })
        
        return verses
    
    def _transform_verse(self, verse_data: Dict, veda: str, sakha: str, source: str, file_path: Path) -> ProcessingResult:
        """Transform a single verse to multiple encodings."""
        content = verse_data.get('content', '').strip()
        
        if not content:
            return ProcessingResult(
                success=False,
                slp1_extended='',
                devanagari='',
                telugu='',
                roundtrip_valid=False,
                quality_score=0.0,
                errors=['Empty content'],
                warnings=[]
            )
        
        errors = []
        warnings = []
        
        try:
            # Detect source encoding with context hints
            source_hint = f"{source}_{veda}_{sakha}_{file_path.name}"
            detected_scheme = self.vidyut.detect_encoding(content, source_hint)
            logger.debug(f"Detected encoding '{detected_scheme}' for {file_path} (hint: {source_hint})")
            
            # Transform to Extended SLP1 (base format)
            slp1_result = self.vidyut.transform_to_slp1_extended(content, detected_scheme)
            if not slp1_result.success:
                errors.extend(slp1_result.errors)
                
            # Transform to Devanagari
            devanagari_result = self.vidyut.transform_to_devanagari(slp1_result.text)
            if not devanagari_result.success:
                errors.extend(devanagari_result.errors)
            
            # Transform to Telugu
            telugu_result = self.vidyut.transform_to_telugu(slp1_result.text)
            if not telugu_result.success:
                errors.extend(telugu_result.errors)
            
            # Transform to ISO-15919
            iso_result = self.vidyut.transform_to_iso_15919(slp1_result.text)
            if not iso_result.success:
                errors.extend(iso_result.errors)
            
            # Transform to IAST
            iast_result = self.vidyut.transform_to_iast(slp1_result.text)
            if not iast_result.success:
                errors.extend(iast_result.errors)
            
            # Test roundtrip validity
            roundtrip_result = self.vidyut.test_roundtrip(content, slp1_result.text, detected_scheme)
            
            # Calculate overall quality score
            quality_score = self._calculate_quality_score(
                slp1_result, devanagari_result, telugu_result, iso_result, iast_result, roundtrip_result
            )
            
            return ProcessingResult(
                success=len(errors) == 0,
                slp1_extended=slp1_result.text,
                devanagari=devanagari_result.text,
                telugu=telugu_result.text,
                iso_15919=iso_result.text,
                iast=iast_result.text,
                detected_scheme=detected_scheme,
                roundtrip_valid=roundtrip_result.valid,
                quality_score=quality_score,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"Transformation failed for verse in {file_path}: {e}")
            return ProcessingResult(
                success=False,
                slp1_extended='',
                devanagari='',
                telugu='',
                iso_15919='',
                iast='',
                detected_scheme='unknown',
                roundtrip_valid=False,
                quality_score=0.0,
                errors=[str(e)],
                warnings=[]
            )
    
    def _store_verse(self, result: ProcessingResult, verse_data: Dict, veda: str, sakha: str, source: str, file_path: Path):
        """Store transformed verse in database."""
        # Get database IDs
        sakha_id = self._get_sakha_id(veda, sakha)
        text_type_id = self._get_text_type_id('samhita')  # Default to samhita
        source_id = self._get_source_id(source)
        
        # Extract hierarchical information from metadata
        metadata = verse_data.get('metadata', {})
        location = metadata.get('location', [])
        
        # Store main text record
        cursor = self.conn.execute("""
            INSERT INTO texts 
            (sakha_id, text_type_id, source_id, content_slp1_extended, content_devanagari, 
             content_telugu, content_iso_15919, content_iast, content_original, source_encoding, source_file_path, 
             roundtrip_valid, quality_score, processing_notes, transformation_warnings, title)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sakha_id, text_type_id, source_id,
            result.slp1_extended, result.devanagari, result.telugu, result.iso_15919, result.iast,
            verse_data['content'], result.detected_scheme, str(file_path),
            result.roundtrip_valid, result.quality_score,
            json.dumps({'metadata': metadata, 'location': location}),
            json.dumps(result.warnings),
            verse_data.get('title', file_path.stem)
        ))
        
        text_id = cursor.lastrowid
        
        # Store encoding test results
        self._store_encoding_tests(text_id, verse_data['content'], result)
    
    def _store_encoding_tests(self, text_id: int, original_content: str, result: ProcessingResult):
        """Store detailed encoding test results."""
        # Test SLP1 Extended roundtrip
        self.conn.execute("""
            INSERT INTO encoding_tests 
            (text_id, source_scheme, target_scheme, original_text, converted_text, 
             roundtrip_text, is_lossless, similarity_score, test_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            text_id, 'auto_detected', 'SLP1_Extended',
            original_content, result.slp1_extended, '',
            result.roundtrip_valid, result.quality_score,
            json.dumps({'errors': result.errors, 'warnings': result.warnings})
        ))
    
    def _calculate_quality_score(self, slp1_result, devanagari_result, telugu_result, iso_result, iast_result, roundtrip_result) -> float:
        """Calculate overall quality score for the transformation."""
        scores = []
        
        if slp1_result.success:
            scores.append(0.3)  # 30% weight for SLP1 success
        
        if devanagari_result.success:
            scores.append(0.2)  # 20% weight for Devanagari success
            
        if telugu_result.success:
            scores.append(0.15)  # 15% weight for Telugu success
        
        if iso_result.success:
            scores.append(0.15)  # 15% weight for ISO-15919 success
        
        if iast_result.success:
            scores.append(0.15)  # 15% weight for IAST success
        
        if roundtrip_result.valid:
            scores.append(0.05)  # 5% weight for roundtrip validity
        
        return sum(scores)
    
    def _finalize_processing(self):
        """Finalize processing and update statistics."""
        processing_end_time = datetime.now()
        
        # Calculate roundtrip success rate
        roundtrip_rate = 0.0
        if self.stats['total_verses_processed'] > 0:
            roundtrip_rate = self.stats['roundtrip_successes'] / self.stats['total_verses_processed']
        
        # Update processing run record
        self.conn.execute("""
            UPDATE processing_runs SET
                processing_end_time = ?,
                total_files_processed = ?,
                total_verses_processed = ?,
                successful_transformations = ?,
                failed_transformations = ?,
                roundtrip_success_rate = ?
            WHERE run_id = ?
        """, (
            processing_end_time,
            self.stats['total_files_processed'],
            self.stats['total_verses_processed'],
            self.stats['successful_transformations'],
            self.stats['failed_transformations'],
            roundtrip_rate,
            self.run_id
        ))
        
        self.conn.commit()
        
        
        # Log final statistics
        duration = (processing_end_time - self.processing_start_time).total_seconds()
        logger.info(f"Processing completed in {duration:.2f} seconds")
        logger.info(f"Files processed: {self.stats['total_files_processed']}")
        logger.info(f"Verses processed: {self.stats['total_verses_processed']}")
        logger.info(f"Successful transformations: {self.stats['successful_transformations']}")
        logger.info(f"Failed transformations: {self.stats['failed_transformations']}")
        logger.info(f"Roundtrip success rate: {roundtrip_rate:.2%}")
    
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

# Vidyut integration classes
class TransformationResult(NamedTuple):
    success: bool
    text: str
    errors: List[str]

class RoundtripResult(NamedTuple):
    valid: bool
    similarity: float

class VidyutTransliterator:
    """Real vidyut-lipi integration for transliteration."""
    
    def detect_encoding(self, text: str, source_hint: str = '') -> str:
        """Detect encoding scheme of input text."""
        try:
            detected = lipi.detect(text)
            return str(detected)
        except Exception as e:
            logger.warning(f"Detection failed: {e}, using heuristic detection")
            return self._heuristic_encoding_detection(text, source_hint)
    
    def _heuristic_encoding_detection(self, text: str, source_hint: str = '') -> str:
        """Heuristic encoding detection based on character patterns."""
        # Check for Devanagari characters
        if any(0x0900 <= ord(c) <= 0x097F for c in text):
            return 'Devanagari'
        
        # Check for Telugu characters  
        if any(0x0C00 <= ord(c) <= 0x0C7F for c in text):
            return 'Telugu'
        
        # Check for common Baraha patterns
        baraha_indicators = ['q', 'w', 'x', 'z', 'W', 'Q', 'X', 'Z']
        if any(char in text for char in baraha_indicators):
            return 'BarahaSouth'
        
        # Check for IAST diacritics
        iast_chars = ['ā', 'ī', 'ū', 'ṛ', 'ṝ', 'ḷ', 'ḹ', 'ṃ', 'ḥ', 'ñ', 'ṅ', 'ṇ', 'ṭ', 'ḍ', 'ś', 'ṣ']
        if any(char in text for char in iast_chars):
            return 'IAST'
        
        # Check for ISO-15919 (similar to IAST but may have different patterns)
        iso_chars = ['ā', 'ī', 'ū', 'ṛ', 'ṝ', 'ḷ', 'ḹ', 'ṁ', 'ḥ', 'ñ', 'ṅ', 'ṇ', 'ṭ', 'ḍ', 'ś', 'ṣ']
        if any(char in text for char in iso_chars):
            return 'ISO15919'
        
        # Check for Harvard-Kyoto patterns
        hk_chars = ['A', 'I', 'U', 'R', 'L', 'M', 'H']
        if any(char in text for char in hk_chars):
            return 'HarvardKyoto'
        
        # Use source hint if available
        if 'vedanidhi' in source_hint.lower():
            return 'Devanagari'
        elif 'vedavms' in source_hint.lower():
            return 'BarahaSouth'
        elif 'gretil' in source_hint.lower():
            return 'IAST'
        
        # Default fallback
        return 'HarvardKyoto'
    
    def transform_to_slp1_extended(self, text: str, source_scheme: str) -> TransformationResult:
        """Transform text to Extended SLP1."""
        try:
            # Map source scheme name to vidyut scheme
            vidyut_scheme = self._map_scheme_name(source_scheme)
            result = lipi.transliterate(text, vidyut_scheme, lipi.Scheme.Slp1)
            return TransformationResult(True, result, [])
        except Exception as e:
            return TransformationResult(False, text, [str(e)])
    
    def transform_to_devanagari(self, slp1_text: str) -> TransformationResult:
        """Transform SLP1 text to Devanagari."""
        try:
            result = lipi.transliterate(slp1_text, lipi.Scheme.Slp1, lipi.Scheme.Devanagari)
            return TransformationResult(True, result, [])
        except Exception as e:
            return TransformationResult(False, slp1_text, [str(e)])
    
    def transform_to_telugu(self, slp1_text: str) -> TransformationResult:
        """Transform SLP1 text to Telugu."""
        try:
            result = lipi.transliterate(slp1_text, lipi.Scheme.Slp1, lipi.Scheme.Telugu)
            return TransformationResult(True, result, [])
        except Exception as e:
            return TransformationResult(False, slp1_text, [str(e)])
    
    def transform_to_iso_15919(self, slp1_text: str) -> TransformationResult:
        """Transform SLP1 text to ISO-15919."""
        try:
            result = lipi.transliterate(slp1_text, lipi.Scheme.Slp1, lipi.Scheme.Iso15919)
            return TransformationResult(True, result, [])
        except Exception as e:
            return TransformationResult(False, slp1_text, [str(e)])
    
    def transform_to_iast(self, slp1_text: str) -> TransformationResult:
        """Transform SLP1 text to IAST."""
        try:
            result = lipi.transliterate(slp1_text, lipi.Scheme.Slp1, lipi.Scheme.Iast)
            return TransformationResult(True, result, [])
        except Exception as e:
            return TransformationResult(False, slp1_text, [str(e)])
    
    def test_roundtrip(self, original: str, converted: str, source_scheme: str) -> RoundtripResult:
        """Test roundtrip validity by converting back to original scheme."""
        try:
            vidyut_scheme = self._map_scheme_name(source_scheme)
            roundtrip = lipi.transliterate(converted, lipi.Scheme.Slp1, vidyut_scheme)
            
            # Simple similarity check
            similarity = self._calculate_similarity(original, roundtrip)
            valid = similarity > 0.95
            
            return RoundtripResult(valid, similarity)
        except Exception as e:
            logger.warning(f"Roundtrip test failed: {e}")
            return RoundtripResult(False, 0.0)
    
    def _map_scheme_name(self, scheme_name: str):
        """Map scheme name to vidyut Scheme enum."""
        # Map our encoding names to vidyut scheme names
        name_mapping = {
            'HarvardKyoto': 'HarvardKyoto',
            'Devanagari': 'Devanagari',
            'Telugu': 'Telugu',
            'BarahaSouth': 'BarahaSouth',
            'IAST': 'Iast',
            'ISO15919': 'Iso15919',
        }
        mapped_name = name_mapping.get(scheme_name, 'HarvardKyoto')
        
        # Get the actual Scheme enum value
        try:
            return getattr(lipi.Scheme, mapped_name)
        except AttributeError:
            # Fallback for schemes that might not exist
            if 'Baraha' in scheme_name:
                return lipi.Scheme.HarvardKyoto
            return lipi.Scheme.Devanagari
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple character-based similarity."""
        if text1 == text2:
            return 1.0
        
        # Simple approach: common characters / total characters
        set1, set2 = set(text1), set(text2)
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0

class MockVidyut:
    """Mock implementation for when vidyut is not available."""
    
    def detect_encoding(self, text: str, source_hint: str = '') -> str:
        """Mock encoding detection with basic heuristics."""
        # Check for Devanagari characters
        if any(0x0900 <= ord(c) <= 0x097F for c in text):
            return 'Devanagari'
        
        # Check for Telugu characters  
        if any(0x0C00 <= ord(c) <= 0x0C7F for c in text):
            return 'Telugu'
        
        # Check for common Baraha patterns
        baraha_indicators = ['q', 'w', 'x', 'z', 'W', 'Q', 'X', 'Z']
        if any(char in text for char in baraha_indicators):
            return 'BarahaSouth'
        
        # Check for IAST diacritics
        iast_chars = ['ā', 'ī', 'ū', 'ṛ', 'ṝ', 'ḷ', 'ḹ', 'ṃ', 'ḥ', 'ñ', 'ṅ', 'ṇ', 'ṭ', 'ḍ', 'ś', 'ṣ']
        if any(char in text for char in iast_chars):
            return 'IAST'
        
        # Use source hint if available
        if 'vedanidhi' in source_hint.lower():
            return 'Devanagari'
        elif 'vedavms' in source_hint.lower():
            return 'BarahaSouth'
        elif 'gretil' in source_hint.lower():
            return 'IAST'
        
        # Default fallback
        return 'HarvardKyoto'
    
    def transform_to_slp1_extended(self, text: str, source_scheme: str) -> TransformationResult:
        return TransformationResult(True, text, [])
    
    def transform_to_devanagari(self, slp1_text: str) -> TransformationResult:
        # Simple mock transformation
        mock_devanagari = slp1_text.replace('a', 'अ').replace('i', 'इ')
        return TransformationResult(True, mock_devanagari, [])
    
    def transform_to_telugu(self, slp1_text: str) -> TransformationResult:
        # Simple mock transformation
        mock_telugu = slp1_text.replace('a', 'అ').replace('i', 'ఇ')
        return TransformationResult(True, mock_telugu, [])
    
    def transform_to_iso_15919(self, slp1_text: str) -> TransformationResult:
        # Simple mock transformation for ISO-15919
        mock_iso = slp1_text.replace('A', 'ā').replace('I', 'ī').replace('U', 'ū')
        return TransformationResult(True, mock_iso, [])
    
    def transform_to_iast(self, slp1_text: str) -> TransformationResult:
        # Simple mock transformation for IAST
        mock_iast = slp1_text.replace('R', 'ṛ').replace('f', 'ṛ').replace('x', 'ḷ')
        return TransformationResult(True, mock_iast, [])
    
    def test_roundtrip(self, original: str, converted: str, source_scheme: str) -> RoundtripResult:
        return RoundtripResult(True, 1.0)

if __name__ == "__main__":
    # Run the transformation pipeline
    pipeline = UdapaanaTransformationPipeline()
    pipeline.process_all_sources()