# Fetch Scripts Organization

This directory contains all scripts and configurations for fetching Vedic source data.

## Structure

```
data/
├── fetch/              # All fetch scripts and configurations
│   ├── vedanidhi/     # Vedanidhi API scripts and config
│   ├── vedavms/       # VedaVMS source documentation  
│   ├── shared/        # Shared processing utilities
│   ├── fetch_all_sources.py # Master coordinator script
│   └── README.md      # This file
└── vedic_texts/       # Target directory for fetched files
    ├── rigveda/shakala/vedanidhi/{text_type}/source/
    ├── yajurveda/taittiriya/vedanidhi/{text_type}/source/
    └── ...
```

## Usage

### Fetch all sources
```bash
python3 fetch_all_sources.py
```

### Fetch specific source
```bash
cd vedanidhi
python3 [specific_vedanidhi_script].py
```

## Configuration

- Each source has its own configuration file
- Configurations specify target texts, download settings, and validation rules
- Shared utilities handle common tasks like JSON validation and file organization

## Source Details

### Vedanidhi (vedanidhi.iiit.ac.in)
- API-based downloads
- Provides structured JSON data
- Covers multiple śākhās with varying completeness

### VedaVMS (vedavms.in)  
- Manual download source
- DOCX files with full accent marks (BarahaSouth encoding)
- Complete Taittirīya corpus

## Integration

Fetch scripts place downloaded files directly into the appropriate source/ directories:
- `data/vedic_texts/{veda}/{sakha}/{source_name}/{text_type}/source/`

This architecture provides:
- **Centralized fetch logic** - All fetch scripts in one place
- **Hierarchical output** - Files automatically organized by veda/śākhā/source
- **No duplication** - Shared utilities prevent repetitive code
- **Clear separation** - Fetch vs processing concerns separated
