# Enhanced Udapaana Processing Pipeline

A comprehensive system for processing Vedic text corpus data with runtime extensible mappings and line-by-line round-trip validation.

## Overview

This enhanced pipeline processes udapaana Vedic texts with:

1. **Runtime Extensible Mappings**: Automatic discovery and handling of unknown accent patterns
2. **Source-Specific Processing**: Sakha-veda-source specific configurations  
3. **Line-by-Line Validation**: Round-trip testing for every single line
4. **Comprehensive Metadata**: Detailed tracking of patterns, quality metrics, and processing statistics
5. **SQLite Storage**: Enhanced database schema with complete audit trail

## Key Features

### 🎯 **Runtime Pattern Discovery**
- Automatically detects unknown accent patterns during processing
- Extends mapping schemas on-the-fly for previously unseen encodings
- Supports sakha-specific variations (Rigveda Shakala, Yajurveda Taittiriya, etc.)

### 🔍 **Comprehensive Validation**
- **Line-by-line round-trip testing** for every line of text
- Multiple validation levels: exact match, normalized match, Unicode normalized
- Detailed similarity metrics and difference analysis
- Export of failed cases for manual review

### 🏛️ **Source-Specific Processing**
- **vedanidhi**: JSON format with Baraha encoding and Vedic accents
- **vedavms**: DOCX format with different Baraha encoding patterns
- **Sakha-specific configurations**: Tailored processing for each recension

### 📊 **Quality Metrics**
- Processing confidence scores
- Round-trip success rates by source/sakha/veda
- Pattern discovery statistics
- Comprehensive quality assessment

## Quick Start

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Ensure vidyut-lipi with extensions is available
# (See vidyut-lipi setup instructions)
```

### Basic Usage

```bash
# Process all udapaana data with analysis
python run_enhanced_pipeline.py

# Custom configuration
python run_enhanced_pipeline.py \
  --data-dir data/vedic_texts \
  --config udapaana_sakha_extensions.yaml \
  --db udapaana_enhanced.sqlite

# Analysis only (skip processing)
python run_enhanced_pipeline.py --analyze-only
```

### Configuration

The pipeline uses YAML-based configuration for sakha-veda-source specific processing:

```yaml
# udapaana_sakha_extensions.yaml
scheme_extensions:
  RigvedaShakalaVedanidhi:
    base_scheme: "BarahaSouth" 
    patterns:
      - name: "anudatta_q"
        pattern: "q"
        pattern_type: "Accent"
        target_mapping:
          Fixed: "{A}"
        confidence: 0.95
```

## Architecture

### Pipeline Stages

1. **Source Detection**: Automatic identification of sakha-veda-source combinations
2. **Pattern Discovery**: Runtime detection of unknown accent patterns  
3. **Extensible Mapping**: Dynamic schema extension based on discoveries
4. **Line Processing**: Individual line conversion with validation
5. **Round-Trip Testing**: Bidirectional conversion validation
6. **Quality Assessment**: Comprehensive metrics and reporting

### Database Schema

Enhanced SQLite schema with:

- **texts**: Main text storage with quality metrics
- **text_lines**: Line-by-line storage with individual validation
- **discovered_patterns**: Runtime pattern discovery tracking
- **round_trip_tests**: Detailed validation results
- **source_detections**: Automatic source identification results
- **pipeline_statistics**: Comprehensive processing metrics

## Data Processing Flow

```
Raw Source Data
       ↓
Source Detection (sakha-veda-source)
       ↓  
Pattern Discovery (unknown accents)
       ↓
Runtime Schema Extension
       ↓
Line-by-Line Processing
       ↓
Round-Trip Validation
       ↓
Quality Assessment
       ↓
SQLite Storage + Reports
```

## Output and Analysis

### Generated Reports

- **Comprehensive HTML Report**: Overall quality assessment and recommendations
- **Quality Metrics by Source**: Success rates and confidence scores
- **Pattern Discovery Analysis**: Discovered patterns with frequency and confidence
- **Failed Cases Export**: CSV of failed round-trip cases for review

### Quality Metrics

- **Round-trip Success Rate**: Percentage of lines with lossless conversion
- **Confidence Scores**: Processing confidence by source and text type
- **Pattern Discovery Stats**: Unique patterns discovered by type and source
- **Processing Statistics**: Comprehensive pipeline performance metrics

## Source-Specific Handling

### vedanidhi Sources
- **Format**: JSON with Devanagari/Baraha text
- **Accents**: `q` (anudatta), `#` (svarita), `$` (dheerga svarita)
- **Sections**: Sanskrit section markers (काण्डम्, अष्टकम्, etc.)
- **Special**: Samaveda PUA Unicode codes for musical notations

