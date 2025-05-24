#!/usr/bin/env python3
"""
Robust parser for Taittiriya texts that handles inconsistent formatting.
"""

import json
import re
from pathlib import Path
from docx import Document
from typing import Dict, List, Any, Optional

class RobustTaittiriyaParser:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.padam_dir = self.base_dir / "raw" / "padam"
        self.samhita_dir = self.base_dir / "raw" / "samhita" 
        self.output_dir = self.base_dir / "parsed"
        self.checkpoint_file = self.base_dir / "robust_parsing_checkpoint.json"
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
    def load_checkpoint(self) -> Dict[str, Any]:
        """Load parsing checkpoint if it exists."""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"completed_files": [], "current_file": None, "samhita_processed": False}
    
    def save_checkpoint(self, checkpoint_data: Dict[str, Any]):
        """Save parsing checkpoint."""
        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
    
    def extract_docx_text(self, docx_path: Path) -> List[str]:
        """Extract text paragraphs from DOCX file."""
        try:
            doc = Document(docx_path)
            paragraphs = []
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    paragraphs.append(text)
            return paragraphs
        except Exception as e:
            print(f"Error reading {docx_path}: {e}")
            return []
    
    def extract_verse_id(self, text: str) -> Optional[str]:
        """Extract verse ID from text line."""
        # Pattern 1: "TS 1.1.1.1" format
        match = re.search(r'TS\s+(\d+\.\d+\.\d+\.\d+)', text)
        if match:
            return match.group(1)
        
        # Pattern 2: Just numbers at start "1.1.1.1"
        match = re.search(r'^(\d+\.\d+\.\d+\.\d+)', text.strip())
        if match:
            return match.group(1)
        
        return None
    
    def clean_verse_text(self, text: str) -> str:
        """Clean verse text by removing verse IDs and formatting markers."""
        # Remove verse ID patterns
        text = re.sub(r'^TS\s+\d+\.\d+\.\d+\.\d+\s*', '', text)
        text = re.sub(r'^\d+\.\d+\.\d+\.\d+\s*', '', text)
        
        # Clean up various formatting markers commonly found in these texts
        # Remove standalone bracketed content like "(iqShE - trica#tvAri(gm)Sat ) (A1)"
        text = re.sub(r'\([^)]*\)\s*\([A-Z]\d+\)\s*$', '', text)
        
        # Remove extra whitespace and normalize
        text = ' '.join(text.split())
        return text.strip()
    
    def parse_verses_from_paragraphs(self, paragraphs: List[str], chapter: str) -> List[Dict[str, Any]]:
        """Parse verses from paragraph list."""
        verses = []
        current_verse = None
        verse_text_lines = []
        
        for para in paragraphs:
            # Skip header/instruction paragraphs
            if any(skip_word in para.lower() for skip_word in [
                'notes for users', 'coding is', 'special care', 'confirm corrections',
                'ushmAn codes', 'vedic/swara symbols', '~g is nasal', '~j is nasal'
            ]):
                continue
            
            verse_id = self.extract_verse_id(para)
            
            if verse_id:
                # Save previous verse if exists
                if current_verse and verse_text_lines:
                    text = ' '.join(verse_text_lines)
                    clean_text = self.clean_verse_text(text)
                    if clean_text:  # Only add if there's actual content
                        verses.append({
                            "verse_id": current_verse,
                            "chapter": chapter,
                            "text": clean_text
                        })
                
                # Start new verse
                current_verse = verse_id
                verse_text_lines = [self.clean_verse_text(para)]
            
            elif current_verse:
                # Continue current verse if it's not a header/instruction line
                cleaned = self.clean_verse_text(para)
                if cleaned and len(cleaned) > 5:  # Ignore very short lines
                    verse_text_lines.append(cleaned)
        
        # Don't forget the last verse
        if current_verse and verse_text_lines:
            text = ' '.join(verse_text_lines)
            clean_text = self.clean_verse_text(text)
            if clean_text:
                verses.append({
                    "verse_id": current_verse,
                    "chapter": chapter,
                    "text": clean_text
                })
        
        return verses
    
    def extract_chapter_from_filename(self, filename: str) -> str:
        """Extract chapter number from filename."""
        # For files like "TS 1.1 Baraha Pada paatam.docx" -> "1.1"
        match = re.search(r'TS\s+(\d+\.\d+)', filename)
        if match:
            return match.group(1)
        
        # For files like "TS 1 Baraha.docx" -> "1"
        match = re.search(r'TS\s+(\d+)', filename)
        if match:
            return match.group(1)
        
        return "unknown"
    
    def process_samhita_file(self) -> Dict[str, Any]:
        """Process the samhita file."""
        samhita_file = self.samhita_dir / "TS 1 Baraha.docx"
        
        if not samhita_file.exists():
            print(f"Warning: Samhita file not found: {samhita_file}")
            return {"verses": []}
        
        print(f"Processing samhita file: {samhita_file.name}")
        
        paragraphs = self.extract_docx_text(samhita_file)
        chapter = self.extract_chapter_from_filename(samhita_file.name)
        
        verses = self.parse_verses_from_paragraphs(paragraphs, chapter)
        
        result = {
            "file_type": "samhita",
            "chapter": chapter,
            "source_file": samhita_file.name,
            "verse_count": len(verses),
            "verses": verses
        }
        
        print(f"Extracted {len(verses)} verses from samhita")
        return result
    
    def process_padam_file(self, padam_file: Path) -> Dict[str, Any]:
        """Process a single padam file."""
        print(f"Processing padam file: {padam_file.name}")
        
        paragraphs = self.extract_docx_text(padam_file)
        chapter = self.extract_chapter_from_filename(padam_file.name)
        
        verses = self.parse_verses_from_paragraphs(paragraphs, chapter)
        
        result = {
            "file_type": "padam",
            "chapter": chapter,
            "source_file": padam_file.name,
            "verse_count": len(verses),
            "verses": verses
        }
        
        print(f"Extracted {len(verses)} verses from {padam_file.name}")
        return result
    
    def match_padam_samhita(self, padam_data: Dict, samhita_data: Dict) -> Dict[str, Any]:
        """Match padam and samhita verses by verse ID."""
        
        # Create lookup for samhita verses
        samhita_lookup = {}
        for verse in samhita_data.get("verses", []):
            verse_id = verse.get("verse_id", "")
            samhita_lookup[verse_id] = verse.get("text", "")
        
        # Match with padam verses
        matched_verses = []
        for padam_verse in padam_data.get("verses", []):
            verse_id = padam_verse.get("verse_id", "")
            padam_text = padam_verse.get("text", "")
            samhita_text = samhita_lookup.get(verse_id, "")
            
            # Log if no samhita match found
            if not samhita_text:
                print(f"Warning: No samhita text found for verse {verse_id}")
            
            matched_verses.append({
                "verse_id": verse_id,
                "chapter": padam_verse.get("chapter", ""),
                "padam": padam_text,
                "samhita": samhita_text,
                "has_samhita_match": bool(samhita_text)
            })
        
        return {
            "chapter": padam_data.get("chapter", ""),
            "source_padam_file": padam_data.get("source_file", ""),
            "verse_count": len(matched_verses),
            "matched_count": sum(1 for v in matched_verses if v["has_samhita_match"]),
            "verses": matched_verses
        }
    
    def process_all_files(self):
        """Process all files with robust parsing."""
        checkpoint = self.load_checkpoint()
        completed_files = set(checkpoint.get("completed_files", []))
        
        # Process samhita file first
        samhita_data = {}
        if not checkpoint.get("samhita_processed", False):
            print("Processing samhita file...")
            samhita_data = self.process_samhita_file()
            
            # Save samhita data
            samhita_output = self.output_dir / "samhita_complete.json"
            with open(samhita_output, 'w', encoding='utf-8') as f:
                json.dump(samhita_data, f, ensure_ascii=False, indent=2)
            
            checkpoint["samhita_processed"] = True
            checkpoint["samhita_data"] = samhita_data
            self.save_checkpoint(checkpoint)
            print(f"Samhita processing complete: {len(samhita_data['verses'])} verses saved")
        else:
            samhita_data = checkpoint.get("samhita_data", {})
            print(f"Using cached samhita data: {len(samhita_data.get('verses', []))} verses")
        
        # Get all padam files
        padam_files = sorted(self.padam_dir.glob("*.docx"))
        print(f"Found {len(padam_files)} padam files to process")
        
        # Process each padam file
        for padam_file in padam_files:
            filename = padam_file.name
            
            if filename in completed_files:
                print(f"Skipping {filename} (already completed)")
                continue
            
            # Update checkpoint
            checkpoint["current_file"] = filename
            self.save_checkpoint(checkpoint)
            
            try:
                # Process padam file
                padam_data = self.process_padam_file(padam_file)
                
                # Match with samhita
                matched_data = self.match_padam_samhita(padam_data, samhita_data)
                
                # Save results
                output_file = self.output_dir / f"{filename.replace('.docx', '_matched.json')}"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(matched_data, f, ensure_ascii=False, indent=2)
                
                print(f"Saved {matched_data['verse_count']} verses to {output_file}")
                print(f"  - {matched_data['matched_count']} verses have samhita matches")
                
                # Update checkpoint
                completed_files.add(filename)
                checkpoint["completed_files"] = list(completed_files)
                checkpoint["current_file"] = None
                self.save_checkpoint(checkpoint)
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue
        
        print("Processing complete!")
        self.create_final_output()
    
    def create_final_output(self):
        """Create final combined output for web app."""
        all_chapters = {}
        total_verses = 0
        total_matched = 0
        
        # Load all matched files
        for json_file in sorted(self.output_dir.glob("*_matched.json")):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            chapter = data["chapter"]
            all_chapters[chapter] = data
            total_verses += data["verse_count"]
            total_matched += data.get("matched_count", 0)
        
        final_output = {
            "metadata": {
                "title": "Taittiriya Samhita - Complete Text",
                "description": "Sanskrit verses with padam (word-by-word) and samhita (continuous) versions",
                "total_chapters": len(all_chapters),
                "total_verses": total_verses,
                "total_matched": total_matched,
                "parsing_method": "Robust pattern-based parsing",
                "format_notes": "Each verse contains 'verse_id', 'chapter', 'padam', 'samhita', and 'has_samhita_match' fields"
            },
            "chapters": all_chapters
        }
        
        final_file = self.output_dir / "taittiriya_complete.json"
        with open(final_file, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, ensure_ascii=False, indent=2)
        
        print(f"\nFinal output created: {final_file}")
        print(f"Summary:")
        print(f"  - {final_output['metadata']['total_chapters']} chapters processed")
        print(f"  - {final_output['metadata']['total_verses']} total verses")
        print(f"  - {final_output['metadata']['total_matched']} verses with samhita matches")
        print(f"  - {final_output['metadata']['total_matched']/final_output['metadata']['total_verses']*100:.1f}% match rate")

def main():
    parser = RobustTaittiriyaParser("/Users/skmnktl/Projects/udapaana/data/taittiriya")
    parser.process_all_files()

if __name__ == "__main__":
    main()