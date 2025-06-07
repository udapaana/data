# Vedic Accent Standards Research

## Current State Analysis

### VedaVMS Baraha Format (Yajurveda Taittirīya)
Our VedaVMS DOCX files use BarahaSouth encoding with the following accent marks:
- `॑` (U+0951) - Udātta (high tone) 
- `॒` (U+0952) - Anudātta (low tone)
- Svarita is unmarked (neutral tone)

Example from our source: `अ॒ग्निमी॑ळे पु॒रोहि॑तम्`

### Vedanidhi Format (Multiple Śākhās)
JSON data from Vedanidhi includes accent marks but inconsistently:
- Some texts have full accent marking
- Others have partial or no accents
- No standardized encoding scheme documented

## Research: Existing ASCII Standards

### 1. ITRANS (Indian Languages Transliteration)
**Standard**: Uses Latin characters with diacritics
**Accent notation**: 
- `a'` for udātta
- `a_` for anudātta  
- `a` for svarita (unmarked)

**Pros**: 
- Widely supported
- ASCII-safe
- Established standard

**Cons**:
- Not designed specifically for Vedic accents
- Limited Sāmaveda support

### 2. Harvard-Kyoto (HK)
**Standard**: ASCII transliteration scheme
**Accent notation**: Not standardized for accents

**Pros**: Simple, widely used
**Cons**: No accent support

### 3. IAST (International Alphabet of Sanskrit Transliteration)
**Standard**: Unicode-based with diacritics
**Accent notation**: Uses combining marks
- `á` for udātta
- `à` for anudātta
- `a` for svarita

**Pros**: Academic standard
**Cons**: Not ASCII-safe, complex for processing

### 4. SLP1 (Sanskrit Library Phonetic Basic)
**Standard**: ASCII scheme from Sanskrit Library project
**Accent notation**: 
- `a/` for udātta
- `a\\` for anudātta
- `a` for svarita

**Pros**: Pure ASCII, designed for Sanskrit
**Cons**: Limited adoption

## Sāmaveda Complexity Analysis

### Unique Sāmaveda Features
1. **Gāna Notation**: Musical notation for chanting
2. **Stobha**: Non-lexical sound units (hum, ho, hā, etc.)
3. **Complex Tone Patterns**: Beyond simple 3-tone system
4. **Elongation Marks**: Various degrees of syllable extension
5. **Pause Indicators**: Rest marks in musical sequence

### Current Sāmaveda Sources
- Our Vedanidhi data includes gāna texts but notation is unclear
- Traditional manuscripts use complex notation systems
- No standardized digital encoding found

## Proposed Solution: Extended Baraha ASCII

### Core Principle
Extend the proven BarahaSouth approach with ASCII-safe alternatives while preserving all accent information.

### Proposed Encoding

#### Basic Accents (All Vedas)
```
Text: Base character
\    : Udātta (high tone) - backslash after
/    : Anudātta (low tone) - forward slash after  
(unmarked): Svarita (neutral tone)
```

#### Extended Sāmaveda Notation
```
Base + tone + [modifiers]

Tones:
\  : Udātta
/  : Anudātta  
=  : Svarita (when explicit marking needed)

Modifiers:
+  : Elongation (1 degree)
++ : Elongation (2 degrees) 
+++ : Elongation (3 degrees)
^  : Pause/rest marker
~  : Glide/transition
|  : Phrase boundary
||  : Section boundary

Stobha indicators:
{ho} : Explicit stobha text
[instrumental] : Non-vocal notation
```

#### Examples
```
Ṛgveda: agni\mī/ḷe puro\hitam
Yajurveda: a/gnimī\ḷe pu/rohi\tam  
Sāmaveda: a/gni\+mī/ḷe++ {ho} pu/rohi\tam^
```

### ASCII Safety
- All special characters are standard ASCII
- No Unicode dependencies
- Easy parsing with regex
- Backward compatible with basic Devanāgarī

### Conversion Pipeline
1. **Input**: Various source formats (Baraha, Unicode, etc.)
2. **Normalization**: Convert to Extended Baraha ASCII
3. **Storage**: Standardized format across all śākhās
4. **Output**: Can generate any target format (Devanāgarī, IAST, etc.)

## Implementation Strategy

### Phase 1: Basic Accent Standardization
1. Convert VedaVMS BarahaSouth to Extended Baraha ASCII
2. Standardize Vedanidhi accent marks to same format
3. Document conversion algorithms

### Phase 2: Sāmaveda Extension
1. Analyze Sāmaveda source materials for full notation requirements
2. Extend ASCII standard for gāna-specific features
3. Implement specialized parsers

### Phase 3: Validation & Testing
1. Round-trip conversion testing
2. Traditional scholar validation
3. Audio synthesis compatibility testing

## Next Steps
1. Implement basic Extended Baraha ASCII parser
2. Convert sample texts from each śākhā
3. Create conversion utilities for all sources
4. Document complete specification