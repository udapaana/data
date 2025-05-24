# Static Transliteration System

This directory contains scripts for generating static transliterations of Sanskrit texts using vidyut-lipi (preferred) or indic-transliteration (fallback).

## Overview

The transliteration system has been updated to use **static pre-generated transliterations** instead of dynamic client-side transliteration. This provides:

- **Better Performance**: No client-side transliteration calculations
- **Higher Quality**: Uses vidyut-lipi, which provides superior transliteration quality
- **Reliability**: Consistent transliterations across all platforms
- **Offline Support**: Works without JavaScript transliteration libraries

## Engine

**vidyut.lipi** - High-quality transliterator from Ambuda project
- Rust-based implementation with official Python bindings  
- Supports 40+ scripts and transliteration schemes
- Superior quality with robust script detection
- Official documentation: https://vidyut.readthedocs.io/en/latest/lipi.html

## Implementation Details

This implementation uses the **official vidyut Python bindings** from:
- Repository: https://github.com/ambuda-org/vidyut/tree/main/bindings-python
- PyPI: https://pypi.org/project/vidyut/
- Documentation: https://vidyut.readthedocs.io/en/latest/lipi.html

## Files

### Core Components

- `transliteration_generator.py` - Main transliteration engine using official vidyut.lipi API
- `transliteration_config.py` - Configuration and version tracking
- `add_static_transliterations.py` - Script to add transliterations to corpus
- `test_transliteration.py` - Test script for verification

### Data Files

- `taittiriya_complete_corpus_with_transliterations.json` - Complete corpus with transliterations
- `web_transliterated/` - Web-ready formats with transliterations

## Usage

### Basic Usage

```bash
# Add transliterations to the complete corpus
python3.11 add_static_transliterations.py

# Test transliteration functionality
python3.11 test_transliteration.py
```

### Regenerating Transliterations

When vidyut-lipi is updated or you need to regenerate transliterations:

1. Update the version in `transliteration_config.py`:
   ```python
   "engine_versions": {
       "vidyut": "0.5.0",  # Update to new version
       ...
   }
   ```

2. Set force regeneration flag:
   ```python
   "force_regenerate": True
   ```

3. Run the transliteration script:
   ```bash
   python3.11 add_static_transliterations.py
   ```

4. Reset the force flag:
   ```python
   "force_regenerate": False
   ```

## Installation

### Installing vidyut.lipi

Install the official Python bindings:

```bash
pip install vidyut
```

Verify installation:
```bash
python3.11 -c "from vidyut.lipi import transliterate, Scheme; print('✓ vidyut.lipi ready')"
```

### Python Version Compatibility

The scripts require Python 3.11+ for vidyut package compatibility:

```bash
python3.11 script_name.py
```

## Supported Scripts

The system supports transliteration to 13 different scripts:

- **Devanagari** (देवनागरी)
- **IAST** (International Alphabet of Sanskrit Transliteration)
- **Harvard-Kyoto** (Academic standard)
- **Baraha** (Source format)
- **ITRANS** (Internet transliteration)
- **Tamil** (தமிழ்)
- **Telugu** (తెలుగు)
- **Kannada** (ಕನ್ನಡ)
- **Malayalam** (മലയാളം)
- **Gujarati** (ગુજરાતી)
- **SLP1** (Sanskrit Library Phonetic)
- **Velthuis** (Academic notation)
- **WX** (Wx notation)

## Data Structure

Each text element in the corpus includes transliteration fields:

```json
{
  "verse_id": "1.1.1",
  "padam": "original_padam_text",
  "padam_transliterations": {
    "devanagari": "देवनागरी_text",
    "iast": "iast_text",
    "tamil": "தமிழ்_text",
    ...
  },
  "samhita": "original_samhita_text",
  "samhita_transliterations": {
    "devanagari": "देवनागरी_text",
    "iast": "iast_text",
    ...
  }
}
```

## Configuration

Edit `transliteration_config.py` to customize:

- **Script selection**: Enable/disable specific scripts
- **Batch processing**: Adjust batch size for large datasets  
- **Version tracking**: Track vidyut version for updates

## Future vidyut-lipi Updates

When vidyut-lipi receives major updates:

1. Install the new version
2. Update `transliteration_config.py` with the new version
3. Run regeneration scripts
4. Test quality improvements
5. Update Vue.js app to use new data

## Troubleshooting

### Module Import Errors

```bash
# Check installed packages
pip list | grep vidyut

# Install missing packages
pip install vidyut
```

### Python Version Issues

```bash
# Use specific Python version
python3.11 script_name.py

# Check if vidyut.lipi works
python3.11 -c "from vidyut.lipi import transliterate; print('✓ vidyut.lipi available')"
```

### Memory Issues with Large Corpus

Adjust batch size in `transliteration_config.py`:

```python
"batch_size": 50  # Reduce for memory-constrained systems
```

## Performance Notes

- Static generation takes ~5-10 minutes for complete corpus
- Web application loads much faster with pre-generated data
- Memory usage peaks during generation but is minimal during serving
- File sizes increase ~10x but provide instant access to all scripts