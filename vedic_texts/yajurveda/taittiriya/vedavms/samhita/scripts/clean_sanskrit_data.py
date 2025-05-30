#!/usr/bin/env python3
"""
Sanskrit Data Cleaner - Focused on cleaning specific issues in Taittiriya texts
"""

import json
import re
import os
from typing import Dict, List, Any
from collections import defaultdict

class SanskritDataCleaner:
    def __init__(self):
        self.stats = defaultdict(int)
        
    def clean_baraha_encoding(self, text: str) -> str:
        """Convert Baraha encoding to standard transliteration."""
        if not text:
            return text
            
        original = text
        
        # Core vowel replacements
        replacements = {
            'aq': 'a',
            'Aq': 'A', 
            'iq': 'i',
            'Iq': 'I',
            'uq': 'u',
            'Uq': 'U',
            'Eq': 'E',
            'Oq': 'O',
            'eq': 'e',
            'oq': 'o',
            
            # Special characters
            '(gm)': 'ṃ',  # anusvara
            '(gg)': 'ṅ',  # velar nasal
            '(gm)q': 'ṃ',
            
            # Retroflex consonants
            'Sh': 'ṣ',
            'N': 'ṇ',
            'T': 'ṭ',
            'Th': 'ṭh',
            'D': 'ḍ',
            'Dh': 'ḍh',
            
            # Special consonants
            'S': 'ś',
            'n~': 'ñ',
            'j~j': 'jñ',
            'jn~': 'jñ',
            
            # Vocalic r/l
            'r.': 'ṛ',
            'R.': 'ṝ',
            'l.': 'ḷ',
            'L.': 'ḻ',
            
            # Visarga and other marks
            'H': 'ḥ',
            '.h': 'ḥ',
            
            # Fix spacing around pipe
            ' | ': '|',
            '| ': '|',
            ' |': '|',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
            
        # Fix accent markers
        text = re.sub(r'#([^ #]+)', r'\1̍', text)  # svarita
        text = re.sub(r'\$', '̱', text)  # anudatta
        
        # Fix multiple spaces
        text = re.sub(r' +', ' ', text)
        text = text.strip()
        
        if text != original:
            self.stats['baraha_cleaned'] += 1
            
        return text
        
    def clean_verse_text(self, verse: Dict[str, Any]) -> Dict[str, Any]:
        """Clean both padam and samhita text in a verse."""
        if 'padam' in verse:
            verse['padam'] = self.clean_baraha_encoding(verse['padam'])
            
        if 'samhita' in verse:
            verse['samhita'] = self.clean_baraha_encoding(verse['samhita'])
            
            # Remove trailing markers like [ ] or (A1) etc
            verse['samhita'] = re.sub(r'\s*\[.*?\]\s*$', '', verse['samhita'])
            verse['samhita'] = re.sub(r'\s*\(A\d+\)\s*$', '', verse['samhita'])
            verse['samhita'] = re.sub(r'\s*\([^)]+\)\s*$', '', verse['samhita'])
            
        # Ensure verse_id format
        if 'verse_id' in verse:
            verse['verse_id'] = verse['verse_id'].strip()
            
        return verse
        
    def clean_section_text(self, section: Dict[str, Any]) -> Dict[str, Any]:
        """Clean brahmana/aranyaka section text."""
        if 'text' in section:
            section['text'] = self.clean_baraha_encoding(section['text'])
            
            # Remove section number markers at end
            section['text'] = re.sub(r'\s*\|\|\s*\d+\s*\(\d+\)\s*$', '', section['text'])
            
        if 'section_id' in section:
            section['section_id'] = section['section_id'].strip()
            
        return section
        
    def process_parsed_files(self):
        """Process all parsed JSON files."""
        parsed_dir = 'parsed'
        
        # Process samhita files
        for filename in os.listdir(parsed_dir):
            if filename.endswith('_matched.json'):
                filepath = os.path.join(parsed_dir, filename)
                print(f"Cleaning samhita file: {filename}")
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if 'verses' in data:
                    for i, verse in enumerate(data['verses']):
                        data['verses'][i] = self.clean_verse_text(verse)
                        
                # Save cleaned version
                output_path = filepath.replace('.json', '_clean.json')
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
            elif filename.startswith(('TB', 'TA')) and filename.endswith('_parsed.json'):
                filepath = os.path.join(parsed_dir, filename)
                print(f"Cleaning brahmana/aranyaka file: {filename}")
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if 'sections' in data:
                    for i, section in enumerate(data['sections']):
                        data['sections'][i] = self.clean_section_text(section)
                        
                # Save cleaned version
                output_path = filepath.replace('.json', '_clean.json')
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
    def process_complete_corpus(self):
        """Process the complete corpus file."""
        corpus_paths = [
            'parsed/taittiriya_complete_corpus.json',
            'web_complete/taittiriya_complete_corpus.json'
        ]
        
        for corpus_path in corpus_paths:
            if os.path.exists(corpus_path):
                print(f"Cleaning complete corpus: {corpus_path}")
                
                with open(corpus_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Clean samhita
                if 'samhita' in data:
                    for chapter_id, chapter_data in data['samhita'].items():
                        if isinstance(chapter_data, dict) and 'verses' in chapter_data:
                            for i, verse in enumerate(chapter_data['verses']):
                                chapter_data['verses'][i] = self.clean_verse_text(verse)
                                
                # Clean brahmana
                if 'brahmana' in data:
                    for file_id, file_data in data['brahmana'].items():
                        if isinstance(file_data, dict) and 'sections' in file_data:
                            for i, section in enumerate(file_data['sections']):
                                file_data['sections'][i] = self.clean_section_text(section)
                                
                # Clean aranyaka
                if 'aranyaka' in data:
                    for file_id, file_data in data['aranyaka'].items():
                        if isinstance(file_data, dict) and 'sections' in file_data:
                            for i, section in enumerate(file_data['sections']):
                                file_data['sections'][i] = self.clean_section_text(section)
                                
                # Save cleaned version
                output_path = corpus_path.replace('.json', '_clean.json')
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
                break
                
    def print_stats(self):
        """Print cleaning statistics."""
        print("\n=== Cleaning Statistics ===")
        for stat, count in self.stats.items():
            print(f"{stat}: {count}")

def main():
    cleaner = SanskritDataCleaner()
    
    # Process individual parsed files
    cleaner.process_parsed_files()
    
    # Process complete corpus
    cleaner.process_complete_corpus()
    
    # Print statistics
    cleaner.print_stats()
    
    print("\nCleaning complete! Look for *_clean.json files.")

if __name__ == '__main__':
    main()