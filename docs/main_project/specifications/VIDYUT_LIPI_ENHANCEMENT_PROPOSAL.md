# Vidyut-Lipi Enhancement Proposal for Vedic Text Support

## Overview

This proposal outlines enhancements to vidyut-lipi to natively support Vedic text encoding discovery and lossless conversion, eliminating the need for external preprocessing.

## Current Limitations

1. **No Vedic accent support**: Vidyut-lipi doesn't recognize Vedic accent markers
2. **Loss of metadata**: Special annotations (nasal markers, ritual notations) are stripped
3. **No encoding discovery**: Cannot auto-detect variant Baraha patterns
4. **Fixed scheme mappings**: No extensibility for scheme variants

## Proposed Architecture

### 1. Encoding Discovery Framework

```rust
pub trait EncodingDetector {
    fn detect(&self, text: &str) -> DetectionResult;
    fn confidence(&self) -> f32;
}

pub struct DetectionResult {
    pub encoding: Scheme,
    pub variant: Option<String>,  // e.g., "vedic", "classical"
    pub features: HashMap<String, Vec<TextFeature>>,
}

pub struct TextFeature {
    pub feature_type: FeatureType,
    pub positions: Vec<usize>,
    pub metadata: HashMap<String, String>,
}

pub enum FeatureType {
    VedicAccent(AccentType),
    NasalAnnotation(String),
    MusicalNotation,
    RitualMarker,
    SectionDivider,
}
```

### 2. Extensible Scheme Definition

```rust
// Current (rigid)
pub enum Scheme {
    Devanagari,
    BarahaSouth,
    Slp1,
    // ... fixed list
}

// Proposed (extensible)
pub struct Scheme {
    pub base_scheme: BaseScheme,
    pub extensions: Vec<SchemeExtension>,
    pub metadata: SchemeMetadata,
}

pub struct SchemeExtension {
    pub name: String,
    pub mappings: HashMap<String, String>,
    pub patterns: Vec<Pattern>,
    pub preserve_during_conversion: bool,
}

pub struct Pattern {
    pub regex: String,
    pub replacement: Option<String>,
    pub feature_type: FeatureType,
}
```

### 3. Vedic Text Support Module

```rust
pub mod vedic {
    pub struct VedicBarahaDetector;
    
    impl EncodingDetector for VedicBarahaDetector {
        fn detect(&self, text: &str) -> DetectionResult {
            let mut features = HashMap::new();
            
            // Detect accent markers
            if let Some(accents) = self.detect_accents(text) {
                features.insert("accents".to_string(), accents);
            }
            
            // Detect nasal annotations
            if let Some(nasals) = self.detect_nasal_annotations(text) {
                features.insert("nasals".to_string(), nasals);
            }
            
            // Return comprehensive result
            DetectionResult {
                encoding: Scheme::baraha_vedic(),
                variant: Some("taittiriya".to_string()),
                features,
            }
        }
    }
    
    impl VedicBarahaDetector {
        fn detect_accents(&self, text: &str) -> Option<Vec<TextFeature>> {
            let patterns = [
                ("q", AccentType::Anudatta),
                ("#", AccentType::Svarita),
                ("$", AccentType::DheergaSvarita),
            ];
            
            // Find all occurrences with positions
            // Return TextFeature objects
        }
        
        fn detect_nasal_annotations(&self, text: &str) -> Option<Vec<TextFeature>> {
            let patterns = [
                (r"\(gm\)", "guttural_m"),
                (r"\(gg\)", "guttural_g"),
                (r"~M", "chandrabindu"),
            ];
            
            // Pattern matching logic
        }
    }
}
```

### 4. Lossless Conversion Pipeline

```rust
pub struct LosslessConverter {
    detectors: Vec<Box<dyn EncodingDetector>>,
    preservers: HashMap<String, Box<dyn FeaturePreserver>>,
}

pub trait FeaturePreserver {
    fn preserve(&self, feature: &TextFeature, target: Scheme) -> PreservedFeature;
    fn restore(&self, preserved: &PreservedFeature, target: Scheme) -> String;
}

impl LosslessConverter {
    pub fn convert(&self, text: &str, target: Scheme) -> ConversionResult {
        // 1. Detect encoding and features
        let detection = self.detect_encoding(text)?;
        
        // 2. Preserve features based on target scheme
        let preserved_features = self.preserve_features(&detection, &target);
        
        // 3. Convert base text
        let base_conversion = self.convert_base_text(text, &detection, &target);
        
        // 4. Merge preserved features
        let final_text = self.merge_features(base_conversion, preserved_features);
        
        ConversionResult {
            text: final_text,
            source_features: detection.features,
            preserved_features,
            is_lossless: true,
        }
    }
}
```

### 5. Scheme Registration API

