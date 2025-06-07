# Extended Baraha ASCII Specification v1.0

## Overview

Extended Baraha ASCII (EBA) is a pure ASCII encoding standard for Vedic texts that preserves all accent information while maintaining compatibility across śākhās. It extends the proven BarahaSouth approach used by VedaVMS.

## Design Principles

1. **ASCII Safety**: Only standard ASCII characters (32-126)
2. **Śākhā Agnostic**: Works for all Vedic traditions
3. **Reversible**: Perfect round-trip conversion to/from source formats
4. **Human Readable**: Clear visual representation of accents
5. **Parser Friendly**: Unambiguous tokenization rules

## Core Specification

### Base Text Encoding
- Use standard Devanāgarī in UTF-8 for the base text
- Apply EBA accent markers as suffixes to syllables
- Preserve word boundaries and punctuation

### Basic Accent Markers

#### Three-Tone System (Ṛgveda, Yajurveda, Atharvaveda)
```
\  : Udātta (high tone) - placed after the accented syllable
/  : Anudātta (low tone) - placed after the accented syllable  
   : Svarita (neutral) - unmarked (default)
=  : Explicit Svarita - when clarity needed
```

#### Examples
```
Source (BarahaSouth): अ॒ग्निमी॑ळे पु॒रोहि॑तम्
EBA Format:          अ/ग्निमी\ळे पु/रोहि\तम्
```

### Extended Notation (Sāmaveda)

#### Elongation Markers
```
+   : Short elongation (1 mātrā extension)
++  : Medium elongation (2 mātrā extension)  
+++ : Long elongation (3+ mātrā extension)
```

#### Musical/Gāna Markers
```
^   : Pause/rest marker
~   : Glide or smooth transition
|   : Phrase boundary (minor)
||  : Section boundary (major)
```

#### Stobha and Non-lexical Elements
```
{text}        : Stobha elements (ho, hā, hum, etc.)
[description] : Instrumental or performance notes
```

#### Complex Sāmaveda Example
```
Source text with gāna: (complex traditional notation)
EBA Format: अ/ग्नि\+मी/ळे++ {हो} | पु/रोहि\तम्^ || या\ज्ञस्य~ देव\++म्
```

### Parsing Rules

#### Tokenization
1. Split text into syllables (following Sanskrit phonology)
2. Identify accent markers as suffixes
3. Process modifiers in order: tone → elongation → musical

#### Precedence
1. Base syllable (required)
2. Tone marker (optional: \, /, =)
3. Elongation (optional: +, ++, +++)
4. Musical markers (optional: ^, ~, |, ||)
5. Special containers (optional: {}, [])

#### Regular Expression Pattern
```regex
([^\\\/\=\+\^\~\|\{\[]+)     # Base syllable
([\\\/\=]?)                  # Tone marker
(\+*)                        # Elongation
([\^\~\|]*)                  # Musical markers
(\{[^}]*\}|\[[^\]]*\])*      # Special containers
```

## Conversion Algorithms

### From BarahaSouth Unicode
```python
def baraha_to_eba(text):
    # Map Unicode combining marks to ASCII
    mapping = {
        '\u0951': '\\',  # udātta
        '\u0952': '/',   # anudātta
        # svarita unmarked
    }
    return apply_mapping(text, mapping)
```

### From Vedanidhi JSON
```python
def vedanidhi_to_eba(json_data):
    # Extract accent information from metadata
    # Apply standardized marking
    # Handle partial accent data
    pass
```

### To Display Formats
```python
def eba_to_devanagari(eba_text):
    # Convert ASCII markers back to Unicode combining marks
    pass

def eba_to_iast(eba_text):
    # Transliterate with IAST accent marks
    pass
```

## Śākhā-Specific Guidelines

### Ṛgveda (Śākala)
- Primary focus on udātta/anudātta distinction
- Svarita usually unmarked unless pedagogically important
- Minimal use of extended notation

### Yajurveda (Taittirīya)
- Full three-tone marking as in VedaVMS sources
- Regional variants (Āndhra/Drāviḍa) noted in metadata
- Consistent accent patterns in ritual contexts

### Sāmaveda (Kauthuma)
- Full extended notation required
- Stobha elements explicitly marked
- Gāna-specific elongations and pauses
- Musical phrase boundaries

### Atharvaveda (Śaunaka)
- Basic three-tone system
- Special notation for magical/ritual emphasis
- Minimal extended features

## Implementation Files

### Core Converter
```python
# eba_converter.py
class EBAConverter:
    def __init__(self, sakha_config):
        self.config = sakha_config
    
    def to_eba(self, source_text, source_format):
        """Convert any source format to EBA"""
        pass
    
    def from_eba(self, eba_text, target_format):
        """Convert EBA to target format"""
        pass
    
    def validate_eba(self, eba_text):
        """Validate EBA syntax"""
        pass
```

### Śākhā Configuration
```json
{
  "rigveda_shakala": {
    "accent_system": "three_tone_basic",
    "default_svarita": "unmarked",
    "extended_notation": false
  },
  "samaveda_kauthuma": {
    "accent_system": "three_tone_extended", 
    "default_svarita": "unmarked",
    "extended_notation": true,
    "stobha_marking": "required",
    "gana_markers": "full"
  }
}
```

## Quality Assurance

### Validation Rules
1. All accent markers must follow valid syllables
2. No orphaned modifiers
3. Balanced container markers ({}, [])
4. Śākhā-appropriate notation usage

### Testing Requirements
1. Round-trip conversion accuracy (100%)
2. Traditional scholar validation
3. Cross-śākhā consistency
4. Performance benchmarks

## Migration Strategy

### Phase 1: VedaVMS Conversion
- Convert all Taittirīya DOCX files to EBA
- Validate against original BarahaSouth
- Create reference implementations

### Phase 2: Vedanidhi Integration  
- Standardize Vedanidhi JSON accent data
- Handle partial/missing accent information
- Generate EBA for all downloaded texts

### Phase 3: Sāmaveda Extension
- Research traditional gāna notation sources
- Implement extended markers
- Validate with Sāmaveda experts

## Version History
- v1.0: Initial specification with basic and extended notation
- Future: Based on implementation feedback and scholarly input