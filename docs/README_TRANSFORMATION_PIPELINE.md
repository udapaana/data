# Udapaana Multi-Encoding Transformation Pipeline

This pipeline transforms Vedic texts from the Udapaana data structure into a SQLite database with five different encodings.

## Core Components

### 1. **udapaana_transformation_pipeline.py**
Main transformation engine that:
- Detects source encoding automatically
- Transforms to Extended SLP1, Devanagari, Telugu, ISO-15919, and IAST
- Performs roundtrip validation using vidyut-lipi
- Stores results in SQLite with quality metrics

### 2. **udapaana_multi_encoding_schema.sql**
Database schema supporting:
- Traditional Vedic hierarchy (veda → śākhā → text type)
- Five encoding formats per verse
- Source encoding tracking
- Quality and validation metrics

### 3. **run_simple_transformation.py**
Production runner that:
- Processes all JSON files in data/vedic_texts
- Shows progress and statistics
- No backup overhead - focused on core transformation

## Usage

```bash
# Transform all Vedic texts to multi-encoding database
python3 run_simple_transformation.py

# Specify custom paths
python3 run_simple_transformation.py --data-dir data/vedic_texts --db-path udapaana_corpus.sqlite

# Verbose output
python3 run_simple_transformation.py --verbose
```

## Output

The pipeline produces `udapaana_corpus.sqlite` containing:

### Encodings per verse:
1. **Extended SLP1** - Base storage format preserving Vedic accents
2. **Devanagari** - देवनागरी script
3. **Telugu** - తెలుగు script  
4. **ISO-15919** - International standard with diacritics
5. **IAST** - Academic transliteration

### Additional data:
- Original content as found in source
- Detected source encoding (Devanagari, Baraha, IAST, etc.)
- Quality score and roundtrip validation status
- Source file path and metadata

## Source Encoding Detection

The pipeline automatically detects:
- **Devanagari** - Unicode range 0x0900-0x097F
- **Telugu** - Unicode range 0x0C00-0x0C7F  
- **Baraha** - Patterns like q, w, x, z
- **IAST** - Diacritical marks like ā, ī, ū, ṛ
- **ISO-15919** - Similar to IAST with ṁ
- **Harvard-Kyoto** - Uppercase patterns

Falls back to source hints:
- vedanidhi → Devanagari
- vedavms → BarahaSouth
- gretil → IAST

## Database Views

Query the results using built-in views:
```sql
-- Summary by source encoding
SELECT * FROM quality_by_source;

-- Full text hierarchy with all encodings
SELECT * FROM text_hierarchy_full;
```

## Requirements

- Python 3.6+
- SQLite3
- vidyut-lipi (optional - falls back to mock if unavailable)

## Data Structure Expected

```
data/vedic_texts/
├── rigveda/
│   └── shakala/
│       └── vedanidhi/
│           └── samhita/
│               └── source/
│                   └── *.json
├── samaveda/
│   └── kauthuma/
│       └── vedanidhi/
│           └── samhita/
│               └── source/
│                   └── *.json
└── ...
```

Each JSON file should contain:
```json
{
  "texts": [
    {
      "vaakya_text": "Sanskrit verse here",
      "vaakya_pk": 1,
      "location": [1, 1, 1]
    }
  ]
}
```