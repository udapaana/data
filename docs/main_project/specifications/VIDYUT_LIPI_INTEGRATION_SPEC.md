# Vidyut-lipi Integration Specification

## Overview

Rather than implementing our own transliteration system, we propose extending [vidyut-lipi](https://docs.rs/vidyut-lipi/latest/vidyut_lipi/) to support Extended Baraha ASCII (EBA) for Vedic accent preservation. This leverages their robust, tested infrastructure while adding the specialized Vedic features we need.

## Current Vidyut-lipi Capabilities

### Supported Schemes
- **Devanagari** (primary)
- **IAST** (International Alphabet of Sanskrit Transliteration)
- **Harvard Kyoto** (HK)
- **ITRANS** 
- **SLP1** (Sanskrit Library Phonetic)
- **Velthuis**

### Architecture
- Rust-based for performance and safety
- Bidirectional conversion between schemes
- Rule-based approach with extensive mappings
- Well-documented API and clear extension points

## Proposed Extension: Extended Baraha ASCII (EBA)

### Integration Approach

#### 1. Add EBA as New Scheme
```rust
// Proposed addition to vidyut-lipi
pub enum Scheme {
    Devanagari,
    Iast,
    HarvardKyoto,
    Itrans,
    Slp1,
    Velthuis,
    ExtendedBarahaAscii,  // NEW: Our proposed scheme
}
```

#### 2. EBA Mapping Rules
```rust
// Core accent mappings
let eba_accent_map = [
    // Basic accents (post-syllable markers)
    ("\\", AccentType::Udatta),      // high tone
    ("/", AccentType::Anudatta),     // low tone  
    ("=", AccentType::SvaritaExplicit), // explicit neutral
    
    // Elongation markers (for Sāmaveda)
    ("+", ElongationType::Short),     // 1 mātrā
    ("++", ElongationType::Medium),   // 2 mātrā
    ("+++", ElongationType::Long),    // 3+ mātrā
    
    // Musical markers (for Sāmaveda gāna)
    ("^", MusicalType::Pause),        // rest
    ("~", MusicalType::Glide),        // transition
    ("|", MusicalType::PhraseBoundary),   // minor pause
    ("||", MusicalType::SectionBoundary), // major pause
];
```

#### 3. Context-Aware Processing
```rust
// Handle Sāmaveda-specific features
fn process_samaveda_notation(input: &str) -> ProcessedText {
    // Parse stobha elements: {ho}, {hā}, etc.
    // Handle elongation combinations
    // Process musical phrase boundaries
}

// Handle general Vedic features  
fn process_vedic_text(input: &str, sakha: VedicTradition) -> ProcessedText {
    match sakha {
        VedicTradition::Rigveda => basic_accent_processing(input),
        VedicTradition::Yajurveda => basic_accent_processing(input),
        VedicTradition::Samaveda => process_samaveda_notation(input),
        VedicTradition::Atharvaveda => basic_accent_processing(input),
    }
}
```

## Specification for Vidyut-lipi Maintainers

### Feature Request Summary
**Add Extended Baraha ASCII (EBA) scheme to vidyut-lipi for Vedic text processing with full accent preservation**

### Technical Requirements

#### 1. Basic Accent Support
- Post-syllable accent markers: `\` (udātta), `/` (anudātta), `=` (explicit svarita)
- Bidirectional conversion with Devanagari accent marks (U+0951, U+0952)
- Preserve accent positioning during transliteration

#### 2. Extended Sāmaveda Support
- Elongation markers: `+`, `++`, `+++`
- Musical notation: `^` (pause), `~` (glide), `|` (phrase), `||` (section)
- Stobha containers: `{text}` for non-lexical elements
- Performance notes: `[description]` for instrumental annotations

#### 3. ASCII Safety Requirements
- All markers must be standard ASCII (32-126)
- No Unicode dependencies for core functionality
- Unambiguous parsing rules
- Backward compatibility with existing schemes

#### 4. Parsing Rules
```
Syllable pattern: [base_text][tone_marker?][elongation*][musical*]
Examples:
- Basic: "agni\mī/ḷe" → अग्नि॑मी॒ळे
- Sāmaveda: "a/gni\+mī/ḷe++^" → अ॒ग्नि॑+मी॒ळे+++^
```

### Implementation Phases

#### Phase 1: Basic EBA Support
```rust
// Minimal implementation for basic accents
impl Transliterator {
    fn eba_to_devanagari(&self, input: &str) -> String {
        // Convert \ → ॑, / → ॒
        // Handle syllable boundaries
        // Preserve word spacing
    }
    
    fn devanagari_to_eba(&self, input: &str) -> String {
        // Convert ॑ → \, ॒ → /  
        // Detect syllable boundaries
        // Apply ASCII markers
    }
}
```

#### Phase 2: Extended Features
```rust
// Add Sāmaveda-specific processing
impl SamavedaProcessor {
    fn process_elongation(&self, input: &str) -> String { /* ... */ }
    fn process_musical_marks(&self, input: &str) -> String { /* ... */ }
    fn handle_stobha(&self, input: &str) -> String { /* ... */ }
}
```

#### Phase 3: Validation & Testing
```rust
// Comprehensive test suite
#[cfg(test)]
mod tests {
    #[test]
    fn test_basic_accent_round_trip() {
        let input = "agni\\mī/ḷe";
        let devanagari = transliterate(input, EBA, Devanagari);
        let back_to_eba = transliterate(devanagari, Devanagari, EBA);
        assert_eq!(input, back_to_eba);
    }
    
    #[test] 
    fn test_samaveda_complex() {
        let input = "a/gni\\+mī/ḷe++^ {ho} |";
        // Test full Sāmaveda notation handling
    }
}
```

## Our Side Implementation

While proposing the vidyut-lipi extension, we'll implement a bridge system:

### Temporary EBA Processor
```python
# data/transformations_tools/eba_bridge.py
class EBABridge:
    """
    Bridge processor until vidyut-lipi supports EBA natively.
    Handles our specific requirements while preparing for integration.
    """
    
    def __init__(self):
        self.accent_map = {
            '\u0951': '\\',  # udātta → \
            '\u0952': '/',   # anudātta → /
        }
    
    def baraha_to_eba(self, baraha_text: str) -> str:
        """Convert BarahaSouth Unicode to EBA ASCII"""
        result = baraha_text
        for unicode_mark, ascii_mark in self.accent_map.items():
            result = result.replace(unicode_mark, ascii_mark)
        return result
    
    def eba_to_devanagari(self, eba_text: str) -> str:
        """Convert EBA back to standard Devanagari"""
        # Reverse mapping for display
        pass
    
    def validate_eba(self, eba_text: str) -> bool:
        """Validate EBA syntax"""
        # Check for orphaned markers, balanced containers, etc.
        pass
```

### Integration Layer
```python
# data/transformations_tools/transliteration_service.py
class TransliterationService:
    """
    Service layer that will use vidyut-lipi when EBA support is added,
    falls back to our bridge implementation until then.
    """
    
    def __init__(self):
        self.use_vidyut_lipi = self._check_vidyut_eba_support()
        if not self.use_vidyut_lipi:
            self.bridge = EBABridge()
    
    def convert(self, text: str, from_scheme: str, to_scheme: str) -> str:
        if self.use_vidyut_lipi:
            # Use vidyut-lipi API when available
            return self._call_vidyut_lipi(text, from_scheme, to_scheme)
        else:
            # Use our bridge implementation
            return self._use_bridge(text, from_scheme, to_scheme)
```

## Benefits of This Approach

### 1. Leverage Existing Infrastructure
- Proven transliteration engine
- Extensive testing and validation
- Active maintenance and community

### 2. Standardization
- EBA becomes part of established library
- Other projects can benefit from Vedic accent support
- Consistent behavior across tools

### 3. Performance
- Rust implementation for speed
- Memory-efficient processing
- Battle-tested with large corpora

### 4. Future-Proofing
- Regular updates and improvements
- Community contributions
- Long-term sustainability

## Contribution Process

### 1. Create GitHub Issue
- Submit feature request to vidyut-lipi repository
- Include this specification
- Provide use cases and benefits

### 2. Prototype Implementation
- Fork vidyut-lipi repository
- Implement basic EBA support
- Create comprehensive test suite

### 3. Submit Pull Request
- Clean, well-documented code
- All tests passing
- Performance benchmarks

### 4. Community Review
- Incorporate feedback
- Refine implementation
- Update documentation

## Timeline

### Immediate (Next 2 weeks)
- Submit GitHub issue with specification
- Begin bridge implementation for our needs
- Test with sample VedaVMS data

### Short-term (1-2 months)
- Prototype vidyut-lipi extension
- Validate with traditional scholars
- Refine specification based on feedback

### Long-term (3-6 months)  
- Complete vidyut-lipi integration
- Migration from bridge to native support
- Performance optimization and testing

This approach gives us the best of both worlds: immediate progress with our bridge implementation while contributing to the broader Sanskrit computational linguistics ecosystem through vidyut-lipi enhancement.