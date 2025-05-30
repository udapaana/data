#!/usr/bin/env python3
"""
Create web-friendly formats from the parsed data.
"""

import json
from pathlib import Path

def create_web_formats():
    """Create various web-friendly formats from the complete data."""
    
    base_dir = Path("/Users/skmnktl/Projects/udapaana/data/taittiriya")
    parsed_dir = base_dir / "parsed"
    web_dir = base_dir / "web"
    web_dir.mkdir(exist_ok=True)
    
    # Load complete data
    complete_file = parsed_dir / "taittiriya_complete.json"
    with open(complete_file, 'r', encoding='utf-8') as f:
        complete_data = json.load(f)
    
    # Format 1: Chapter-wise separate files
    chapters_dir = web_dir / "chapters"
    chapters_dir.mkdir(exist_ok=True)
    
    for chapter_id, chapter_data in complete_data["chapters"].items():
        chapter_file = chapters_dir / f"chapter_{chapter_id.replace('.', '_')}.json"
        with open(chapter_file, 'w', encoding='utf-8') as f:
            json.dump(chapter_data, f, ensure_ascii=False, indent=2)
    
    # Format 2: Verse index for search
    verse_index = []
    for chapter_id, chapter_data in complete_data["chapters"].items():
        for verse in chapter_data["verses"]:
            verse_index.append({
                "id": verse["verse_id"],
                "chapter": chapter_id,
                "padam_preview": verse["padam"][:100] + "..." if len(verse["padam"]) > 100 else verse["padam"],
                "has_samhita": verse["has_samhita_match"]
            })
    
    index_file = web_dir / "verse_index.json"
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(verse_index, f, ensure_ascii=False, indent=2)
    
    # Format 3: Statistics
    stats = {
        "total_chapters": complete_data["metadata"]["total_chapters"],
        "total_verses": complete_data["metadata"]["total_verses"],
        "verses_with_samhita": complete_data["metadata"]["total_matched"],
        "match_percentage": round(complete_data["metadata"]["total_matched"] / complete_data["metadata"]["total_verses"] * 100, 1),
        "chapters_with_matches": len([ch for ch in complete_data["chapters"].values() if ch["matched_count"] > 0]),
        "verse_distribution": {}
    }
    
    for chapter_id, chapter_data in complete_data["chapters"].items():
        stats["verse_distribution"][chapter_id] = {
            "total": chapter_data["verse_count"],
            "matched": chapter_data["matched_count"]
        }
    
    stats_file = web_dir / "statistics.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    # Format 4: Search-optimized flat structure
    search_data = []
    for chapter_id, chapter_data in complete_data["chapters"].items():
        for verse in chapter_data["verses"]:
            search_data.append({
                "verse_id": verse["verse_id"],
                "chapter": chapter_id,
                "padam": verse["padam"],
                "samhita": verse.get("samhita", ""),
                "has_samhita": verse["has_samhita_match"]
            })
    
    search_file = web_dir / "search_data.json"
    with open(search_file, 'w', encoding='utf-8') as f:
        json.dump(search_data, f, ensure_ascii=False, indent=2)
    
    # Format 5: Minified version for production
    minified_file = web_dir / "taittiriya_minified.json"
    with open(minified_file, 'w', encoding='utf-8') as f:
        json.dump(complete_data, f, ensure_ascii=False, separators=(',', ':'))
    
    print(f"Created web formats in {web_dir}:")
    print(f"  - {len(list(chapters_dir.glob('*.json')))} chapter files")
    print(f"  - verse_index.json ({len(verse_index)} verses)")
    print(f"  - statistics.json")
    print(f"  - search_data.json")
    print(f"  - taittiriya_minified.json")
    
    # Show file sizes
    for file in web_dir.glob("*.json"):
        size_kb = file.stat().st_size / 1024
        print(f"    {file.name}: {size_kb:.1f} KB")

if __name__ == "__main__":
    create_web_formats()