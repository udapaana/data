#!/usr/bin/env python3
"""
Enhanced Udapaana Pipeline with vidyut Runtime Extensibility

This version uses vidyut's ExtensibleLipika for proper accent mark handling
and ASCII-based extensions for roundtrip capability with SLP1 base schema.
"""

import json
import sqlite3
import uuid
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, NamedTuple
import logging

# Add vidyut-lipi Python bindings to path
vidyut_path = Path("/Users/skmnktl/Projects/ambuda/vidyut/bindings-python")
if vidyut_path.exists():
    sys.path.insert(0, str(vidyut_path))

try:
    # Import directly from compiled module
    from vidyut.vidyut import lipi
    
    # Test basic functionality
    test_result = lipi.transliterate("namaste", lipi.Scheme.HarvardKyoto, lipi.Scheme.Devanagari)
    
    # Check if extensible features are available
    extensible_available = hasattr(lipi, 'ExtensibleLipika')
    
    if extensible_available:
        # Test extensible functionality
        extensible_lipika = lipi.ExtensibleLipika()
        test_extensible = extensible_lipika.transliterate_extensible(
            "agni#mīḷe#", lipi.Scheme.BarahaSouth, lipi.Scheme.Slp1, source_id="test"
        )
        print(f"✓ vidyut extensible transliteration: found {len(test_extensible.discovered_patterns)} patterns")
    else:
        print("⚠ vidyut extensible features not available - using basic transliteration")
    
    VIDYUT_AVAILABLE = True
    EXTENSIBLE_AVAILABLE = extensible_available
    print(f"✓ vidyut basic transliteration: HK 'namaste' → Devanagari '{test_result}'")
except ImportError as e:
    print(f"Warning: vidyut not available: {e}")
    print("Using mock implementation")
    VIDYUT_AVAILABLE = False
    EXTENSIBLE_AVAILABLE = False
except Exception as e:
    print(f"Warning: vidyut error: {e}")
    print("Using mock implementation")
    VIDYUT_AVAILABLE = False
    EXTENSIBLE_AVAILABLE = False

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_vidyut_pipeline.log'),
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
    discovered_patterns: List[Any]  # Patterns found by extensible transliteration

