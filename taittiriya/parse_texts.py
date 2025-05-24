#!/usr/bin/env python3
"""
Parse Taittiriya padam and samhita files and create structured output.
This script processes DOCX files and creates JSON output with checkpoints.
"""

import json
import os
import re
from pathlib import Path
from docx import Document
from typing import Dict, List, Any, Optional

class TaittiriyaParser:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.padam_dir = self.base_dir / "raw" / "padam"
        self.samhita_dir = self.base_dir / "raw" / "samhita" 
        self.output_dir = self.base_dir / "parsed"
        self.checkpoint_file = self.base_dir / "parsing_checkpoint.json"
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
    def load_checkpoint(self) -> Dict[str, Any]:
        """Load parsing checkpoint if it exists."""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"completed_files": [], "current_file": None, "samhita_cache": {}}
    
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
                if text:  # Skip empty paragraphs
                    paragraphs.append(text)
            return paragraphs
        except Exception as e:
            print(f"Error reading {docx_path}: {e}")
            return []
    
    def parse_verse_number(self, text: str) -> Optional[str]:
        """Extract verse number from text (e.g., '1.1.1', '1.1.2' etc.)"""
        # Look for patterns like "1.1.1" at the beginning of lines
        match = re.search(r'^\s*(\d+\.\d+\.\d+)', text)
        if match:
            return match.group(1)
        return None
    
    def clean_verse_text(self, text: str) -> str:
        """Clean verse text by removing verse numbers and extra whitespace."""
        # Remove verse numbers from the beginning
        text = re.sub(r'^\s*\d+\.\d+\.\d+\s*', '', text)
        # Normalize whitespace
        text = ' '.join(text.split())
        return text.strip()
    
    def load_samhita_text(self, chapter: str) -> Dict[str, str]:
        """Load and parse samhita text for a given chapter."""
        samhita_file = self.samhita_dir / f"TS {chapter} Baraha.docx"
        if not samhita_file.exists():
            print(f"Warning: Samhita file not found: {samhita_file}")
            return {}
        
        paragraphs = self.extract_docx_text(samhita_file)
        samhita_verses = {}
        
        for para in paragraphs:
            verse_num = self.parse_verse_number(para)
            if verse_num:
                clean_text = self.clean_verse_text(para)
                if clean_text:
                    samhita_verses[verse_num] = clean_text
        
        return samhita_verses
    
    def parse_padam_file(self, padam_file: Path, samhita_verses: Dict[str, str]) -> Dict[str, Any]:
        """Parse a single padam file and match with samhita verses."""
        paragraphs = self.extract_docx_text(padam_file)
        
        # Extract chapter info from filename (e.g., "TS 1.1 Baraha Pada paatam.docx" -> "1.1")
        filename = padam_file.stem
        chapter_match = re.search(r'TS (\d+\.\d+)', filename)
        chapter = chapter_match.group(1) if chapter_match else "unknown"
        
        verses = []
        
        for para in paragraphs:
            verse_num = self.parse_verse_number(para)
            if verse_num:
                padam_text = self.clean_verse_text(para)
                samhita_text = samhita_verses.get(verse_num, "")
                
                if padam_text:  # Only include verses with actual content
                    verse_data = {
                        "verse_number": verse_num,
                        "chapter": chapter,
                        "padam": padam_text,
                        "samhita": samhita_text
                    }
                    verses.append(verse_data)
        
        return {
            "chapter": chapter,
            "source_file": padam_file.name,
            "verse_count": len(verses),
            "verses": verses
        }
    
    def process_all_files(self):
        """Process all padam files with checkpoint support."""
        checkpoint = self.load_checkpoint()
        completed_files = set(checkpoint.get("completed_files", []))
        samhita_cache = checkpoint.get("samhita_cache", {})
        
        # Get all padam files
        padam_files = sorted(self.padam_dir.glob("*.docx"))
        
        print(f"Found {len(padam_files)} padam files to process")
        
        for padam_file in padam_files:
            filename = padam_file.name
            
            # Skip if already completed
            if filename in completed_files:
                print(f"Skipping {filename} (already completed)")
                continue
                
            print(f"Processing {filename}...")
            
            # Update checkpoint with current file
            checkpoint["current_file"] = filename
            self.save_checkpoint(checkpoint)
            
            # Extract chapter number for samhita lookup
            chapter_match = re.search(r'TS (\d+)', filename)
            chapter = chapter_match.group(1) if chapter_match else "1"
            
            # Load samhita verses (with caching)
            if chapter not in samhita_cache:
                print(f"Loading samhita for chapter {chapter}...")
                samhita_cache[chapter] = self.load_samhita_text(chapter)
                checkpoint["samhita_cache"] = samhita_cache
                self.save_checkpoint(checkpoint)
            
            # Parse padam file
            result = self.parse_padam_file(padam_file, samhita_cache[chapter])
            
            # Save individual result
            output_file = self.output_dir / f"{filename.replace('.docx', '.json')}"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"Saved {len(result['verses'])} verses to {output_file}")
            
            # Update checkpoint
            completed_files.add(filename)
            checkpoint["completed_files"] = list(completed_files)
            checkpoint["current_file"] = None
            self.save_checkpoint(checkpoint)
        
        print("All files processed successfully!")
        
        # Create combined output
        self.create_combined_output()
    
    def create_combined_output(self):
        """Create a combined JSON file with all parsed data."""
        combined_data = {
            "metadata": {
                "title": "Taittiriya Samhita - Padam and Samhita",
                "description": "Parsed Sanskrit texts with word-by-word (padam) and continuous (samhita) recitations",
                "total_chapters": 0,
                "total_verses": 0
            },
            "chapters": {}
        }
        
        # Load all individual JSON files
        for json_file in sorted(self.output_dir.glob("TS *.json")):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            chapter = data["chapter"]
            combined_data["chapters"][chapter] = data
            combined_data["metadata"]["total_verses"] += data["verse_count"]
        
        combined_data["metadata"]["total_chapters"] = len(combined_data["chapters"])
        
        # Save combined file
        combined_file = self.output_dir / "taittiriya_complete.json"
        with open(combined_file, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=2)
        
        print(f"Created combined output: {combined_file}")
        print(f"Total: {combined_data['metadata']['total_chapters']} chapters, {combined_data['metadata']['total_verses']} verses")

def main():
    parser = TaittiriyaParser("/Users/skmnktl/Projects/udapaana/data/taittiriya")
    parser.process_all_files()

if __name__ == "__main__":
    main()