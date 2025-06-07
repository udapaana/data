# vidyut-lipi Extensibility Analysis: Moving Beyond Manual Scheme Updates

## Current State: Manual Updates Required

### What Needs Manual Changes Today

For each new source scheme, the current implementation requires:

1. **Detection Logic Updates** (`detect.rs`)
   ```rust
   // Manual addition for each new scheme
   if matches!(c, 'q' | '#' | '$' | '&') {  // Baraha-specific
       return Some(BarahaSouth);
   }
   if matches!(bigram, b"kh" | b"gh" | b"ch") {  // Hypothetical new scheme
       return Some(NewScheme);
   }
   ```

2. **Adapter Implementation** (`adapters.rs`)
   ```rust
   // Manual struct for each scheme
   pub struct NewSchemeAdapter;
   impl SchemeAdapter for NewSchemeAdapter { /* ... */ }
   ```

3. **Integration Mappings** (`integration.rs`)
   ```rust
   // Manual mapping rules for each scheme pair
   (NewScheme, Devanagari) => { /* manual mappings */ }
   (Devanagari, NewScheme) => { /* reverse mappings */ }
   ```

4. **Factory Registration** (`integration.rs`)
   ```rust
   Scheme::NewScheme => Some(Box::new(NewSchemeAdapter)),
   ```

### Problems with This Approach

1. **Code Bloat**: Each scheme adds ~100-200 lines across multiple files
2. **Maintenance Burden**: Updates require deep knowledge of codebase
3. **Testing Overhead**: Each scheme needs comprehensive test coverage
4. **Deployment Friction**: New schemes require library recompilation
5. **Contributor Barrier**: Adding schemes requires Rust expertise

## Proposed Solution: Data-Driven Extensibility

### 1. Configuration-Based Scheme Definition

Replace hardcoded logic with external configuration:

```rust
// schemes/baraha_vedic.toml
[scheme]
name = "BarahaVedic"
base_scheme = "BarahaSouth"
description = "Baraha encoding with Vedic accent markers"

[detection]
priority = 10  # Higher = checked first

[[detection.patterns]]
type = "character"
chars = ["q", "#", "$", "&"]
confidence = 0.9

[[detection.patterns]]
type = "sequence"
patterns = ["(gm)", "(gg)", "(nn)", "~M", "~j", "~g", "^^"]
confidence = 0.95

[[detection.patterns]]
type = "regex"
pattern = r"\([a-z]{2,3}\)"
confidence = 0.7

[accents]
anudatta = "q"
udatta = "#"
svarita = "#"  # Same as udatta in this scheme
dheerga_svarita = "$"
avagraha = "&"

[notations]
guttural_m = "(gm)"
guttural_g = "(gg)"
dental_n = "(nn)"
chandrabindu = "~M"
palatal_nasal = "~j"
guttural_nasal = "~g"
compound_separator = "^^"
pada_boundary = "|"
section_boundary = "||"

[mappings]
# Target scheme mappings
[mappings.devanagari]
"q" = "\u{0952}"
"#" = "\u{0951}"
"$" = "\u{0954}"
"(gm)" = "(ग्म्)"
"~M" = "ॅ"

[mappings.slp1]
"q" = "\\"
"#" = "^"
"$" = "^^"
"(gm)" = "{gm}"
"~M" = "{~M}"

[preprocessing]
# Optional text normalization rules
normalize_case = [
    ["(GM)", "(gm)"],
    ["(GG)", "(gg)"]
]

[postprocessing]
# Optional cleanup rules
preserve_case = true
```

### 2. Dynamic Scheme Loading System

```rust
pub struct SchemeRegistry {
    schemes: HashMap<String, SchemeDefinition>,
    detectors: Vec<Box<dyn SchemeDetector>>,
    adapters: HashMap<String, Box<dyn SchemeAdapter>>,
}

impl SchemeRegistry {
    pub fn load_from_directory(path: &Path) -> Result<Self, Error> {
        let mut registry = Self::new();
        
        for entry in fs::read_dir(path)? {
            let path = entry?.path();
            if path.extension() == Some("toml") {
                let config = fs::read_to_string(&path)?;
                let scheme_def: SchemeDefinition = toml::from_str(&config)?;
                registry.register_scheme(scheme_def)?;
            }
        }
        
        Ok(registry)
    }
    
    pub fn register_scheme(&mut self, def: SchemeDefinition) -> Result<(), Error> {
        // Create detector from patterns
        let detector = ConfigBasedDetector::new(&def.detection);
        self.detectors.push(Box::new(detector));
        
        // Create adapter from mappings
        let adapter = ConfigBasedAdapter::new(&def);
        self.adapters.insert(def.name.clone(), Box::new(adapter));
        
        self.schemes.insert(def.name.clone(), def);
        Ok(())
    }
}
```

### 3. Pattern-Based Detection Engine

```rust
pub trait SchemeDetector: Send + Sync {
    fn detect(&self, text: &str) -> DetectionResult;
    fn priority(&self) -> u32;
}

pub struct ConfigBasedDetector {
    patterns: Vec<DetectionPattern>,
    confidence_threshold: f32,
    priority: u32,
}

impl SchemeDetector for ConfigBasedDetector {
    fn detect(&self, text: &str) -> DetectionResult {
        let mut total_confidence = 0.0;
        let mut pattern_matches = 0;
        
        for pattern in &self.patterns {
            if let Some(confidence) = pattern.matches(text) {
                total_confidence += confidence;
                pattern_matches += 1;
            }
        }
        
        if pattern_matches > 0 {
            let avg_confidence = total_confidence / pattern_matches as f32;
            if avg_confidence >= self.confidence_threshold {
                return DetectionResult::Match {
                    scheme: self.scheme_name.clone(),
                    confidence: avg_confidence,
                };
            }
        }
        
        DetectionResult::NoMatch
    }
}

pub enum DetectionPattern {
    Character { chars: HashSet<char>, confidence: f32 },
    Sequence { patterns: Vec<String>, confidence: f32 },
    Regex { regex: Regex, confidence: f32 },
    Bigram { patterns: Vec<[u8; 2]>, confidence: f32 },
    Custom { detector: Box<dyn Fn(&str) -> Option<f32>> },
}
```

