# Udapaana Vedic Text Data Repository

This repository contains source Vedic text data collected from multiple authoritative sources for the Udapaana project.

## Overview

**Total Verses**: 84,484 texts from 191 source files
- **Vedanidhi**: 76,835 verses (131 JSON files)
- **VedaVMS**: 7,649 verses (60 DOCX + 60 JSON files)

## Structure

```
data/
├── README.md                           # This file
├── VEDIC_TEXT_ENCODING_ANALYSIS.md    # Encoding analysis documentation
├── fetch/                              # Download scripts and tools
│   ├── vedanidhi/                      # Vedanidhi API download scripts
│   └── vedavms/                        # VedaVMS source configuration
├── source_exploration_results.json     # Source discovery metadata
└── vedic_texts/                        # Main text repository
    ├── rigveda/
    │   └── shakala/
    │       └── vedanidhi/
    │           ├── samhita/
    │           ├── brahmana/
    │           └── aranyaka/
    ├── yajurveda/
    │   └── taittiriya/
    │       ├── vedanidhi/
    │       │   ├── samhita/
    │       │   └── brahmana/
    │       └── vedavms/
    │           ├── samhita/
    │           ├── brahmana/
    │           └── aranyaka/
    ├── samaveda/
    │   └── kauthuma/
    │       └── vedanidhi/
    │           ├── samhita/
    │           ├── brahmana/
    │           └── aranyaka/
    └── atharvaveda/
        └── shaunaka/
            └── vedanidhi/
                ├── samhita/
                └── brahmana/
```

## Data Sources

### 1. Vedanidhi (vedanidhi.org)
- **Format**: JSON API downloads
- **Encoding**: Primarily Devanagari with mixed ASCII punctuation
- **Accent Marks**: Preserved using ASCII characters (., ~, -, ^)
- **Coverage**: All four Vedas with various text types

### 2. VedaVMS (vedavms.in)
- **Format**: DOCX files (converted to JSON)
- **Encoding**: Baraha ASCII encoding
- **Accent Marks**: Preserved using Baraha notation (q, #, etc.)
- **Coverage**: Taittiriya Yajurveda (samhita, brahmana, aranyaka)

## Encoding Details

### Source Encodings Detected
- **Devanagari**: 73,421 texts (87%)
- **SLP1**: 7,032 texts (8%)
- **HarvardKyoto**: 3,349 texts (4%)
- **Baraha/ITRANS/Others**: ~1,000 texts (1%)

### Special Characters
- **Mixed Encodings**: Many texts contain Devanagari script with ASCII punctuation
- **Accent Preservation**: Critical for proper Vedic recitation
- **Pattern Analysis**: See VEDIC_TEXT_ENCODING_ANALYSIS.md

## Data Quality

- **Source Fidelity**: All texts preserved exactly as received
- **No Corruption**: Verified hierarchical structure for each Veda
- **Accent Marks**: Preserved in original format
- **Unique Content**: Each śākhā contains appropriate texts

## Usage

This data serves as the source for:
1. **Udapaana Database**: Multi-encoding transformation pipeline
2. **VedaVid Application**: Educational platform for Vedic studies
3. **Research**: Computational linguistics and Vedic studies

## Processing Pipeline

The data can be processed using the Udapaana transformation pipeline to generate:
- Extended SLP1 (base storage format)
- Devanagari (display format)
- Telugu script
- ISO-15919 (scholarly romanization)
- IAST (academic standard)

## License

These texts are ancient heritage documents in the public domain. The compilation and organization are part of the Udapaana project.

## Contributing

To add new sources or report issues:
1. Ensure source authenticity
2. Preserve original encoding
3. Maintain hierarchical structure
4. Document accent notation system

---
Last Updated: June 7, 2025