# GitHub Issue for vidyut-lipi

**Title**: Feature Request: Add Extended Baraha ASCII (EBA) scheme for Vedic accent preservation

## Summary

We propose adding Extended Baraha ASCII (EBA) as a new transliteration scheme to vidyut-lipi to support full Vedic accent preservation in an ASCII-safe format. This would enable proper digital representation of accented Vedic texts while leveraging vidyut-lipi's robust transliteration infrastructure.

## Background

### Current Challenge
Vedic texts require accurate accent preservation for:
- Traditional recitation learning (adhyayana)
- Scholarly analysis and research
- Cross-platform digital storage and transmission
- Audio synthesis and pronunciation guides

Existing schemes in vidyut-lipi either:
- Lack accent support entirely (HK, SLP1)
- Use Unicode that's not ASCII-safe (IAST with combining marks)
- Don't handle complex Sāmaveda musical notation

### Our Use Case
We're building **Udapaana**, a comprehensive digital library of Vedic texts across all major śākhās (traditions):
- Ṛgveda Śākala (10,552 texts)
- Yajurveda Taittirīya (4,903 texts) - complete with accents
- Sāmaveda Kauthuma (1,875 texts) - with musical notation
- Atharvaveda Śaunaka (328 texts)

Our corpus includes complete accent information from traditional sources like VedaVMS, which uses BarahaSouth encoding with full udātta/anudātta marking.

## Proposed Solution: Extended Baraha ASCII (EBA)

### Design Principles
1. **ASCII Safety**: Only standard ASCII characters (32-126)
2. **Bidirectional**: Perfect round-trip conversion with Devanagari
3. **Śākhā Agnostic**: Works across all Vedic traditions
4. **Human Readable**: Clear visual representation
5. **Parser Friendly**: Unambiguous tokenization

### Core Specification

#### Basic Accent Markers
```
\  : Udātta (high tone) - placed after accented syllable
/  : Anudātta (low tone) - placed after accented syllable  
=  : Explicit Svarita (neutral) - when clarity needed
   : Implicit Svarita (unmarked) - default state
```

#### Extended Sāmaveda Features
```
+   : Short elongation (1 mātrā)
++  : Medium elongation (2 mātrā)  
+++ : Long elongation (3+ mātrā)
^   : Pause/rest marker
~   : Glide/smooth transition
|   : Phrase boundary (minor)
||  : Section boundary (major)
{text} : Stobha elements (ho, hā, hum, etc.)
[desc] : Performance/instrumental notes
```

#### Examples
```
Basic Ṛgveda: agni\mī/ḷe puro\hitam → अग्नि॑मी॒ळे पुरो॑हितम्
Yajurveda: a/gnimī\ḷe pu/rohi\tam → अ॒ग्निमी॑ळे पु॒रोहि॑तम्  
Sāmaveda: a/gni\+mī/ḷe++ {ho} | → अ॒ग्नि॑+मी॒ळे+++{हो}|
```

## Technical Implementation

### Proposed API Extension
```rust
// Add to existing Scheme enum
pub enum Scheme {
    // ... existing schemes
    ExtendedBarahaAscii,
}

// Core conversion functions
impl Transliterator {
    pub fn eba_to_devanagari(&self, input: &str) -> String {
        // Convert ASCII accent markers to Unicode combining marks
        // Handle syllable boundaries and word spacing
    }
    
    pub fn devanagari_to_eba(&self, input: &str) -> String {
        // Extract Unicode accent marks to ASCII markers
        // Preserve syllable structure
    }
}
```

### Accent Mapping
```rust
let accent_mappings = [
    ("\\", "\u0951"),  // udātta combining mark
    ("/", "\u0952"),   // anudātta combining mark
    ("=", ""),         // explicit svarita (unmarked in Unicode)
];
```

