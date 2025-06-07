# UDAPAANA PROJECT DOCUMENTATION

This consolidated documentation contains all essential information about the Udapaana project, data sources, processing pipelines, and architectural decisions.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Data Sources and Provenance](#data-sources-and-provenance)
3. [Data Processing Pipeline](#data-processing-pipeline)
4. [Database Architecture](#database-architecture)
5. [Data Quality Analysis](#data-quality-analysis)
6. [Vedanidhi Integration](#vedanidhi-integration)
7. [Technical Implementation](#technical-implementation)

---

## 1. Project Overview

### Vision
Udapaana serves as:
1. **Master Repository**: Comprehensive collection of Vedic texts across all śākhās
2. **Data Pipeline**: Robust processing infrastructure from raw texts to web-ready formats
3. **Tool Platform**: Foundation for multiple applications consuming the processed data

### Current Implementation Status
- **Implemented**: Taittirīya Śākhā (Kṛṣṇa Yajurveda) - Complete corpus of 4,903 texts
- **Planned**: All major Vedic śākhās as outlined in the comprehensive structure

### Repository Structure
```
udapaana/
├── data/                     # Master data directory
│   ├── taittiriya/          # Complete Taittirīya implementation
│   ├── unified_corpus/      # Processed unified data
│   ├── vedanidhi/          # Downloaded Vedanidhi data
│   └── vedic_corpus.sqlite  # SQLite database
├── *.py                     # Processing scripts
└── UDAPAANA_DOCUMENTATION.md
```

---

## 2. Data Sources and Provenance

### Primary Sources

#### 1. Local DOCX Collection (Complete)
- **Source**: Personal collection of Baraha-encoded DOCX files
- **Content**: Complete Taittirīya corpus (Saṃhitā, Brāhmaṇa, Āraṇyaka)
- **Format**: Baraha encoding in Devanagari script
- **Status**: Fully processed and integrated

#### 2. Vedanidhi Digital Library
- **URL**: http://vedanidhi.gov.in
- **Content**: Government repository of Vedic texts
- **Coverage**: Multiple śākhās with variants
- **Access**: Public API with structured endpoints

### Data Inventory

#### Completed: Kṛṣṇa Yajurveda - Taittirīya Śākhā
- **Total Texts**: 4,903 items
  - Saṃhitā: 2,198 verses (7 kāṇḍas)
  - Brāhmaṇa: 1,997 sections (3 kāṇḍas)
  - Āraṇyaka: 708 sections (10 prapāṭhakas)
- **Pāṭha Types**: Pada and Saṃhitā for verses
- **Regional Variants**: Mixed Āndhra/Drāviḍa readings

### Source Quality Assessment
1. **DOCX Collection**: High quality, consistent encoding, complete texts
2. **Vedanidhi**: Variable quality, some encoding issues, extensive coverage
3. **Future Sources**: GRETIL, manuscript collections, critical editions

---

## 3. Data Processing Pipeline

### Processing Scripts

#### Core Parser Scripts
1. **enhanced_parser.py** - Primary samhita/padam parser
2. **brahmana_aranyaka_parser.py** - Prose text parser
3. **create_complete_dataset.py** - Unified corpus generator
4. **create_enhanced_web_format.py** - Web optimization

#### SQLite Database Scripts
1. **build_vedic_sqlite.py** - Standard database builder
2. **build_vedic_sqlite_fast.py** - Optimized version
3. **build_vedic_sqlite_parallel.py** - Parallel processing
4. **create_sqlite_database.py** - Database creation utility

### Processing Workflow
```bash
# 1. Parse raw DOCX files
python3 enhanced_parser.py
python3 brahmana_aranyaka_parser.py

# 2. Create unified corpus
python3 create_complete_dataset.py

# 3. Generate web formats
python3 create_enhanced_web_format.py

# 4. Build SQLite database
python3 build_vedic_sqlite_fast.py
```

### Data Transformation Steps
1. **Extraction**: Parse DOCX/HTML to extract text and structure
2. **Cleaning**: Remove formatting, normalize Unicode
3. **Structuring**: Apply hierarchical text organization
4. **Enhancement**: Add metadata, cross-references
5. **Optimization**: Create indexed database

---

## 4. Database Architecture

### SQLite Schema Design

#### Core Tables
```sql
-- Texts table
CREATE TABLE texts (
    id INTEGER PRIMARY KEY,
    text_id TEXT UNIQUE NOT NULL,
    veda TEXT NOT NULL,
    sakha TEXT NOT NULL,
    text_type TEXT NOT NULL,
    kanda INTEGER,
    prapathaka INTEGER,
    anuvaka INTEGER,
    verse_number INTEGER,
    full_reference TEXT NOT NULL
);

-- Content table
CREATE TABLE content (
    id INTEGER PRIMARY KEY,
    text_id TEXT NOT NULL,
    content_type TEXT NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY (text_id) REFERENCES texts(text_id)
);

-- Metadata table
CREATE TABLE metadata (
    id INTEGER PRIMARY KEY,
    text_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    FOREIGN KEY (text_id) REFERENCES texts(text_id)
);
```

### Performance Optimizations
1. **Indexing**: Strategic indexes on frequently queried fields
2. **FTS5**: Full-text search for Sanskrit content
3. **Compression**: GZIP compression reduces size by ~70%
4. **Batching**: Parallel processing for large datasets

### Database Statistics
- **Uncompressed**: ~150-200MB
- **Compressed**: ~45-60MB
- **Total Records**: ~15,000 (texts + content + metadata)
- **Query Performance**: <10ms for indexed queries

---

## 5. Data Quality Analysis

### Quality Metrics

#### Text Completeness
- Saṃhitā: 100% coverage (all 2,198 verses)
- Brāhmaṇa: 100% coverage (all 1,997 sections)
- Āraṇyaka: 100% coverage (all 708 sections)

#### Data Integrity
1. **Structural Consistency**: Valid hierarchical references
2. **Content Validation**: No empty texts, proper encoding
3. **Cross-references**: Verified pada-saṃhitā mappings
4. **Variant Tracking**: Inline notation preserved

### Known Issues
1. **Regional Variants**: Not separated into distinct entries
2. **Accent Marks**: Not preserved from source
3. **Commentaries**: Not included in current dataset
4. **Cross-śākhā References**: To be added

---

## 6. Vedanidhi Integration

### API Structure
```
Base URL: http://vedanidhi.gov.in/vedanidhi/
Endpoints:
- /browse.htm - Hierarchical browsing
- /show_text.htm - Text display
- /show_padam.htm - Word analysis
```

### Downloaded Content
Successfully downloaded and cached:
- Rigveda samples
- Samaveda sections
- Yajurveda variants
- Atharvaveda portions

### Integration Challenges
1. **Encoding**: Mixed UTF-8 and legacy encodings
2. **Structure**: Inconsistent HTML formatting
3. **Variants**: Different notation systems
4. **Completeness**: Some texts fragmentary

---

## 7. Technical Implementation

### Unified Data Structure
```json
{
  "text_id": "ts_1_1_1_1",
  "veda": "krishna_yajurveda",
  "sakha": "taittiriya",
  "text_type": "samhita",
  "location": {
    "kanda": 1,
    "prapathaka": 1,
    "anuvaka": 1,
    "verse": 1
  },
  "content": {
    "samhita": "agnimīḷe purohitaṃ",
    "pada": "agnim īḷe puraḥ hitam"
  },
  "metadata": {
    "source": "baraha_docx",
    "timestamp": "2024-01-01"
  }
}
```

### File Formats

#### 1. JSON Batches
- Chunked into ~100 texts per file
- Optimized for streaming and partial loading
- Total: ~800 batch files

#### 2. SQLite Database
- Single file database
- Full-text search enabled
- Compressed backup available

#### 3. Web Formats
- Optimized JSON for frontend
- Separate samhita/pada versions
- Metadata indices

### Future Architecture Plans

#### Multi-Source Integration
```
sources/
├── baraha_docx/        # Current data
├── vedanidhi/          # Government portal
├── gretil/             # Academic texts
└── manuscripts/        # Digitized MSS
```

#### Variant Management
- Separate variant readings
- Critical apparatus support
- Regional pronunciation notes
- Manuscript sigla tracking

---

## Appendix: Script Usage

### Essential Scripts to Keep

1. **build_vedic_sqlite.py** - Main database builder
2. **build_vedic_sqlite_fast.py** - Performance optimized
3. **build_vedic_sqlite_parallel.py** - Multi-core processing
4. **create_sqlite_database.py** - Database utilities
5. **create_test_sqlite.py** - Testing utilities

### Data Processing Scripts (in taittiriya/)
1. **enhanced_parser.py** - Main text parser
2. **brahmana_aranyaka_parser.py** - Prose parser
3. **create_complete_dataset.py** - Corpus builder
4. **create_enhanced_web_format.py** - Web optimizer
5. **validate_complete_corpus.py** - Data validation

---

*Last Updated: May 2024*