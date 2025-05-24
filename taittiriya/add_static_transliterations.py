#!/usr/bin/env python3
"""
Add static transliterations to the complete Taittiriya corpus using vidyut-lipi.
This script processes the existing complete corpus and adds transliterations for all texts.
"""

import json
from pathlib import Path
from transliteration_generator import transliteration_generator

def add_transliterations_to_complete_corpus():
    """Add static transliterations to the complete corpus."""
    
    base_dir = Path("/Users/skmnktl/Projects/udapaana/data/taittiriya")
    parsed_dir = base_dir / "parsed"
    
    # Load the complete corpus
    complete_corpus_file = parsed_dir / "taittiriya_complete_corpus.json"
    if not complete_corpus_file.exists():
        print("Error: Complete corpus file not found. Please run create_complete_dataset.py first.")
        return
    
    print("Loading complete corpus...")
    with open(complete_corpus_file, 'r', encoding='utf-8') as f:
        corpus_data = json.load(f)
    
    print(f"Loaded corpus with {corpus_data.get('metadata', {}).get('total_texts', 'unknown')} texts")
    
    # Process corpus with transliterations
    enhanced_corpus = transliteration_generator.process_corpus_with_transliterations(corpus_data)
    
    # Update metadata
    if 'metadata' in enhanced_corpus:
        enhanced_corpus['metadata']['has_transliterations'] = True
        enhanced_corpus['metadata']['transliteration_scripts'] = [
            script['script'] for script in transliteration_generator.SUPPORTED_SCRIPTS
        ]
        enhanced_corpus['metadata']['transliteration_engine'] = 'vidyut-lipi'
    
    # Save enhanced corpus
    enhanced_corpus_file = parsed_dir / "taittiriya_complete_corpus_with_transliterations.json"
    print(f"Saving enhanced corpus to {enhanced_corpus_file}...")
    
    with open(enhanced_corpus_file, 'w', encoding='utf-8') as f:
        json.dump(enhanced_corpus, f, ensure_ascii=False, indent=2)
    
    print(f"Enhanced corpus saved successfully!")
    print(f"Total texts processed: {enhanced_corpus.get('metadata', {}).get('total_texts', 'unknown')}")
    print(f"Transliteration scripts added: {len(transliteration_generator.SUPPORTED_SCRIPTS)}")

def create_transliterated_web_formats():
    """Create web formats with transliterations."""
    
    base_dir = Path("/Users/skmnktl/Projects/udapaana/data/taittiriya")
    parsed_dir = base_dir / "parsed"
    web_dir = base_dir / "web_transliterated"
    web_dir.mkdir(exist_ok=True)
    
    # Load enhanced corpus
    enhanced_corpus_file = parsed_dir / "taittiriya_complete_corpus_with_transliterations.json"
    if not enhanced_corpus_file.exists():
        print("Error: Enhanced corpus with transliterations not found. Please run add_transliterations_to_complete_corpus() first.")
        return
    
    print("Loading enhanced corpus with transliterations...")
    with open(enhanced_corpus_file, 'r', encoding='utf-8') as f:
        enhanced_corpus = json.load(f)
    
    # Create API directory for metadata
    api_dir = web_dir / "api"
    api_dir.mkdir(exist_ok=True)
    
    # Save metadata
    metadata = {
        "scripts": transliteration_generator.SUPPORTED_SCRIPTS,
        "total_texts": enhanced_corpus.get('metadata', {}).get('total_texts', 0),
        "has_transliterations": True,
        "transliteration_engine": "vidyut-lipi"
    }
    
    with open(api_dir / "metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    # Create chapter-wise files for samhita
    if 'samhita' in enhanced_corpus:
        chapters_dir = web_dir / "chapters"
        chapters_dir.mkdir(exist_ok=True)
        
        for chapter_id, chapter_data in enhanced_corpus['samhita'].items():
            chapter_file = chapters_dir / f"chapter_{chapter_id.replace('.', '_')}.json"
            with open(chapter_file, 'w', encoding='utf-8') as f:
                json.dump(chapter_data, f, ensure_ascii=False, indent=2)
    
    # Create book-wise files for brahmana
    if 'brahmana' in enhanced_corpus:
        brahmana_dir = web_dir / "brahmana"
        brahmana_dir.mkdir(exist_ok=True)
        
        for book_id, book_data in enhanced_corpus['brahmana'].items():
            book_file = brahmana_dir / f"book_{book_id}.json"
            with open(book_file, 'w', encoding='utf-8') as f:
                json.dump(book_data, f, ensure_ascii=False, indent=2)
    
    # Create book-wise files for aranyaka
    if 'aranyaka' in enhanced_corpus:
        aranyaka_dir = web_dir / "aranyaka"
        aranyaka_dir.mkdir(exist_ok=True)
        
        for book_id, book_data in enhanced_corpus['aranyaka'].items():
            book_file = aranyaka_dir / f"book_{book_id}.json"
            with open(book_file, 'w', encoding='utf-8') as f:
                json.dump(book_data, f, ensure_ascii=False, indent=2)
    
    # Create minified version for production
    minified_data = {
        "metadata": enhanced_corpus.get('metadata', {}),
        "samhita": enhanced_corpus.get('samhita', {}),
        "brahmana": enhanced_corpus.get('brahmana', {}),
        "aranyaka": enhanced_corpus.get('aranyaka', {})
    }
    
    with open(web_dir / "taittiriya_transliterated_minified.json", 'w', encoding='utf-8') as f:
        json.dump(minified_data, f, ensure_ascii=False, separators=(',', ':'))
    
    print(f"Web formats with transliterations created in {web_dir}")

if __name__ == "__main__":
    print("Adding static transliterations to Taittiriya corpus...")
    add_transliterations_to_complete_corpus()
    
    print("\nCreating web formats with transliterations...")
    create_transliterated_web_formats()
    
    print("\nAll tasks completed successfully!")