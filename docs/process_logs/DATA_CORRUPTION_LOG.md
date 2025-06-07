# Data Corruption Issue Log

## Date: May 28, 2025

### Issue Summary
All Vedanidhi downloaded data contains only Rigveda content, regardless of the intended Veda/Śākhā.

### Update: Source Evaluation
1. **Vedanidhi Status**: Has good data but frustratingly organized. Many placeholders, but authentic content where available.
2. **Academic Sources**: Not suitable for adhyayana due to metric restoration and critical editions
3. **Best Practice**: Use traditional sources only - no academic "corrections"

### Evidence
1. **Identical record counts**: Every śākhā shows exactly 55,820 total records
2. **Wrong location structure**: All files show Rigveda structure (01 ऋ, अष्ट, अध्या, सू)
3. **Duplicate content**: Same mantras appear across different Vedas
4. **SQLite corruption**: Database built from this data shows 22,836 texts for every śākhā

### Affected Data
- `/data/vedanidhi/raw/` - All downloaded files
- `/data/unified_corpus/` - All processed batches
- `/data/vedic_corpus.sqlite` - Entire database

### Impact
- No authentic Samaveda data
- No authentic Atharvaveda data  
- No authentic Yajurveda data (except Taittirīya from DOCX)
- Misleading unified corpus with false uniformity

### Root Cause Analysis
Need to investigate:
1. Download script logic
2. API endpoint configuration
3. Data validation during download
4. Why the same data was saved for different Vedas

### Unaffected Data
- `/data/taittiriya/` - Personal DOCX collection remains valid
- 4,903 authentic Taittirīya texts with proper structure

### Next Steps
1. Delete all corrupted Vedanidhi data
2. Investigate download scripts
3. Implement proper validation
4. Re-download with verification
5. Rebuild SQLite with clean data