```rust
pub struct SchemeRegistry {
    schemes: HashMap<String, Scheme>,
    detectors: HashMap<String, Box<dyn EncodingDetector>>,
}

impl SchemeRegistry {
    pub fn register_scheme(&mut self, scheme: Scheme) {
        self.schemes.insert(scheme.name(), scheme);
    }
    
    pub fn register_detector(&mut self, name: &str, detector: Box<dyn EncodingDetector>) {
        self.detectors.insert(name.to_string(), detector);
    }
    
    pub fn register_vedic_support(&mut self) {
        // Register all Vedic schemes and detectors
        self.register_scheme(Scheme::baraha_vedic());
        self.register_detector("baraha_vedic", Box::new(VedicBarahaDetector));
        
        // Register feature preservers
        self.register_preserver("vedic_accents", Box::new(VedicAccentPreserver));
        self.register_preserver("nasal_annotations", Box::new(NasalAnnotationPreserver));
    }
}
```

## Implementation Examples

### Example 1: Auto-detection and Conversion

```rust
let registry = SchemeRegistry::new();
registry.register_vedic_support();

let converter = LosslessConverter::new(&registry);
let text = "BaqdraM karNE#BiH SRuNuqyAma# dEvAH";

// Auto-detect and convert
let result = converter.auto_convert(text, Scheme::slp1_extended())?;

assert!(result.is_lossless);
assert_eq!(result.text, "Ba{A}draM karNE{S}BiH SRuNu{A}yAma{S} dEvAH");
```

### Example 2: Custom Scheme Definition

```rust
// Define custom Taittiriya Baraha scheme
let taittiriya_baraha = Scheme::builder()
    .base_scheme(BaseScheme::BarahaSouth)
    .add_extension(SchemeExtension {
        name: "vedic_accents".to_string(),
        mappings: hashmap! {
            "q" => "{anudatta}",
            "#" => "{svarita}",
            "$" => "{dheerga_svarita}",
        },
        preserve_during_conversion: true,
    })
    .add_extension(SchemeExtension {
        name: "nasal_annotations".to_string(),
        patterns: vec![
            Pattern::new(r"\(gm\)", "{guttural_m}"),
            Pattern::new(r"\(gg\)", "{guttural_g}"),
        ],
        preserve_during_conversion: true,
    })
    .build();

registry.register_scheme(taittiriya_baraha);
```

### Example 3: Feature-Aware Conversion

```rust
let converter = LosslessConverter::new(&registry);

// Convert with feature awareness
let result = converter.convert_with_options(
    text,
    ConversionOptions {
        target: Scheme::devanagari_vedic(),
        preserve_features: vec!["accents", "nasals"],
        accent_style: AccentStyle::UnicodeCombiners,
        validation: ValidationLevel::Strict,
    }
)?;

// Result includes feature mapping
for (original, converted) in result.feature_mappings {
    println!("{} -> {}", original, converted);
}
```

## Benefits

1. **Native Vedic support**: No preprocessing needed
2. **Extensible architecture**: Easy to add new scripts/variants
3. **Lossless by design**: Features tracked throughout pipeline
4. **Auto-detection**: Intelligent encoding discovery
5. **Backward compatible**: Existing API still works

## Migration Path

1. **Phase 1**: Implement detection framework (non-breaking)
2. **Phase 2**: Add Vedic modules as optional features
3. **Phase 3**: Integrate with main conversion pipeline
4. **Phase 4**: Deprecate simple enum-based schemes

## Python Bindings

```python
from vidyut.lipi import Scheme, LosslessConverter, VedicSupport

# Enable Vedic support
VedicSupport.register()

# Auto-detect and convert
converter = LosslessConverter()
result = converter.auto_convert(
    "aqgnim iqLE# puroqhitaM#",
    target=Scheme.SLP1_EXTENDED
)

print(result.text)  # "a{A}gnim i{A}LE{S} puro{A}hita{S}M"
print(result.is_lossless)  # True
print(result.detected_encoding)  # "baraha_vedic"
```

## Testing Strategy

```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_vedic_accent_detection() {
        let detector = VedicBarahaDetector;
        let text = "agni#m iqLE#";
        let result = detector.detect(text);
        
        assert_eq!(result.variant, Some("vedic"));
        assert!(result.features.contains_key("accents"));
    }
    
    #[test]
    fn test_round_trip_conversion() {
        let text = "aqGaSa(gm)#saq | dRu(gm)ha#sva";
        let converter = LosslessConverter::new_with_vedic_support();
        
        let slp1 = converter.convert(text, Scheme::slp1_extended())?;
        let back = converter.convert(&slp1.text, Scheme::baraha_vedic())?;
        
        assert_eq!(text, back.text);
    }
}
```

## Conclusion

These enhancements would make vidyut-lipi a comprehensive solution for Indic text processing, especially for Vedic texts. The extensible architecture allows community contributions while maintaining the library's performance and correctness guarantees.