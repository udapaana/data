#!/usr/bin/env python3
"""
Create web-friendly formats for Taittiriya Brahmana and Aranyaka data.
"""

import json
from pathlib import Path
from collections import defaultdict

def create_brahmana_aranyaka_web_formats():
    """Create various web-friendly formats from the brahmana and aranyaka data."""
    
    base_dir = Path("/Users/skmnktl/Projects/udapaana/data/taittiriya")
    parsed_dir = base_dir / "parsed"
    web_dir = base_dir / "web_brahmana_aranyaka"
    web_dir.mkdir(exist_ok=True)
    
    # Load complete data
    complete_file = parsed_dir / "taittiriya_brahmana_aranyaka_complete.json"
    with open(complete_file, 'r', encoding='utf-8') as f:
        complete_data = json.load(f)
    
    print(f"Loaded data: {complete_data['metadata']['total_sections']} total sections")
    print(f"  - {complete_data['metadata']['total_brahmana_sections']} brahmana sections")
    print(f"  - {complete_data['metadata']['total_aranyaka_sections']} aranyaka sections")
    
    # Format 1: Separate files by text type
    brahmana_dir = web_dir / "brahmana"
    aranyaka_dir = web_dir / "aranyaka"
    brahmana_dir.mkdir(exist_ok=True)
    aranyaka_dir.mkdir(exist_ok=True)
    
    # Process brahmana files
    brahmana_by_book = defaultdict(list)
    for file_data in complete_data["brahmana"]["files"]:
        for section in file_data["sections"]:
            book = section["section_id"].split('.')[0]
            brahmana_by_book[book].append(section)
    
    for book, sections in brahmana_by_book.items():
        book_file = brahmana_dir / f"book_{book}.json"
        book_data = {
            "text_type": "brahmana",
            "book": book,
            "section_count": len(sections),
            "sections": sections
        }
        with open(book_file, 'w', encoding='utf-8') as f:
            json.dump(book_data, f, ensure_ascii=False, indent=2)
    
    # Process aranyaka files
    aranyaka_by_book = defaultdict(list)
    for file_data in complete_data["aranyaka"]["files"]:
        for section in file_data["sections"]:
            book = section["section_id"].split('.')[0]
            aranyaka_by_book[book].append(section)
    
    for book, sections in aranyaka_by_book.items():
        book_file = aranyaka_dir / f"book_{book}.json"
        book_data = {
            "text_type": "aranyaka",
            "book": book,
            "section_count": len(sections),
            "sections": sections
        }
        with open(book_file, 'w', encoding='utf-8') as f:
            json.dump(book_data, f, ensure_ascii=False, indent=2)
    
    # Format 2: Section index for search
    section_index = []
    
    # Add brahmana sections
    for file_data in complete_data["brahmana"]["files"]:
        for section in file_data["sections"]:
            section_index.append({
                "id": section["section_id"],
                "text_type": "brahmana",
                "book": section["section_id"].split('.')[0],
                "file_info": section["file_info"],
                "text_preview": section["text"][:200] + "..." if len(section["text"]) > 200 else section["text"]
            })
    
    # Add aranyaka sections
    for file_data in complete_data["aranyaka"]["files"]:
        for section in file_data["sections"]:
            section_index.append({
                "id": section["section_id"],
                "text_type": "aranyaka", 
                "book": section["section_id"].split('.')[0],
                "file_info": section["file_info"],
                "text_preview": section["text"][:200] + "..." if len(section["text"]) > 200 else section["text"]
            })
    
    index_file = web_dir / "section_index.json"
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(section_index, f, ensure_ascii=False, indent=2)
    
    # Format 3: Statistics
    stats = {
        "total_files": complete_data["metadata"]["total_brahmana_files"] + complete_data["metadata"]["total_aranyaka_files"],
        "total_sections": complete_data["metadata"]["total_sections"],
        "brahmana": {
            "files": complete_data["metadata"]["total_brahmana_files"],
            "sections": complete_data["metadata"]["total_brahmana_sections"],
            "books": len(brahmana_by_book)
        },
        "aranyaka": {
            "files": complete_data["metadata"]["total_aranyaka_files"],
            "sections": complete_data["metadata"]["total_aranyaka_sections"],
            "books": len(aranyaka_by_book)
        },
        "distribution": {
            "brahmana_by_book": {book: len(sections) for book, sections in brahmana_by_book.items()},
            "aranyaka_by_book": {book: len(sections) for book, sections in aranyaka_by_book.items()}
        }
    }
    
    stats_file = web_dir / "statistics.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    # Format 4: Search-optimized flat structure
    search_data = []
    
    # Add all sections
    for file_data in complete_data["brahmana"]["files"]:
        for section in file_data["sections"]:
            search_data.append({
                "section_id": section["section_id"],
                "text_type": "brahmana",
                "book": section["section_id"].split('.')[0],
                "file_info": section["file_info"],
                "text": section["text"]
            })
    
    for file_data in complete_data["aranyaka"]["files"]:
        for section in file_data["sections"]:
            search_data.append({
                "section_id": section["section_id"],
                "text_type": "aranyaka",
                "book": section["section_id"].split('.')[0],
                "file_info": section["file_info"],
                "text": section["text"]
            })
    
    search_file = web_dir / "search_data.json"
    with open(search_file, 'w', encoding='utf-8') as f:
        json.dump(search_data, f, ensure_ascii=False, indent=2)
    
    # Format 5: Minified version for production
    minified_file = web_dir / "brahmana_aranyaka_minified.json"
    with open(minified_file, 'w', encoding='utf-8') as f:
        json.dump(complete_data, f, ensure_ascii=False, separators=(',', ':'))
    
    # Format 6: API-ready endpoints
    api_dir = web_dir / "api"
    api_dir.mkdir(exist_ok=True)
    
    # Metadata endpoint
    metadata = {
        "version": "1.0",
        "description": "Taittiriya Brahmana and Aranyaka texts",
        "total_sections": complete_data["metadata"]["total_sections"],
        "available_types": ["brahmana", "aranyaka"],
        "brahmana_books": sorted(brahmana_by_book.keys()),
        "aranyaka_books": sorted(aranyaka_by_book.keys())
    }
    
    with open(api_dir / "metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    # Section lookup by ID
    section_lookup = {}
    for item in search_data:
        section_lookup[item["section_id"]] = item
    
    with open(api_dir / "sections_by_id.json", 'w', encoding='utf-8') as f:
        json.dump(section_lookup, f, ensure_ascii=False, indent=2)
    
    print(f"Created brahmana-aranyaka web formats in {web_dir}:")
    print(f"  - {len(list(brahmana_dir.glob('*.json')))} brahmana book files")
    print(f"  - {len(list(aranyaka_dir.glob('*.json')))} aranyaka book files")
    print(f"  - section_index.json ({len(section_index)} sections)")
    print(f"  - statistics.json")
    print(f"  - search_data.json")
    print(f"  - brahmana_aranyaka_minified.json")
    print(f"  - API simulation files in api/")
    
    # Show file sizes
    for file in web_dir.glob("*.json"):
        size_kb = file.stat().st_size / 1024
        print(f"    {file.name}: {size_kb:.1f} KB")

if __name__ == "__main__":
    create_brahmana_aranyaka_web_formats()