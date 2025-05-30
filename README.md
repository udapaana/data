# Data Directory

This directory contains all Vedic text data for the Udapaana project.

## Structure

```
data/
├── vedanidhi_complete/    # Primary source - accented texts from vedanidhi.org
├── taittiriya/           # Legacy DOCX source - no accents
├── unified_corpus/       # Archived - contained corrupted data
└── vedic_corpus.sqlite   # SQLite database (to be rebuilt)
```

## Active Downloads

Currently downloading from Vedanidhi:
- Status: 58/107 sources complete
- Check: `python3 ../check_download_status.py`

## Data Quality

- **vedanidhi_complete**: Has accent marks (svara), suitable for adhyayana
- **taittiriya**: Clean text but NO accents, reference only
- **unified_corpus**: CORRUPTED - all śākhās contained Rigveda data

## See Also

- [Master Tracker](../VEDIC_TEXT_TRACKER.md) - Status of all texts
- [Data Organization](../DATA_ORGANIZATION.md) - Detailed structure
- [Source Inventory](../SOURCE_INVENTORY.md) - All data sources