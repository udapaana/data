# Data Collection Strategy for Udapaana

## Current Status

### Available High-Quality Data
1. **Taittirīya Śākhā (Kṛṣṇa Yajurveda)** ✅
   - Source: Personal DOCX collection
   - Quality: Excellent (manually verified)
   - Coverage: Complete (4,903 texts)
   - Structure: Authentic Kāṇḍa/Prapāṭhaka/Anuvāka hierarchy preserved
   - Components: Saṃhitā (2,198), Brāhmaṇa (1,997), Āraṇyaka (708)

### Corrupted Data Sources
1. **Unified Corpus** ❌
   - All śākhās show Rigveda structure (contamination)
   - Total: 91,344 texts (all corrupted)
   - Issue: Processing destroyed authentic hierarchical structures

2. **Vedanidhi API** ⚠️
   - API access requires authentication
   - Previous downloads resulted in Rigveda contamination
   - Structure unclear, quality unknown

## Data Collection Plan

### Phase 1: Preserve What We Have
1. **Taittirīya Data**
   - Use existing high-quality data from `data/taittiriya_backup/`
   - Already properly structured and validated
   - Ready for immediate use in VedaVid

### Phase 2: Academic Sources (With Annotation)
Since the user confirmed academic sources can be used with proper annotation:

1. **GRETIL (Göttingen Register of Electronic Texts in Indian Languages)**
   - URL: http://gretil.sub.uni-goettingen.de/
   - Coverage: Multiple śākhās
   - Note: May have metric restoration, needs annotation

2. **Sanskrit Documents**
   - URL: https://sanskritdocuments.org/
   - Coverage: Various Vedic texts
   - Format: Multiple encodings available

3. **TITUS (Thesaurus Indogermanischer Text- und Sprachmaterialien)**
   - URL: http://titus.uni-frankfurt.de/
   - Coverage: Indo-European texts including Vedic
   - Quality: Academic standard

4. **Muktabodha Digital Library**
   - URL: https://www.muktabodha.org/
   - Coverage: Manuscript scans and searchable texts
   - Focus: Tantric and Vedic texts

### Phase 3: Direct Sources
1. **Traditional Pāṭhaśālās**
   - Contact traditional Vedic schools
   - Request digital texts or recordings
   - Ensure authentic transmission

2. **Government Repositories**
   - National Mission for Manuscripts
   - State Sanskrit academies
   - University Sanskrit departments

## Data Quality Requirements

### For Adhyayana (Study/Recitation)
1. **MUST have svara (accent) marks** - No unaccented texts
2. **No metric restoration** (academic reconstructions)
3. **Preserve authentic śākhā structures**
4. **Maintain pada/saṃhitā pāṭha distinctions**
5. **Regional variants marked but not merged**
6. **Traditional transmission only** - No critical editions

### Annotation Schema for Academic Sources
```json
{
  "source_metadata": {
    "type": "academic",
    "modifications": ["metric_restoration", "critical_apparatus"],
    "suitable_for": ["research", "comparison"],
    "adhyayana_suitable": false,
    "notes": "Contains editorial reconstructions"
  }
}
```

## Implementation Steps

### Step 1: Inventory Available Sources
Create comprehensive list of:
- What we have (quality data)
- What's corrupted (needs cleaning)
- What's available (external sources)

### Step 2: Create Source-Specific Parsers
Each source needs custom parser respecting:
- Original encoding (IAST, Harvard-Kyoto, etc.)
- Structural organization
- Metadata format
- Quality indicators

### Step 3: Build Validation Pipeline
- Verify Veda/Śākhā attribution
- Check for cross-contamination
- Validate hierarchical structure
- Flag academic modifications

### Step 4: Unified Storage Format
```json
{
  "text_id": "unique_identifier",
  "veda": "name",
  "shakha": "name",
  "authentic_hierarchy": {
    // Śākhā-specific structure
  },
  "source": {
    "origin": "source_name",
    "quality": "traditional|academic|unknown",
    "modifications": [],
    "adhyayana_suitable": true|false
  },
  "content": {
    "primary": "text",
    "variants": []
  }
}
```

## Priority Sources by Śākhā

### Rigveda
1. GRETIL Śākala Saṃhitā (with annotation)
2. Sanskrit Documents collection
3. Vedanidhi (if accessible)

### Yajurveda
1. ✅ Taittirīya - Already have quality data
2. Maitrāyaṇī - GRETIL/Sanskrit Documents
3. Śukla - VSM edition from GRETIL

### Sāmaveda
1. Kauthuma - Sanskrit Documents
2. Jaiminīya - Academic sources

### Atharvaveda
1. Śaunaka - GRETIL
2. Paippalāda - Limited availability

## Next Actions

1. ✅ Use existing Taittirīya data immediately
2. Create parser for GRETIL texts
3. Build academic source annotation system
4. Implement validation pipeline
5. Clean SQLite database with validated data