### vedavms Sources  
- **Format**: DOCX with Baraha encoding
- **Accents**: Different pattern variations from vedanidhi
- **Nasals**: `(gm)`, `(gg)`, `~m`, `~n` patterns
- **Structure**: TS/TB/TA sectional organization

## Quality Assurance

### Validation Levels

1. **Exact Match**: Character-for-character identity
2. **Normalized Match**: After whitespace normalization
3. **Unicode Normalized**: After Unicode NFC normalization
4. **Similarity Score**: Levenshtein distance-based scoring

### Quality Categories

- **Excellent** (>95% success): Standardized encoding sources
- **Good** (85-95% success): Minor encoding variations
- **Acceptable** (70-85% success): Requires custom mappings
- **Needs Review** (<70% success): Significant encoding issues

## Advanced Usage

### Custom Pattern Addition

```python
from pipeline.enhanced_udapaana_pipeline import EnhancedUdapaanaPipeline

pipeline = EnhancedUdapaanaPipeline()

# Add custom pattern mapping
pipeline.lipika.add_custom_mapping(
    from_scheme="BarahaSouth",
    to_scheme="Slp1", 
    source_pattern="§",
    target_pattern="{SECTION}",
    source="custom_source"
)
```

### Analysis and Reporting

```python
from pipeline.analyze_pipeline_results import UdapaanaPipelineAnalyzer

analyzer = UdapaanaPipelineAnalyzer("udapaana_enhanced.sqlite")

# Run comprehensive analysis
analyzer.analyze_all("results/")

# Export failed cases for review
analyzer.export_failed_round_trips_for_review("failed_cases.csv")
```

## Development

### Project Structure

```
udapaana/
├── pipeline/                    # Core pipeline modules
│   ├── enhanced_udapaana_pipeline.py
│   ├── analyze_pipeline_results.py
│   └── utils/                   # Processing utilities
├── data/                        # Source text data
│   └── vedic_texts/            # Organized by veda/sakha/source
├── schemas/                     # YAML schema definitions
├── docs/                        # Documentation
└── scripts/                     # Utility scripts
```

### Testing

```bash
# Test enhanced pipeline
python -m pytest pipeline/tests/

# Test specific components
python scripts/test_enhanced_converter.py
python scripts/test_enhanced_detection.py

# Manual quality check
python scripts/analyze_encoding_issues.py
```

### Contributing

1. **Add new source support**: Update source detection and configuration
2. **Enhance pattern discovery**: Add new pattern types and detection rules
3. **Improve validation**: Add new validation metrics and quality checks
4. **Extend analysis**: Add new reporting and visualization features

## Performance

### Benchmarks

- **Processing Speed**: ~1000 lines/second on average hardware
- **Memory Usage**: ~500MB for typical corpus processing
- **Storage**: ~2x source size for complete metadata storage

### Optimization

- Pattern discovery caching for repeated processing
- Incremental processing support for large corpora
- Parallel processing for independent sources
- Database indexing for fast analysis queries

## Troubleshooting

### Common Issues

1. **Round-trip failures**: Check source encoding detection accuracy
2. **Low confidence patterns**: Review pattern discovery thresholds
3. **Processing errors**: Validate input data format and encoding
4. **Performance issues**: Consider batch processing for large datasets

### Debug Mode

```bash
# Enable debug logging
python run_enhanced_pipeline.py --log-level DEBUG

# Process single file for testing
python scripts/test_specific_source.py path/to/file.json
```

## Migration from Previous Pipeline

### Database Migration

```sql
-- Backup existing data
.backup udapaana_corpus_backup.sqlite

-- Run enhanced schema
.read enhanced_schema.sql
```

### Configuration Migration

Previous configurations can be converted using:

```bash
python scripts/migrate_configuration.py old_config.json new_config.yaml
```

## License

This project is released under the MIT License. See LICENSE file for details.

## Acknowledgments

- Built on the vidyut-lipi transliteration system
- Processes texts from vedanidhi and vedavms sources
- Designed for accurate preservation of Vedic textual traditions