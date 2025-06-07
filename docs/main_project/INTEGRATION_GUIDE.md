# Udapaana Source Integration Guide

This guide documents how to integrate new Vedic text sources into the Udapaana corpus database.

## Overview

The Udapaana pipeline processes raw Vedic texts from various sources and stores them in a unified SQLite database using SLP1 encoding. Each source undergoes a standardized transformation pipeline with full provenance tracking.

## Current Sources

### 1. VedaVMS (vedavms)
- **Format**: DOCX files with Baraha encoding
- **Coverage**: Taittiriya Yajurveda (Samhita, Brahmana, Aranyaka)
- **Location**: `data/vedic_texts/yajurveda/taittiriya/vedavms/`
- **Encoding**: Baraha script (South Indian variant)
- **Structure**: Files named like "TS 1.1 Baraha Pada paatam.docx"

### 2. Vedanidhi (vedanidhi)  
- **Format**: JSON API responses
- **Coverage**: All four Vedas with multiple recensions
- **Location**: `data/vedic_texts/*/vedanidhi/`
- **Encoding**: Devanagari Unicode
- **Structure**: Hierarchical JSON with metadata

## Integration Process

### Step 1: Source Assessment

Before integrating a new source, document:

1. **Source Information**:
   - Name and URL of the source
   - Academic credentials/reliability
   - License and usage terms
   - Coverage (which texts are available)

2. **Technical Details**:
   - File formats (PDF, DOCX, XML, HTML, etc.)
   - Text encoding (Devanagari, IAST, Baraha, etc.)
   - Structure/organization
   - Quality assessment

3. **Example Documentation**:
```yaml
source_name: "new_source_name"
url: "https://example.com"
description: "Brief description of the source"
license: "CC-BY-SA 4.0"
coverage:
  - rigveda_shakala_samhita
  - rigveda_shakala_brahmana
encoding: "iast"
formats: ["xml", "html"]
quality: "high"  # high/medium/low
academic_note: "Published by XYZ University"
```

### Step 2: Directory Structure

Create directory structure following the pattern:
```
data/vedic_texts/{veda}/{sakha}/{source_name}/
├── source/           # Raw downloaded files
├── documentation/    # Source-specific docs
└── metadata.json    # Source metadata
```

Example for a new GRETIL source:
```
data/vedic_texts/rigveda/shakala/gretil/
├── source/
│   ├── rv_shakala_samhita.xml
│   └── rv_shakala_brahmana.xml
├── documentation/
│   └── gretil_encoding_notes.md
└── metadata.json
```

### Step 3: Metadata Documentation

Create `metadata.json` for each source:
```json
{
  "source_name": "gretil",
  "description": "Göttingen Register of Electronic Texts in Indian Languages",
  "url": "http://gretil.sub.uni-goettingen.de/",
  "download_date": "2025-01-06",
  "license": "Academic use permitted",
  "encoding": "iast",
  "quality_notes": "High quality, manually verified",
  "coverage": {
    "rigveda": {
      "shakala": {
        "samhita": "complete",
        "brahmana": "partial"
      }
    }
  },
  "file_mapping": {
    "rv_shakala_samhita.xml": {
      "text_type": "samhita",
      "structure": "mandala/sukta/rc",
      "encoding": "iast"
    }
  }
}
```

### Step 4: Parser Development

For each new source format, create a parser in `pipeline/parsers/`:

```python
# pipeline/parsers/gretil_parser.py
class GretilParser:
    def __init__(self):
        self.source_name = "gretil"
    
    def parse_file(self, file_path):
        """Parse GRETIL XML file and extract structured text."""
        # Implementation specific to GRETIL format
        pass
    
    def extract_metadata(self, file_path):
        """Extract metadata from GRETIL file."""
        pass
    
    def get_encoding_scheme(self):
        """Return the encoding scheme used by this source."""
        return "iast"
```

### Step 5: Pipeline Integration

Update the main pipeline to handle the new source:

1. **Add source to database**:
```sql
INSERT INTO sources (name, description, url) 
VALUES ('gretil', 'Göttingen Register of Electronic Texts', 'http://gretil.sub.uni-goettingen.de/');
```

2. **Update pipeline configuration**:
```yaml
# config/pipeline.yaml
sources:
  gretil:
    parser_class: "GretilParser"
    encoding: "iast"
    priority: "high"
    round_trip_test: true
```

3. **Add to source registry**:
```python
# pipeline/source_registry.py
from .parsers.gretil_parser import GretilParser

SOURCE_PARSERS = {
    'vedanidhi': VedanidhiParser,
    'vedavms': VedavmsParser,
    'gretil': GretilParser,  # New source
}
```

## Quality Control

### Round-Trip Testing

Every encoding conversion must pass round-trip testing:

1. Original encoding → SLP1 → Original encoding
2. Verify character-level equivalence
3. Document any lossy conversions
4. Log test results in `encoding_tests` table

### Cross-Source Validation

When multiple sources contain the same text:

1. Compare SLP1 versions for consistency
2. Flag significant differences for manual review
3. Document variants in `text_relations` table
4. Use the `verse_comparisons` view for analysis

### Data Provenance

Every transformation is logged:

1. Input file checksums
2. Processing parameters
3. Output checksums
4. Timestamp and processing metadata
5. Any errors or warnings

## Testing New Sources

### 1. Small-Scale Test
```python
# Test with a single file first
parser = GretilParser()
result = parser.parse_file("test_file.xml")
tester = RoundTripTester()
test_result = tester.test_round_trip(result.text, "iast", "slp1")
assert test_result['is_lossless']
```

### 2. Batch Processing
```python
# Process all files from the source
pipeline = VedicPipeline()
pipeline.process_source("gretil")
```

### 3. Validation Queries
```sql
-- Check data was inserted correctly
SELECT COUNT(*) FROM texts WHERE source_id = (SELECT id FROM sources WHERE name = 'gretil');

-- Compare with existing sources
SELECT * FROM verse_comparisons 
WHERE source1_name = 'gretil' OR source2_name = 'gretil'
LIMIT 10;
```

## Common Issues and Solutions

### Encoding Problems
- **Issue**: Characters not converting correctly
- **Solution**: Verify source encoding, check vidyut-lipi scheme mapping
- **Test**: Run round-trip tests on sample texts

### Structure Mapping
- **Issue**: Source uses different organizational scheme
- **Solution**: Create mapping rules in parser, document in metadata
- **Example**: Some sources use "chapter" instead of "adhyaya"

### Quality Issues
- **Issue**: OCR errors or formatting artifacts
- **Solution**: Add normalization rules, document known issues
- **Track**: Log all normalizations in `processing_log` table

## Documentation Requirements

For each new source integration, create:

1. **Integration Report**: Document the process, decisions, and any issues
2. **Parser Documentation**: How the parser works and any special cases
3. **Quality Assessment**: Analysis of the source quality and coverage
4. **Test Results**: Round-trip test results and any data loss issues

## Example Integration Checklist

- [ ] Source assessment completed
- [ ] Directory structure created
- [ ] Metadata.json documented
- [ ] Parser implemented and tested
- [ ] Round-trip tests passing
- [ ] Source added to database
- [ ] Pipeline configuration updated
- [ ] Cross-source validation completed
- [ ] Documentation updated
- [ ] Integration report written

This systematic approach ensures consistent, high-quality integration of new sources while maintaining full traceability and reproducibility.