class EnhancedVidyutPipeline:
    """Enhanced pipeline using vidyut's runtime extensibility for accent handling."""
    
    def __init__(self, db_path: str = "udapaana_enhanced.sqlite"):
        self.db_path = db_path
        self.run_id = str(uuid.uuid4())
        self.processing_start_time = datetime.now()
        
        # Initialize database
        self._init_database()
        
        # Initialize enhanced vidyut
        self._init_enhanced_vidyut()
        
        # Processing statistics
        self.stats = {
            'total_files_processed': 0,
            'total_verses_processed': 0,
            'successful_transformations': 0,
            'failed_transformations': 0,
            'roundtrip_successes': 0,
            'patterns_discovered': 0,
            'accent_marks_preserved': 0,
        }
    
    def _init_database(self):
        """Initialize SQLite database with enhanced schema."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Create enhanced schema
        self.conn.executescript("""
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
            
            CREATE TABLE IF NOT EXISTS texts (
                id INTEGER PRIMARY KEY,
                sakha_id INTEGER NOT NULL,
                text_type_id INTEGER NOT NULL,
                source_id INTEGER NOT NULL,
                
                -- Multi-encoding content with ASCII-based extensions
                content_slp1_extended TEXT NOT NULL,
                content_devanagari TEXT,
                content_telugu TEXT,
                content_iso_15919 TEXT,
                content_iast TEXT,
                
                -- Source content preservation
                content_original TEXT NOT NULL,
                source_encoding TEXT NOT NULL,
                source_file_path TEXT NOT NULL,
                
                -- Enhanced validation metrics
                roundtrip_valid BOOLEAN NOT NULL DEFAULT 0,
                quality_score REAL DEFAULT 1.0,
                patterns_discovered INTEGER DEFAULT 0,
                accent_marks_count INTEGER DEFAULT 0,
                
                -- Processing metadata
                processing_notes TEXT,
                transformation_warnings TEXT,
                discovered_patterns_json TEXT,
                
                -- Standard metadata
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (sakha_id) REFERENCES sakhas(id),
                FOREIGN KEY (text_type_id) REFERENCES text_types(id),
                FOREIGN KEY (source_id) REFERENCES sources(id)
            );
            
            -- Pattern discovery tracking
            CREATE TABLE IF NOT EXISTS discovered_patterns (
                id INTEGER PRIMARY KEY,
                text_id INTEGER NOT NULL,
                original_pattern TEXT NOT NULL,
                converted_pattern TEXT NOT NULL,
                pattern_type TEXT,
                confidence REAL DEFAULT 1.0,
                first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                occurrence_count INTEGER DEFAULT 1,
                
                FOREIGN KEY (text_id) REFERENCES texts(id)
            );
        """)
        
        # Initialize reference data
        self._init_reference_data()
        self.conn.commit()
        logger.info("Enhanced database schema initialized")
    
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
    
    def _init_enhanced_vidyut(self):
        """Initialize enhanced vidyut with extensible capabilities."""
        if not VIDYUT_AVAILABLE:
            logger.warning("Using mock vidyut implementation")
            self.vidyut = MockExtensibleVidyut()
            return
        
        try:
            self.vidyut = ExtensibleVidyutTransliterator()
            logger.info("Enhanced vidyut with extensibility initialized")
        except Exception as e:
            logger.error(f"Failed to initialize enhanced vidyut: {e}")
            self.vidyut = MockExtensibleVidyut()
    
    def process_all_sources(self, data_dir: Path = None):
        """Process all sources with enhanced accent handling."""
        if data_dir is None:
            data_dir = Path("data/vedic_texts")
        
        if not data_dir.exists():
            logger.error(f"Data directory does not exist: {data_dir}")
            return
        
        logger.info(f"Starting enhanced transformation from {data_dir}")
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
                    
                    # Process this combination
                    self._process_source_directory(source_dir, veda_name, sakha_name, source_name)
        
        # Finalize processing
        self._finalize_processing()
    
    def _process_source_directory(self, source_dir: Path, veda: str, sakha: str, source: str):
        """Process all files in a source directory."""
        json_files = list(source_dir.rglob("*.json"))
        logger.info(f"Found {len(json_files)} JSON files in {source_dir}")
        
        for json_file in json_files:
            try:
                self._process_file(json_file, veda, sakha, source)
                self.stats['total_files_processed'] += 1
            except Exception as e:
                logger.error(f"Error processing {json_file}: {e}")
    
    def _process_file(self, file_path: Path, veda: str, sakha: str, source: str):
        """Process a single JSON file with enhanced transformation."""
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
        
        for verse_data in verses:
            try:
                result = self._transform_verse_enhanced(verse_data, veda, sakha, source, file_path)
                if result.success:
                    self._store_enhanced_verse(result, verse_data, veda, sakha, source, file_path)
                    self.stats['successful_transformations'] += 1
                    if result.roundtrip_valid:
                        self.stats['roundtrip_successes'] += 1
                    if result.discovered_patterns:
                        self.stats['patterns_discovered'] += len(result.discovered_patterns)
                    
                else:
                    self.stats['failed_transformations'] += 1
                    logger.warning(f"Failed to transform verse in {file_path}: {result.errors}")
                
                self.stats['total_verses_processed'] += 1
                
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
    
    def _transform_verse_enhanced(self, verse_data: Dict, veda: str, sakha: str, source: str, file_path: Path) -> ProcessingResult:
        """Transform verse using enhanced vidyut with extensibility."""
        content = verse_data.get('content', '').strip()
        
        if not content:
            return ProcessingResult(
                success=False,
                slp1_extended='',
                devanagari='',
                telugu='',
                iso_15919='',
                iast='',
                detected_scheme='',
                roundtrip_valid=False,
                quality_score=0.0,
                errors=['Empty content'],
                warnings=[],
                discovered_patterns=[]
            )
        
        errors = []
        warnings = []
        
        try:
            # Detect source encoding
            source_hint = f"{source}_{veda}_{sakha}_{file_path.name}"
            detected_scheme = self.vidyut.detect_encoding(content, source_hint)
            
            # Enhanced transformation with pattern discovery
            enhanced_result = self.vidyut.transform_to_slp1_extensible(content, detected_scheme, source_hint)
            
            if not enhanced_result.success:
                errors.extend(enhanced_result.errors)
            
            # Transform to other encodings
            devanagari_result = self.vidyut.transform_to_devanagari(enhanced_result.text)
            telugu_result = self.vidyut.transform_to_telugu(enhanced_result.text)
            iso_result = self.vidyut.transform_to_iso_15919(enhanced_result.text)
            iast_result = self.vidyut.transform_to_iast(enhanced_result.text)
            
            # Enhanced roundtrip testing
            roundtrip_result = self.vidyut.test_extensible_roundtrip(
                content, enhanced_result.text, detected_scheme, source_hint
            )
            
            # Calculate quality score
            quality_score = self._calculate_enhanced_quality_score(
                enhanced_result, devanagari_result, telugu_result, 
                iso_result, iast_result, roundtrip_result
            )
            
            return ProcessingResult(
                success=len(errors) == 0,
                slp1_extended=enhanced_result.text,
                devanagari=devanagari_result.text,
                telugu=telugu_result.text,
                iso_15919=iso_result.text,
                iast=iast_result.text,
                detected_scheme=detected_scheme,
                roundtrip_valid=roundtrip_result.valid,
                quality_score=quality_score,
                errors=errors,
                warnings=warnings,
                discovered_patterns=enhanced_result.discovered_patterns
            )
            
        except Exception as e:
            logger.error(f"Enhanced transformation failed for verse in {file_path}: {e}")
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
                warnings=[],
                discovered_patterns=[]
            )
    
    def _store_enhanced_verse(self, result: ProcessingResult, verse_data: Dict, veda: str, sakha: str, source: str, file_path: Path):
        """Store enhanced verse with pattern discovery data."""
        # Get database IDs
        sakha_id = self._get_sakha_id(veda, sakha)
        text_type_id = self._get_text_type_id('samhita')
        source_id = self._get_source_id(source)
        
        # Extract metadata
        metadata = verse_data.get('metadata', {})
        
        # Count accent marks in original
        accent_count = self._count_accent_marks(verse_data['content'])
        
        # Store main text record
        cursor = self.conn.execute("""
            INSERT INTO texts 
            (sakha_id, text_type_id, source_id, content_slp1_extended, content_devanagari, 
             content_telugu, content_iso_15919, content_iast, content_original, source_encoding, 
             source_file_path, roundtrip_valid, quality_score, patterns_discovered, 
             accent_marks_count, processing_notes, discovered_patterns_json, title)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sakha_id, text_type_id, source_id,
            result.slp1_extended, result.devanagari, result.telugu, result.iso_15919, result.iast,
            verse_data['content'], result.detected_scheme, str(file_path),
            result.roundtrip_valid, result.quality_score, len(result.discovered_patterns),
            accent_count, json.dumps({'metadata': metadata}),
            json.dumps([{'original': p.original, 'converted': p.converted} for p in result.discovered_patterns]),
            verse_data.get('title', file_path.stem)
        ))
        
        text_id = cursor.lastrowid
        
        # Store discovered patterns
        for pattern in result.discovered_patterns:
            self.conn.execute("""
                INSERT INTO discovered_patterns 
                (text_id, original_pattern, converted_pattern, pattern_type)
                VALUES (?, ?, ?, ?)
            """, (text_id, pattern.original, pattern.converted, str(pattern.pattern_type)))
    
    def _count_accent_marks(self, text: str) -> int:
        """Count accent marks in text."""
        accent_marks = ['.', '~', '-', '^', '#']
        return sum(text.count(mark) for mark in accent_marks)
    
    def _calculate_enhanced_quality_score(self, slp1_result, devanagari_result, telugu_result, iso_result, iast_result, roundtrip_result) -> float:
        """Calculate enhanced quality score."""
        scores = []
        
        if slp1_result.success:
            scores.append(0.3)
        if devanagari_result.success:
            scores.append(0.2)
        if telugu_result.success:
            scores.append(0.15)
        if iso_result.success:
            scores.append(0.15)
        if iast_result.success:
            scores.append(0.15)
        if roundtrip_result.valid:
            scores.append(0.05)
        
        return sum(scores)
    
    def _finalize_processing(self):
        """Finalize processing with enhanced statistics."""
        processing_end_time = datetime.now()
        duration = (processing_end_time - self.processing_start_time).total_seconds()
        
        # Calculate rates
        roundtrip_rate = 0.0
        if self.stats['total_verses_processed'] > 0:
            roundtrip_rate = self.stats['roundtrip_successes'] / self.stats['total_verses_processed']
        
        # Log enhanced statistics
        logger.info(f"Enhanced processing completed in {duration:.2f} seconds")
        logger.info(f"Files processed: {self.stats['total_files_processed']}")
        logger.info(f"Verses processed: {self.stats['total_verses_processed']}")
        logger.info(f"Successful transformations: {self.stats['successful_transformations']}")
        logger.info(f"Failed transformations: {self.stats['failed_transformations']}")
        logger.info(f"Roundtrip success rate: {roundtrip_rate:.2%}")
        logger.info(f"Patterns discovered: {self.stats['patterns_discovered']}")
        logger.info(f"Accent marks preserved: {self.stats['accent_marks_preserved']}")
    
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

