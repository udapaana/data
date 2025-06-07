-- Udapaana Vedic Corpus Database Schema
-- Base storage in SLP1 with multi-source support for cross-comparisons

-- Core hierarchical structure based on traditional sakha organization
CREATE TABLE vedas (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE, -- 'rigveda', 'samaveda', 'yajurveda', 'atharvaveda'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sakhas (
    id INTEGER PRIMARY KEY,
    veda_id INTEGER NOT NULL,
    name TEXT NOT NULL, -- 'shakala', 'kauthuma', 'taittiriya', 'shaunaka'
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (veda_id) REFERENCES vedas(id),
    UNIQUE(veda_id, name)
);

CREATE TABLE text_types (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE, -- 'samhita', 'brahmana', 'aranyaka', 'upanishad'
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data sources for provenance and comparison
CREATE TABLE sources (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE, -- 'vedanidhi', 'vedavms', 'gretil', etc.
    description TEXT,
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Core text storage - organized by sakha hierarchy 
CREATE TABLE texts (
    id INTEGER PRIMARY KEY,
    sakha_id INTEGER NOT NULL,
    text_type_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    
    -- Traditional hierarchical identifiers (vary by veda/sakha)
    kanda INTEGER,          -- For Samaveda, Yajurveda, Atharvaveda
    ashtaka INTEGER,        -- For Rigveda
    adhyaya INTEGER,        -- Chapter/section
    prapathaka INTEGER,     -- Sub-section
    anuvaka INTEGER,        -- Sub-sub-section
    sukta INTEGER,          -- Hymn (mainly Rigveda)
    mantra INTEGER,         -- Verse number within sukta/section
    pada TEXT,              -- Pada identifier (a, b, c, d, etc.)
    
    -- Text content in SLP1 (our base storage format)
    content_slp1 TEXT NOT NULL,
    
    -- Source encoding and original content for reference
    source_encoding TEXT NOT NULL, -- 'baraha', 'devanagari', 'iast', etc.
    content_original TEXT NOT NULL,
    
    -- Metadata
    title TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (sakha_id) REFERENCES sakhas(id),
    FOREIGN KEY (text_type_id) REFERENCES text_types(id),
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

-- Index for efficient lookups and comparisons
CREATE INDEX idx_texts_hierarchy ON texts(sakha_id, text_type_id, kanda, ashtaka, adhyaya, sukta, mantra);
CREATE INDEX idx_texts_source ON texts(source_id);

-- Indexes for encoding metadata table
CREATE INDEX idx_encoding_source_encoding ON text_encoding_metadata(source_encoding_final);
CREATE INDEX idx_encoding_sakha_type ON text_encoding_metadata(veda, sakha, text_type);
CREATE INDEX idx_encoding_quality ON text_encoding_metadata(conversion_lossless, quality_score);
CREATE INDEX idx_encoding_timestamp ON text_encoding_metadata(conversion_timestamp);
CREATE INDEX idx_encoding_method ON text_encoding_metadata(conversion_method);

-- Cross-references between texts (parallel verses, citations, etc.)
CREATE TABLE text_relations (
    id INTEGER PRIMARY KEY,
    source_text_id INTEGER NOT NULL,
    target_text_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL, -- 'parallel', 'citation', 'variant', 'commentary'
    confidence REAL DEFAULT 1.0, -- 0.0 to 1.0
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (source_text_id) REFERENCES texts(id),
    FOREIGN KEY (target_text_id) REFERENCES texts(id),
    UNIQUE(source_text_id, target_text_id, relation_type)
);

-- Data provenance tracking for each transformation stage
CREATE TABLE processing_log (
    id INTEGER PRIMARY KEY,
    text_id INTEGER NOT NULL,
    stage TEXT NOT NULL, -- 'extraction', 'normalization', 'encoding_conversion', 'structure_mapping'
    input_checksum TEXT,
    output_checksum TEXT,
    parameters TEXT, -- JSON of processing parameters
    errors TEXT,
    warnings TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (text_id) REFERENCES texts(id)
);

-- Comprehensive encoding metadata and format tracking
CREATE TABLE text_encoding_metadata (
    text_id TEXT PRIMARY KEY, -- Links to texts.id
    source_file_path TEXT NOT NULL,
    
    -- Source encoding detection and validation
    source_encoding_detected TEXT NOT NULL,
    source_encoding_confidence REAL,
    source_encoding_manual TEXT,
    source_encoding_final TEXT NOT NULL,
    
    -- Source features and characteristics
    source_features TEXT, -- JSON object with detected features
    
    -- Target encoding information
    target_encoding TEXT NOT NULL DEFAULT 'slp1_extended',
    
    -- Conversion process details
    conversion_method TEXT NOT NULL,
    conversion_version TEXT,
    conversion_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Quality metrics and validation
    conversion_lossless BOOLEAN NOT NULL,
    round_trip_checksum_original TEXT,
    round_trip_checksum_converted TEXT,
    quality_score REAL,
    
    -- Feature preservation tracking
    features_preserved TEXT, -- JSON object with preservation details
    
    -- Śākhā-specific metadata
    veda TEXT,
    sakha TEXT,
    text_type TEXT,
    regional_variant TEXT,
    
    -- Source preservation for debugging
    original_sample TEXT, -- First 500 chars of original
    original_header TEXT,
    
    -- Processing notes and validation
    conversion_notes TEXT,
    preprocessing_applied TEXT, -- JSON array of preprocessing steps
    validation_errors TEXT, -- JSON array of errors/warnings
    
    FOREIGN KEY (text_id) REFERENCES texts(id)
);

-- Round-trip test results for encoding validation (simplified)
CREATE TABLE encoding_tests (
    id INTEGER PRIMARY KEY,
    text_id INTEGER NOT NULL,
    source_encoding TEXT NOT NULL,
    target_encoding TEXT NOT NULL,
    original_text TEXT NOT NULL,
    converted_text TEXT NOT NULL,
    round_trip_text TEXT NOT NULL,
    is_lossless BOOLEAN NOT NULL,
    diff_details TEXT, -- Details of any differences found
    test_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (text_id) REFERENCES texts(id)
);

-- Views for common queries

-- Cross-source comparison view
CREATE VIEW verse_comparisons AS
SELECT 
    t1.sakha_id,
    t1.text_type_id,
    t1.kanda, t1.ashtaka, t1.adhyaya, t1.sukta, t1.mantra, t1.pada,
    s1.name as source1_name,
    t1.content_slp1 as source1_content,
    s2.name as source2_name,
    t2.content_slp1 as source2_content,
    CASE WHEN t1.content_slp1 = t2.content_slp1 THEN 1 ELSE 0 END as is_identical
FROM texts t1
JOIN texts t2 ON (
    t1.sakha_id = t2.sakha_id AND
    t1.text_type_id = t2.text_type_id AND
    COALESCE(t1.kanda, -1) = COALESCE(t2.kanda, -1) AND
    COALESCE(t1.ashtaka, -1) = COALESCE(t2.ashtaka, -1) AND
    COALESCE(t1.adhyaya, -1) = COALESCE(t2.adhyaya, -1) AND
    COALESCE(t1.sukta, -1) = COALESCE(t2.sukta, -1) AND
    COALESCE(t1.mantra, -1) = COALESCE(t2.mantra, -1) AND
    COALESCE(t1.pada, '') = COALESCE(t2.pada, '') AND
    t1.id < t2.id
)
JOIN sources s1 ON t1.source_id = s1.id
JOIN sources s2 ON t2.source_id = s2.id;

-- Complete text hierarchy view
CREATE VIEW text_hierarchy AS
SELECT 
    t.id,
    v.name as veda,
    s.name as sakha,
    tt.name as text_type,
    src.name as source,
    t.kanda, t.ashtaka, t.adhyaya, t.prapathaka, t.anuvaka, t.sukta, t.mantra, t.pada,
    t.content_slp1,
    t.title
FROM texts t
JOIN sakhas s ON t.sakha_id = s.id
JOIN vedas v ON s.veda_id = v.id
JOIN text_types tt ON t.text_type_id = tt.id
JOIN sources src ON t.source_id = src.id;

-- Initialize core reference data
INSERT INTO vedas (name) VALUES 
    ('rigveda'),
    ('samaveda'), 
    ('yajurveda'),
    ('atharvaveda');

INSERT INTO text_types (name, description) VALUES
    ('samhita', 'Primary mantric texts'),
    ('brahmana', 'Ritual explanation texts'),
    ('aranyaka', 'Forest treatises'),
    ('upanishad', 'Philosophical treatises');

INSERT INTO sources (name, description) VALUES
    ('vedanidhi', 'Digital library API downloads'),
    ('vedavms', 'Baraha-encoded DOCX files'),
    ('gretil', 'Göttingen Register of Electronic Texts in Indian Languages');