#!/usr/bin/env python3
"""
Data Quality Improvement Script for Taittiriya Corpus
Identifies and fixes common data quality issues in parsed Sanskrit texts.
"""

import json
import re
import os
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict
import unicodedata

class DataQualityImprover:
    def __init__(self):
        self.issues_found = defaultdict(list)
        self.fixes_applied = defaultdict(int)
        
    def normalize_unicode(self, text: str) -> str:
        """Normalize Unicode characters to ensure consistency."""
        # Use NFC (Canonical Decomposition, followed by Canonical Composition)
        return unicodedata.normalize('NFC', text)
        
    def fix_whitespace_issues(self, text: str) -> str:
        """Fix common whitespace issues."""
        original = text
        
        # Remove multiple spaces
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove spaces before punctuation
        text = re.sub(r' +([|,;.!?])', r'\1', text)
        
        # Ensure space after punctuation (except at end)
        text = re.sub(r'([|,;.!?])(?=[^\s])', r'\1 ', text)
        
        # Remove trailing/leading whitespace
        text = text.strip()
        
        if text != original:
            self.fixes_applied['whitespace'] += 1
            
        return text
        
    def fix_special_characters(self, text: str) -> str:
        """Fix inconsistent special character usage."""
        original = text
        
        # Fix common encoding issues
        replacements = {
            '\u0952': '॒',  # Vedic grave accent
            '\u0951': '॑',  # Vedic acute accent
            'aq': 'a',  # Common transliteration issue
            'Eq': 'E',
            'iq': 'i',
            'Iq': 'I',
            'uq': 'u',
            'Uq': 'U',
            'Oq': 'O',
            '(gm)': 'ṃ',  # Anusvara
            '(gg)': 'ṅ',  # Velar nasal
            'r.': 'ṛ',
            'R.': 'Ṛ',
            'l.': 'ḷ',
            'L.': 'Ḷ',
            'S': 'ś',
            'Sh': 'ṣ',
            'N': 'ṇ',
            'n~': 'ñ',
            'ch': 'c',
            'Ch': 'C',
            'jn~': 'jñ',
            'j~j': 'jñ'
        }
        
        for old, new in replacements.items():
            if old in text:
                text = text.replace(old, new)
                self.fixes_applied['special_chars'] += 1
                
        # Fix diacritical marks
        text = re.sub(r'#([^\s#]+)', r'\1̍', text)  # Svarita marker
        text = re.sub(r'\$', '̱', text)  # Anudatta marker
        
        if text != original:
            self.issues_found['special_chars'].append(f"Fixed: {original[:50]}...")
            
        return text
        
    def fix_verse_numbering(self, verse_id: str) -> str:
        """Ensure consistent verse numbering format."""
        # Standard format: X.Y.Z.W where X,Y,Z,W are numbers
        if re.match(r'^\d+\.\d+\.\d+\.\d+$', verse_id):
            return verse_id
            
        # Fix common issues
        verse_id = verse_id.strip()
        verse_id = re.sub(r'\s+', '', verse_id)  # Remove spaces
        verse_id = re.sub(r'[,;]', '.', verse_id)  # Replace wrong separators
        
        if not re.match(r'^\d+\.\d+\.\d+\.\d+$', verse_id):
            self.issues_found['verse_numbering'].append(f"Invalid format: {verse_id}")
            
        return verse_id
        
    def validate_samhita_verse(self, verse: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and fix issues in samhita verses."""
        # Fix verse ID
        if 'verse_id' in verse:
            verse['verse_id'] = self.fix_verse_numbering(verse['verse_id'])
            
        # Fix padam text
        if 'padam' in verse:
            verse['padam'] = self.fix_whitespace_issues(verse['padam'])
            verse['padam'] = self.fix_special_characters(verse['padam'])
            verse['padam'] = self.normalize_unicode(verse['padam'])
            
        # Fix samhita text
        if 'samhita' in verse:
            verse['samhita'] = self.fix_whitespace_issues(verse['samhita'])
            verse['samhita'] = self.fix_special_characters(verse['samhita'])
            verse['samhita'] = self.normalize_unicode(verse['samhita'])
            
        # Validate matching status
        if verse.get('has_samhita_match') and ('padam' not in verse or 'samhita' not in verse):
            self.issues_found['matching'].append(f"Verse {verse.get('verse_id')} claims match but missing text")
            verse['has_samhita_match'] = False
            
        return verse
        
    def validate_brahmana_section(self, section: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and fix issues in brahmana/aranyaka sections."""
        # Fix section ID
        if 'section_id' in section:
            section['section_id'] = self.fix_verse_numbering(section['section_id'])
            
        # Fix text
        if 'text' in section:
            section['text'] = self.fix_whitespace_issues(section['text'])
            section['text'] = self.fix_special_characters(section['text'])
            section['text'] = self.normalize_unicode(section['text'])
            
            # Check for empty or too short text
            if len(section['text'].strip()) < 10:
                self.issues_found['empty_text'].append(f"Section {section.get('section_id')} has very short text")
                
        return section
        
    def check_duplicates(self, items: List[Dict[str, Any]], id_field: str) -> Set[str]:
        """Check for duplicate IDs."""
        seen_ids = set()
        duplicates = set()
        
        for item in items:
            item_id = item.get(id_field)
            if item_id:
                if item_id in seen_ids:
                    duplicates.add(item_id)
                    self.issues_found['duplicates'].append(f"Duplicate ID: {item_id}")
                seen_ids.add(item_id)
                
        return duplicates
        
    def process_samhita_file(self, filepath: str) -> None:
        """Process a samhita JSON file."""
        print(f"Processing samhita file: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Check structure
        if isinstance(data, dict) and 'verses' in data:
            # Fix each verse
            verses = data['verses']
            for i, verse in enumerate(verses):
                verses[i] = self.validate_samhita_verse(verse)
                
            # Check for duplicates
            self.check_duplicates(verses, 'verse_id')
            
            # Update counts
            if 'verse_count' in data:
                actual_count = len(verses)
                if data['verse_count'] != actual_count:
                    self.issues_found['counts'].append(
                        f"File {filepath}: claimed {data['verse_count']} verses, found {actual_count}"
                    )
                    data['verse_count'] = actual_count
                    
        # Save cleaned data
        output_path = filepath.replace('.json', '_cleaned.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    def process_brahmana_file(self, filepath: str) -> None:
        """Process a brahmana/aranyaka JSON file."""
        print(f"Processing brahmana/aranyaka file: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Check structure
        if isinstance(data, dict) and 'sections' in data:
            # Fix each section
            sections = data['sections']
            for i, section in enumerate(sections):
                sections[i] = self.validate_brahmana_section(section)
                
            # Check for duplicates
            self.check_duplicates(sections, 'section_id')
            
            # Update counts
            if 'section_count' in data:
                actual_count = len(sections)
                if data['section_count'] != actual_count:
                    self.issues_found['counts'].append(
                        f"File {filepath}: claimed {data['section_count']} sections, found {actual_count}"
                    )
                    data['section_count'] = actual_count
                    
        # Save cleaned data
        output_path = filepath.replace('.json', '_cleaned.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    def process_complete_corpus(self, filepath: str) -> None:
        """Process the complete corpus file."""
        print(f"Processing complete corpus: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Process samhita sections
        if 'samhita' in data:
            for kanda_num, kanda_data in data['samhita'].items():
                if isinstance(kanda_data, dict):
                    for chapter_num, chapter_data in kanda_data.items():
                        if isinstance(chapter_data, dict) and 'verses' in chapter_data:
                            verses = chapter_data['verses']
                            for i, verse in enumerate(verses):
                                verses[i] = self.validate_samhita_verse(verse)
                            
        # Process brahmana sections
        if 'brahmana' in data:
            for file_id, file_data in data['brahmana'].items():
                if 'sections' in file_data:
                    sections = file_data['sections']
                    for i, section in enumerate(sections):
                        sections[i] = self.validate_brahmana_section(section)
                        
        # Process aranyaka sections
        if 'aranyaka' in data:
            for file_id, file_data in data['aranyaka'].items():
                if 'sections' in file_data:
                    sections = file_data['sections']
                    for i, section in enumerate(sections):
                        sections[i] = self.validate_brahmana_section(section)
                        
        # Update metadata
        if 'metadata' in data and 'totals' in data['metadata']:
            # Recount everything
            samhita_count = sum(
                len(chapter.get('verses', [])) 
                for kanda in data.get('samhita', {}).values()
                for chapter in kanda.values()
            )
            brahmana_count = sum(
                len(file_data.get('sections', []))
                for file_data in data.get('brahmana', {}).values()
            )
            aranyaka_count = sum(
                len(file_data.get('sections', []))
                for file_data in data.get('aranyaka', {}).values()
            )
            
            total_count = samhita_count + brahmana_count + aranyaka_count
            
            if data['metadata']['totals']['total_texts'] != total_count:
                self.issues_found['totals'].append(
                    f"Total count mismatch: claimed {data['metadata']['totals']['total_texts']}, found {total_count}"
                )
                data['metadata']['totals']['total_texts'] = total_count
                
        # Save cleaned data
        output_path = filepath.replace('.json', '_cleaned.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    def generate_report(self) -> str:
        """Generate a report of issues found and fixes applied."""
        report = ["\n=== Data Quality Report ==="]
        
        report.append("\n## Issues Found:")
        for issue_type, issues in self.issues_found.items():
            report.append(f"\n### {issue_type.replace('_', ' ').title()}:")
            report.append(f"Total: {len(issues)}")
            # Show first 5 examples
            for issue in issues[:5]:
                report.append(f"  - {issue}")
            if len(issues) > 5:
                report.append(f"  ... and {len(issues) - 5} more")
                
        report.append("\n## Fixes Applied:")
        for fix_type, count in self.fixes_applied.items():
            report.append(f"- {fix_type.replace('_', ' ').title()}: {count}")
            
        return "\n".join(report)


def main():
    improver = DataQualityImprover()
    
    # Process samhita files
    samhita_files = [
        'parsed/TS 1.1 Baraha Pada paatam_matched.json',
        'parsed/TS 1.2 Baraha Pada paatam_matched.json',
        'parsed/TS 1.3 Baraha Pada paatam_matched.json',
        'parsed/TS 1.4 Baraha Pada paatam_matched.json',
        'parsed/TS 1.5 Baraha Pada paatam_matched.json',
        'parsed/TS 1.6 Baraha Pada paatam_matched.json',
        'parsed/TS 1.7 Baraha Pada paatam_matched.json',
        'parsed/TS 1.8 Baraha Pada paatam_matched.json',
    ]
    
    for filepath in samhita_files:
        if os.path.exists(filepath):
            improver.process_samhita_file(filepath)
            
    # Process brahmana files
    brahmana_files = [
        'parsed/TB 1.1-1.4 Baraha_parsed.json',
        'parsed/TB 1.5-1.8 Baraha_parsed.json',
        'parsed/TB 2.1-2.4 Baraha_parsed.json',
        'parsed/TB 2.5-2.8 Baraha_parsed.json',
        'parsed/TB 3.1-3.6 Baraha_parsed.json',
        'parsed/TB 3.7-3.12 Baraha_parsed.json',
    ]
    
    for filepath in brahmana_files:
        if os.path.exists(filepath):
            improver.process_brahmana_file(filepath)
            
    # Process aranyaka files
    aranyaka_files = [
        'parsed/TA 1-4 Baraha_parsed.json',
        'parsed/TA 5-6 Baraha_parsed.json',
        'parsed/TA 7-8 Baraha_parsed.json',
    ]
    
    for filepath in aranyaka_files:
        if os.path.exists(filepath):
            improver.process_brahmana_file(filepath)  # Same structure as brahmana
            
    # Process complete corpus
    if os.path.exists('parsed/taittiriya_complete_corpus.json'):
        improver.process_complete_corpus('parsed/taittiriya_complete_corpus.json')
    elif os.path.exists('web_complete/taittiriya_complete_corpus.json'):
        improver.process_complete_corpus('web_complete/taittiriya_complete_corpus.json')
        
    # Generate and save report
    report = improver.generate_report()
    print(report)
    
    with open('data_quality_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
        
    print("\nData quality improvement complete. Check *_cleaned.json files for cleaned data.")


if __name__ == '__main__':
    main()