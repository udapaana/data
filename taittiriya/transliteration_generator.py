#!/usr/bin/env python3
"""
Static transliteration generator using vidyut-lipi for Sanskrit texts.
Replaces dynamic indic-transliteration calls with pre-generated static assets.
"""

from typing import Dict, Any, Optional
import json

# Import vidyut-lipi Python bindings (official API)
try:
    from vidyut.lipi import transliterate, Scheme
    VIDYUT_AVAILABLE = True
    print("Using vidyut.lipi (official Python bindings) for transliteration")
except ImportError:
    print("Error: vidyut-lipi Python bindings not available.")
    print("Please install vidyut:")
    print("  pip install vidyut")
    print("\nFor the complete implementation:")
    print("1. Install vidyut Python package for data generation")
    print("2. Web app will use static transliterations (no dynamic JS needed)")
    raise ImportError("vidyut-lipi not available")

class StaticTransliterationGenerator:
    """Generate static transliterations for all supported scripts using vidyut-lipi."""
    
    # Mapping from script names to vidyut-lipi Scheme enums
    SCRIPT_MAPPING = {
        'devanagari': Scheme.Devanagari,
        'iast': Scheme.Iast,
        'harvard-kyoto': Scheme.HarvardKyoto,
        'baraha': Scheme.BarahaSouth,  # Using BarahaSouth for compatibility
        'itrans': Scheme.Itrans,
        'tamil': Scheme.Tamil,
        'telugu': Scheme.Telugu,
        'kannada': Scheme.Kannada,
        'malayalam': Scheme.Malayalam,
        'gujarati': Scheme.Gujarati,
        'slp1': Scheme.Slp1,
        'velthuis': Scheme.Velthuis,
        'wx': Scheme.Wx
    }
    
    SUPPORTED_SCRIPTS = [
        {'name': 'devanagari', 'label': 'देवनागरी', 'script': 'devanagari'},
        {'name': 'iast', 'label': 'IAST', 'script': 'iast'},
        {'name': 'harvard-kyoto', 'label': 'Harvard-Kyoto', 'script': 'harvard-kyoto'},
        {'name': 'baraha', 'label': 'Baraha', 'script': 'baraha'},
        {'name': 'itrans', 'label': 'ITRANS', 'script': 'itrans'},
        {'name': 'tamil', 'label': 'தமிழ்', 'script': 'tamil'},
        {'name': 'telugu', 'label': 'తెలుగు', 'script': 'telugu'},
        {'name': 'kannada', 'label': 'ಕನ್ನಡ', 'script': 'kannada'},
        {'name': 'malayalam', 'label': 'മലയാളം', 'script': 'malayalam'},
        {'name': 'gujarati', 'label': 'ગુજરાતી', 'script': 'gujarati'},
        {'name': 'slp1', 'label': 'SLP1', 'script': 'slp1'},
        {'name': 'velthuis', 'label': 'Velthuis', 'script': 'velthuis'},
        {'name': 'wx', 'label': 'WX', 'script': 'wx'}
    ]
    
    def __init__(self):
        """Initialize the transliteration generator with vidyut-lipi."""
        # No initialization needed for the functional API
        pass
        
    def transliterate_text(self, text: str, from_script: str = 'baraha', to_script: str = 'devanagari') -> str:
        """Transliterate text from one script to another using vidyut-lipi."""
        if not text or not text.strip():
            return text
            
        # Get source and target schemes
        from_scheme = self.SCRIPT_MAPPING.get(from_script)
        to_scheme = self.SCRIPT_MAPPING.get(to_script)
        
        if not from_scheme or not to_scheme:
            print(f"Warning: Script '{from_script}' or '{to_script}' not supported")
            return text
            
        try:
            # Use official vidyut.lipi API for transliteration
            result = transliterate(text, from_scheme, to_scheme)
            return result
        except Exception as e:
            print(f"Warning: Transliteration failed for '{text[:50]}...': {e}")
            return text
    
    def generate_all_transliterations(self, text: str, from_script: str = 'baraha') -> Dict[str, str]:
        """Generate transliterations for all supported scripts."""
        transliterations = {}
        
        for script_info in self.SUPPORTED_SCRIPTS:
            script_name = script_info['script']
            try:
                transliterations[script_name] = self.transliterate_text(text, from_script, script_name)
            except Exception as e:
                print(f"Failed to transliterate to {script_name}: {e}")
                transliterations[script_name] = text
                
        return transliterations
    
    def add_transliterations_to_verse(self, verse_data: Dict[str, Any], from_script: str = 'baraha') -> Dict[str, Any]:
        """Add transliterations to a verse data structure."""
        enhanced_verse = verse_data.copy()
        
        # Add transliterations for padam if present
        if 'padam' in verse_data and verse_data['padam']:
            enhanced_verse['padam_transliterations'] = self.generate_all_transliterations(
                verse_data['padam'], from_script
            )
        
        # Add transliterations for samhita if present  
        if 'samhita' in verse_data and verse_data['samhita']:
            enhanced_verse['samhita_transliterations'] = self.generate_all_transliterations(
                verse_data['samhita'], from_script
            )
            
        return enhanced_verse
    
    def add_transliterations_to_section(self, section_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add transliterations to a brahmana or aranyaka section."""
        if not isinstance(section_data, dict):
            return section_data
            
        enhanced_section = section_data.copy()
        
        # Add transliterations for text field
        if 'text' in section_data and section_data['text']:
            try:
                enhanced_section['text_transliterations'] = self.generate_transliterations(section_data['text'])
            except Exception as e:
                print(f"Warning: Failed to transliterate section text: {e}")
        
        return enhanced_section
    
    def add_transliterations_to_section(self, section_data: Dict[str, Any], from_script: str = 'baraha') -> Dict[str, Any]:
        """Add transliterations to a section data structure (for brahmana/aranyaka)."""
        enhanced_section = section_data.copy()
        
        # Add transliterations for text content if present
        if 'text' in section_data and section_data['text']:
            enhanced_section['text_transliterations'] = self.generate_all_transliterations(
                section_data['text'], from_script
            )
            
        return enhanced_section
    
    def process_corpus_with_transliterations(self, corpus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process entire corpus to add transliterations to all text elements."""
        enhanced_corpus = corpus_data.copy()
        
        print("Adding transliterations to corpus...")
        
        # Process samhita data
        if 'samhita' in corpus_data:
            print("Processing samhita verses...")
            enhanced_corpus['samhita'] = {}
            for chapter_id, chapter_data in corpus_data['samhita'].items():
                enhanced_corpus['samhita'][chapter_id] = {}
                for verse_id, verse_data in chapter_data.items():
                    enhanced_corpus['samhita'][chapter_id][verse_id] = self.add_transliterations_to_verse(verse_data)
                print(f"  Completed chapter {chapter_id}")
        
        # Process brahmana data
        if 'brahmana' in corpus_data:
            print("Processing brahmana sections...")
            enhanced_corpus['brahmana'] = {}
            for book_id, book_data in corpus_data['brahmana'].items():
                enhanced_corpus['brahmana'][book_id] = {}
                for section_id, section_data in book_data.items():
                    enhanced_corpus['brahmana'][book_id][section_id] = self.add_transliterations_to_section(section_data)
                print(f"  Completed book {book_id}")
        
        # Process aranyaka data
        if 'aranyaka' in corpus_data:
            print("Processing aranyaka sections...")
            enhanced_corpus['aranyaka'] = {}
            for book_id, book_data in corpus_data['aranyaka'].items():
                enhanced_corpus['aranyaka'][book_id] = {}
                for section_id, section_data in book_data.items():
                    enhanced_corpus['aranyaka'][book_id][section_id] = self.add_transliterations_to_section(section_data)
                print(f"  Completed book {book_id}")
                
        print("Transliteration processing complete!")
        return enhanced_corpus

# Create global instance for use in other scripts
transliteration_generator = StaticTransliterationGenerator()