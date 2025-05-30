#!/usr/bin/env python3
"""
Demo script showing the complete transliteration workflow with vidyut-lipi.
"""

from transliteration_generator import transliteration_generator
import json

def demo_single_text():
    """Demo transliterating a single Sanskrit text."""
    print("=== Single Text Transliteration Demo ===")
    
    # Sample Sanskrit verse from Taittiriya Samhita
    sanskrit_text = "oM asato mA sadgamaya tamaso mA jyotirgamaya"
    
    print(f"Original text (BarahaSouth): {sanskrit_text}")
    print("\nTransliterations using vidyut-lipi:")
    
    # Generate all transliterations
    transliterations = transliteration_generator.generate_all_transliterations(sanskrit_text)
    
    for script, transliterated in transliterations.items():
        print(f"  {script:15}: {transliterated}")

def demo_verse_structure():
    """Demo adding transliterations to a verse structure."""
    print("\n=== Verse Structure Demo ===")
    
    # Sample verse data structure
    verse_data = {
        "verse_id": "1.1.1",
        "chapter": "1.1",
        "padam": "oM asato mA sadgamaya",
        "samhita": "oM asato mA sadgamaya",
        "has_samhita_match": True
    }
    
    print("Original verse data:")
    print(json.dumps(verse_data, indent=2, ensure_ascii=False))
    
    # Add transliterations
    enhanced_verse = transliteration_generator.add_transliterations_to_verse(verse_data)
    
    print("\nEnhanced with transliterations:")
    print(json.dumps({k: v for k, v in enhanced_verse.items() if k in ['verse_id', 'padam_transliterations']}, 
                     indent=2, ensure_ascii=False))

def demo_quality_comparison():
    """Demo showing vidyut-lipi quality for different types of Sanskrit text."""
    print("\n=== Quality Demonstration ===")
    
    test_cases = [
        ("Simple mantra", "oM namaH zivAya"),
        ("Complex compound", "brahmaNyAdevAnAM prathamasya"),
        ("Vedic accent", "agnimeeLe purohitaM"),
        ("Long compound", "sarvadevaganasahAyaM")
    ]
    
    for description, text in test_cases:
        print(f"\n{description}: {text}")
        
        # Show key transliterations
        for script in ['devanagari', 'iast', 'tamil']:
            result = transliteration_generator.transliterate_text(text, 'baraha', script)
            script_label = transliteration_generator.SUPPORTED_SCRIPTS[
                next(i for i, s in enumerate(transliteration_generator.SUPPORTED_SCRIPTS) if s['script'] == script)
            ]['label']
            print(f"  {script_label}: {result}")

if __name__ == "__main__":
    print("🚀 vidyut-lipi Static Transliteration Demo")
    print("=" * 50)
    
    try:
        demo_single_text()
        demo_verse_structure()
        demo_quality_comparison()
        
        print("\n" + "=" * 50)
        print("✨ Demo completed successfully!")
        print("🎯 vidyut-lipi provides high-quality transliterations")
        print("⚡ Static generation ensures consistent performance")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()