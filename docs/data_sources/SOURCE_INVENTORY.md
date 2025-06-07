# Vedic Text Source Inventory

## Current Sources

### 1. Vedanidhi (vedanidhi.org)
- **Type**: Web portal with AJAX API
- **Coverage**: All four Vedas, multiple śākhās
- **Quality**: Generally good, ~70-98% accent coverage
- **Access**: Requires authentication cookies
- **Status**: Downloading (58/107 completed)

#### Advantages
- Comprehensive collection
- Proper accent marks (svara)
- Hierarchical organization
- Free access

#### Issues
- Some duplicate content
- Validation failures for some texts
- Mixed śākhā content in some cases

### 2. Local DOCX Collection (Taittirīya)
- **Type**: Microsoft Word files (Baraha encoded)
- **Coverage**: Complete Taittirīya śākhā only
- **Quality**: Good text, NO accents
- **Access**: Already available
- **Status**: Fully processed

#### Advantages
- Complete corpus
- Clean text
- Includes regional variants

#### Issues
- No accent marks
- Single śākhā only
- Proprietary encoding

## Potential Sources (To Investigate)

### 3. GRETIL (Göttingen Register of Electronic Texts in Indian Languages)
- **URL**: http://gretil.sub.uni-goettingen.de/
- **Coverage**: Wide range of Sanskrit texts
- **Quality**: Academic transcriptions
- **Format**: Various (HTML, TXT, TEI)
- **Priority**: HIGH

### 4. Sanskrit Documents (sanskritdocuments.org)
- **URL**: https://sanskritdocuments.org/
- **Coverage**: Vedic and classical texts
- **Quality**: Community maintained
- **Format**: Multiple (PDF, HTML, ITRANS)
- **Priority**: HIGH

### 5. Muktabodha Digital Library
- **URL**: https://www.muktabodha.org/
- **Coverage**: Manuscripts and texts
- **Quality**: Scanned manuscripts + transcriptions
- **Format**: PDF, searchable texts
- **Priority**: MEDIUM

### 6. TITUS (Thesaurus Indogermanischer Text- und Sprachmaterialien)
- **URL**: http://titus.uni-frankfurt.de/
- **Coverage**: Indo-European texts including Vedic
- **Quality**: Academic standard
- **Format**: Custom encoding
- **Priority**: MEDIUM

### 7. Sacred Texts Archive
- **URL**: https://www.sacred-texts.com/hin/
- **Coverage**: English translations + some originals
- **Quality**: Older digitizations
- **Format**: HTML
- **Priority**: LOW (mainly translations)

### 8. Vedic Heritage Portal (vedicheritage.gov.in)
- **URL**: http://vedicheritage.gov.in/
- **Coverage**: Government portal
- **Quality**: Unknown
- **Format**: Unknown
- **Priority**: MEDIUM

### 9. Regional Manuscript Libraries

#### Saraswathi Mahal Library, Thanjavur
- **Coverage**: South Indian manuscripts
- **Quality**: Original manuscripts
- **Access**: Limited digital access
- **Priority**: HIGH for Taittirīya variants

#### Oriental Research Institute, Mysore
- **Coverage**: Karnataka manuscripts
- **Quality**: Critical editions
- **Access**: Some digitization
- **Priority**: HIGH for Kṛṣṇa Yajurveda

#### Bhandarkar Oriental Research Institute, Pune
- **Coverage**: Wide collection
- **Quality**: Critical editions
- **Access**: Limited online
- **Priority**: HIGH for critical texts

### 10. Traditional Pāṭhaśālā Sources

#### Audio Recordings
- Various YouTube channels
- Vedic learning apps
- Traditional school recordings
- **Priority**: MEDIUM (for pronunciation reference)

## Source Evaluation Criteria

### Essential Requirements
1. **Accent marks** (svara) - MANDATORY for adhyayana
2. **Authentic text** - No reconstructions
3. **Complete texts** - Not fragments
4. **Clear śākhā identification**

### Quality Metrics
- A: Full accents, critical edition
- B: Full accents, single source
- C: Partial accents
- D: No accents but authentic
- F: Unsuitable (no accents, reconstructed)

## Source Acquisition Priority

### Immediate (Currently downloading)
1. Complete Vedanidhi download
2. Process validation failures

### High Priority
1. **Śukla Yajurveda** (Mādhyandina)
   - Check: GRETIL, Sanskrit Documents
   - Most widely used tradition
   
2. **Complete Atharvaveda** (Śaunaka)
   - Resolve Vedanidhi issues
   - Check: GRETIL
   
3. **Maitrāyaṇī Saṃhitā**
   - Check: GRETIL, TITUS
   - Important Kṛṣṇa YV tradition

### Medium Priority
1. **Jaiminīya Sāmaveda**
   - Check: Kerala manuscripts
   - Unique musical tradition
   
2. **Paippalāda Atharvaveda**
   - Check: Orissa manuscripts
   - Different recension
   
3. **Prātiśākhyas**
   - Check: Academic sources
   - Phonetic treatises

### Future Exploration
1. Brāhmaṇa texts (other śākhās)
2. Āraṇyakas (complete set)
3. Vedāṅga texts
4. Commentaries (Sāyaṇa, etc.)

## Technical Considerations

### Download Methods
1. **Web scraping**: For HTML sources
2. **API access**: For structured data
3. **PDF extraction**: For manuscript scans
4. **Manual entry**: For small texts

### Processing Requirements
1. **Encoding conversion**: ITRANS, Velthuis, etc.
2. **Accent restoration**: From manuscripts
3. **Variant collation**: Multiple sources
4. **Quality validation**: Automated checks

## Next Steps

1. **Complete current downloads**
   - Vedanidhi: 49 sources remaining
   - Monitor validation issues

2. **Evaluate GRETIL**
   - Check Vedic section
   - Assess accent availability
   - Test download methods

3. **Survey Sanskrit Documents**
   - Identify Vedic texts
   - Check encoding formats
   - Evaluate quality

4. **Create automated scrapers**
   - For each major source
   - With validation built-in
   - Respecting rate limits

5. **Build source comparison tools**
   - Cross-reference same texts
   - Identify best versions
   - Flag discrepancies