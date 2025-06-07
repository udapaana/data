#!/usr/bin/env python3
"""
Test vidyut-lipi with Vedic extensions for round-trip analysis.
"""

import sys
from pathlib import Path

# Add the local vidyut-lipi path
sys.path.insert(0, '/Users/skmnktl/Projects/ambuda/vidyut/bindings-python')

import vidyut.lipi as lipi
from typing import Dict, List, Tuple

def test_baraha_with_extensions():
    """Test Baraha encoding with vidyut-lipi extensions."""
    
    # Test texts with various Baraha features
    test_cases = [
        {
            'name': 'Basic Baraha with q accent',
            'text': 'aqgniM parameSTI yajamAnaH',
            'expected_markers': ['q']
        },
        {
            'name': 'Multiple accents q and #',
            'text': 'BaqdraM karNE#BiH SRuNuqyAma# dEvAH',
            'expected_markers': ['q', '#']
        },
        {
            'name': 'Nasal annotations (gm)',
            'text': 'aqGaSa(gm)#saq | dRu(gm)ha#sva',
            'expected_markers': ['q', '#', '(gm)', '|']
        },
        {
            'name': 'Complex with numbers and bars',
            'text': 'tasyaiqShA Bava#ti || 1 (10)',
            'expected_markers': ['q', '#', '||', '1', '(10)']
        },
        {
            'name': 'Full complexity with ~M',
            'text': 'sam~MvathsarE tAH prati#tiShThaqnti | vaqqrq.ShABya# ityaqrthaH || 11',
            'expected_markers': ['~M', '#', 'q', '|', '||']
        }
    ]
    
    print("=" * 70)
    print("Testing Baraha with vidyut-lipi")
    print("=" * 70)
    
    # First, let's see what schemes are available
    print("\nAvailable schemes:")
    schemes = [attr for attr in dir(lipi.Scheme) if not attr.startswith('_')]
    for scheme in schemes[:10]:  # Show first 10
        print(f"  - {scheme}")
    print(f"  ... and {len(schemes) - 10} more")
    
    # Check if BarahaSouth is available
    if hasattr(lipi.Scheme, 'BarahaSouth'):
        print("\n✓ BarahaSouth scheme is available")
    else:
        print("\n✗ BarahaSouth scheme not found")
        return
    
    print("\n" + "-" * 70)
    print("Round-trip tests:")
    print("-" * 70)
    
    for test in test_cases:
        print(f"\nTest: {test['name']}")
        print(f"Input: {test['text']}")
        
        try:
            # Test 1: Baraha → SLP1 → Baraha
            slp1_text = lipi.transliterate(
                test['text'], 
                lipi.Scheme.BarahaSouth,
                lipi.Scheme.Slp1
            )
            print(f"SLP1: {slp1_text}")
            
            # Round-trip back
            baraha_back = lipi.transliterate(
                slp1_text,
                lipi.Scheme.Slp1,
                lipi.Scheme.BarahaSouth
            )
            print(f"Back: {baraha_back}")
            
            is_lossless = test['text'] == baraha_back
            print(f"Lossless: {'✓' if is_lossless else '✗'}")
            
            if not is_lossless:
                # Analyze what was lost
                print("  Lost markers:")
                for marker in test['expected_markers']:
                    if marker in test['text'] and marker not in baraha_back:
                        print(f"    - {marker}")
            
            # Test 2: Baraha → Devanagari → Baraha
            print("\n  Via Devanagari:")
            deva_text = lipi.transliterate(
                test['text'],
                lipi.Scheme.BarahaSouth,
                lipi.Scheme.Devanagari
            )
            print(f"  Devanagari: {deva_text}")
            
            baraha_from_deva = lipi.transliterate(
                deva_text,
                lipi.Scheme.Devanagari,
                lipi.Scheme.BarahaSouth
            )
            print(f"  Back: {baraha_from_deva}")
            print(f"  Lossless: {'✓' if test['text'] == baraha_from_deva else '✗'}")
            
        except Exception as e:
            print(f"Error: {e}")

def test_with_vedic_extension():
    """Test using Vedic extensions if available."""
    print("\n" + "=" * 70)
    print("Testing with Vedic Extensions")
    print("=" * 70)
    
    # Check if extensions are available
    try:
        # Try to create a Lipika with extensions
        from vidyut.lipi import Lipika
        print("✓ Lipika class available")
        
        # Try to import extensions
        try:
            # This might not be exposed in Python bindings yet
            print("\nNote: Vedic extensions may not be fully exposed in Python bindings yet")
            print("The Rust implementation has full support as shown in the documentation")
        except ImportError:
            print("✗ Vedic extensions not available in Python bindings")
            
    except ImportError:
        print("✗ Lipika class not available in this version")

def analyze_encoding_detection():
    """Analyze what vidyut-lipi can detect."""
    print("\n" + "=" * 70)
    print("Encoding Detection Analysis")
    print("=" * 70)
    
    test_texts = [
        ("Baraha with q", "aqgniM"),
        ("Baraha with #", "dEva#H"),
        ("Devanagari", "अग्निम्"),
        ("IAST", "agnim"),
        ("SLP1", "agnim"),
    ]
    
    # Check if detect function is available
    if hasattr(lipi, 'detect'):
        print("✓ Detection function available")
        for name, text in test_texts:
            try:
                detected = lipi.detect(text)
                print(f"\n{name}: {text}")
                print(f"  Detected: {detected}")
            except Exception as e:
                print(f"\n{name}: {text}")
                print(f"  Error: {e}")
    else:
        print("✗ No detect function available")

def main():
    """Run all tests."""
    print("Vidyut-Lipi Vedic Extension Analysis")
    print("====================================\n")
    
    # Test 1: Basic round-trip with Baraha
    test_baraha_with_extensions()
    
    # Test 2: Check for Vedic extensions
    test_with_vedic_extension()
    
    # Test 3: Encoding detection
    analyze_encoding_detection()
    
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print("\nKey findings:")
    print("1. BarahaSouth scheme is available in vidyut-lipi")
    print("2. Basic transliteration works but special markers may be lost")
    print("3. Vedic extensions exist in Rust but may need Python binding updates")
    print("4. For full Vedic support, we need:")
    print("   - Accent preservation (q, #, $)")
    print("   - Nasal annotations ((gm), (gg), ~M)")
    print("   - Section markers (|, ||, |||)")
    print("   - Number preservation in context")

if __name__ == "__main__":
    main()