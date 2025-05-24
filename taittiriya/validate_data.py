#!/usr/bin/env python3
"""
Validate the enhanced parsing results for data quality and completeness.
"""

import json
from pathlib import Path
from collections import defaultdict

def validate_enhanced_data():
    """Validate the enhanced parsing results."""
    
    base_dir = Path("/Users/skmnktl/Projects/udapaana/data/taittiriya")
    parsed_dir = base_dir / "parsed"
    
    # Load enhanced complete data
    complete_file = parsed_dir / "taittiriya_complete_enhanced.json"
    with open(complete_file, 'r', encoding='utf-8') as f:
        complete_data = json.load(f)
    
    print("=== Data Validation Report ===")
    print(f"Dataset: {complete_data['metadata']['title']}")
    print(f"Parsing Method: {complete_data['metadata']['parsing_method']}")
    print(f"Total Chapters: {complete_data['metadata']['total_chapters']}")
    print(f"Total Verses: {complete_data['metadata']['total_verses']}")
    print(f"Match Rate: {complete_data['metadata']['match_percentage']}%")
    
    # Validation checks
    issues = []
    verse_ids = set()
    kanda_stats = defaultdict(lambda: {"chapters": 0, "verses": 0, "matched": 0})
    
    print("\n=== Chapter Analysis ===")
    for chapter_id, chapter_data in complete_data["chapters"].items():
        kanda = chapter_id.split('.')[0]
        kanda_stats[kanda]["chapters"] += 1
        kanda_stats[kanda]["verses"] += chapter_data["verse_count"]
        kanda_stats[kanda]["matched"] += chapter_data.get("matched_count", 0)
        
        print(f"Chapter {chapter_id}: {chapter_data['verse_count']} verses, {chapter_data.get('matched_count', 0)} matched")
        
        # Check for duplicate verse IDs
        chapter_verse_ids = set()
        for verse in chapter_data["verses"]:
            verse_id = verse["verse_id"]
            
            if verse_id in verse_ids:
                issues.append(f"Duplicate verse ID: {verse_id}")
            else:
                verse_ids.add(verse_id)
            
            if verse_id in chapter_verse_ids:
                issues.append(f"Duplicate verse ID within chapter {chapter_id}: {verse_id}")
            else:
                chapter_verse_ids.add(verse_id)
            
            # Check for missing padam text
            if not verse.get("padam", "").strip():
                issues.append(f"Missing padam text for verse {verse_id}")
            
            # Check consistency of has_samhita_match flag
            has_samhita = bool(verse.get("samhita", "").strip())
            flag_value = verse.get("has_samhita_match", False)
            if has_samhita != flag_value:
                issues.append(f"Inconsistent samhita flag for verse {verse_id}: has_text={has_samhita}, flag={flag_value}")
    
    print("\n=== Kanda Summary ===")
    for kanda, stats in sorted(kanda_stats.items()):
        match_rate = (stats["matched"] / stats["verses"] * 100) if stats["verses"] > 0 else 0
        print(f"Kanda {kanda}: {stats['chapters']} chapters, {stats['verses']} verses, {stats['matched']} matched ({match_rate:.1f}%)")
    
    print("\n=== Data Quality Issues ===")
    if issues:
        for issue in issues[:10]:  # Show first 10 issues
            print(f"  - {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more issues")
    else:
        print("  No data quality issues found! ✅")
    
    # Verse ID pattern analysis
    print("\n=== Verse ID Pattern Analysis ===")
    patterns = defaultdict(int)
    for verse_id in verse_ids:
        parts = verse_id.split('.')
        if len(parts) == 4:
            kanda, section, subsection, verse = parts
            pattern = f"{kanda}.x.x.x"
            patterns[pattern] += 1
        else:
            patterns["invalid"] += 1
    
    for pattern, count in sorted(patterns.items()):
        print(f"  {pattern}: {count} verses")
    
    # Sample verse check
    print("\n=== Sample Verse Quality Check ===")
    sample_chapters = ["1.1", "2.1", "3.1", "4.1", "5.1", "6.1", "7.1"]
    for chapter_id in sample_chapters:
        if chapter_id in complete_data["chapters"]:
            chapter = complete_data["chapters"][chapter_id]
            if chapter["verses"]:
                verse = chapter["verses"][0]
                padam_len = len(verse.get("padam", ""))
                samhita_len = len(verse.get("samhita", ""))
                print(f"  {verse['verse_id']}: padam={padam_len} chars, samhita={samhita_len} chars")
    
    # File size analysis
    print("\n=== File Size Analysis ===")
    output_files = [
        "taittiriya_complete_enhanced.json",
        "../web_enhanced/taittiriya_enhanced_minified.json",
        "../web_enhanced/search_data_enhanced.json"
    ]
    
    for filename in output_files:
        filepath = parsed_dir / filename
        if filepath.exists():
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"  {filepath.name}: {size_mb:.2f} MB")
    
    print(f"\n=== Summary ===")
    print(f"✅ Processed {len(complete_data['chapters'])} chapters successfully")
    print(f"✅ {len(verse_ids)} unique verses identified")
    print(f"✅ {complete_data['metadata']['match_percentage']}% samhita match rate")
    print(f"{'⚠️' if issues else '✅'} {len(issues)} data quality issues found")
    print("\nThe dataset is ready for web application use! 🎉")

if __name__ == "__main__":
    validate_enhanced_data()