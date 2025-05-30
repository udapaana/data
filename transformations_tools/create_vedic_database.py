#!/usr/bin/env python3

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import re

class VedicDatabaseBuilder:
    """Build SQLite database with UVTS-encoded Vedic texts"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Connect to SQLite database"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        # Enable foreign keys
        self.cursor.execute("PRAGMA foreign_keys = ON")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def create_schema(self):
        """Create database schema for Vedic texts"""
        
        # Main texts table with UVTS encoding
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS vedic_texts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            -- Text identification
            text_id TEXT UNIQUE NOT NULL,  -- e.g., "TS.1.1.1.1"
            sakha TEXT NOT NULL,            -- e.g., "taittiriya"
            veda TEXT NOT NULL,             -- e.g., "yajurveda"
            text_type TEXT NOT NULL,        -- samhita, brahmana, aranyaka, upanishad
            
            -- Regional and manuscript info
            regional_variant TEXT,          -- andhra, dravida, etc.
            manuscript_tradition TEXT,      -- ms:poona, ms:mysore, etc.
            patha_type TEXT NOT NULL,       -- samhita, pada, krama, ghana
            
            -- Hierarchical location
            hierarchy_json TEXT NOT NULL,   -- Full hierarchy as JSON
            kanda INTEGER,
            prapathaka INTEGER,
            anuvaka INTEGER,
            verse_number INTEGER,
            
            -- UVTS encoded text
            uvts_text TEXT NOT NULL,        -- The actual text in UVTS format
            
            -- Accent information
            accent_count INTEGER,
            udatta_count INTEGER,
            anudatta_count INTEGER,
            svarita_count INTEGER,
            accent_density REAL,            -- Accents per 100 characters
            
            -- Source tracking
            source_file TEXT NOT NULL,
            source_type TEXT,               -- vedavms, vedanidhi, etc.
            
            -- Quality metrics
            quality_score REAL,
            conversion_confidence REAL,
            validation_errors TEXT,         -- JSON array of errors
            
            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- Indexes for efficient querying
            CHECK (text_type IN ('samhita', 'brahmana', 'aranyaka', 'upanishad')),
            CHECK (patha_type IN ('samhita', 'pada', 'krama', 'jata', 'ghana'))
        )""")
        
        # Create indexes for performance
        self.cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sakha_hierarchy 
        ON vedic_texts(sakha, kanda, prapathaka, anuvaka, verse_number)
        """)
        
        self.cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_veda_text_type 
        ON vedic_texts(veda, text_type)
        """)
        
        self.cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_regional_variant 
        ON vedic_texts(regional_variant)
        """)
        
        self.cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_quality_score 
        ON vedic_texts(quality_score DESC)
        """)
        
        # Accent patterns table for analysis
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS accent_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text_id TEXT NOT NULL,
            pattern_type TEXT NOT NULL,     -- udatta_sequence, anudatta_sequence, etc.
            pattern TEXT NOT NULL,          -- The actual pattern
            occurrences INTEGER,
            positions TEXT,                 -- JSON array of positions
            
            FOREIGN KEY (text_id) REFERENCES vedic_texts(text_id)
        )""")
        
        # Cross-references table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS cross_references (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_text_id TEXT NOT NULL,
            target_text_id TEXT NOT NULL,
            reference_type TEXT,            -- parallel, variant, commentary
            notes TEXT,
            
            FOREIGN KEY (source_text_id) REFERENCES vedic_texts(text_id),
            FOREIGN KEY (target_text_id) REFERENCES vedic_texts(text_id)
        )""")
        
        # Metadata table for tracking data provenance
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        # Full-text search virtual table
        self.cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS vedic_texts_fts USING fts5(
            text_id,
            uvts_text,
            content=vedic_texts,
            content_rowid=id
        )""")
        
        # Trigger to keep FTS in sync
        self.cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS vedic_texts_fts_insert 
        AFTER INSERT ON vedic_texts BEGIN
            INSERT INTO vedic_texts_fts(rowid, text_id, uvts_text) 
            VALUES (new.id, new.text_id, new.uvts_text);
        END
        """)
        
        self.cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS vedic_texts_fts_update 
        AFTER UPDATE ON vedic_texts BEGIN
            UPDATE vedic_texts_fts 
            SET text_id = new.text_id, uvts_text = new.uvts_text 
            WHERE rowid = old.id;
        END
        """)
        
        self.cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS vedic_texts_fts_delete 
        AFTER DELETE ON vedic_texts BEGIN
            DELETE FROM vedic_texts_fts WHERE rowid = old.id;
        END
        """)
        
        self.conn.commit()
    
    def generate_text_id(self, sakha: str, hierarchy: Dict) -> str:
        """Generate unique text ID from hierarchy"""
        # Map śākhā to abbreviation
        sakha_abbrev = {
            'taittiriya': 'TS',
            'sakala': 'RV',
            'kauthuma': 'SV',
            'madhyandina': 'VS',
            'kanva': 'VSK',
            'jaiminiya': 'SVJ',
            'ranayaniya': 'SVR',
            'saunaka': 'AV',
            'paippalada': 'AVP'
        }.get(sakha, sakha.upper()[:3])
        
        # Build hierarchical ID
        parts = [sakha_abbrev]
        
        # Add hierarchy levels
        for level in ['kanda', 'prapathaka', 'anuvaka', 'verse', 'section']:
            if level in hierarchy and hierarchy[level] is not None:
                parts.append(str(hierarchy[level]))
        
        return '.'.join(parts)
    
    def detect_veda(self, sakha: str) -> str:
        """Detect which Veda a śākhā belongs to"""
        veda_mapping = {
            # Rigveda
            'sakala': 'rigveda',
            'baskala': 'rigveda',
            
            # Yajurveda
            'taittiriya': 'yajurveda',
            'maitrayani': 'yajurveda',
            'katha': 'yajurveda',
            'kapishthala': 'yajurveda',
            'madhyandina': 'yajurveda',
            'kanva': 'yajurveda',
            
            # Samaveda
            'kauthuma': 'samaveda',
            'ranayaniya': 'samaveda',
            'jaiminiya': 'samaveda',
            
            # Atharvaveda
            'saunaka': 'atharvaveda',
            'paippalada': 'atharvaveda'
        }
        
        return veda_mapping.get(sakha, 'unknown')
    
    def insert_text(self, stage3_data: Dict) -> Optional[int]:
        """Insert a text entry from Stage 3 output"""
        try:
            # Extract data
            text_id = self.generate_text_id(stage3_data['sakha'], stage3_data['hierarchy'])
            
            # Prepare validation errors as JSON
            validation_errors = json.dumps(stage3_data.get('validation_errors', []))
            
            # Extract hierarchy numbers
            hierarchy = stage3_data['hierarchy']
            kanda = hierarchy.get('kanda')
            prapathaka = hierarchy.get('prapathaka')
            anuvaka = hierarchy.get('anuvaka')
            verse_number = hierarchy.get('verse')
            
            # Insert into database
            self.cursor.execute("""
            INSERT INTO vedic_texts (
                text_id, sakha, veda, text_type,
                regional_variant, manuscript_tradition, patha_type,
                hierarchy_json, kanda, prapathaka, anuvaka, verse_number,
                uvts_text,
                accent_count, udatta_count, anudatta_count, svarita_count, accent_density,
                source_file, source_type,
                quality_score, conversion_confidence, validation_errors
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                text_id,
                stage3_data['sakha'],
                self.detect_veda(stage3_data['sakha']),
                stage3_data['text_type'],
                stage3_data.get('regional_variant'),
                stage3_data.get('manuscript_tradition'),
                stage3_data['patha_type'],
                json.dumps(hierarchy),
                kanda, prapathaka, anuvaka, verse_number,
                stage3_data['uvts_text'],
                stage3_data['accents_converted'],
                stage3_data['uvts_udatta_count'],
                stage3_data['uvts_anudatta_count'],
                stage3_data['uvts_svarita_count'],
                stage3_data['accent_density'],
                stage3_data['source_id'],
                'vedavms',  # Assuming VedaVMS for now
                stage3_data['quality_score'],
                stage3_data['conversion_confidence'],
                validation_errors
            ))
            
            return self.cursor.lastrowid
            
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                print(f"  ⚠ Text already exists: {text_id}")
            else:
                print(f"  ✗ Database error: {e}")
            return None
        except Exception as e:
            print(f"  ✗ Error inserting text: {e}")
            return None
    
    def insert_accent_patterns(self, text_id: str, accent_positions: List[Dict]):
        """Insert accent pattern analysis"""
        # Group accents by type
        patterns = {}
        for accent in accent_positions:
            accent_type = accent['accent_type']
            if accent_type not in patterns:
                patterns[accent_type] = []
            patterns[accent_type].append(accent['position'])
        
        # Insert pattern summaries
        for pattern_type, positions in patterns.items():
            self.cursor.execute("""
            INSERT INTO accent_patterns (text_id, pattern_type, pattern, occurrences, positions)
            VALUES (?, ?, ?, ?, ?)
            """, (
                text_id,
                pattern_type,
                f"{pattern_type}_pattern",
                len(positions),
                json.dumps(positions[:10])  # Store first 10 positions as sample
            ))
    
    def process_stage3_files(self, stage3_dir: Path) -> Dict[str, int]:
        """Process all Stage 3 output files"""
        stage3_files = list(stage3_dir.glob("*.json"))
        
        if not stage3_files:
            print(f"No Stage 3 files found in {stage3_dir}")
            return {"processed": 0, "failed": 0}
        
        processed = 0
        failed = 0
        
        print(f"\nProcessing {len(stage3_files)} Stage 3 files into database...")
        
        for stage3_file in stage3_files:
            print(f"Processing: {stage3_file.name}")
            
            try:
                with open(stage3_file, 'r', encoding='utf-8') as f:
                    stage3_data = json.load(f)
                
                # Insert into database
                row_id = self.insert_text(stage3_data)
                
                if row_id:
                    # Also insert accent patterns
                    text_id = self.generate_text_id(
                        stage3_data['sakha'], 
                        stage3_data['hierarchy']
                    )
                    if stage3_data.get('accent_positions'):
                        self.insert_accent_patterns(text_id, stage3_data['accent_positions'])
                    
                    processed += 1
                    print(f"  ✓ Inserted as: {text_id}")
                else:
                    failed += 1
                    
            except Exception as e:
                print(f"  ✗ Failed to process: {e}")
                failed += 1
        
        self.conn.commit()
        return {"processed": processed, "failed": failed}
    
    def add_metadata(self):
        """Add metadata about the database"""
        metadata = {
            'uvts_version': '1.0',
            'created_date': datetime.now().isoformat(),
            'total_texts': self.cursor.execute("SELECT COUNT(*) FROM vedic_texts").fetchone()[0],
            'sakhas_included': json.dumps(
                [row[0] for row in self.cursor.execute("SELECT DISTINCT sakha FROM vedic_texts").fetchall()]
            ),
            'average_quality_score': self.cursor.execute(
                "SELECT AVG(quality_score) FROM vedic_texts"
            ).fetchone()[0] or 0,
            'texts_with_accents': self.cursor.execute(
                "SELECT COUNT(*) FROM vedic_texts WHERE accent_count > 0"
            ).fetchone()[0]
        }
        
        for key, value in metadata.items():
            self.cursor.execute("""
            INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)
            """, (key, str(value)))
        
        self.conn.commit()
    
    def create_summary_views(self):
        """Create useful summary views"""
        
        # Śākhā summary view
        self.cursor.execute("""
        CREATE VIEW IF NOT EXISTS sakha_summary AS
        SELECT 
            sakha,
            veda,
            COUNT(*) as total_texts,
            COUNT(DISTINCT text_type) as text_types,
            AVG(quality_score) as avg_quality,
            AVG(accent_density) as avg_accent_density,
            COUNT(DISTINCT regional_variant) as regional_variants
        FROM vedic_texts
        GROUP BY sakha, veda
        """)
        
        # High quality texts view
        self.cursor.execute("""
        CREATE VIEW IF NOT EXISTS high_quality_texts AS
        SELECT * FROM vedic_texts
        WHERE quality_score >= 80
        AND conversion_confidence >= 90
        AND accent_count > 0
        ORDER BY quality_score DESC
        """)
        
        self.conn.commit()

def main():
    """Build the Vedic SQLite database"""
    base_dir = Path(__file__).parent.parent
    
    # Setup paths
    stage3_dir = base_dir / "transformations" / "stage_03_accent_standardization"
    db_path = base_dir / "vedic_corpus_uvts.sqlite"
    
    # Remove existing database if exists
    if db_path.exists():
        print(f"Removing existing database: {db_path}")
        db_path.unlink()
    
    # Create database builder
    builder = VedicDatabaseBuilder(db_path)
    
    print("=" * 60)
    print("CREATING VEDIC CORPUS DATABASE (UVTS)")
    print("=" * 60)
    
    try:
        # Connect and create schema
        builder.connect()
        print("\nCreating database schema...")
        builder.create_schema()
        print("✓ Schema created")
        
        # Process Stage 3 files
        results = builder.process_stage3_files(stage3_dir)
        
        # Add metadata
        print("\nAdding metadata...")
        builder.add_metadata()
        print("✓ Metadata added")
        
        # Create views
        print("\nCreating summary views...")
        builder.create_summary_views()
        print("✓ Views created")
        
        # Print summary
        print("\n" + "=" * 60)
        print("DATABASE CREATION COMPLETE")
        print("=" * 60)
        print(f"Database: {db_path}")
        print(f"Size: {db_path.stat().st_size / 1024 / 1024:.2f} MB")
        print(f"Texts processed: {results['processed']}")
        print(f"Texts failed: {results['failed']}")
        
        # Show sample queries
        print("\nSample queries you can run:")
        print("- SELECT * FROM vedic_texts WHERE sakha = 'taittiriya' LIMIT 5;")
        print("- SELECT * FROM sakha_summary;")
        print("- SELECT * FROM high_quality_texts LIMIT 10;")
        print("- SELECT * FROM vedic_texts_fts WHERE uvts_text MATCH 'agni*';")
        
    finally:
        builder.close()

if __name__ == "__main__":
    main()