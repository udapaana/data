#!/usr/bin/env python3
"""
Parser for Taittiriya Brahmana and Aranyaka texts.
These texts don't have padam versions and have different organizational structures.
"""

import json
import re
from pathlib import Path
from docx import Document
from typing import Dict, List, Any, Optional

class BrahmanaAranyakaParser:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.brahmana_dir = self.base_dir / "raw" / "brahmana"
        self.aranyaka_dir = self.base_dir / "raw" / "aranyaka"
        self.output_dir = self.base_dir / "parsed"
        self.checkpoint_file = self.base_dir / "brahmana_aranyaka_checkpoint.json"
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
    def load_checkpoint(self) -> Dict[str, Any]:
        """Load parsing checkpoint if it exists."""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "completed_brahmana_files": [],
            "completed_aranyaka_files": [],
            "current_file": None
        }
    
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
    
    def extract_section_id(self, text: str, text_type: str) -> Optional[str]:
        """Extract section ID from text line."""
        if text_type == "brahmana":
            # Pattern for TB sections: "TB 1.1.1.1", "T.B.1.1.1.1", or "1.1.1.1"
            match = re.search(r'T\.?B\.?\s*(\d+\.\d+\.\d+\.\d+)', text)
            if match:
                return match.group(1)
            
            match = re.search(r'^(\d+\.\d+\.\d+\.\d+)', text.strip())
            if match:
                return match.group(1)
                
        elif text_type == "aranyaka":
            # Pattern for TA sections: "TA 1.1.1", "T.A.1.1.1", or "1.1.1"
            match = re.search(r'T\.?A\.?\s*(\d+\.\d+\.\d+)', text)
            if match:
                return match.group(1)
            
            match = re.search(r'^(\d+\.\d+\.\d+)', text.strip())
            if match:
                return match.group(1)
        
        return None
    
    def clean_section_text(self, text: str, text_type: str) -> str:
        """Clean section text by removing section IDs and formatting markers."""
        if text_type == "brahmana":
            # Remove TB section ID patterns
            text = re.sub(r'^T\.?B\.?\s*\d+\.\d+\.\d+\.\d+\s*', '', text)
            text = re.sub(r'^\d+\.\d+\.\d+\.\d+\s*', '', text)
        elif text_type == "aranyaka":
            # Remove TA section ID patterns
            text = re.sub(r'^T\.?A\.?\s*\d+\.\d+\.\d+\s*', '', text)
            text = re.sub(r'^\d+\.\d+\.\d+\s*', '', text)
        
        # Clean up various formatting markers
        text = re.sub(r'\([^)]*\)\s*\([A-Z]\d+\)\s*$', '', text)
        
        # Remove extra whitespace and normalize
        text = ' '.join(text.split())
        return text.strip()
    
    def parse_sections_from_paragraphs(self, paragraphs: List[str], text_type: str, file_info: str) -> List[Dict[str, Any]]:
        """Parse sections from paragraph list."""
        sections = []
        current_section = None
        section_text_lines = []
        
        for para in paragraphs:
            # Skip header/instruction paragraphs
            if any(skip_word in para.lower() for skip_word in [
                'notes for users', 'coding is', 'special care', 'confirm corrections',
                'ushmAn codes', 'vedic/swara symbols', '~g is nasal', '~j is nasal',
                'kRuShNa yajurvEdIya', 'taittirIya', 'brahmaNE', 'AraNyakE'
            ]):
                continue
            
            section_id = self.extract_section_id(para, text_type)
            
            if section_id:
                # Save previous section if exists
                if current_section and section_text_lines:
                    text = ' '.join(section_text_lines)
                    clean_text = self.clean_section_text(text, text_type)
                    if clean_text:  # Only add if there's actual content
                        sections.append({
                            "section_id": current_section,
                            "file_info": file_info,
                            "text": clean_text,
                            "text_type": text_type
                        })
                
                # Start new section
                current_section = section_id
                section_text_lines = [self.clean_section_text(para, text_type)]
            
            elif current_section:
                # Continue current section if it's not a header/instruction line
                cleaned = self.clean_section_text(para, text_type)
                if cleaned and len(cleaned) > 10:  # Ignore very short lines
                    section_text_lines.append(cleaned)
        
        # Don't forget the last section
        if current_section and section_text_lines:
            text = ' '.join(section_text_lines)
            clean_text = self.clean_section_text(text, text_type)
            if clean_text:
                sections.append({
                    "section_id": current_section,
                    "file_info": file_info,
                    "text": clean_text,
                    "text_type": text_type
                })
        
        return sections
    
    def extract_file_info_from_filename(self, filename: str, text_type: str) -> str:
        """Extract file information from filename."""
        if text_type == "brahmana":
            # For files like "TB 1.1-1.4 Baraha.docx"
            match = re.search(r'TB\s+([0-9.-]+)', filename)
            if match:
                return match.group(1)
        elif text_type == "aranyaka":
            # For files like "TA 1-4 Baraha.docx"
            match = re.search(r'TA\s+([0-9.-]+)', filename)
            if match:
                return match.group(1)
        
        return filename.replace('.docx', '')
    
    def process_brahmana_file(self, brahmana_file: Path) -> Dict[str, Any]:
        """Process a single brahmana file."""
        print(f"Processing brahmana file: {brahmana_file.name}")
        
        paragraphs = self.extract_docx_text(brahmana_file)
        file_info = self.extract_file_info_from_filename(brahmana_file.name, "brahmana")
        
        sections = self.parse_sections_from_paragraphs(paragraphs, "brahmana", file_info)
        
        result = {
            "text_type": "brahmana",
            "file_info": file_info,
            "source_file": brahmana_file.name,
            "section_count": len(sections),
            "sections": sections
        }
        
        print(f"Extracted {len(sections)} sections from {brahmana_file.name}")
        return result
    
    def process_aranyaka_file(self, aranyaka_file: Path) -> Dict[str, Any]:
        """Process a single aranyaka file."""
        print(f"Processing aranyaka file: {aranyaka_file.name}")
        
        paragraphs = self.extract_docx_text(aranyaka_file)
        file_info = self.extract_file_info_from_filename(aranyaka_file.name, "aranyaka")
        
        sections = self.parse_sections_from_paragraphs(paragraphs, "aranyaka", file_info)
        
        result = {
            "text_type": "aranyaka",
            "file_info": file_info,
            "source_file": aranyaka_file.name,
            "section_count": len(sections),
            "sections": sections
        }
        
        print(f"Extracted {len(sections)} sections from {aranyaka_file.name}")
        return result
    
    def process_all_files(self):
        """Process all brahmana and aranyaka files."""
        checkpoint = self.load_checkpoint()
        completed_brahmana = set(checkpoint.get("completed_brahmana_files", []))
        completed_aranyaka = set(checkpoint.get("completed_aranyaka_files", []))
        
        all_brahmana_data = []
        all_aranyaka_data = []
        
        # Process brahmana files
        brahmana_files = sorted(self.brahmana_dir.glob("*.docx"))
        print(f"Found {len(brahmana_files)} brahmana files to process")
        
        for brahmana_file in brahmana_files:
            filename = brahmana_file.name
            
            if filename in completed_brahmana:
                print(f"Skipping brahmana {filename} (already completed)")
                continue
            
            # Update checkpoint
            checkpoint["current_file"] = filename
            self.save_checkpoint(checkpoint)
            
            try:
                # Process brahmana file
                brahmana_data = self.process_brahmana_file(brahmana_file)
                all_brahmana_data.append(brahmana_data)
                
                # Save individual result
                output_file = self.output_dir / f"{filename.replace('.docx', '_parsed.json')}"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(brahmana_data, f, ensure_ascii=False, indent=2)
                
                print(f"Saved {brahmana_data['section_count']} sections to {output_file}")
                
                # Update checkpoint
                completed_brahmana.add(filename)
                checkpoint["completed_brahmana_files"] = list(completed_brahmana)
                checkpoint["current_file"] = None
                self.save_checkpoint(checkpoint)
                
            except Exception as e:
                print(f"Error processing brahmana {filename}: {e}")
                continue
        
        # Process aranyaka files
        aranyaka_files = sorted(self.aranyaka_dir.glob("*.docx"))
        print(f"Found {len(aranyaka_files)} aranyaka files to process")
        
        for aranyaka_file in aranyaka_files:
            filename = aranyaka_file.name
            
            if filename in completed_aranyaka:
                print(f"Skipping aranyaka {filename} (already completed)")
                continue
            
            # Update checkpoint
            checkpoint["current_file"] = filename
            self.save_checkpoint(checkpoint)
            
            try:
                # Process aranyaka file
                aranyaka_data = self.process_aranyaka_file(aranyaka_file)
                all_aranyaka_data.append(aranyaka_data)
                
                # Save individual result
                output_file = self.output_dir / f"{filename.replace('.docx', '_parsed.json')}"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(aranyaka_data, f, ensure_ascii=False, indent=2)
                
                print(f"Saved {aranyaka_data['section_count']} sections to {output_file}")
                
                # Update checkpoint
                completed_aranyaka.add(filename)
                checkpoint["completed_aranyaka_files"] = list(completed_aranyaka)
                checkpoint["current_file"] = None
                self.save_checkpoint(checkpoint)
                
            except Exception as e:
                print(f"Error processing aranyaka {filename}: {e}")
                continue
        
        print("Processing complete!")
        self.create_combined_output(all_brahmana_data, all_aranyaka_data)
    
    def create_combined_output(self, brahmana_data: List[Dict], aranyaka_data: List[Dict]):
        """Create combined output for brahmana and aranyaka texts."""
        
        # Count totals
        total_brahmana_sections = sum(data["section_count"] for data in brahmana_data)
        total_aranyaka_sections = sum(data["section_count"] for data in aranyaka_data)
        
        combined_output = {
            "metadata": {
                "title": "Taittiriya Brahmana and Aranyaka - Complete Text",
                "description": "Sanskrit prose texts from the Taittiriya tradition",
                "total_brahmana_files": len(brahmana_data),
                "total_aranyaka_files": len(aranyaka_data),
                "total_brahmana_sections": total_brahmana_sections,
                "total_aranyaka_sections": total_aranyaka_sections,
                "total_sections": total_brahmana_sections + total_aranyaka_sections,
                "parsing_method": "Brahmana-Aranyaka specialized parsing",
                "format_notes": "Each section contains 'section_id', 'file_info', 'text', and 'text_type' fields"
            },
            "brahmana": {
                "files": brahmana_data,
                "total_sections": total_brahmana_sections
            },
            "aranyaka": {
                "files": aranyaka_data,
                "total_sections": total_aranyaka_sections
            }
        }
        
        # Save combined file
        combined_file = self.output_dir / "taittiriya_brahmana_aranyaka_complete.json"
        with open(combined_file, 'w', encoding='utf-8') as f:
            json.dump(combined_output, f, ensure_ascii=False, indent=2)
        
        print(f"\nCombined output created: {combined_file}")
        print(f"Summary:")
        print(f"  - {len(brahmana_data)} brahmana files processed")
        print(f"  - {len(aranyaka_data)} aranyaka files processed")
        print(f"  - {total_brahmana_sections} brahmana sections")
        print(f"  - {total_aranyaka_sections} aranyaka sections")
        print(f"  - {total_brahmana_sections + total_aranyaka_sections} total sections")

def main():
    parser = BrahmanaAranyakaParser("/Users/skmnktl/Projects/udapaana/data/taittiriya")
    parser.process_all_files()

if __name__ == "__main__":
    main()