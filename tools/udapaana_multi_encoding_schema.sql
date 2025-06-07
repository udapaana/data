-- Udapaana Multi-Encoding Database Schema
-- Optimized for storing verses in Extended SLP1, Devanagari, and Telugu
-- with comprehensive roundtrip testing and quality metrics

-- Core hierarchical structure
CREATE TABLE IF NOT EXISTS vedas (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE, -- 'rigveda', 'samaveda', 'yajurveda', 'atharvaveda'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sakhas (
    id INTEGER PRIMARY KEY,
    veda_id INTEGER NOT NULL,
    name TEXT NOT NULL, -- 'shakala', 'kauthuma', 'taittiriya', 'shaunaka'
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (veda_id) REFERENCES vedas(id),
    UNIQUE(veda_id, name)
);

CREATE TABLE IF NOT EXISTS text_types (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE, -- 'samhita', 'brahmana', 'aranyaka', 'upanishad'
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE, -- 'vedanidhi', 'vedavms', 'gretil', etc.
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
    
    -- Traditional hierarchical identifiers (flexible for different traditions)
    kanda INTEGER,          -- For Samaveda, Yajurveda, Atharvaveda
    ashtaka INTEGER,        -- For Rigveda
    adhyaya INTEGER,        -- Chapter/section
    prapathaka INTEGER,     -- Sub-section
    anuvaka INTEGER,        -- Sub-sub-section
    sukta INTEGER,          -- Hymn (mainly Rigveda)
    mantra INTEGER,         -- Verse number within sukta/section
    pada TEXT,              -- Pada identifier (a, b, c, d, etc.)
    
    -- Multi-encoding content storage
    -- Extended SLP1 as base format (preserves Vedic accents and special characters)
    content_slp1_extended TEXT NOT NULL,
    
    -- Rendered script outputs
    content_devanagari TEXT,    -- Devanagari rendering
    content_telugu TEXT,        -- Telugu rendering
    content_iso_15919 TEXT,     -- ISO-15919 transliteration
    content_iast TEXT,          -- IAST transliteration
    
    -- Source preservation
    content_original TEXT NOT NULL,       -- Original source text as found
    source_encoding TEXT NOT NULL,        -- Detected/determined source encoding
    source_file_path TEXT NOT NULL,       -- Full path to source file
    
    -- Transformation quality metrics
    roundtrip_valid BOOLEAN NOT NULL DEFAULT 0,        -- Can we roundtrip losslessly?
    quality_score REAL DEFAULT 1.0,                    -- Overall transformation quality (0.0-1.0)
    encoding_confidence REAL DEFAULT 1.0,              -- Confidence in encoding detection (0.0-1.0)
    
    -- Processing metadata
    processing_notes TEXT,                              -- JSON with processing metadata
    transformation_warnings TEXT,                       -- JSON array of warnings during transformation
    vidyut_version TEXT,                               -- Version of vidyut-lipi used
    
    -- Standard metadata
    title TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (sakha_id) REFERENCES sakhas(id),
    FOREIGN KEY (text_type_id) REFERENCES text_types(id),
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

-- Detailed encoding test results for quality assurance
CREATE TABLE IF NOT EXISTS encoding_tests (
    id INTEGER PRIMARY KEY,
    text_id INTEGER NOT NULL,
    
    -- Test configuration
    source_scheme TEXT NOT NULL,           -- Original encoding scheme
    target_scheme TEXT NOT NULL,           -- Target encoding scheme
    test_type TEXT NOT NULL,               -- 'forward', 'roundtrip', 'multi_step'
    
    -- Test content
    original_text TEXT NOT NULL,           -- Input text
    converted_text TEXT NOT NULL,          -- Output text
    roundtrip_text TEXT,                   -- Result of round-trip conversion
    
    -- Test results
    is_lossless BOOLEAN NOT NULL,          -- Perfect conversion?
    exact_match BOOLEAN NOT NULL,          -- Exact character match?
    normalized_match BOOLEAN,              -- Match after normalization?
    
    -- Detailed metrics
    char_differences INTEGER DEFAULT 0,    -- Number of character differences
    length_difference INTEGER DEFAULT 0,   -- Difference in string length
    similarity_score REAL DEFAULT 0.0,     -- Similarity score (0.0-1.0)
    levenshtein_distance INTEGER,          -- Edit distance
    
    -- Additional analysis
    diff_details TEXT,                     -- JSON with detailed differences
    problem_patterns TEXT,                 -- JSON array of problematic patterns found
    test_notes TEXT,                       -- Human-readable test notes
    
    -- Test metadata
    test_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    vidyut_version TEXT,
    
    FOREIGN KEY (text_id) REFERENCES texts(id)
);

-- Pattern discovery and analysis for improving transliteration
CREATE TABLE IF NOT EXISTS discovered_patterns (
    id INTEGER PRIMARY KEY,
    
    -- Pattern details
    source_pattern TEXT NOT NULL,          -- Original pattern found
    target_mapping TEXT NOT NULL,          -- Suggested SLP1 mapping
    pattern_type TEXT NOT NULL,            -- 'accent', 'nasal', 'conjunct', 'punctuation', 'other'
    context_before TEXT,                   -- Characters before pattern
    context_after TEXT,                    -- Characters after pattern
    
    -- Discovery context
    first_seen_in_file TEXT NOT NULL,      -- File where first discovered
    first_seen_in_veda TEXT,               -- Veda where first seen
    first_seen_in_sakha TEXT,              -- Sakha where first seen
    first_seen_in_source TEXT,             -- Source where first seen
    
    -- Statistics
    frequency_count INTEGER DEFAULT 1,     -- How many times seen
    confidence_score REAL NOT NULL,        -- Confidence in mapping (0.0-1.0)
    success_rate REAL DEFAULT 0.0,         -- Success rate in roundtrip tests
    
    -- Validation
    manual_verified BOOLEAN DEFAULT 0,     -- Has been manually verified?
    is_systematic BOOLEAN DEFAULT 0,       -- Is this a systematic pattern?
    needs_attention BOOLEAN DEFAULT 0,     -- Flagged for manual review?
    
    -- Timestamps
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_verified_at TIMESTAMP,
    
    -- Make sure we don't duplicate patterns
    UNIQUE(source_pattern, target_mapping, first_seen_in_source)
);

-- Processing runs for tracking pipeline execution
CREATE TABLE IF NOT EXISTS processing_runs (
    id INTEGER PRIMARY KEY,
    run_id TEXT NOT NULL UNIQUE,           -- UUID for this run
    
    -- Input statistics
    total_files_processed INTEGER DEFAULT 0,
    total_verses_processed INTEGER DEFAULT 0,
    
    -- Transformation statistics
    successful_transformations INTEGER DEFAULT 0,
    failed_transformations INTEGER DEFAULT 0,
    partial_transformations INTEGER DEFAULT 0,
    
    -- Quality metrics
    roundtrip_success_rate REAL DEFAULT 0.0,
    average_quality_score REAL DEFAULT 0.0,
    verses_with_perfect_roundtrip INTEGER DEFAULT 0,
    verses_with_failed_roundtrip INTEGER DEFAULT 0,
    
    -- Pattern discovery
    new_patterns_discovered INTEGER DEFAULT 0,
    total_unique_patterns INTEGER DEFAULT 0,
    
    -- Source breakdown (JSON)
    source_statistics TEXT,                -- JSON object with per-source stats
    
    -- Configuration and versions
    vidyut_version TEXT,
    pipeline_version TEXT,
    config_used TEXT,                      -- JSON with configuration parameters
    
    -- Timing
    processing_start_time TIMESTAMP NOT NULL,
    processing_end_time TIMESTAMP,
    total_processing_time_seconds REAL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Error tracking for debugging and improvement
CREATE TABLE IF NOT EXISTS processing_errors (
    id INTEGER PRIMARY KEY,
    run_id TEXT NOT NULL,
    
    -- Error context
    error_type TEXT NOT NULL,              -- 'encoding_error', 'file_error', 'transformation_error', etc.
    file_path TEXT,                        -- File where error occurred
    line_number INTEGER,                   -- Line number if applicable
    
    -- Error details
    error_message TEXT NOT NULL,
    error_traceback TEXT,
    
    -- Input that caused error
    problematic_input TEXT,
    input_encoding TEXT,
    
    -- Attempted processing
    attempted_transformation TEXT,
    partial_result TEXT,
    
    -- Resolution
    resolved BOOLEAN DEFAULT 0,
    resolution_notes TEXT,
    resolution_date TIMESTAMP,
    
    error_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (run_id) REFERENCES processing_runs(run_id)
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_texts_hierarchy 
    ON texts(sakha_id, text_type_id, kanda, ashtaka, adhyaya, sukta, mantra);
CREATE INDEX IF NOT EXISTS idx_texts_source ON texts(source_id);
CREATE INDEX IF NOT EXISTS idx_texts_quality ON texts(roundtrip_valid, quality_score);
CREATE INDEX IF NOT EXISTS idx_texts_encoding ON texts(source_encoding);
CREATE INDEX IF NOT EXISTS idx_texts_file_path ON texts(source_file_path);

CREATE INDEX IF NOT EXISTS idx_encoding_tests_text ON encoding_tests(text_id);
CREATE INDEX IF NOT EXISTS idx_encoding_tests_schemes ON encoding_tests(source_scheme, target_scheme);
CREATE INDEX IF NOT EXISTS idx_encoding_tests_results ON encoding_tests(is_lossless, exact_match);
CREATE INDEX IF NOT EXISTS idx_encoding_tests_quality ON encoding_tests(similarity_score);

CREATE INDEX IF NOT EXISTS idx_patterns_frequency ON discovered_patterns(frequency_count DESC);
CREATE INDEX IF NOT EXISTS idx_patterns_type ON discovered_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_patterns_source ON discovered_patterns(first_seen_in_source, first_seen_in_veda);
CREATE INDEX IF NOT EXISTS idx_patterns_verification ON discovered_patterns(manual_verified, needs_attention);

CREATE INDEX IF NOT EXISTS idx_processing_runs_timestamp ON processing_runs(processing_start_time);
CREATE INDEX IF NOT EXISTS idx_processing_errors_run ON processing_errors(run_id);
CREATE INDEX IF NOT EXISTS idx_processing_errors_type ON processing_errors(error_type);

-- Views for common analyses

-- Quality summary by source
CREATE VIEW IF NOT EXISTS quality_by_source AS
SELECT 
    s.name as source_name,
    v.name as veda_name,
    sk.name as sakha_name,
    COUNT(*) as total_verses,
    SUM(CASE WHEN t.roundtrip_valid THEN 1 ELSE 0 END) as successful_roundtrips,
    CAST(SUM(CASE WHEN t.roundtrip_valid THEN 1 ELSE 0 END) AS REAL) / COUNT(*) as roundtrip_success_rate,
    AVG(t.quality_score) as avg_quality_score,
    AVG(t.encoding_confidence) as avg_encoding_confidence
FROM texts t
JOIN sources s ON t.source_id = s.id
JOIN sakhas sk ON t.sakha_id = sk.id
JOIN vedas v ON sk.veda_id = v.id
GROUP BY s.id, v.id, sk.id
ORDER BY roundtrip_success_rate DESC;

-- Pattern analysis summary
CREATE VIEW IF NOT EXISTS pattern_analysis AS
SELECT 
    pattern_type,
    COUNT(*) as unique_patterns,
    SUM(frequency_count) as total_occurrences,
    AVG(confidence_score) as avg_confidence,
    AVG(success_rate) as avg_success_rate,
    SUM(CASE WHEN manual_verified THEN 1 ELSE 0 END) as verified_patterns,
    SUM(CASE WHEN needs_attention THEN 1 ELSE 0 END) as patterns_needing_attention
FROM discovered_patterns
GROUP BY pattern_type
ORDER BY total_occurrences DESC;

-- Complete text hierarchy with all encodings
CREATE VIEW IF NOT EXISTS text_hierarchy_full AS
SELECT 
    t.id,
    v.name as veda,
    sk.name as sakha,
    tt.name as text_type,
    s.name as source,
    t.kanda, t.ashtaka, t.adhyaya, t.prapathaka, t.anuvaka, t.sukta, t.mantra, t.pada,
    t.content_slp1_extended,
    t.content_devanagari,
    t.content_telugu,
    t.content_original,
    t.source_encoding,
    t.roundtrip_valid,
    t.quality_score,
    t.title
FROM texts t
JOIN sakhas sk ON t.sakha_id = sk.id
JOIN vedas v ON sk.veda_id = v.id
JOIN text_types tt ON t.text_type_id = tt.id
JOIN sources s ON t.source_id = s.id;

-- Processing performance tracking
CREATE VIEW IF NOT EXISTS processing_performance AS
SELECT 
    run_id,
    processing_start_time,
    total_verses_processed,
    total_processing_time_seconds,
    CASE 
        WHEN total_processing_time_seconds > 0 
        THEN total_verses_processed / total_processing_time_seconds 
        ELSE 0 
    END as verses_per_second,
    roundtrip_success_rate,
    average_quality_score,
    new_patterns_discovered
FROM processing_runs
WHERE processing_end_time IS NOT NULL
ORDER BY processing_start_time DESC;

-- Initialize core reference data
INSERT OR IGNORE INTO vedas (name) VALUES 
    ('rigveda'),
    ('samaveda'), 
    ('yajurveda'),
    ('atharvaveda');

INSERT OR IGNORE INTO text_types (name, description) VALUES
    ('samhita', 'Primary mantric texts'),
    ('brahmana', 'Ritual explanation texts'),
    ('aranyaka', 'Forest treatises'),
    ('upanishad', 'Philosophical treatises');

INSERT OR IGNORE INTO sources (name, description) VALUES
    ('vedanidhi', 'Digital library API downloads'),
    ('vedavms', 'Baraha-encoded DOCX files'),
    ('gretil', 'Göttingen Register of Electronic Texts in Indian Languages');

-- Insert sakhas for each veda
INSERT OR IGNORE INTO sakhas (veda_id, name) VALUES
    ((SELECT id FROM vedas WHERE name = 'rigveda'), 'shakala'),
    ((SELECT id FROM vedas WHERE name = 'yajurveda'), 'taittiriya'),
    ((SELECT id FROM vedas WHERE name = 'samaveda'), 'kauthuma'),
    ((SELECT id FROM vedas WHERE name = 'atharvaveda'), 'shaunaka');