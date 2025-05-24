# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a data repository for Taittiriya texts, which are part of the Vedic Sanskrit corpus. The repository stores and processes Sanskrit texts through a structured pipeline.

## Directory Structure

- `raw/` - Contains source documents in DOCX format
  - `samhita/` - Samhita texts (continuous recitation format)
  - `padam/` - Pada texts (word-by-word format)
- `parsed/` - Contains processed JSON outputs from raw texts

## Data Processing Pipeline

The repository follows a pattern where:
1. Raw Sanskrit texts are stored as DOCX files in `raw/`
2. These are processed into structured JSON format in `parsed/`
3. Texts are organized by recitation style (samhita vs pada)

## File Naming Convention

- Raw files follow pattern: `TS X.Y Baraha [Type] paatam.docx` where:
  - TS = Taittiriya Samhita
  - X.Y = Chapter/section numbers
  - Baraha = Script/encoding type
  - Type = Pada (word-by-word) or omitted for Samhita (continuous)

## Text Processing

This repository contains a complete parsing pipeline for Taittiriya Sanskrit texts:

### Processing Scripts
- `enhanced_parser.py` - Enhanced samhita/padam parser with multi-kanda support
- `brahmana_aranyaka_parser.py` - Specialized parser for brahmana and aranyaka texts
- `create_complete_dataset.py` - Creates unified corpus combining all text types
- `create_enhanced_web_format.py` - Generate samhita/padam web formats
- `create_brahmana_aranyaka_web_format.py` - Generate brahmana/aranyaka web formats
- **`add_static_transliterations.py` - Add static transliterations using vidyut-lipi**

### Transliteration System
- **Static transliterations** using vidyut-lipi (preferred) or indic-transliteration (fallback)
- Supports 13 scripts: Devanagari, IAST, Harvard-Kyoto, Tamil, Telugu, etc.
- Pre-generated for better performance and quality
- See `TRANSLITERATION_README.md` for details

### Commands
- Parse samhita/padam: `python3 enhanced_parser.py`
- Parse brahmana/aranyaka: `python3 brahmana_aranyaka_parser.py`
- Create complete corpus: `python3 create_complete_dataset.py`
- **Add transliterations: `python3.11 add_static_transliterations.py`**
- Create individual web formats: `python3 create_enhanced_web_format.py` or `python3 create_brahmana_aranyaka_web_format.py`

### Output Structure
- `parsed/` - Contains processed JSON files
  - Samhita files by kanda: `samhita_kanda_*.json`
  - Enhanced samhita dataset: `taittiriya_complete_enhanced.json`
  - Brahmana/aranyaka files: `TB_*.json`, `TA_*.json`
  - Combined brahmana/aranyaka: `taittiriya_brahmana_aranyaka_complete.json`
  - **Complete corpus: `taittiriya_complete_corpus.json`**
- `web_enhanced/` - Samhita/padam web formats
- `web_brahmana_aranyaka/` - Brahmana/aranyaka web formats
- `web_complete/` - Complete corpus web formats
- **`web_transliterated/` - Complete corpus with static transliterations (RECOMMENDED)**
- Checkpoint files enable resuming interrupted processing

### Complete Corpus Data Quality
- **📊 Total: 4,903 texts in the complete Taittiriya corpus**
- **📜 Samhita: 2,198 verses (99.95% with both padam and samhita)**
- **📚 Brahmana: 1,997 sections across 6 files**
- **🌲 Aranyaka: 708 sections across 3 files**
- **🔍 All texts are fully searchable and web-ready**