# Data Organization Structure

## Directory Hierarchy

```
udapaana/
├── data/                           # All raw and processed data
│   ├── vedic_texts_by_sakha/      # PRIMARY: Organized by śākhā-source
│   │   ├── rigveda_शाकलशाखा/     # Rigveda - Śākala recension
│   │   │   ├── vedanidhi_010101_शाकलसंहिता/
│   │   │   │   ├── 010101_शाकलसंहिता.json
│   │   │   │   └── metadata.json
│   │   │   └── ...
│   │   ├── samaveda_कौथुमशाखा/   # Sāmaveda - Kauthuma  
│   │   ├── yajurveda_तैत्तिरीयशाखा/ # Yajurveda - Taittirīya
│   │   └── atharvaveda_शौनकशाखा/   # Atharvaveda - Śaunaka
│   │
│   ├── vedanidhi_complete/        # Original download structure (backup)
│   │   ├── validation_failures/   # Failed downloads for review
│   │   ├── download_progress.json # Tracks download status
│   │   └── validated_download.log # Detailed log
│   │
│   ├── vedanidhi_backup_*/        # Timestamped backups
│   │
│   ├── taittiriya/                # Legacy DOCX-sourced data
│   │   ├── raw/                   # Original DOCX files
│   │   ├── parsed/                # Parsed JSON
│   │   ├── web_enhanced/          # Web-ready format
│   │   └── scripts/               # Processing scripts
│   │
│   ├── vedanidhi_archive/         # Old exploration data
│   │   └── old_explorations/      # Can be deleted if needed
│   │
│   └── vedic_corpus.sqlite        # SQLite database (to be rebuilt)
│
├── scripts/                       # Data processing scripts
│   ├── validated_continuous_downloader.py
│   ├── reorganize_by_sakha_source.py
│   ├── update_metadata.py
│   ├── build_vedic_sqlite.py
│   └── ...
│
├── docs/                          # Documentation (if created)
│   └── ...
│
├── VEDIC_TEXT_TRACKER.md         # Master acquisition tracker
├── DATA_ORGANIZATION.md          # This file
├── SOURCE_INVENTORY.md           # All data sources
├── UDAPAANA_DOCUMENTATION.md    # Project overview
│
└── vedavid/                      # Web application (to be rebuilt)
```

## Data Formats

### Raw Data (from sources)

#### Vedanidhi Format
```json
{
  "data": [
    {
      "vaakya_pk": 12345,
      "vaakya_sk": "01010101",
      "vaakya_text": "अग्निमीळे पुरोहितं...",
      "location": ["ऋ", "शा", null, "01 मण्डल", "001 सूक्त", "01"],
      "permission": false
    }
  ],
  "meta": {
    "total_records": 1028,
    "source_id": "010101",
    "veda": "Rigveda",
    "shakha": "शाकलशाखा",
    "text_type": "शाकलसंहिता"
  }
}
```

#### DOCX Format (Taittirīya)
- Baraha encoded text
- Hierarchical structure marked by headers
- Regional variants inline: (A1), (D2), etc.

### Processed Data

#### Unified Format (proposed)
```json
{
  "text_id": "rv_1_1_1",
  "veda": "rigveda",
  "shakha": "śākala",
  "text_type": "saṃhitā",
  "location": {
    "mandala": 1,
    "sukta": 1,
    "rk": 1
  },
  "content": {
    "original": "अग्निमीळे पुरोहितं यज्ञस्य देवमृत्विजम् ।",
    "transliteration": "agnimīḷe purohitaṃ yajñasya devamṛtvijam |",
    "accents": {
      "marked": true,
      "system": "vedic",
      "coverage": 0.98
    }
  },
  "variants": [],
  "metadata": {
    "source": "vedanidhi_010101",
    "acquired": "2025-05-29",
    "validation": "passed"
  }
}
```

### Database Schema

#### SQLite Structure (proposed)
```sql
-- Master texts table
CREATE TABLE texts (
    text_id TEXT PRIMARY KEY,
    veda TEXT NOT NULL,
    shakha TEXT NOT NULL,
    text_type TEXT NOT NULL,
    location_json TEXT NOT NULL,
    content TEXT NOT NULL,
    has_accents BOOLEAN,
    accent_coverage REAL,
    source_id TEXT,
    created_at TIMESTAMP
);

-- Hierarchical navigation
CREATE TABLE hierarchy (
    id INTEGER PRIMARY KEY,
    veda TEXT NOT NULL,
    shakha TEXT NOT NULL,
    level1 TEXT,  -- mandala/kanda
    level2 TEXT,  -- sukta/prapathaka
    level3 TEXT,  -- rk/anuvaka
    level4 TEXT,  -- verse/mantra
    text_id TEXT REFERENCES texts(text_id)
);

-- Source tracking
CREATE TABLE sources (
    source_id TEXT PRIMARY KEY,
    source_type TEXT,  -- vedanidhi, docx, manuscript
    url TEXT,
    acquisition_date DATE,
    validation_status TEXT,
    notes TEXT
);

-- Variants and cross-references
CREATE TABLE variants (
    id INTEGER PRIMARY KEY,
    text_id TEXT REFERENCES texts(text_id),
    variant_type TEXT,  -- regional, manuscript, pronunciation
    variant_text TEXT,
    source_id TEXT
);
```

## File Naming Conventions

### Downloaded Files
- Vedanidhi: `{source_id}.json` (e.g., `010101.json`)
- Processed: `{veda}_{shakha}_{type}.json`
- SQLite: `vedic_corpus_v2.sqlite`

### Script Files
- Downloaders: `*_downloader.py`
- Processors: `*_processor.py`
- Validators: `*_validator.py`
- Builders: `build_*.py`

## Quality Control

### Validation Levels

1. **Source Validation**
   - Check expected Veda markers
   - Verify hierarchical structure
   - Detect duplicate content

2. **Content Validation**
   - Accent mark coverage
   - Text encoding consistency
   - Structural completeness

3. **Cross-Source Validation**
   - Compare overlapping texts
   - Identify variant readings
   - Flag discrepancies

### Tracking Files

- `download_progress.json` - Current download state
- `validation_failures/` - Failed validations for review
- `source_inventory.json` - All identified sources
- `quality_metrics.json` - Accent coverage, completeness

## Processing Pipeline

```
1. Source Discovery
   ↓
2. Download & Initial Validation
   ↓
3. Format Standardization
   ↓
4. Content Enhancement
   - Add transliteration
   - Mark variants
   - Add cross-references
   ↓
5. Database Integration
   ↓
6. Quality Verification
   ↓
7. Web Format Generation
```

## Backup Strategy

1. **Raw Data**: Keep all original downloads
2. **Processed Data**: Version control major changes
3. **Database**: Regular SQLite backups
4. **Scripts**: Git version control
5. **Documentation**: Update with each major change

## Future Additions

### Planned Sources
- GRETIL texts
- Sanskrit Documents
- Muktabodha manuscripts
- Academic editions
- Traditional recordings

### Directory Structure
```
data/
├── gretil/
├── sanskrit_documents/
├── muktabodha/
├── manuscripts/
└── audio/
```