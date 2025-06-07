# Vedic Text Encoding Analysis

## Overview
This document analyzes the encoding patterns used across different Vedic text sources in the udapaana project, focusing on how accents and special characters are represented.

## 1. Taittirīya Yajurveda (VedaVMS Source)

### Encoding Pattern
- **Script**: Extended Baraha ASCII (EBA)
- **Accent Marks**:
  - Udātta (high tone): `#` after the syllable
  - Anudātta (low tone): `q` after the syllable
  - Svarita (falling tone): Combinations like `iq`, `Eq`, etc.
  - Double accents: `##`
  
### Examples:
```
iqShE tvAq | UqrjE tvAq | vAqyava#H
yaqj~jasya# | GOqShat | aqsiq | pratyu#ShTaqm
```

### Special Characters:
- Anusvāra: `M`
- Visarga: `H`
- Avagraha: `&`
- Halanta: `q` (also used for anudātta)
- Nasalized vowels: `(gm)`, `(gg)` for different nasal types

## 2. Taittirīya Yajurveda (Vedanidhi Source)

### Encoding Pattern
- **Script**: Devanagari with inline accent marks
- **Accent Marks**:
  - Udātta: `.` after the syllable
  - Anudātta: `ˆ` after the syllable
  - Combined accents appear inline

### Examples:
```
वायु.र्वै क्षेपिष्ठा देवता
सˆ एवैनं भूति.ङ्गमयति
प्राणो वै वायु.-रपानो नियु.
```

## 3. Ṛgveda (Vedanidhi Source)

### Encoding Pattern
- Similar to Taittirīya Vedanidhi
- Uses Devanagari with inline accent marks
- Udātta and anudātta marked similarly

## 4. Sāmaveda (Vedanidhi Source)

### Encoding Pattern
- **Script**: Devanagari with special Sāmavedic notations
- **Accent Marks**:
  - Uses standard Vedic accent marks
  - Additional musical notations with spaces and special characters
  
### Examples:
```
अग्न आ याहि वीतये
त्व मग्ने यज्ञाना होता
अग्नि न्दूतँ वृणीमहे
```

### Unique Features:
- Sāmaveda includes musical notation marks
- Spaces within words indicate prolongation or musical breaks
- Special marks like `~` for specific musical notes

## 5. Atharvaveda (Vedanidhi Source)

### Encoding Pattern
- **Script**: Devanagari with inline accent marks
- **Accent Marks**:
  - Similar to other Vedanidhi sources
  - Uses `.` for udātta, `ˆ` for anudātta
  
### Examples:
```
वेन.स्त.त्पश्य.त्परम.ङ्गुहा
सˆ न पिता जनिता सˆ उत बन्धु
```

## Common Patterns Across Sources

### 1. VedaVMS Sources (Baraha)
- Use ASCII-based encoding
- Accents marked with specific characters (#, q)
- Consistent across all texts from this source
- Easy to process programmatically

### 2. Vedanidhi Sources (All Vedas)
- Use Devanagari script
- Inline accent marks (., ˆ)
- More visually accurate representation
- Requires Unicode processing

## Unique Features by Śākhā

### Taittirīya (Yajurveda)
- Most comprehensive accent marking
- Both Baraha and Devanagari versions available
- Clear distinction between different accent types

### Śākala (Ṛgveda)
- Standard Vedic accent notation
- Focus on preservation of traditional markings

### Kauthuma (Sāmaveda)
- Musical notation integrated with text
- Special spacing for musical purposes
- Additional marks beyond standard accents

### Śaunaka (Atharvaveda)
- Similar to Ṛgveda in accent marking
- Consistent use of standard Vedic notation

## Technical Considerations

1. **Encoding Conversion**:
   - Baraha to Unicode conversion needed for VedaVMS
   - Accent marks need special handling
   - Preserve original accent information

2. **Data Validation**:
   - Check for consistency in accent marking
   - Validate special character usage
   - Ensure proper Unicode representation

3. **Processing Pipeline**:
   - Different parsers needed for Baraha vs Devanagari
   - Accent extraction and standardization
   - Unified output format required

## Recommendations

1. Create separate parsers for Baraha and Devanagari sources
2. Develop accent standardization module
3. Implement validation for each encoding type
4. Create mapping tables for accent conversions
5. Preserve original encoding information in metadata