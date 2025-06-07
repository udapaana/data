#!/usr/bin/env python3
"""Integrate DOCX Taittirīya data into the new śākhā-source structure."""

import json
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def integrate_taittiriya_docx():
    """Add DOCX Taittirīya data to the new structure."""
    # Paths
    docx_dir = Path("data/taittiriya")
    sakha_dir = Path("data/vedic_texts_by_sakha/yajurveda_तैत्तिरीयशाखा")
    
    # Find the complete dataset
    complete_file = None
    for pattern in ["*complete_corpus.json", "*enhanced_web_format.json", "*complete_dataset.json"]:
        matches = list(docx_dir.glob(f"**/{pattern}"))
        if matches:
            complete_file = matches[0]
            logger.info(f"Found complete dataset: {complete_file}")
            break
    
    if not complete_file:
        logger.error("No complete dataset found in taittiriya directory")
        return
    
    # Create source directory
    docx_source_dir = sakha_dir / "docx_baraha_complete"
    docx_source_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy the complete file
    dest_file = docx_source_dir / "taittiriya_complete_corpus.json"
    shutil.copy2(complete_file, dest_file)
    logger.info(f"Copied to: {dest_file}")
    
    # Read and analyze the data
    with open(complete_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Count total texts across all sections
    total_texts = 0
    if 'samhita' in data:
        total_texts += len(data['samhita'])
    if 'brahmana' in data:
        total_texts += len(data['brahmana'])
    if 'aranyaka' in data:
        total_texts += len(data['aranyaka'])
    
    # Get metadata info if available
    doc_metadata = data.get('metadata', {})
    
    # Create metadata
    metadata = {
        "source_id": "docx_baraha_complete",
        "source_type": "docx_baraha",
        "file_name": "taittiriya_complete_corpus.json",
        "veda": "Yajurveda",
        "shakha": "तैत्तिरीयशाखा",
        "text_type": "Complete Corpus (Saṃhitā + Brāhmaṇa + Āraṇyaka)",
        "total_records": total_texts,
        "sections": {
            "samhita": len(data.get('samhita', [])),
            "brahmana": len(data.get('brahmana', [])),
            "aranyaka": len(data.get('aranyaka', []))
        },
        "has_accents": False,
        "accent_coverage": 0.0,
        "regional_variants": True,
        "pada_format": True,
        "encoding": "Baraha (converted to Devanagari)",
        "completeness": "Complete traditional corpus",
        "date_processed": "2024-2025",
        "original_metadata": doc_metadata,
        "notes": f"{total_texts:,} texts from DOCX files. No accents but includes regional variants and pada format."
    }
    
    # Write metadata
    meta_file = docx_source_dir / "metadata.json"
    with open(meta_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Created metadata: {meta_file}")
    logger.info(f"DOCX source integrated: {len(data)} texts")
    
    # Also copy the web-ready formats if they exist
    for pattern in ["*web_enhanced*", "*web_format*"]:
        matches = list(docx_dir.glob(f"**/{pattern}"))
        for match in matches:
            if match.is_file() and match.suffix == '.json':
                dest = docx_source_dir / match.name
                shutil.copy2(match, dest)
                logger.info(f"Also copied: {match.name}")

def create_source_comparison():
    """Create a comparison of Taittirīya sources."""
    sakha_dir = Path("data/vedic_texts_by_sakha/yajurveda_तैत्तिरीयशाखा")
    
    comparison = {
        "shakha": "Taittirīya (Kṛṣṇa Yajurveda)",
        "sources": []
    }
    
    for source_dir in sakha_dir.iterdir():
        if source_dir.is_dir():
            meta_file = source_dir / "metadata.json"
            if meta_file.exists():
                with open(meta_file, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                    
                comparison["sources"].append({
                    "source_id": meta.get("source_id", source_dir.name),
                    "type": meta.get("source_type", "vedanidhi"),
                    "texts": meta.get("total_records", 0),
                    "accents": meta.get("has_accents", False),
                    "accent_coverage": meta.get("accent_coverage", 0.0),
                    "variants": meta.get("regional_variants", False),
                    "pada_format": meta.get("pada_format", False),
                    "notes": meta.get("notes", "")
                })
    
    # Write comparison
    comp_file = sakha_dir / "SOURCES_COMPARISON.md"
    with open(comp_file, 'w', encoding='utf-8') as f:
        f.write("# Taittirīya Sources Comparison\n\n")
        f.write("| Source | Type | Texts | Accents | Coverage | Variants | Pada |\n")
        f.write("|--------|------|-------|---------|----------|----------|------|\n")
        
        for src in comparison["sources"]:
            accents = "✅" if src["accents"] else "❌"
            variants = "✅" if src["variants"] else "❌"
            pada = "✅" if src["pada_format"] else "❌"
            coverage = f"{src['accent_coverage']*100:.1f}%" if src["accents"] else "0%"
            
            f.write(f"| {src['source_id']} | {src['type']} | {src['texts']:,} | {accents} | {coverage} | {variants} | {pada} |\n")
        
        f.write(f"\n## Summary\n\n")
        f.write(f"Total sources: {len(comparison['sources'])}\n\n")
        
        for src in comparison["sources"]:
            f.write(f"### {src['source_id']}\n")
            f.write(f"- **Type**: {src['type']}\n")
            f.write(f"- **Texts**: {src['texts']:,}\n")
            f.write(f"- **Notes**: {src['notes']}\n\n")
    
    logger.info(f"Created comparison: {comp_file}")

if __name__ == "__main__":
    logger.info("Integrating DOCX Taittirīya data...")
    integrate_taittiriya_docx()
    
    logger.info("Creating source comparison...")
    create_source_comparison()
    
    logger.info("Integration complete!")