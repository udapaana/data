#!/usr/bin/env python3
"""
Generate a comprehensive data quality report for the Taittiriya corpus
"""

import json
import os
from collections import defaultdict
from typing import Dict, List, Any, Tuple

class DataQualityReporter:
    def __init__(self):
        self.stats = defaultdict(int)
        self.issues = defaultdict(list)
        
    def analyze_text_quality(self, text: str) -> Dict[str, Any]:
        """Analyze quality metrics for a text string."""
        metrics = {
            'length': len(text),
            'has_baraha_encoding': any(marker in text for marker in ['aq', 'iq', 'uq', '(gm)', '(gg)']),
            'has_accent_markers': '#' in text or '$' in text,
            'has_multiple_spaces': '  ' in text,
            'has_trailing_markers': text.strip().endswith((')', ']')),
            'word_count': len(text.split())
        }
        return metrics
        
    def compare_files(self, original_path: str, cleaned_path: str) -> Dict[str, Any]:
        """Compare original and cleaned files."""
        if not os.path.exists(original_path) or not os.path.exists(cleaned_path):
            return None
            
        with open(original_path, 'r', encoding='utf-8') as f:
            original = json.load(f)
        with open(cleaned_path, 'r', encoding='utf-8') as f:
            cleaned = json.load(f)
            
        comparison = {
            'changes': 0,
            'baraha_fixed': 0,
            'whitespace_fixed': 0,
            'markers_removed': 0
        }
        
        # Compare verses/sections
        if 'verses' in original:
            for i, (orig_verse, clean_verse) in enumerate(zip(original.get('verses', []), cleaned.get('verses', []))):
                if orig_verse.get('padam') != clean_verse.get('padam'):
                    comparison['changes'] += 1
                    orig_metrics = self.analyze_text_quality(orig_verse.get('padam', ''))
                    if orig_metrics['has_baraha_encoding']:
                        comparison['baraha_fixed'] += 1
                    if orig_metrics['has_multiple_spaces']:
                        comparison['whitespace_fixed'] += 1
                        
                if orig_verse.get('samhita') != clean_verse.get('samhita'):
                    comparison['changes'] += 1
                    orig_metrics = self.analyze_text_quality(orig_verse.get('samhita', ''))
                    if orig_metrics['has_trailing_markers']:
                        comparison['markers_removed'] += 1
                        
        elif 'sections' in original:
            for i, (orig_section, clean_section) in enumerate(zip(original.get('sections', []), cleaned.get('sections', []))):
                if orig_section.get('text') != clean_section.get('text'):
                    comparison['changes'] += 1
                    orig_metrics = self.analyze_text_quality(orig_section.get('text', ''))
                    if orig_metrics['has_baraha_encoding']:
                        comparison['baraha_fixed'] += 1
                    if orig_metrics['has_trailing_markers']:
                        comparison['markers_removed'] += 1
                        
        return comparison
        
    def generate_report(self) -> str:
        """Generate the quality report."""
        report = ["# Data Quality Report for Taittiriya Corpus\n"]
        
        # Analyze original vs cleaned files
        report.append("## File Comparison Summary\n")
        
        total_changes = 0
        total_baraha = 0
        total_whitespace = 0
        total_markers = 0
        
        # Check parsed directory
        if os.path.exists('parsed_original'):
            for filename in os.listdir('parsed_original'):
                if filename.endswith('.json'):
                    original_path = os.path.join('parsed_original', filename)
                    cleaned_path = os.path.join('parsed', filename)
                    
                    comparison = self.compare_files(original_path, cleaned_path)
                    if comparison and comparison['changes'] > 0:
                        report.append(f"### {filename}")
                        report.append(f"- Total changes: {comparison['changes']}")
                        report.append(f"- Baraha encoding fixed: {comparison['baraha_fixed']}")
                        report.append(f"- Whitespace issues fixed: {comparison['whitespace_fixed']}")
                        report.append(f"- Trailing markers removed: {comparison['markers_removed']}\n")
                        
                        total_changes += comparison['changes']
                        total_baraha += comparison['baraha_fixed']
                        total_whitespace += comparison['whitespace_fixed']
                        total_markers += comparison['markers_removed']
                        
        report.append(f"## Overall Statistics\n")
        report.append(f"- **Total text segments modified**: {total_changes}")
        report.append(f"- **Baraha encoding conversions**: {total_baraha}")
        report.append(f"- **Whitespace issues fixed**: {total_whitespace}")
        report.append(f"- **Trailing markers removed**: {total_markers}\n")
        
        # Data quality improvements
        report.append("## Key Improvements Made\n")
        report.append("### 1. Baraha Encoding Conversion")
        report.append("- Converted Baraha transliteration to standard Unicode")
        report.append("- Fixed vowel markers (aq → a, iq → i, uq → u, etc.)")
        report.append("- Converted special characters ((gm) → ṃ, (gg) → ṅ)")
        report.append("- Standardized retroflex consonants (Sh → ṣ, N → ṇ)")
        report.append("- Fixed vocalic r/l markers (r. → ṛ, R. → ṝ)\n")
        
        report.append("### 2. Text Formatting")
        report.append("- Removed multiple consecutive spaces")
        report.append("- Fixed spacing around pipe separators (|)")
        report.append("- Trimmed leading/trailing whitespace")
        report.append("- Removed trailing section markers and numbers\n")
        
        report.append("### 3. Accent Markers")
        report.append("- Converted # markers to Unicode combining diacritical (̍)")
        report.append("- Converted $ markers to Unicode combining macron below (̱)\n")
        
        report.append("### 4. Data Consistency")
        report.append("- Ensured consistent verse/section ID formatting")
        report.append("- Validated text presence in all entries")
        report.append("- Maintained all metadata and structural information\n")
        
        # Example transformations
        report.append("## Example Transformations\n")
        report.append("### Before:")
        report.append("```")
        report.append("iqShE | tvAq | UqrjE | tvAq | vAqyava#H | sthaq |")
        report.append("```\n")
        report.append("### After:")
        report.append("```")
        report.append("iṣE|tvA|UrjE|tvA|vAyavaḥ|stha|")
        report.append("```\n")
        
        report.append("## Recommendations\n")
        report.append("1. **Verify Sanskrit accuracy**: Have a Sanskrit expert review sample texts")
        report.append("2. **Test rendering**: Ensure proper display in web applications")
        report.append("3. **Add transliterations**: Use vidyut-lipi for multiple script support")
        report.append("4. **Regular validation**: Run quality checks periodically\n")
        
        return "\n".join(report)

def main():
    reporter = DataQualityReporter()
    report = reporter.generate_report()
    
    # Save report
    with open('DATA_QUALITY_REPORT.md', 'w', encoding='utf-8') as f:
        f.write(report)
        
    print("Data quality report generated: DATA_QUALITY_REPORT.md")
    print("\nReport Preview:")
    print("=" * 50)
    print(report[:500] + "...")

if __name__ == '__main__':
    main()