# Vedanidhi Data Fetch Plan

## What I Need From You

### 1. **Priority Śākhās to Download**
Which śākhās should we prioritize? For example:
- Rigveda Śākala (if properly structured)
- Śukla Yajurveda (Mādhyandina/Kāṇva)
- Sāmaveda (which śākhā?)
- Atharvaveda Śaunaka

### 2. **Validation Criteria**
For each śākhā, what structure should we expect? Examples:
- Rigveda: Maṇḍala → Sūkta → Ṛk
- Taittirīya: Kāṇḍa → Prapāṭhaka → Anuvāka
- Śukla Yajurveda: Adhyāya → Verse
- Help me build a validation map

### 3. **Text Type Priorities**
Which to fetch first:
- Saṃhitā only?
- Pada pāṭha only?
- Both together?
- Brāhmaṇa/Āraṇyaka?

### 4. **Quality Thresholds**
Should we:
- Skip if no svara marks detected?
- Skip if structure seems wrong?
- Save but flag questionable data?

### 5. **API Access Details**
Do you have any specific knowledge about:
- Rate limits we should respect?
- Best time to access?
- Any authentication needs?

## My Implementation Plan

### Phase 1: Test Fetch (Need Your Input)
```python
# Example - need your priorities
TEST_TARGETS = [
    {
        'veda': '01',  # Rigveda
        'shakha': '0101',  # Śākala
        'text_type': '010101',  # Saṃhitā
        'expected_structure': ['अष्ट', 'अध्या', 'सू'],
        'sample_size': 100
    },
    # Add more based on your priorities
]
```

### Phase 2: Validation Functions
```python
def validate_vedanidhi_response(data, target):
    """
    Check:
    1. Location array matches expected Veda
    2. Structure terms match śākhā
    3. No Rigveda contamination
    4. Reasonable text diversity
    """
    pass
```

### Phase 3: Smart Fetching
- Start with small batches
- Validate immediately
- Stop if validation fails
- Log everything

## Specific Questions for You:

1. **Śākala Rigveda** - Do we want this even though we found it everywhere before?

2. **Śukla Yajurveda** - Which śākhā code? Mādhyandina or Kāṇva?

3. **Incomplete Data** - If a śākhā has only partial data (e.g., only first 3 kāṇḍas), should we:
   - Take what's available
   - Skip entirely
   - Mark as incomplete

4. **Storage Structure** - Should we maintain Vedanidhi's structure or reorganize?

5. **Existing Taittirīya** - Skip downloading from Vedanidhi since we have better data?

## Ready to Start

Once you provide the priorities and validation criteria, I can create a robust fetcher that:
- Won't repeat the previous mistakes
- Validates data before saving
- Provides clear progress/error reporting
- Can resume if interrupted

What would you like me to fetch first?