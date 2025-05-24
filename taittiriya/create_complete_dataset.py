#!/usr/bin/env python3
"""
Create the complete Taittiriya dataset combining samhita/padam, brahmana, and aranyaka.
"""

import json
from pathlib import Path

def create_complete_dataset():
    """Create the final complete dataset combining all text types."""
    
    base_dir = Path("/Users/skmnktl/Projects/udapaana/data/taittiriya")
    parsed_dir = base_dir / "parsed"
    web_dir = base_dir / "web_complete"
    web_dir.mkdir(exist_ok=True)
    
    # Load all component datasets
    print("Loading component datasets...")
    
    # Load samhita/padam data
    samhita_file = parsed_dir / "taittiriya_complete_enhanced.json"
    with open(samhita_file, 'r', encoding='utf-8') as f:
        samhita_data = json.load(f)
    
    # Load brahmana/aranyaka data
    brahmana_aranyaka_file = parsed_dir / "taittiriya_brahmana_aranyaka_complete.json"
    with open(brahmana_aranyaka_file, 'r', encoding='utf-8') as f:
        brahmana_aranyaka_data = json.load(f)
    
    print(f"Samhita/Padam: {samhita_data['metadata']['total_verses']} verses")
    print(f"Brahmana: {brahmana_aranyaka_data['metadata']['total_brahmana_sections']} sections")
    print(f"Aranyaka: {brahmana_aranyaka_data['metadata']['total_aranyaka_sections']} sections")
    
    # Create complete dataset
    complete_dataset = {
        "metadata": {
            "title": "Complete Taittiriya Corpus",
            "description": "Complete digitized texts of Taittiriya Samhita, Brahmana, and Aranyaka",
            "components": {
                "samhita": {
                    "description": "Mantra texts with padam (word-by-word) and samhita (continuous) versions",
                    "total_kandas": samhita_data["metadata"]["total_chapters"] // 8,  # Rough estimate
                    "total_chapters": samhita_data["metadata"]["total_chapters"],
                    "total_verses": samhita_data["metadata"]["total_verses"],
                    "match_percentage": samhita_data["metadata"]["match_percentage"]
                },
                "brahmana": {
                    "description": "Prose explanations and ritual instructions",
                    "total_files": brahmana_aranyaka_data["metadata"]["total_brahmana_files"],
                    "total_sections": brahmana_aranyaka_data["metadata"]["total_brahmana_sections"]
                },
                "aranyaka": {
                    "description": "Forest texts with philosophical and mystical content", 
                    "total_files": brahmana_aranyaka_data["metadata"]["total_aranyaka_files"],
                    "total_sections": brahmana_aranyaka_data["metadata"]["total_aranyaka_sections"]
                }
            },
            "totals": {
                "total_texts": (samhita_data["metadata"]["total_verses"] + 
                              brahmana_aranyaka_data["metadata"]["total_brahmana_sections"] +
                              brahmana_aranyaka_data["metadata"]["total_aranyaka_sections"]),
                "total_files_processed": (samhita_data["metadata"]["total_chapters"] +
                                        brahmana_aranyaka_data["metadata"]["total_brahmana_files"] +
                                        brahmana_aranyaka_data["metadata"]["total_aranyaka_files"])
            },
            "parsing_info": {
                "samhita_parsing": samhita_data["metadata"]["parsing_method"],
                "brahmana_aranyaka_parsing": brahmana_aranyaka_data["metadata"]["parsing_method"]
            }
        },
        "samhita": samhita_data["chapters"],
        "brahmana": brahmana_aranyaka_data["brahmana"],
        "aranyaka": brahmana_aranyaka_data["aranyaka"]
    }
    
    # Save complete dataset
    complete_file = web_dir / "taittiriya_complete_corpus.json"
    with open(complete_file, 'w', encoding='utf-8') as f:
        json.dump(complete_dataset, f, ensure_ascii=False, indent=2)
    
    # Create search index for all texts
    search_index = []
    
    # Add samhita verses
    for chapter_id, chapter_data in samhita_data["chapters"].items():
        for verse in chapter_data["verses"]:
            search_index.append({
                "id": verse["verse_id"],
                "type": "samhita",
                "chapter": chapter_id,
                "kanda": chapter_id.split('.')[0],
                "padam_preview": verse["padam"][:150] + "..." if len(verse["padam"]) > 150 else verse["padam"],
                "samhita_preview": verse.get("samhita", "")[:150] + "..." if len(verse.get("samhita", "")) > 150 else verse.get("samhita", ""),
                "has_samhita": verse["has_samhita_match"]
            })
    
    # Add brahmana sections
    for file_data in brahmana_aranyaka_data["brahmana"]["files"]:
        for section in file_data["sections"]:
            search_index.append({
                "id": section["section_id"],
                "type": "brahmana",
                "book": section["section_id"].split('.')[0],
                "file_info": section["file_info"],
                "text_preview": section["text"][:150] + "..." if len(section["text"]) > 150 else section["text"]
            })
    
    # Add aranyaka sections
    for file_data in brahmana_aranyaka_data["aranyaka"]["files"]:
        for section in file_data["sections"]:
            search_index.append({
                "id": section["section_id"],
                "type": "aranyaka",
                "book": section["section_id"].split('.')[0],
                "file_info": section["file_info"],
                "text_preview": section["text"][:150] + "..." if len(section["text"]) > 150 else section["text"]
            })
    
    search_index_file = web_dir / "complete_search_index.json"
    with open(search_index_file, 'w', encoding='utf-8') as f:
        json.dump(search_index, f, ensure_ascii=False, indent=2)
    
    # Create summary statistics
    summary_stats = {
        "corpus_overview": {
            "total_components": 3,
            "total_texts": complete_dataset["metadata"]["totals"]["total_texts"],
            "components": {
                "samhita_verses": complete_dataset["metadata"]["components"]["samhita"]["total_verses"],
                "brahmana_sections": complete_dataset["metadata"]["components"]["brahmana"]["total_sections"],
                "aranyaka_sections": complete_dataset["metadata"]["components"]["aranyaka"]["total_sections"]
            }
        },
        "quality_metrics": {
            "samhita_match_rate": f"{complete_dataset['metadata']['components']['samhita']['match_percentage']}%",
            "total_searchable_items": len(search_index)
        }
    }
    
    stats_file = web_dir / "corpus_statistics.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(summary_stats, f, ensure_ascii=False, indent=2)
    
    # Create minified version
    minified_file = web_dir / "taittiriya_corpus_minified.json"
    with open(minified_file, 'w', encoding='utf-8') as f:
        json.dump(complete_dataset, f, ensure_ascii=False, separators=(',', ':'))
    
    print(f"\nComplete corpus created in {web_dir}:")
    print(f"  - taittiriya_complete_corpus.json (full dataset)")
    print(f"  - complete_search_index.json ({len(search_index)} searchable items)")
    print(f"  - corpus_statistics.json")
    print(f"  - taittiriya_corpus_minified.json")
    
    # Show file sizes
    for file in web_dir.glob("*.json"):
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"    {file.name}: {size_mb:.2f} MB")
    
    print(f"\n🎉 COMPLETE TAITTIRIYA CORPUS READY!")
    print(f"📊 Total: {complete_dataset['metadata']['totals']['total_texts']} texts")
    print(f"   📜 {complete_dataset['metadata']['components']['samhita']['total_verses']} samhita verses")
    print(f"   📚 {complete_dataset['metadata']['components']['brahmana']['total_sections']} brahmana sections")
    print(f"   🌲 {complete_dataset['metadata']['components']['aranyaka']['total_sections']} aranyaka sections")

if __name__ == "__main__":
    create_complete_dataset()