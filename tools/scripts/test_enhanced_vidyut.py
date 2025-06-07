#!/usr/bin/env python3
"""
Test the enhanced vidyut-lipi with our improvements.
"""

import sys
from pathlib import Path

# Add the local vidyut-lipi path
sys.path.insert(0, '/Users/skmnktl/Projects/ambuda/vidyut/bindings-python')

import vidyut.lipi as lipi

def test_enhanced_detection():
    """Test our enhanced detection logic."""
    print("Enhanced Detection Tests")
    print("=" * 50)
    
    test_cases = [
        # Baraha Vedic markers
        ("aqgniM", "BarahaSouth"),
        ("dEva#H", "BarahaSouth"),
        ("pra$NaH", "BarahaSouth"),
        ("priya&jaH", "BarahaSouth"),
        
        # Baraha nasal annotations
        ("ka(gm)H", "BarahaSouth"),
        ("sa(gg)ma", "BarahaSouth"),
        ("sam~MvathsarE", "BarahaSouth"),
        ("sa~jjana", "BarahaSouth"),
        ("word^^compound", "BarahaSouth"),
        
        # Complex Baraha
        ("aqGaSa(gm)#saq", "BarahaSouth"),
        ("BaqdraM karNE#BiH", "BarahaSouth"),
        
        # Non-Baraha (should detect correctly)
        ("agnim", "HarvardKyoto"),
        ("kfta", "Slp1"),
        ("अग्निम्", "Devanagari"),
    ]
    
    for text, expected in test_cases:
        detected = lipi.detect(text)
        status = "✓" if detected == expected else "✗"
        print(f"{status} '{text}' → {detected} (expected {expected})")

def test_enhanced_roundtrip():
    """Test round-trip conversion with our enhancements."""
    print("\nEnhanced Round-Trip Tests")
    print("=" * 50)
    
    baraha_texts = [
        "aqgniM",
        "dEva#H", 
        "pra$NaH",
        "ka(gm)H",
        "sam~MvathsarE",
        "BaqdraM karNE#BiH",
        "aqGaSa(gm)#saq | dRu(gm)ha#sva",
    ]
    
    for text in baraha_texts:
        print(f"\nTesting: {text}")
        
        try:
            # Test Baraha → Devanagari → Baraha
            deva = lipi.transliterate(text, lipi.Scheme.BarahaSouth, lipi.Scheme.Devanagari)
            back = lipi.transliterate(deva, lipi.Scheme.Devanagari, lipi.Scheme.BarahaSouth)
            
            print(f"  Devanagari: {deva}")
            print(f"  Back: {back}")
            print(f"  Lossless: {'✓' if text == back else '✗'}")
            
            if text != back:
                print(f"    Original: '{text}'")
                print(f"    Result:   '{back}'")
                
                # Analyze differences
                if len(text) != len(back):
                    print(f"    Length: {len(text)} → {len(back)}")
                
                for i, (a, b) in enumerate(zip(text, back)):
                    if a != b:
                        print(f"    Pos {i}: '{a}' → '{b}'")
                        break
            
            # Test Baraha → SLP1 → Baraha
            slp1 = lipi.transliterate(text, lipi.Scheme.BarahaSouth, lipi.Scheme.Slp1)
            back_slp1 = lipi.transliterate(slp1, lipi.Scheme.Slp1, lipi.Scheme.BarahaSouth)
            
            print(f"  SLP1: {slp1}")
            print(f"  SLP1 lossless: {'✓' if text == back_slp1 else '✗'}")
            
        except Exception as e:
            print(f"  Error: {e}")

def test_case_preservation():
    """Test if case is preserved correctly."""
    print("\nCase Preservation Tests")
    print("=" * 50)
    
    case_tests = [
        "BaqdraM",      # Should preserve capital B
        "karNE#BiH",    # Mixed case
        "dEvAH",        # Mixed case with accent
        "saMskRutam",   # Standard mixed case
    ]
    
    for text in case_tests:
        deva = lipi.transliterate(text, lipi.Scheme.BarahaSouth, lipi.Scheme.Devanagari)
        back = lipi.transliterate(deva, lipi.Scheme.Devanagari, lipi.Scheme.BarahaSouth)
        
        print(f"'{text}' → '{deva}' → '{back}'")
        
        # Check if capital letters are preserved
        original_caps = [i for i, c in enumerate(text) if c.isupper()]
        result_caps = [i for i, c in enumerate(back) if c.isupper()]
        
        if original_caps == result_caps:
            print(f"  Case preserved: ✓")
        else:
            print(f"  Case preserved: ✗ (original caps at {original_caps}, result caps at {result_caps})")

def main():
    """Run all enhanced tests."""
    print("Testing Enhanced vidyut-lipi")
    print("===========================\n")
    
    test_enhanced_detection()
    test_enhanced_roundtrip()
    test_case_preservation()
    
    print("\n" + "=" * 50)
    print("Summary")
    print("=" * 50)
    print("If detection tests show ✓ for Baraha patterns, our detection enhancement worked!")
    print("If round-trip tests show ✓, our mapping enhancements worked!")
    print("Any remaining ✗ items indicate areas that still need work.")

if __name__ == "__main__":
    main()