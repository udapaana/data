#!/usr/bin/env python3
"""
Test improved encoding conversion with preservation of Vedic features.
"""

import sys
import json
from pathlib import Path

# Add project paths
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append('/Users/skmnktl/Projects/ambuda/vidyut/bindings-python')

from pipeline.utils.vedic_encoding_handler import VedicEncodingHandler
from pipeline.stages.stage_03_encoding_conversion import EncodingConverter
import logging

logging.basicConfig(level=logging.INFO)

def test_baraha_preservation():
    """Test preservation of Baraha special features."""
    handler = VedicEncodingHandler()
    
    test_cases = [
        {
            'name': 'Basic accents',
            'text': 'aqgniM parameSTI yajamAnaH',
            'expected_features': ['anudatta']
        },
        {
            'name': 'Multiple accent types',
            'text': 'BaqdraM karNE#BiH SRuNuqyAma# dEvAH',
            'expected_features': ['anudatta', 'svarita']
        },
        {
            'name': 'Nasal annotations',
            'text': 'aqGaSa(gm)#saq | dRu(gm)ha#sva',
            'expected_features': ['nasal_annotations', 'section_markers']
        },
        {
            'name': 'Complex with numbers',
            'text': 'tasyaiqShA Bava#ti || 1 (10)',
            'expected_features': ['numbers', 'section_markers']
        },
        {
            'name': 'Full complexity',
            'text': 'aqgnirvAqyuScaq sUrya#Sca | saqha sa#~jca-skaqrarddhi#yA || 2 (10)',
            'expected_features': ['anudatta', 'svarita', 'nasal', 'numbers', 'sections']
        }
    ]
    
    print("=" * 70)
    print("Testing Baraha Text Preservation")
    print("=" * 70)
    
    all_passed = True
    
    for test in test_cases:
        print(f"\nTest: {test['name']}")
        print(f"Input: {test['text']}")
        
        # Detect features
        features = handler.detect_encoding(test['text'])
        print(f"Detected: {features}")
        
        # Preprocess
        processed, preserved = handler.preprocess_baraha(test['text'])
        print(f"Processed: {repr(processed[:50])}...")
        print(f"Preserved items: {len(preserved['accents'])} accents, "
              f"{len(preserved['nasals'])} nasals, {len(preserved['numbers'])} numbers")
        
        # Restore
        restored = handler.postprocess_slp1(processed, preserved)
        
        # Check lossless
        is_lossless = test['text'] == restored
        print(f"Lossless: {'✓' if is_lossless else '✗'}")
        
        if not is_lossless:
            print(f"  Original : {test['text']}")
            print(f"  Restored : {restored}")
            all_passed = False
        else:
            print("  Perfect restoration!")
    
    return all_passed

def test_full_pipeline():
    """Test the full encoding conversion pipeline."""
    converter = EncodingConverter()
    
    test_data = [
        {
            'source_file': 'test_baraha_accents.txt',
            'encoding': 'baraha',
            'normalized_text': 'BaqdraM karNE#BiH SRuNuqyAma# dEvAH | aqGaSa(gm)#saq',
            'metadata': {
                'veda': 'yajurveda',
                'sakha': 'taittiriya',
                'text_type': 'samhita'
            }
        },
        {
            'source_file': 'test_devanagari.txt',
            'encoding': 'devanagari',
            'normalized_text': 'अग्निमीळे पुरोहितं यज्ञस्य देवम्',
            'metadata': {
                'veda': 'rigveda',
                'sakha': 'shakala',
                'text_type': 'samhita'
            }
        }
    ]
    
    print("\n" + "=" * 70)
    print("Testing Full Pipeline Conversion")
    print("=" * 70)
    
    results = converter.batch_convert(test_data)
    
    for result in results:
        print(f"\nFile: {result['source_file']}")
        print(f"Encoding: {result['source_encoding']}")
        print(f"Original: {result.get('original_text', 'N/A')[:50]}...")
        print(f"SLP1: {result.get('slp1_text', 'N/A')[:50]}...")
        
        round_trip = result.get('round_trip_result', {})
        print(f"Round-trip: {'✓ Lossless' if round_trip.get('is_lossless') else '✗ Lossy'}")
        
        if round_trip.get('was_preprocessed'):
            print("  Used preprocessing for Baraha special features")
        
        validation = result.get('validation_result', {})
        if validation.get('warnings'):
            print(f"Warnings: {validation['warnings']}")

def test_sakha_extensions():
    """Test sakha-specific encoding extensions."""
    handler = VedicEncodingHandler()
    
    test_cases = [
        {
            'text': 'agnim īḷe purohitaṃ',
            'sakha': 'shakala',
            'text_type': 'samhita'
        },
        {
            'text': 'iṣe tvā ūrje tvā',
            'sakha': 'taittiriya',
            'text_type': 'brahmana'
        },
        {
            'text': 'agna ā yāhi vītaye',
            'sakha': 'kauthuma',
            'text_type': 'samhita'
        }
    ]
    
    print("\n" + "=" * 70)
    print("Testing Sakha-Specific Extensions")
    print("=" * 70)
    
    for test in test_cases:
        extended = handler.create_sakha_extension(
            test['text'], 
            test['sakha'], 
            test['text_type']
        )
        print(f"\nŚākhā: {test['sakha']} - {test['text_type']}")
        print(f"Original: {test['text']}")
        print(f"Extended: {extended[:60]}...")

def main():
    """Run all tests."""
    print("Vedic Encoding Improvement Tests")
    print("================================\n")
    
    # Test 1: Baraha preservation
    baraha_passed = test_baraha_preservation()
    
    # Test 2: Full pipeline
    test_full_pipeline()
    
    # Test 3: Sakha extensions
    test_sakha_extensions()
    
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Baraha preservation: {'✓ All tests passed' if baraha_passed else '✗ Some tests failed'}")
    print("\nRecommendations:")
    print("1. Use preprocessing for all Baraha texts with special markers")
    print("2. Maintain separate preserved data for round-trip validation")
    print("3. Consider using Wx encoding as intermediate format (as noted in CLAUDE.md)")
    print("4. Implement sakha-specific validation rules")

if __name__ == "__main__":
    main()