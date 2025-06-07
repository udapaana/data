# Unified Data Structure for Vedic Texts

## Overview

This document defines the common data structure for storing Vedic texts across all śākhās while preserving their unique organizational traditions. The structure emerges from the transformation pipeline and serves as the foundation for all applications.

## Design Principles

1. **Śākhā Authenticity**: Preserve traditional hierarchical organization of each śākhā
2. **Cross-Compatibility**: Enable cross-śākhā searching and comparison
3. **Accent Preservation**: Full fidelity accent information in Extended Baraha ASCII
4. **Transformation Auditing**: Complete provenance from source to final format
5. **Extensibility**: Support for future śākhās and text types

## Core Structure Schema

### Top-Level Document
```json
{
  "corpus_metadata": {
    "veda": "yajurveda",
    "sakha": "taittiriya", 
    "source": "vedavms",
    "text_type": "samhita",
    "version": "1.0",
    "created": "2025-05-29T...",
    "total_texts": 2198,
    "transformation_id": "tf_20250529_001"
  },
  "transformation_history": {
    "pipeline_version": "1.0",
    "stages_completed": ["01_source_extraction", "02_text_normalization", ...],
    "final_stage": "07_final_format",
    "audit_trail": "transformations/transformation_summary.json"
  },
  "accent_system": {
    "encoding": "extended_baraha_ascii",
    "version": "1.0",
    "coverage": 1.0,
    "special_features": ["regional_variants", "pada_format"]
  },
  "hierarchy_schema": {
    "type": "taittiriya_traditional",
    "levels": ["kanda", "prapathaka", "anuvaka", "mantra"],
    "addressing": "hierarchical_dot_notation"
  },
  "texts": [
    // Array of text objects
  ]
}
```

### Text Object Schema
```json
{
  "text_id": "ts_1_1_1_1",
  "hierarchy": {
    "kanda": 1,
    "prapathaka": 1, 
    "anuvaka": 1,
    "mantra": 1,
    "canonical_address": "TS 1.1.1.1",
    "traditional_address": "तैत्तिरीयसंहिता प्रथमकाण्डे प्रथमप्रपाठके प्रथमानुवाके प्रथममन्त्रे"
  },
  "content": {
    "eba_text": "य\श्चिद्धी\+++र् दे/वे\ष्व^प्र\था इ\यंत न\ प्र/वे\दा",
    "devanagari": "य॑श्चिद्धी॒रो दे॑वेष्व॒प्रथा॑ इ॒यं त॑न॒ प्र॑वेदा",
    "transliteration": "yaśhiddhīro deveṣvaprathā iyaṃ tan praved a",
    "word_boundaries": ["यश्चित्", "धीरः", "देवेषु", "अप्रथाः", "इयम्", "तत्", "प्रवेद"],
    "pada_format": "य॑श्चित् | धी॒रो | दे॑वेषु | अ॒प्रथा॑ः | इ॒यम् | त॑त् | प्र॑वेद",
    "syllable_count": 11,
    "metrical_pattern": "jagati"
  },
  "variants": [
    {
      "type": "regional",
      "tradition": "andhra",
      "eba_text": "य\श्चिद्धी\+++र् दे/वे\ष्व^प्र\था इ\यंत न\ प्र/वे\दा",
      "notes": "Standard Andhra pronunciation"
    },
    {
      "type": "regional", 
      "tradition": "dravida",
      "eba_text": "य\श्चिद्धी\+++र् दे/वे\ष्व^प्र\था इ\यंत न\ प्र/वे\दा",
      "notes": "Dravidian regional variant"
    }
  ],
  "metadata": {
    "ritual_context": "agnihotra",
    "deity": "agni",
    "rishi": "vishvamitra",
    "chandas": "jagati",
    "svara_notes": "complex_accent_pattern",
    "traditional_commentaries": ["sayana", "bhatta_bhaskara"]
  },
  "cross_references": {
    "parallel_passages": [
      {"text_id": "rv_1_1_1", "similarity": 0.85, "type": "source"},
      {"text_id": "ms_1_1_1", "similarity": 0.92, "type": "parallel_tradition"}
    ],
    "ritual_connections": [
      {"text_id": "ts_1_1_2_1", "relationship": "sequential_ritual"},
      {"text_id": "tb_1_1_1_1", "relationship": "brahmana_explanation"}
    ]
  },
  "source_provenance": {
    "original_file": "TS 1 Baraha.docx",
    "extraction_timestamp": "2025-05-29T...",
    "page_reference": "page_1_paragraph_3",
    "quality_score": 0.98,
    "human_validated": true
  }
}
```