### Parsing Rules
1. **Syllable Detection**: Use Sanskrit phonological rules
2. **Marker Attachment**: Accent markers attach to preceding syllable
3. **Container Handling**: Process `{...}` and `[...]` as atomic units
4. **Validation**: Check for orphaned markers and balanced containers

## Benefits for vidyut-lipi

### 1. Expands Academic Use Cases
- Supports traditional Vedic scholarship
- Enables accent-aware text processing
- Facilitates pronunciation and audio applications

### 2. ASCII Safety
- Works in environments where Unicode is problematic
- Easy to type and edit
- Safe for file names, URLs, and legacy systems

### 3. Performance
- ASCII processing is faster than Unicode normalization
- Smaller memory footprint for large corpora
- Simple regex-based parsing

### 4. Community Impact
- First comprehensive ASCII scheme for Vedic accents
- Could become standard in Sanskrit digital humanities
- Opens new research possibilities

## Implementation Plan

### Phase 1: Basic Support
- Add EBA as new scheme enum
- Implement basic accent conversion (\ /)
- Create test suite with round-trip validation

### Phase 2: Extended Features
- Add Sāmaveda musical notation support
- Implement container handling ({}, [])
- Extended validation and error reporting

### Phase 3: Integration
- Documentation and examples
- Performance optimization
- Community feedback integration

## Test Cases

### Round-trip Conversion
```rust
#[test]
fn test_eba_round_trip() {
    let cases = [
        ("agni\\mī/ḷe", "अग्नि॑मी॒ळे"),
        ("ya\\śhchid dhī/ro", "य॑श्चिद् धी॒रो"),
        // ... more test cases
    ];
    
    for (eba, devanagari) in cases {
        let converted = transliterate(eba, EBA, Devanagari);
        assert_eq!(converted, devanagari);
        
        let back = transliterate(converted, Devanagari, EBA);
        assert_eq!(back, eba);
    }
}
```

### Sāmaveda Features
```rust
#[test]
fn test_samaveda_notation() {
    let input = "a/gni\\+mī/ḷe++ {ho} |";
    let result = transliterate(input, EBA, Devanagari);
    // Verify musical notation handling
}
```

## Resources

### Documentation
- [Complete EBA Specification](https://github.com/user/udapaana/blob/main/EXTENDED_BARAHA_ASCII_SPECIFICATION.md)
- [Vidyut-lipi Integration Plan](https://github.com/user/udapaana/blob/main/VIDYUT_LIPI_INTEGRATION_SPEC.md)
- [Traditional Sources Analysis](https://github.com/user/udapaana/blob/main/VEDIC_ACCENT_STANDARDS.md)

### Sample Data
- VedaVMS Taittirīya corpus (4,903 texts with full accents)
- Vedanidhi multi-śākhā collection (partial accents)
- Traditional manuscript samples

### Bridge Implementation
We have a working Python implementation that demonstrates EBA processing:
- [EBA Bridge Code](https://github.com/user/udapaana/blob/main/data/transformations_tools/eba_bridge.py)
- Conversion algorithms
- Validation logic
- Test suite

## Timeline

We're planning to implement this feature and would be happy to contribute:

**Immediate** (if accepted):
- Detailed implementation plan
- Complete test suite
- Performance benchmarks

**1-2 months**:
- Pull request with basic EBA support
- Documentation and examples
- Community testing

**Ongoing**:
- Maintenance and improvements
- Extended feature development
- User feedback integration

## Questions for Maintainers

1. Are you open to adding specialized schemes like EBA?
2. Any preferred approach for handling extended notation?
3. Would you like us to submit a prototype implementation first?
4. Any concerns about ASCII-based accent representation?

We believe EBA would be a valuable addition to vidyut-lipi's comprehensive transliteration ecosystem and are committed to implementing it properly with full testing and documentation.

## Contact

- Project: [Udapaana](https://github.com/user/udapaana)
- Use case: Digital Vedic library with accent preservation
- Scale: 17,000+ texts across 4 major Vedic traditions

Thank you for considering this feature request!