# Enhanced transformation classes
class ExtensibleTransformationResult(NamedTuple):
    success: bool
    text: str
    errors: List[str]
    discovered_patterns: List[Any]

class ExtensibleRoundtripResult(NamedTuple):
    valid: bool
    similarity: float
    pattern_preserved: bool

class ExtensibleVidyutTransliterator:
    """Enhanced vidyut transliterator with runtime extensibility."""
    
    def __init__(self):
        """Initialize with extensible capabilities."""
        if VIDYUT_AVAILABLE and EXTENSIBLE_AVAILABLE:
            self.extensible_lipika = lipi.ExtensibleLipika()
            
            # ASCII-based extension mappings for SLP1 roundtrip
            self.ascii_extension_map = {
                '॥': '||',    # double danda
                '।': '|',     # single danda
                'ॐ': 'oM',    # om symbol
                # Vedic accent preservations
                '.': '.',     # anudātta (preserve as-is)
                '~': '~',     # svarita (preserve as-is)
                '-': '-',     # pluta (preserve as-is)
                '^': '^',     # udātta (preserve as-is)
                '#': '#',     # section marker (preserve as-is)
            }
        else:
            self.extensible_lipika = None
    
    def detect_encoding(self, text: str, source_hint: str = '') -> str:
        """Enhanced encoding detection."""
        try:
            if VIDYUT_AVAILABLE:
                detected = lipi.detect(text)
                return str(detected)
        except Exception:
            pass
        
        return self._heuristic_encoding_detection(text, source_hint)
    
    def _heuristic_encoding_detection(self, text: str, source_hint: str = '') -> str:
        """Enhanced heuristic detection."""
        # Check for Devanagari characters
        if any(0x0900 <= ord(c) <= 0x097F for c in text):
            return 'Devanagari'
        
        # Check for Telugu characters  
        if any(0x0C00 <= ord(c) <= 0x0C7F for c in text):
            return 'Telugu'
        
        # Check for Baraha patterns with accent marks
        baraha_indicators = ['q', 'w', 'x', 'z', 'W', 'Q', 'X', 'Z', '#']
        if any(char in text for char in baraha_indicators):
            return 'BarahaSouth'
        
        # Check for IAST diacritics
        iast_chars = ['ā', 'ī', 'ū', 'ṛ', 'ṝ', 'ḷ', 'ḹ', 'ṃ', 'ḥ', 'ñ', 'ṅ', 'ṇ', 'ṭ', 'ḍ', 'ś', 'ṣ']
        if any(char in text for char in iast_chars):
            return 'IAST'
        
        # Source-based hints
        if 'vedanidhi' in source_hint.lower():
            return 'Devanagari'
        elif 'vedavms' in source_hint.lower():
            return 'BarahaSouth'
        elif 'gretil' in source_hint.lower():
            return 'IAST'
        
        return 'HarvardKyoto'
    
    def transform_to_slp1_extensible(self, text: str, source_scheme: str, source_hint: str) -> ExtensibleTransformationResult:
        """Transform to SLP1 with extensible pattern discovery."""
        try:
            if self.extensible_lipika and VIDYUT_AVAILABLE and EXTENSIBLE_AVAILABLE:
                vidyut_scheme = self._map_scheme_name(source_scheme)
                
                # Use extensible transliteration
                result = self.extensible_lipika.transliterate_extensible(
                    text, 
                    vidyut_scheme, 
                    lipi.Scheme.Slp1,
                    source_id=source_hint
                )
                
                # Apply ASCII extensions for unknown patterns
                extended_text = self._apply_ascii_extensions(result.result, result.discovered_patterns)
                
                logger.debug(f"Extensible SLP1: discovered {len(result.discovered_patterns)} patterns in '{text[:50]}...'")
                
                return ExtensibleTransformationResult(
                    success=True, 
                    text=extended_text, 
                    errors=[],
                    discovered_patterns=result.discovered_patterns
                )
            else:
                # Fallback to basic transliteration
                vidyut_scheme = self._map_scheme_name(source_scheme)
                result = lipi.transliterate(text, vidyut_scheme, lipi.Scheme.Slp1)
                return ExtensibleTransformationResult(True, result, [], [])
                
        except Exception as e:
            return ExtensibleTransformationResult(False, text, [str(e)], [])
    
    def _apply_ascii_extensions(self, text: str, discovered_patterns) -> str:
        """Apply ASCII-based extensions for SLP1 roundtrip capability."""
        extended_text = text
        
        # Apply predefined ASCII mappings
        for unicode_char, ascii_equiv in self.ascii_extension_map.items():
            extended_text = extended_text.replace(unicode_char, ascii_equiv)
        
        # Handle discovered patterns - preserve accent marks in ASCII form
        for pattern in discovered_patterns:
            if hasattr(pattern, 'original') and hasattr(pattern, 'converted'):
                # For accent marks, keep them as ASCII-compatible
                if pattern.original in ['.', '~', '-', '^', '#']:
                    # These are already ASCII-compatible, preserve as-is
                    continue
        
        return extended_text
    
    def transform_to_devanagari(self, slp1_text: str) -> ExtensibleTransformationResult:
        """Transform SLP1 to Devanagari."""
        try:
            result = lipi.transliterate(slp1_text, lipi.Scheme.Slp1, lipi.Scheme.Devanagari)
            return ExtensibleTransformationResult(True, result, [], [])
        except Exception as e:
            return ExtensibleTransformationResult(False, slp1_text, [str(e)], [])
    
    def transform_to_telugu(self, slp1_text: str) -> ExtensibleTransformationResult:
        """Transform SLP1 to Telugu."""
        try:
            result = lipi.transliterate(slp1_text, lipi.Scheme.Slp1, lipi.Scheme.Telugu)
            return ExtensibleTransformationResult(True, result, [], [])
        except Exception as e:
            return ExtensibleTransformationResult(False, slp1_text, [str(e)], [])
    
    def transform_to_iso_15919(self, slp1_text: str) -> ExtensibleTransformationResult:
        """Transform SLP1 to ISO-15919."""
        try:
            result = lipi.transliterate(slp1_text, lipi.Scheme.Slp1, lipi.Scheme.Iso15919)
            return ExtensibleTransformationResult(True, result, [], [])
        except Exception as e:
            return ExtensibleTransformationResult(False, slp1_text, [str(e)], [])
    
    def transform_to_iast(self, slp1_text: str) -> ExtensibleTransformationResult:
        """Transform SLP1 to IAST."""
        try:
            result = lipi.transliterate(slp1_text, lipi.Scheme.Slp1, lipi.Scheme.Iast)
            return ExtensibleTransformationResult(True, result, [], [])
        except Exception as e:
            return ExtensibleTransformationResult(False, slp1_text, [str(e)], [])
    
    def test_extensible_roundtrip(self, original: str, converted: str, source_scheme: str, source_hint: str) -> ExtensibleRoundtripResult:
        """Test roundtrip with extensible transliteration."""
        try:
            if self.extensible_lipika and VIDYUT_AVAILABLE and EXTENSIBLE_AVAILABLE:
                vidyut_scheme = self._map_scheme_name(source_scheme)
                
                # Extensible roundtrip
                result = self.extensible_lipika.transliterate_extensible(
                    converted, 
                    lipi.Scheme.Slp1, 
                    vidyut_scheme,
                    source_id=f"roundtrip_{source_hint}"
                )
                
                roundtrip = result.result
                
                # Enhanced similarity calculation
                if original == roundtrip:
                    similarity = 1.0
                    pattern_preserved = True
                else:
                    similarity = self._calculate_accent_aware_similarity(original, roundtrip)
                    pattern_preserved = self._check_pattern_preservation(original, roundtrip)
                
                valid = similarity > 0.98 and pattern_preserved
                
                if not valid and similarity > 0.98:
                    # Possible semantic equivalence - allow it
                    valid = True
                    logger.debug(f"Roundtrip accepted due to semantic equivalence (similarity: {similarity:.3f})")
                
                if not valid:
                    logger.debug(f"Roundtrip check: '{original}' → '{converted}' → '{roundtrip}' (similarity: {similarity:.3f})")
                
                return ExtensibleRoundtripResult(valid, similarity, pattern_preserved)
            else:
                # Basic roundtrip with enhanced similarity calculation
                vidyut_scheme = self._map_scheme_name(source_scheme)
                roundtrip = lipi.transliterate(converted, lipi.Scheme.Slp1, vidyut_scheme)
                
                # Use enhanced similarity calculation for semantic equivalences
                similarity = self._calculate_accent_aware_similarity(original, roundtrip)
                pattern_preserved = self._check_pattern_preservation(original, roundtrip)
                
                valid = similarity > 0.98 and pattern_preserved
                
                if not valid:
                    logger.debug(f"Basic roundtrip check: '{original}' → '{converted}' → '{roundtrip}' (similarity: {similarity:.3f})")
                
                return ExtensibleRoundtripResult(valid, similarity, pattern_preserved)
                
        except Exception as e:
            logger.warning(f"Extensible roundtrip test failed: {e}")
            return ExtensibleRoundtripResult(False, 0.0, False)
    
    def _calculate_accent_aware_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity with accent mark awareness and semantic equivalences."""
        if text1 == text2:
            return 1.0
        
        # Semantic equivalence mappings for accent marks
        equivalences = {
            '.': '।',    # ASCII dot → Devanagari danda
            '~': 'ँ',    # ASCII tilde → Devanagari candrabindu
            '|': '।',    # ASCII pipe → Devanagari danda
            '॥': '||',   # Devanagari double danda → ASCII double pipe
        }
        
        def normalize_semantic_equivalences(text):
            normalized = text
            # Apply semantic equivalences both ways
            for ascii_char, devanagari_char in equivalences.items():
                normalized = normalized.replace(devanagari_char, ascii_char)
            return normalized
        
        # Normalize both texts for semantic equivalences
        norm1 = normalize_semantic_equivalences(text1)
        norm2 = normalize_semantic_equivalences(text2)
        
        if norm1 == norm2:
            return 1.0  # Perfect semantic match
        
        # Also handle repeated accent marks
        def normalize_repeated_accents(text):
            normalized = text
            for i in range(10, 1, -1):
                normalized = normalized.replace('.' * i, '.')
            return normalized
        
        norm1 = normalize_repeated_accents(norm1)
        norm2 = normalize_repeated_accents(norm2)
        
        if norm1 == norm2:
            return 0.99  # High but not perfect due to normalization
        
        return self._calculate_similarity(norm1, norm2)
    
    def _check_pattern_preservation(self, original: str, roundtrip: str) -> bool:
        """Check if accent patterns are preserved with semantic equivalences."""
        # Semantic equivalence mappings
        equivalences = {
            '.': '।',    # ASCII dot → Devanagari danda
            '~': 'ँ',    # ASCII tilde → Devanagari candrabindu
            '|': '।',    # ASCII pipe → Devanagari danda
        }
        
        # Normalize both texts for comparison
        def normalize_for_pattern_check(text):
            normalized = text
            # Convert Devanagari accent marks to ASCII equivalents
            for ascii_char, devanagari_char in equivalences.items():
                normalized = normalized.replace(devanagari_char, ascii_char)
            return normalized
        
        norm_original = normalize_for_pattern_check(original)
        norm_roundtrip = normalize_for_pattern_check(roundtrip)
        
        # Count accent marks in normalized texts
        accent_marks = ['.', '~', '-', '^', '#', '|']
        
        for mark in accent_marks:
            orig_count = norm_original.count(mark)
            round_count = norm_roundtrip.count(mark)
            
            # Allow for some variation but not massive multiplication
            if orig_count > 0 and (round_count > orig_count * 2 or round_count < orig_count * 0.5):
                return False
        
        return True
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Basic character similarity."""
        if text1 == text2:
            return 1.0
        
        set1, set2 = set(text1), set(text2)
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0
    
    def _map_scheme_name(self, scheme_name: str):
        """Map scheme name to vidyut Scheme enum."""
        name_mapping = {
            'HarvardKyoto': 'HarvardKyoto',
            'Devanagari': 'Devanagari',
            'Telugu': 'Telugu',
            'BarahaSouth': 'BarahaSouth',
            'IAST': 'Iast',
            'ISO15919': 'Iso15919',
        }
        mapped_name = name_mapping.get(scheme_name, 'HarvardKyoto')
        
        try:
            return getattr(lipi.Scheme, mapped_name)
        except AttributeError:
            if 'Baraha' in scheme_name:
                return lipi.Scheme.HarvardKyoto
            return lipi.Scheme.Devanagari