## Śākhā-Specific Adaptations

### Ṛgveda Śākala
```json
{
  "hierarchy_schema": {
    "type": "rigveda_shakala",
    "levels": ["mandala", "sukta", "rik"],
    "addressing": "mandala.sukta.rik"
  },
  "content": {
    "metrical_analysis": "detailed",
    "rishi_lineage": "traditional_attribution",
    "devata_classification": "comprehensive"
  }
}
```

### Sāmaveda Kauthuma  
```json
{
  "hierarchy_schema": {
    "type": "samaveda_kauthuma",
    "levels": ["parvan", "adhyaya", "khanda", "gana"],
    "addressing": "parvan.adhyaya.khanda.gana"
  },
  "content": {
    "gana_notation": "full_musical_marks",
    "stobha_elements": "explicit_marking",
    "elongation_patterns": "multi_level"
  },
  "musical_metadata": {
    "raga_hints": "traditional_associations",
    "tempo_markers": "pause_and_transition",
    "performance_notes": "ritual_context"
  }
}
```

### Atharvaveda Śaunaka
```json
{
  "hierarchy_schema": {
    "type": "atharvaveda_shaunaka", 
    "levels": ["kanda", "sukta", "mantra"],
    "addressing": "kanda.sukta.mantra"
  },
  "content": {
    "magical_classification": "abhichara_paushti_shanti",
    "practical_applications": "ritual_use_cases",
    "folk_connections": "traditional_practices"
  }
}
```

## Processing Workflow

### 1. Source → Transformations
```
source/TS_1_Baraha.docx → transformations/01_source_extraction/extracted_text.json
```

### 2. Iterative Pipeline  
```
01_source_extraction → 02_text_normalization → 03_accent_standardization →
04_structure_mapping → 05_cross_references → 06_validation → 07_final_format
```

### 3. Final Output
```
transformations/07_final_format/final_corpus.json → parsed/taittiriya_samhita_unified.json
```

## Quality Assurance Standards

### Accent Accuracy
- Round-trip conversion testing (source → EBA → display format)
- Traditional scholar validation  
- Cross-śākhā consistency checking

### Structural Integrity
- Hierarchical completeness validation
- Cross-reference link validation
- Metadata consistency checking

### Source Fidelity
- Original text preservation verification
- Transformation audit trail completeness
- Human expert validation checkpoints

## API Integration Points

### Text Retrieval
```javascript
// Get specific text
gettext("ts_1_1_1_1") → complete text object

// Get hierarchical range  
getTextRange("ts_1_1") → all texts in Kāṇḍa 1, Prapāṭhaka 1

// Cross-śākhā search
searchAcrossCorpora("agni", ["rigveda", "yajurveda"]) → matching texts
```

### Accent Processing
```javascript
// Convert EBA to display format
ebaToDevanagari("य\श्चिद्धी\र्") → "य॑श्चिद्धी॒र्"

// Extract accent patterns
getAccentPattern("ts_1_1_1_1") → [udatta, anudatta, svarita, ...]
```

### Cross-Reference Navigation
```javascript
// Get parallel passages
getParallels("ts_1_1_1_1") → [rv_1_1_1, ms_1_1_1, ...]

// Navigate ritual sequence
getRitualSequence("ts_1_1_1_1") → [previous, current, next]
```

## Migration Path

### Phase 1: VedaVMS (Complete)
- Taittirīya Saṃhitā, Brāhmaṇa, Āraṇyaka
- Full accent coverage with regional variants
- Complete transformation pipeline

### Phase 2: Vedanidhi Integration
- Ṛgveda, Sāmaveda, Atharvaveda texts
- Partial accent data standardization
- Cross-śākhā reference building

### Phase 3: Enhancement
- Additional sources integration
- Scholar validation processes
- Advanced cross-reference detection

## File Organization

```
data/vedic_texts/{veda}/{sakha}/{source}/{text_type}/
├── source/                    # Original files
├── transformations/           # Complete pipeline with logging
│   ├── 01_source_extraction/
│   ├── 02_text_normalization/
│   ├── 03_accent_standardization/
│   ├── 04_structure_mapping/
│   ├── 05_cross_references/
│   ├── 06_validation/
│   └── 07_final_format/
└── parsed/                    # Final unified format
    └── {sakha}_{text_type}_unified.json
```

This unified structure preserves the authenticity of each śākhā while enabling powerful cross-textual analysis and modern digital access patterns.