### 4. Generic Mapping Engine

```rust
pub struct ConfigBasedAdapter {
    scheme_name: String,
    mappings: HashMap<String, HashMap<String, String>>,
    accents: HashMap<AccentType, String>,
    notations: HashMap<SpecialNotation, String>,
}

impl SchemeAdapter for ConfigBasedAdapter {
    fn scheme(&self) -> Scheme {
        Scheme::from_name(&self.scheme_name)
    }
    
    fn accent_representation(&self, accent: AccentType) -> Option<String> {
        self.accents.get(&accent).cloned()
    }
    
    fn create_mappings_for(&self, target_scheme: &str) -> HashMap<String, String> {
        self.mappings.get(target_scheme).cloned().unwrap_or_default()
    }
}
```

### 5. Plugin Architecture (Advanced)

For maximum flexibility, support runtime loading:

```rust
// External crate: vidyut-lipi-kannada-vedic
pub struct KannadaVedicScheme;

impl SchemePlugin for KannadaVedicScheme {
    fn scheme_definition(&self) -> SchemeDefinition {
        SchemeDefinition {
            name: "KannadaVedic".to_string(),
            detection: DetectionRules {
                patterns: vec![
                    Pattern::Character { chars: vec!['೒', '೓'], confidence: 0.95 },
                    Pattern::Sequence { patterns: vec!["(ಗ್ಮ್)".to_string()], confidence: 0.9 },
                ],
                priority: 15,
            },
            // ... rest of definition
        }
    }
}

// In main application
fn main() {
    let mut registry = SchemeRegistry::new();
    
    // Load built-in schemes
    registry.load_from_directory("schemes/")?;
    
    // Load plugins
    registry.register_plugin(Box::new(KannadaVedicScheme))?;
    
    let lipi = Lipika::with_registry(registry);
}
```

## Benefits of Data-Driven Approach

### 1. **Zero-Code Scheme Addition**
```bash
# Add new scheme without touching Rust code
cp templates/vedic_scheme.toml schemes/malayalam_vedic.toml
# Edit the TOML file
# Restart application - new scheme available!
```

### 2. **Community Contributions**
- Scholars can contribute schemes without Rust knowledge
- TOML is human-readable and version-controllable
- Easy to review and validate new schemes

### 3. **Rapid Iteration**
- Test new detection patterns instantly
- A/B test different mapping strategies
- Adjust confidence thresholds based on data

### 4. **Validation and Testing**
```rust
#[test]
fn validate_all_schemes() {
    let registry = SchemeRegistry::load_from_directory("schemes/").unwrap();
    
    for scheme in registry.schemes() {
        // Automatic validation
        assert!(scheme.validate().is_ok());
        
        // Round-trip testing
        for test_case in &scheme.test_cases {
            assert_round_trip(&scheme, test_case);
        }
    }
}
```

### 5. **Automatic Documentation**
Generate documentation from scheme definitions:
```bash
vidyut-lipi generate-docs schemes/ > SUPPORTED_SCHEMES.md
```

## Migration Strategy

### Phase 1: Configuration Infrastructure
- Add TOML parsing and scheme definition structs
- Create `ConfigBasedDetector` and `ConfigBasedAdapter`
- Maintain backward compatibility with hardcoded schemes

### Phase 2: Convert Existing Schemes
- Export current schemes to TOML format
- Test equivalence between hardcoded and config-based versions
- Gradually replace hardcoded implementations

### Phase 3: Enhanced Features
- Add machine learning-based detection
- Support for conditional mappings
- Advanced preprocessing pipelines

### Phase 4: Plugin System
- Runtime scheme loading
- Community plugin repository
- Automatic scheme discovery

## Example: Adding a New Scheme

**Before (Manual):**
```rust
// 1. Update detect.rs (5-10 lines)
// 2. Create adapter (50-100 lines)  
// 3. Update integration.rs (20-50 lines)
// 4. Update factory (2-5 lines)
// 5. Add tests (50+ lines)
// 6. Recompile and redeploy
```

**After (Data-Driven):**
```toml
# schemes/new_manuscript_style.toml
[scheme]
name = "ManuscriptDevanagari"
description = "18th century manuscript style with unique accent marks"

[detection]
priority = 8

[[detection.patterns]]
type = "character"  
chars = ["॑", "॒", "॓", "᳚", "᳛"]
confidence = 0.9

[accents]
udatta = "॑"
anudatta = "॒"
svarita = "॓"

[mappings.devanagari]
"॑" = "॑"  # Identity mapping

[mappings.baraha_south]
"॑" = "#"
"॒" = "q"

[test_cases]
basic = ["देव॑", "अग्नि॒", "सोम॓"]
```

**Result:** New scheme available immediately without code changes!

## Conclusion

The data-driven approach transforms vidyut-lipi from a "static library with hardcoded schemes" into a "dynamic platform for transliteration schemes." This enables:

- **Scholars** to contribute schemes in their areas of expertise
- **Rapid deployment** of new manuscript discoveries  
- **Zero-downtime** scheme updates
- **Community-driven** expansion of supported texts
- **Systematic validation** of all schemes

This architectural change would make vidyut-lipi truly extensible and community-friendly while maintaining its performance and accuracy.