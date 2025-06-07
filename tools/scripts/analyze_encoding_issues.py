#!/usr/bin/env python3
"""
Analyze encoding issues in round-trip conversions.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple
import difflib

# Add project paths
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append('/Users/skmnktl/Projects/ambuda/vidyut/bindings-python')

import vidyut.lipi as lipi

def analyze_baraha_special_chars(text: str) -> Dict[str, List[Tuple[int, str]]]:
    """Identify special Baraha characters and patterns."""
    special_patterns = {
        'accent_marks': ['q', '#', '$', '&'],
        'nasal_annotations': ['(gm)', '(gg)', '~M', '~j', '~g'],
        'compound_markers': ['^^'],
        'numbers_in_text': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
        'special_punctuation': ['|', '||', '( )', '.', ',']
    }
    
    findings = {}
    for pattern_type, patterns in special_patterns.items():
        findings[pattern_type] = []
        for pattern in patterns:
            idx = 0
            while True:
                idx = text.find(pattern, idx)
                if idx == -1:
                    break
                context_start = max(0, idx - 10)
                context_end = min(len(text), idx + len(pattern) + 10)
                context = text[context_start:context_end]
                findings[pattern_type].append((idx, context))
                idx += 1
    
    return findings

def test_vidyut_lipi_conversion(text: str, source_scheme: str = 'BarahaSouth') -> Dict:
    """Test vidyut-lipi conversion and identify issues."""
    results = {
        'original': text,
        'original_length': len(text),
        'conversions': {}
    }
    
    # Map scheme names to vidyut-lipi enums
    scheme_map = {
        'BarahaSouth': lipi.Scheme.BarahaSouth,
        'Slp1': lipi.Scheme.Slp1,
        'Devanagari': lipi.Scheme.Devanagari,
        'Iast': lipi.Scheme.Iast
    }
    
    source_enum = scheme_map[source_scheme]
    
    # Test conversion to different targets
    for target_name, target_enum in scheme_map.items():
        if target_name == source_scheme:
            continue
            
        try:
            # Forward conversion
            converted = lipi.transliterate(text, source_enum, target_enum)
            
            # Backward conversion
            roundtrip = lipi.transliterate(converted, target_enum, source_enum)
            
            results['conversions'][target_name] = {
                'converted': converted,
                'converted_length': len(converted),
                'roundtrip': roundtrip,
                'roundtrip_length': len(roundtrip),
                'is_lossless': text == roundtrip,
                'length_change': len(converted) - len(text),
                'roundtrip_length_change': len(roundtrip) - len(text)
            }
            
            if text != roundtrip:
                # Find differences
                diff = list(difflib.unified_diff(
                    text.splitlines(keepends=True),
                    roundtrip.splitlines(keepends=True),
                    fromfile='original',
                    tofile='roundtrip',
                    n=3
                ))
                results['conversions'][target_name]['diff'] = ''.join(diff[:20])  # First 20 lines
                
        except Exception as e:
            results['conversions'][target_name] = {
                'error': str(e)
            }
    
    return results

def analyze_conversion_output():
    """Analyze the stage3 conversion output for patterns."""
    output_file = Path('/Users/skmnktl/Projects/udapaana/output/stage3_conversion_results.json')
    
    if not output_file.exists():
        print("Output file not found")
        return
    
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Analyze failure patterns
    failures = []
    for item in data:
        if 'round_trip_result' in item and not item['round_trip_result'].get('is_lossless', True):
            failures.append({
                'file': item.get('source_file', 'unknown'),
                'encoding': item.get('source_encoding', 'unknown'),
                'diff_details': item['round_trip_result'].get('diff_details', ''),
                'original_length': item.get('original_length', 0),
                'converted_length': item.get('slp1_length', 0)
            })
    
    print(f"\nFound {len(failures)} lossy conversions out of {len(data)} total")
    
    # Group by encoding
    by_encoding = {}
    for f in failures:
        enc = f['encoding']
        if enc not in by_encoding:
            by_encoding[enc] = []
        by_encoding[enc].append(f)
    
    print("\nFailures by encoding:")
    for enc, items in by_encoding.items():
        print(f"  {enc}: {len(items)} failures")
        
        # Show sample
        if items:
            sample = items[0]
            print(f"    Sample: {sample['file']}")
            print(f"    Issue: {sample['diff_details']}")
            print()

def main():
    """Main analysis function."""
    print("=== Encoding Issue Analysis ===\n")
    
    # Test with known problematic Baraha text
    test_texts = [
        # Simple text with basic accents
        "aqgniM parameSTI yajamAnaH",
        
        # Text with nasal annotations
        "aqGaSa(gm)#saq | dRu(gm)ha#sva",
        
        # Text with special markers
        "BaqdraM karNE#BiH SRuNuqyAma# dEvAH",
        
        # Text with compound markers
        "s^^symbol represents letters separately",
        
        # Text with numbers
        "tasyaiqShA Bava#ti || 1 (10)"
    ]
    
    print("1. Testing sample Baraha texts:")
    print("-" * 50)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}: {text[:50]}...")
        
        # Analyze special characters
        special_chars = analyze_baraha_special_chars(text)
        print("  Special characters found:")
        for char_type, occurrences in special_chars.items():
            if occurrences:
                print(f"    {char_type}: {len(occurrences)} occurrences")
        
        # Test conversion
        results = test_vidyut_lipi_conversion(text)
        print("  Conversion results:")
        for target, result in results['conversions'].items():
            if 'error' in result:
                print(f"    {target}: ERROR - {result['error']}")
            else:
                print(f"    {target}: {'✓ Lossless' if result['is_lossless'] else '✗ Lossy'}")
                if not result['is_lossless']:
                    print(f"      Length change: {result['length_change']}")
                    print(f"      Roundtrip length change: {result['roundtrip_length_change']}")
    
    print("\n2. Analyzing conversion output file:")
    print("-" * 50)
    analyze_conversion_output()
    
    print("\n3. Recommendations:")
    print("-" * 50)
    print("- Pre-process Baraha text to handle special annotations")
    print("- Create custom mapping for nasal annotations like (gm), (gg)")
    print("- Handle accent markers q, #, $ before conversion")
    print("- Preserve numerical annotations separately")
    print("- Consider using Wx encoding as intermediate format")

if __name__ == "__main__":
    main()