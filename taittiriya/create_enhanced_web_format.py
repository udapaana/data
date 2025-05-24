#!/usr/bin/env python3
"""
Create enhanced web-friendly formats from the complete enhanced data.
"""

import json
from pathlib import Path

def create_enhanced_web_formats():
    """Create various web-friendly formats from the enhanced complete data."""
    
    base_dir = Path("/Users/skmnktl/Projects/udapaana/data/taittiriya")
    parsed_dir = base_dir / "parsed"
    web_dir = base_dir / "web_enhanced"
    web_dir.mkdir(exist_ok=True)
    
    # Load enhanced complete data
    complete_file = parsed_dir / "taittiriya_complete_enhanced.json"
    with open(complete_file, 'r', encoding='utf-8') as f:
        complete_data = json.load(f)
    
    print(f"Loaded data: {complete_data['metadata']['total_verses']} verses, {complete_data['metadata']['match_percentage']}% match rate")
    
    # Format 1: Chapter-wise separate files
    chapters_dir = web_dir / "chapters"
    chapters_dir.mkdir(exist_ok=True)
    
    for chapter_id, chapter_data in complete_data["chapters"].items():
        chapter_file = chapters_dir / f"chapter_{chapter_id.replace('.', '_')}.json"
        with open(chapter_file, 'w', encoding='utf-8') as f:
            json.dump(chapter_data, f, ensure_ascii=False, indent=2)
    
    # Format 2: Kanda-wise organization
    kandas_dir = web_dir / "kandas"
    kandas_dir.mkdir(exist_ok=True)
    
    kandas = {}
    for chapter_id, chapter_data in complete_data["chapters"].items():
        kanda = chapter_id.split('.')[0]
        if kanda not in kandas:
            kandas[kanda] = {
                "kanda": kanda,
                "chapters": {},
                "total_verses": 0,
                "total_matched": 0
            }
        
        kandas[kanda]["chapters"][chapter_id] = chapter_data
        kandas[kanda]["total_verses"] += chapter_data["verse_count"]
        kandas[kanda]["total_matched"] += chapter_data.get("matched_count", 0)
    
    for kanda_id, kanda_data in kandas.items():
        kanda_file = kandas_dir / f"kanda_{kanda_id}.json"
        with open(kanda_file, 'w', encoding='utf-8') as f:
            json.dump(kanda_data, f, ensure_ascii=False, indent=2)
    
    # Format 3: Enhanced verse index for search
    verse_index = []
    for chapter_id, chapter_data in complete_data["chapters"].items():
        kanda = chapter_id.split('.')[0]
        for verse in chapter_data["verses"]:
            verse_index.append({
                "id": verse["verse_id"],
                "chapter": chapter_id,
                "kanda": kanda,
                "padam_preview": verse["padam"][:100] + "..." if len(verse["padam"]) > 100 else verse["padam"],
                "samhita_preview": verse["samhita"][:100] + "..." if len(verse.get("samhita", "")) > 100 else verse.get("samhita", ""),
                "has_samhita": verse["has_samhita_match"]
            })
    
    index_file = web_dir / "verse_index_enhanced.json"
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(verse_index, f, ensure_ascii=False, indent=2)
    
    # Format 4: Enhanced statistics
    kanda_stats = {}
    for kanda_id, kanda_data in kandas.items():
        kanda_stats[kanda_id] = {
            "total_chapters": len(kanda_data["chapters"]),
            "total_verses": kanda_data["total_verses"],
            "matched_verses": kanda_data["total_matched"],
            "match_percentage": round(kanda_data["total_matched"] / kanda_data["total_verses"] * 100, 1) if kanda_data["total_verses"] > 0 else 0
        }
    
    stats = {
        "total_kandas": len(kandas),
        "total_chapters": complete_data["metadata"]["total_chapters"],
        "total_verses": complete_data["metadata"]["total_verses"],
        "verses_with_samhita": complete_data["metadata"]["total_matched"],
        "match_percentage": complete_data["metadata"]["match_percentage"],
        "kanda_distribution": kanda_stats,
        "chapter_distribution": {}
    }
    
    for chapter_id, chapter_data in complete_data["chapters"].items():
        stats["chapter_distribution"][chapter_id] = {
            "total": chapter_data["verse_count"],
            "matched": chapter_data["matched_count"],
            "match_percentage": round(chapter_data["matched_count"] / chapter_data["verse_count"] * 100, 1) if chapter_data["verse_count"] > 0 else 0
        }
    
    stats_file = web_dir / "statistics_enhanced.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    # Format 5: Search-optimized flat structure
    search_data = []
    for chapter_id, chapter_data in complete_data["chapters"].items():
        kanda = chapter_id.split('.')[0]
        for verse in chapter_data["verses"]:
            search_data.append({
                "verse_id": verse["verse_id"],
                "chapter": chapter_id,
                "kanda": kanda,
                "padam": verse["padam"],
                "samhita": verse.get("samhita", ""),
                "has_samhita": verse["has_samhita_match"]
            })
    
    search_file = web_dir / "search_data_enhanced.json"
    with open(search_file, 'w', encoding='utf-8') as f:
        json.dump(search_data, f, ensure_ascii=False, indent=2)
    
    # Format 6: Minified version for production
    minified_file = web_dir / "taittiriya_enhanced_minified.json"
    with open(minified_file, 'w', encoding='utf-8') as f:
        json.dump(complete_data, f, ensure_ascii=False, separators=(',', ':'))
    
    # Format 7: API-ready endpoints simulation
    api_dir = web_dir / "api"
    api_dir.mkdir(exist_ok=True)
    
    # Metadata endpoint
    metadata = {
        "version": "2.0",
        "last_updated": complete_data["metadata"],
        "available_kandas": list(kandas.keys()),
        "total_verses": complete_data["metadata"]["total_verses"],
        "match_rate": complete_data["metadata"]["match_percentage"]
    }
    
    with open(api_dir / "metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    # Verse lookup by ID
    verse_lookup = {}
    for chapter_id, chapter_data in complete_data["chapters"].items():
        for verse in chapter_data["verses"]:
            verse_lookup[verse["verse_id"]] = {
                "verse_id": verse["verse_id"],
                "chapter": chapter_id,
                "kanda": chapter_id.split('.')[0],
                "padam": verse["padam"],
                "samhita": verse.get("samhita", ""),
                "has_samhita": verse["has_samhita_match"]
            }
    
    with open(api_dir / "verses_by_id.json", 'w', encoding='utf-8') as f:
        json.dump(verse_lookup, f, ensure_ascii=False, indent=2)
    
    print(f"Created enhanced web formats in {web_dir}:")
    print(f"  - {len(list(chapters_dir.glob('*.json')))} chapter files")
    print(f"  - {len(list(kandas_dir.glob('*.json')))} kanda files")
    print(f"  - verse_index_enhanced.json ({len(verse_index)} verses)")
    print(f"  - statistics_enhanced.json")
    print(f"  - search_data_enhanced.json")
    print(f"  - taittiriya_enhanced_minified.json")
    print(f"  - API simulation files in api/")
    
    # Show file sizes
    for file in web_dir.glob("*.json"):
        size_kb = file.stat().st_size / 1024
        print(f"    {file.name}: {size_kb:.1f} KB")

if __name__ == "__main__":
    create_enhanced_web_formats()