# Udapaana Transformation Pipeline Design

## Overview

The Udapaana pipeline transforms raw Vedic text sources into a unified SQLite database with SLP1 encoding, organized by traditional sakha structure, with complete provenance tracking and multi-source comparison capabilities.

## Design Principles

1. **Data Integrity**: Round-trip testing ensures lossless conversions
2. **Provenance**: Every transformation step is logged and traceable  
3. **Multi-Source**: Store all sources to enable cross-comparison
4. **Sakha Organization**: Follow traditional Vedic text organization
5. **Academic Standards**: Use SLP1 as the standard scholarly encoding
6. **Reproducibility**: Documented process for integrating new sources

## Pipeline Architecture

```
Raw Sources → [Stage 1] → [Stage 2] → [Stage 3] → [Stage 4] → [Stage 5] → SQLite Database
   ↓             ↓           ↓           ↓           ↓           ↓
DOCX/JSON    Extracted   Normalized   SLP1      Structured   Database
(Various)      Text        Text      Encoded      Data       Records
```

### Stage 1: Source Extraction
**Purpose**: Extract text content from various source formats

**Inputs**:
- DOCX files (VedaVMS - Baraha encoding)
- JSON files (Vedanidhi - Devanagari Unicode)

**Operations**:
- Parse DOCX using python-docx library
- Extract JSON data from API responses
- Preserve original formatting metadata
- Extract hierarchical structure information

**Outputs**:
- Raw text content with original encoding preserved
- Metadata (source, file info, structure hints)
- Initial provenance record

**Round-Trip Testing**: N/A (no encoding conversion yet)

### Stage 2: Text Normalization
**Purpose**: Clean and standardize text while preserving content

**Inputs**: 
- Raw extracted text with formatting artifacts
- Original encoding information

**Operations**:
- Remove unnecessary whitespace and formatting
- Standardize punctuation and diacriticals
- Clean OCR artifacts and obvious errors
- Normalize verse/section separators
- Preserve important structural markers

**Outputs**:
- Cleaned text in original encoding
- List of normalizations applied

**Round-Trip Testing**: Compare normalized vs original for content preservation

### Stage 3: Encoding Conversion
**Purpose**: Convert all texts to SLP1 for unified storage

**Inputs**:
- Normalized text in source encoding (Baraha, Devanagari, etc.)
- Source encoding metadata

**Operations**:
- Use vidyut-lipi for transliteration
- Apply source-specific conversion rules
- Handle special characters and accents
- Validate conversion quality

**Outputs**:
- Text in SLP1 encoding
- Original text preserved for reference
- Round-trip test results

**Round-Trip Testing**: 
- Critical stage: Original → SLP1 → Original
- Must be lossless or differences documented
- Failed round-trips require manual review

### Stage 4: Structure Mapping
**Purpose**: Parse hierarchical structure and map to standardized schema

**Inputs**:
- SLP1-encoded text
- Source metadata and structure hints

**Operations**:
- Parse traditional text divisions (kanda, adhyaya, sukta, mantra, etc.)
- Map source-specific structure to standardized schema
- Extract cross-references and parallels
- Identify text boundaries and relationships

**Outputs**:
- Structured text records with hierarchical metadata
- Cross-reference information
- Mapping decisions documented

**Round-Trip Testing**: Verify structure parsing doesn't alter text content

### Stage 5: Database Loading
**Purpose**: Insert structured data into SQLite with full provenance

**Inputs**:
- Structured SLP1 text records
- Complete provenance chain from all stages

**Operations**:
- Insert into appropriate tables based on veda/sakha/text_type
- Create cross-reference relationships
- Log complete processing history
- Generate data quality metrics

**Outputs**:
- Database records in `texts` table
- Provenance records in `processing_log` table
- Cross-references in `text_relations` table
- Test results in `encoding_tests` table

**Round-Trip Testing**: Verify database round-trip (read what was written)

## Data Flow Example

