# Hierarchical Vedic Text Organization

## Structure

```
vedic_texts/
├── rigveda/
│   └── shakala/
│       └── vedanidhi/
│           ├── samhita/
│           │   ├── raw/
│           │   ├── parsed/
│           │   └── scripts/
│           ├── brahmana/
│           └── aranyaka/
│
├── samaveda/
│   └── kauthuma/
│       └── vedanidhi/
│           ├── samhita/
│           └── brahmana/
│
├── yajurveda/
│   └── taittiriya/
│       ├── vedavms/
│       │   ├── samhita/
│       │   │   ├── raw/        # DOCX files
│       │   │   ├── parsed/     # JSON processed
│       │   │   └── scripts/    # Processing tools
│       │   ├── brahmana/
│       │   └── aranyaka/
│       └── vedanidhi/
│           ├── samhita/
│           └── brahmana/
│
└── atharvaveda/
    └── shaunaka/
        └── vedanidhi/
            ├── samhita/
            └── brahmana/
```

## Benefits

1. **True Hierarchy**: Veda → Śākhā → Source → Text Type → Processing Stage
2. **Source Separation**: Each source has its own space
3. **Processing Stages**: Raw → Parsed → Scripts clearly separated
4. **Extensible**: Easy to add new Vedas, śākhās, sources, text types
5. **Future Ready**: Space for Dharmasūtras, Śrautasūtras, etc.

## Text Type Categories

- **samhita**: Mantras (verses)
- **brahmana**: Ritual explanations (prose)
- **aranyaka**: Forest texts (philosophical)
- **upanishad**: Philosophical texts (grouped with aranyaka)
- **dharmasutra**: Legal texts (future)
- **shrautasutra**: Ritual manuals (future)
- **grhyasutra**: Domestic rituals (future)

## Processing Stages

- **raw**: Original files (DOCX, XML, etc.)
- **parsed**: Processed JSON with metadata
- **scripts**: Source-specific processing tools
