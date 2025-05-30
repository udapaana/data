#!/usr/bin/env python3
"""
Test the smart parser on a small sample
"""

import os
from pathlib import Path
from docx import Document

def extract_docx_text(docx_path):
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

def test_text_extraction():
    """Test basic text extraction from DOCX files."""
    base_dir = Path("/Users/skmnktl/Projects/udapaana/data/taittiriya")
    
    # Test padam file
    padam_file = base_dir / "raw/padam/TS 1.1 Baraha Pada paatam.docx"
    if padam_file.exists():
        text = extract_docx_text(padam_file)
        print(f"Padam file text length: {len(text)}")
        print("First 500 characters:")
        print(text[:500])
        print("\n" + "="*50 + "\n")
    
    # Test samhita file  
    samhita_file = base_dir / "raw/samhita/TS 1 Baraha.docx"
    if samhita_file.exists():
        text = extract_docx_text(samhita_file)
        print(f"\nSamhita file text length: {len(text)}")
        print("Sample from middle (chars 5000-5500):")
        print(text[5000:5500])
        
        # Look for verse patterns
        lines = text.split('\n')
        verse_lines = []
        for line in lines:
            if 'TS 1.1.' in line or line.strip().startswith('1.1.'):
                verse_lines.append(line.strip())
                if len(verse_lines) >= 10:  # Just show first 10
                    break
        
        print(f"\nFound {len(verse_lines)} verse-like lines:")
        for line in verse_lines:
            print(f"  {line[:100]}..." if len(line) > 100 else f"  {line}")

if __name__ == "__main__":
    test_text_extraction()