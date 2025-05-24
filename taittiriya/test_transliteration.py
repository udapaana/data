#!/usr/bin/env python3
"""
Test script to verify vidyut-lipi transliteration functionality.
"""

from transliteration_generator import transliteration_generator

def test_basic_transliteration():
    """Test basic transliteration functionality."""
    
    # Test text in Baraha format
    test_text = "namaste"
    
    print(f"Original text (Baraha): {test_text}")
    print("\nTransliterations:")
    
    # Test transliteration to all supported scripts
    transliterations = transliteration_generator.generate_all_transliterations(test_text)
    
    for script, transliterated in transliterations.items():
        print(f"  {script}: {transliterated}")

def test_sanskrit_text():
    """Test with actual Sanskrit text."""
    
    # Sample Sanskrit text from Taittiriya Samhita
    sanskrit_text = "oM SAntiH SAntiH SAntiH"
    
    print(f"\nSanskrit text (Baraha): {sanskrit_text}")
    print("\nTransliterations:")
    
    transliterations = transliteration_generator.generate_all_transliterations(sanskrit_text)
    
    for script, transliterated in transliterations.items():
        print(f"  {script}: {transliterated}")

if __name__ == "__main__":
    print("Testing vidyut-lipi transliteration...")
    
    try:
        test_basic_transliteration()
        test_sanskrit_text()
        print("\n✓ Transliteration test completed successfully!")
    except Exception as e:
        print(f"\n✗ Transliteration test failed: {e}")
        import traceback
        traceback.print_exc()