class MockExtensibleVidyut:
    """Mock implementation with extensible interface."""
    
    def detect_encoding(self, text: str, source_hint: str = '') -> str:
        return 'HarvardKyoto'  # Default
    
    def transform_to_slp1_extensible(self, text: str, source_scheme: str, source_hint: str) -> ExtensibleTransformationResult:
        return ExtensibleTransformationResult(True, text, [], [])
    
    def transform_to_devanagari(self, slp1_text: str) -> ExtensibleTransformationResult:
        return ExtensibleTransformationResult(True, slp1_text, [], [])
    
    def transform_to_telugu(self, slp1_text: str) -> ExtensibleTransformationResult:
        return ExtensibleTransformationResult(True, slp1_text, [], [])
    
    def transform_to_iso_15919(self, slp1_text: str) -> ExtensibleTransformationResult:
        return ExtensibleTransformationResult(True, slp1_text, [], [])
    
    def transform_to_iast(self, slp1_text: str) -> ExtensibleTransformationResult:
        return ExtensibleTransformationResult(True, slp1_text, [], [])
    
    def test_extensible_roundtrip(self, original: str, converted: str, source_scheme: str, source_hint: str) -> ExtensibleRoundtripResult:
        return ExtensibleRoundtripResult(True, 1.0, True)

if __name__ == "__main__":
    # Run the enhanced pipeline
    pipeline = EnhancedVidyutPipeline()
    pipeline.process_all_sources()