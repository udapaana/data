# Available Accented Texts for Adhyayana

## Currently Available (High Quality)

### 1. Taittirīya Śākhā (Kṛṣṇa Yajurveda) ✅
- **Source**: Personal DOCX collection with Baraha encoding
- **Svara**: Full accent marks preserved
- **Coverage**: Complete corpus (4,903 texts)
  - Saṃhitā: 2,198 verses with pada/saṃhitā
  - Brāhmaṇa: 1,997 sections  
  - Āraṇyaka: 708 sections
- **Quality**: Excellent for adhyayana
- **Location**: `data/taittiriya_backup/`

## Potential Sources for Other Śākhās

### Traditional Digital Sources
1. **Sanskrit Documents (sanskritdocuments.org)**
   - Some texts have svara marks
   - Need to verify each text individually
   - Often in ITRANS or custom encoding

2. **Vedic Heritage Portal (vedicsciences.net)**
   - Traditional texts with accents
   - Limited coverage but high quality

3. **Audio-Text Correlations**
   - Many pāṭhaśālās have recordings with text
   - Can extract accented text from teaching materials

### What We DON'T Want
- ❌ GRETIL texts (mostly unaccented academic editions)
- ❌ Critical editions without svara
- ❌ Reconstructed texts
- ❌ Plain transliterations without accent marks

## Immediate Action Plan

### Phase 1: Use What We Have
1. **Taittirīya Śākhā** - Ready to use immediately
2. Build VedaVid to work with this first
3. Design system to accommodate other śākhās as they become available

### Phase 2: Targeted Collection
1. Contact traditional sources directly:
   - Vedapatashalas with digital archives
   - Traditional publishers (Sringeri, Kanchi, etc.)
   - Individual pandits with manuscript collections

2. Verify svara marks before including ANY text

### Phase 3: Community Contribution
1. Build upload system for verified texts
2. Allow traditional reciters to contribute
3. Peer review by qualified pandits

## Technical Requirements for Accented Texts

### Encoding Support Needed
1. **Vedic Unicode Block** (U+1CD0 to U+1CFF)
   - Udātta, anudātta, svarita marks
   - Vedic tone marks
   
2. **Common Encodings to Support**
   - Baraha (as in our Taittirīya texts)
   - ITRANS with accent extensions
   - Harvard-Kyoto with accent marks
   - Direct Unicode

### Storage Format
```json
{
  "text": "अग्निमीळे पुरोहितं",
  "svara_marked": true,
  "encoding": "baraha|unicode|itrans",
  "accents": {
    "system": "taittiriya|rgvedic|maitrayaniya",
    "marks": ["udatta", "anudatta", "svarita", "pracaya"]
  }
}
```

## Conclusion

Since unaccented texts are useless for adhyayana, we should:

1. **Start with Taittirīya** - We have excellent accented data
2. **Be very selective** - Only add texts with proper svara marks
3. **Reject academic sources** - Unless they preserve traditional accents
4. **Build incrementally** - Better to have one complete śākhā than many incomplete ones

The focus should be on quality over quantity - one properly accented text is worth more than a hundred unaccented ones for recitation learning.