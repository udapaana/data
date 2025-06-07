# Alternative Sources for Vedic Texts with Svara and Pada/Saṃhitā

## 1. **Sanskrit Documents (sanskritdocuments.org)**
- **Pros**: 
  - Well-structured, maintained by scholars
  - Has both pada and saṃhitā for many texts
  - Includes accent marks (svara) for some texts
  - Free and open
- **Available**:
  - Rigveda with accents
  - Some Yajurveda texts
  - Good metadata
- **Format**: UTF-8 text files, some with ITRANS encoding

## 2. **GRETIL (Göttingen Register of Electronic Texts in Indian Languages)**
- **URL**: http://gretil.sub.uni-goettingen.de/
- **Pros**:
  - Academic quality
  - Multiple śākhās available
  - Some texts have svara notation
- **Available**:
  - Rigveda Śākala
  - Śukla Yajurveda (Mādhyandina & Kāṇva)
  - Sāmaveda collections
  - Atharvaveda Śaunaka
- **Format**: Various encodings, needs conversion

## 3. **Maharishi University Vedic Literature Collection**
- **URL**: https://vedicreserve.miu.edu/
- **Pros**:
  - Complete texts with proper encoding
  - Authentic śākhā divisions maintained
  - Some with audio recordings
- **Available**:
  - Multiple Yajurveda śākhās
  - Good Sāmaveda resources
- **Note**: May require permission/registration

## 4. **TITUS (Thesaurus Indogermanischer Text- und Sprachmaterialien)**
- **URL**: http://titus.uni-frankfurt.de/
- **Pros**:
  - Academic standard texts
  - Rigveda with full accent marks
  - Pada pāṭha available
  - Well-documented encoding
- **Available**:
  - Rigveda with Padapāṭha
  - Various Brāhmaṇa texts
- **Format**: Custom encoding, needs conversion

## 5. **Sacred Texts Archive (sacred-texts.com)**
- **Pros**:
  - Ralph T.H. Griffith translations alongside Sanskrit
  - Some texts have transliterated Sanskrit
- **Cons**:
  - Not always with svara
  - Mixed quality
- **Best for**: Cross-referencing

## 6. **Vedic Heritage Portal (vedicheritage.gov.in)**
- **Pros**:
  - Government of India project
  - Audio with text
  - Authentic pronunciations
- **Available**:
  - Select śākhās with audio
  - Teaching materials
- **Note**: More focused on preservation than bulk data

## 7. **Local Manuscript Collections**
### French Institute of Pondicherry
- Excellent Śaiva/Vaiṣṇava texts
- Some Vedic manuscripts digitized

### Muktabodha Digital Library
- **URL**: https://www.muktabodha.org/
- Searchable manuscripts
- Some Vedic texts with accents

## Recommended Approach for Udapaana

### Priority 1: GRETIL + Sanskrit Documents
These two sources combined would give:
- Rigveda Śākala (complete with svara)
- Śukla Yajurveda Mādhyandina
- Śukla Yajurveda Kāṇva
- Sāmaveda Kauthuma
- Atharvaveda Śaunaka

### Priority 2: TITUS for Rigveda
- Best quality Rigveda with full accents
- Properly encoded Padapāṭha
- Academic standard

### Priority 3: Maharishi University
- For additional śākhās
- Good audio resources

## Technical Considerations

### Encoding Conversions Needed
1. **ITRANS → Devanagari**: Sanskrit Documents
2. **Harvard-Kyoto → Devanagari**: Some GRETIL texts
3. **Custom academic → UTF-8**: TITUS
4. **ISO-15919 → Devanagari**: Various sources

### Svara Notation Systems
Different sources use different accent marking:
1. **Vedic Unicode**: U+0951, U+0952 (udātta, anudātta)
2. **ITRANS**: Capital letters, special markers
3. **Harvard-Kyoto**: Numbers and special characters
4. **Visual marks**: Vertical lines, dots

## Data Quality Verification

For each source, verify:
1. **Svara completeness**: Not just partial marking
2. **Pada-Saṃhitā alignment**: Both versions match
3. **Text completeness**: No missing sections
4. **Encoding consistency**: Throughout the text
5. **Authentic śākhā**: Not mixed traditions

## Implementation Strategy

```python
# Example structure for multi-source integration
sources/
├── gretil/
│   ├── rigveda/
│   ├── yajurveda/
│   └── processing_scripts/
├── sanskrit_documents/
│   ├── raw/
│   └── converters/
├── titus/
│   └── rigveda_accented/
└── unified_processor.py
```

Would you like me to start implementing parsers for any of these sources?