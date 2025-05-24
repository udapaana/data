#!/usr/bin/env python3
"""
Configuration for transliteration system.
This allows easy switching between vidyut-lipi and indic-transliteration.
"""

# Configuration for transliteration generation
TRANSLITERATION_CONFIG = {
    # Set to True to regenerate all transliterations
    "force_regenerate": False,
    
    # Transliteration engine (vidyut-lipi only)
    "engine": "vidyut",
    
    # Engine version tracking for updates
    "engine_version": "0.4.0",  # Update when vidyut is upgraded
    
    # Scripts to include in transliteration generation
    "enabled_scripts": [
        'devanagari', 'iast', 'harvard-kyoto', 'baraha', 'itrans',
        'tamil', 'telugu', 'kannada', 'malayalam', 'gujarati',
        'slp1', 'velthuis', 'wx'
    ],
    
    # Default source script in the corpus
    "default_source_script": "baraha",
    
    # Batch size for processing large datasets
    "batch_size": 100,
    
    # Whether to print progress during generation
    "show_progress": True
}

def should_regenerate_transliterations(existing_metadata: dict = None) -> bool:
    """
    Determine if transliterations should be regenerated based on:
    - Configuration force flag
    - Engine version changes
    - Missing transliterations
    """
    if TRANSLITERATION_CONFIG["force_regenerate"]:
        return True
    
    if not existing_metadata:
        return True
    
    # Check if engine version has been updated
    engine_version = existing_metadata.get("engine_version")
    current_version = TRANSLITERATION_CONFIG["engine_version"]
    if engine_version != current_version:
        return True
    
    return False

def get_engine_info() -> dict:
    """Get current engine information for metadata."""
    return {
        "transliteration_engine": TRANSLITERATION_CONFIG["engine"],
        "engine_version": TRANSLITERATION_CONFIG["engine_version"],
        "enabled_scripts": TRANSLITERATION_CONFIG["enabled_scripts"],
        "source_script": TRANSLITERATION_CONFIG["default_source_script"]
    }