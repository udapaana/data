#!/usr/bin/env python3
"""
Smart parser for Taittiriya texts using LLM to handle inconsistent formatting.
"""

import json
import os
import re
from pathlib import Path
from docx import Document
from typing import Dict, List, Any, Optional
import openai
import time

class SmartTaittiriyaParser:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.padam_dir = self.base_dir / "raw" / "padam"
        self.samhita_dir = self.base_dir / "raw" / "samhita" 
        self.output_dir = self.base_dir / "parsed"
        self.checkpoint_file = self.base_dir / "smart_parsing_checkpoint.json"
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
        # OpenAI client (assumes OPENAI_API_KEY is set)
        self.client = openai.OpenAI()
        
    def load_checkpoint(self) -> Dict[str, Any]:
        """Load parsing checkpoint if it exists."""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"completed_files": [], "current_file": None, "processed_chunks": {}}
    
    def save_checkpoint(self, checkpoint_data: Dict[str, Any]):
        """Save parsing checkpoint."""
        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
    
    def extract_docx_text(self, docx_path: Path) -> str:
        """Extract all text from DOCX file as a single string."""
        try:
            doc = Document(docx_path)
            full_text = []
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    full_text.append(text)
            return '\n'.join(full_text)
        except Exception as e:
            print(f"Error reading {docx_path}: {e}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 3000) -> List[str]:
        """Split text into manageable chunks for API processing."""
        chunks = []
        lines = text.split('\n')
        current_chunk = []
        current_length = 0
        
        for line in lines:
            line_length = len(line) + 1  # +1 for newline
            if current_length + line_length > chunk_size and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_length = line_length
            else:
                current_chunk.append(line)
                current_length += line_length
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    
    def parse_chunk_with_llm(self, chunk: str, file_type: str, chapter: str) -> List[Dict[str, Any]]:
        """Use LLM to parse a chunk of text and extract verse information."""
        
        system_prompt = f"""You are parsing Sanskrit texts from the Taittiriya Samhita. Extract verses with their identifiers.

File type: {file_type} (either "padam" for word-by-word or "samhita" for continuous recitation)
Chapter: {chapter}

For each verse you find:
1. Extract the verse identifier (like "TS 1.1.1.1", "1.1.1.1", or similar patterns)
2. Extract the Sanskrit text content (excluding the identifier)
3. Clean up the text by removing extra formatting markers

Return ONLY a valid JSON array of objects, each with:
- "verse_id": the verse identifier 
- "text": the cleaned Sanskrit text
- "chapter": the chapter number

If no verses are found, return an empty array [].
Do not include any explanation or markdown - just the JSON array."""

        user_prompt = f"Parse this text chunk:\n\n{chunk}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Try to parse as JSON
            try:
                verses = json.loads(result_text)
                if isinstance(verses, list):
                    return verses
                else:
                    print(f"Warning: LLM returned non-list: {type(verses)}")
                    return []
            except json.JSONDecodeError as e:
                print(f"Warning: LLM returned invalid JSON: {e}")
                print(f"Response was: {result_text[:200]}...")
                return []
                
        except Exception as e:
            print(f"Error calling LLM API: {e}")
            return []
    
    def process_file_with_llm(self, file_path: Path, file_type: str) -> Dict[str, Any]:
        """Process a complete file using LLM chunking."""
        print(f"Processing {file_path.name} as {file_type}...")
        
        # Extract chapter from filename
        filename = file_path.stem
        chapter_match = re.search(r'(\d+\.?\d*)', filename)
        chapter = chapter_match.group(1) if chapter_match else "unknown"
        
        # Extract text
        full_text = self.extract_docx_text(file_path)
        if not full_text:
            return {"chapter": chapter, "verses": [], "error": "No text extracted"}
        
        # Split into chunks
        chunks = self.chunk_text(full_text)
        print(f"Split into {len(chunks)} chunks")
        
        all_verses = []
        
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}...")
            verses = self.parse_chunk_with_llm(chunk, file_type, chapter)
            all_verses.extend(verses)
            
            # Small delay to be API-friendly
            time.sleep(0.5)
        
        return {
            "chapter": chapter,
            "file_type": file_type,
            "source_file": file_path.name,
            "verse_count": len(all_verses),
            "verses": all_verses
        }
    
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
            
            matched_verses.append({
                "verse_id": verse_id,
                "chapter": padam_verse.get("chapter", ""),
                "padam": padam_text,
                "samhita": samhita_text
            })
        
        return {
            "chapter": padam_data.get("chapter", ""),
            "verse_count": len(matched_verses),
            "verses": matched_verses
        }
    
    def process_all_files(self):
        """Process all files with smart parsing."""
        checkpoint = self.load_checkpoint()
        completed_files = set(checkpoint.get("completed_files", []))
        
        # Get all padam files
        padam_files = sorted(self.padam_dir.glob("*.docx"))
        
        print(f"Found {len(padam_files)} padam files to process")
        
        # First, process samhita file (single file for chapter 1)
        samhita_file = self.samhita_dir / "TS 1 Baraha.docx"
        samhita_data = {}
        
        if samhita_file.exists() and "samhita_processed" not in checkpoint:
            print("Processing samhita file...")
            samhita_data = self.process_file_with_llm(samhita_file, "samhita")
            
            # Save samhita data
            samhita_output = self.output_dir / "samhita_complete.json"
            with open(samhita_output, 'w', encoding='utf-8') as f:
                json.dump(samhita_data, f, ensure_ascii=False, indent=2)
            
            checkpoint["samhita_processed"] = True
            checkpoint["samhita_data"] = samhita_data
            self.save_checkpoint(checkpoint)
        else:
            samhita_data = checkpoint.get("samhita_data", {})
        
        # Process padam files
        for padam_file in padam_files:
            filename = padam_file.name
            
            if filename in completed_files:
                print(f"Skipping {filename} (already completed)")
                continue
            
            # Update checkpoint
            checkpoint["current_file"] = filename
            self.save_checkpoint(checkpoint)
            
            # Process padam file
            padam_data = self.process_file_with_llm(padam_file, "padam")
            
            # Match with samhita
            matched_data = self.match_padam_samhita(padam_data, samhita_data)
            
            # Save results
            output_file = self.output_dir / f"{filename.replace('.docx', '_matched.json')}"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(matched_data, f, ensure_ascii=False, indent=2)
            
            print(f"Saved {len(matched_data['verses'])} matched verses to {output_file}")
            
            # Update checkpoint
            completed_files.add(filename)
            checkpoint["completed_files"] = list(completed_files)
            checkpoint["current_file"] = None
            self.save_checkpoint(checkpoint)
        
        print("Processing complete!")
        self.create_final_output()
    
    def create_final_output(self):
        """Create final combined output for web app."""
        all_chapters = {}
        
        # Load all matched files
        for json_file in sorted(self.output_dir.glob("*_matched.json")):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            chapter = data["chapter"]
            all_chapters[chapter] = data
        
        final_output = {
            "metadata": {
                "title": "Taittiriya Samhita - Complete Text",
                "description": "Sanskrit verses with padam (word-by-word) and samhita (continuous) versions",
                "total_chapters": len(all_chapters),
                "total_verses": sum(len(ch["verses"]) for ch in all_chapters.values()),
                "parsing_method": "LLM-assisted smart parsing"
            },
            "chapters": all_chapters
        }
        
        final_file = self.output_dir / "taittiriya_complete.json"
        with open(final_file, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, ensure_ascii=False, indent=2)
        
        print(f"Created final output: {final_file}")
        print(f"Total: {final_output['metadata']['total_chapters']} chapters, {final_output['metadata']['total_verses']} verses")

def main():
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set it with: export OPENAI_API_KEY='your-api-key'")
        return
    
    parser = SmartTaittiriyaParser("/Users/skmnktl/Projects/udapaana/data/taittiriya")
    parser.process_all_files()

if __name__ == "__main__":
    main()