### VedaVMS DOCX File Processing
```
Input: "TS 1.1 Baraha Pada paatam.docx"
  ↓ Stage 1: Extract using python-docx
Raw Text: "agniM paràméSThI..." (Baraha encoding)
  ↓ Stage 2: Normalize formatting
Clean Text: "agniM parameSTI..." (Baraha encoding)
  ↓ Stage 3: Convert to SLP1 via vidyut-lipi
SLP1 Text: "agniM parameSTI..." (SLP1 encoding)
  ↓ Stage 4: Parse structure
Structured: veda=yajurveda, sakha=taittiriya, text_type=samhita, kanda=1, prapathaka=1, anuvaka=1
  ↓ Stage 5: Insert to database
Database Record: texts.id=1, content_slp1="agniM parameSTI...", sakha_id=3, etc.
```

### Vedanidhi JSON File Processing
```
Input: "01010102_शाकलसंहिता_-_(01010102)_अष्टकम्.json"
  ↓ Stage 1: Parse JSON structure
Raw Text: "अग्निमीळे पुरोहितं..." (Devanagari Unicode)
  ↓ Stage 2: Normalize Unicode
Clean Text: "अग्निमीळे पुरोहितं..." (Devanagari Unicode)  
  ↓ Stage 3: Convert to SLP1 via vidyut-lipi
SLP1 Text: "agnimILe purohitaM..." (SLP1 encoding)
  ↓ Stage 4: Parse structure from filename and content
Structured: veda=rigveda, sakha=shakala, text_type=samhita, ashtaka=1, mandala=1, sukta=1, rc=1
  ↓ Stage 5: Insert to database
Database Record: texts.id=2, content_slp1="agnimILe purohitaM...", sakha_id=1, etc.
```

## Error Handling and Quality Control

### Round-Trip Test Failures
- **Automatic Retry**: Try alternative conversion paths
- **Manual Review Queue**: Flag for human verification
- **Documentation**: Record all lossy conversions
- **Source Annotation**: Mark problematic source sections

### Data Quality Issues
- **Validation Rules**: Check for obvious errors (impossible character combinations)
- **Cross-Source Comparison**: Flag inconsistencies between sources
- **Manual Curation**: Queue suspected issues for review
- **Quality Metrics**: Track error rates by source and text type

### Processing Failures
- **Graceful Degradation**: Continue processing other files
- **Detailed Logging**: Capture full error context
- **Recovery**: Ability to restart from any stage
- **Notification**: Alert on critical failures

## Configuration Management

### Pipeline Configuration (`config/pipeline.yaml`)
```yaml
sources:
  vedanidhi:
    enabled: true
    encoding: "devanagari"
    parser: "VedanidhiParser"
    priority: "high"
  vedavms:
    enabled: true
    encoding: "baraha"
    parser: "VedavmsParser"
    priority: "high"

encoding:
  target: "slp1"
  round_trip_test: true
  fail_on_lossy: false
  
database:
  path: "udapaana_corpus.sqlite"
  backup_before_load: true
  
logging:
  level: "INFO"
  provenance_detail: "full"
```

## Performance Considerations

### Batch Processing
- Process files in parallel where possible
- Use database transactions for consistency
- Implement progress tracking and resume capability

### Memory Management
- Stream large files rather than loading entirely
- Clear intermediate results after each stage
- Monitor memory usage during processing

### Database Optimization
- Use appropriate indexes for common queries
- Batch inserts for better performance
- Regular database maintenance (VACUUM, ANALYZE)

## Validation and Testing

### Unit Tests
- Test each stage in isolation
- Mock file inputs for consistent testing
- Verify round-trip functions work correctly

### Integration Tests
- End-to-end pipeline testing with sample files
- Cross-source comparison validation
- Database schema and query testing

### Quality Assurance
- Sample manual verification of processed texts
- Statistical analysis of conversion quality
- Regular cross-source consistency checks

This design provides a robust, scalable foundation for processing Vedic texts while maintaining academic standards and full traceability.