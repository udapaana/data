#!/usr/bin/env python3
"""
Validate Downloaded Vedanidhi Data
Check for content diversity and prevent duplicate data issues
"""

import json
from pathlib import Path
from collections import defaultdict
import hashlib

def validate_data_diversity():
    """Check if we're getting diverse content or repeated data"""
    
    download_dir = Path("data/vedanidhi_complete")
    
    print("Validating downloaded Vedanidhi data for content diversity...")
    print("=" * 70)
    
    # Track content hashes and patterns
    content_hashes = set()
    text_samples = defaultdict(list)
    veda_patterns = defaultdict(set)
    
    json_files = list(download_dir.rglob("*.json"))
    if not json_files:
        print("No JSON files found!")
        return
    
    # Filter out progress files
    data_files = [f for f in json_files if 'progress' not in f.name and 'summary' not in f.name]
    
    print(f"Found {len(data_files)} data files to validate")
    print()
    
    for file_path in data_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            metadata = data.get('metadata', {})
            texts = data.get('texts', [])
            
            if not texts:
                continue
            
            veda = metadata.get('veda', 'unknown')
            shakha = metadata.get('shakha', 'unknown')
            text_type = metadata.get('text_type', 'unknown')
            source_id = metadata.get('source_id', 'unknown')
            
            print(f"📁 {file_path.name}")
            print(f"   Veda: {veda}")
            print(f"   Śākhā: {shakha}")
            print(f"   Type: {text_type}")
            print(f"   Source ID: {source_id}")
            print(f"   Texts: {len(texts)}")
            
            # Sample first few texts for content analysis
            sample_texts = texts[:5]
            location_patterns = []
            content_samples = []
            
            for text in sample_texts:
                location = text.get('location', [])
                content = text.get('vaakya_text', '')
                
                if isinstance(location, list) and location:
                    location_patterns.append(location[0] if location[0] else 'empty')
                else:
                    location_patterns.append(str(location)[:20] if location else 'empty')
                
                content_samples.append(content[:50] + '...' if len(content) > 50 else content)
                
                # Create hash of content to detect duplicates
                content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
                content_hashes.add(content_hash)
            
            print(f"   Location patterns: {location_patterns}")
            print(f"   Content samples:")
            for i, sample in enumerate(content_samples):
                print(f"     {i+1}: {sample}")
            
            # Check for Veda-specific markers
            all_content = ' '.join(text.get('vaakya_text', '') for text in sample_texts)
            
            # Detect Veda markers
            veda_markers = {
                'rigveda': ['ऋ', 'मण्डल', 'सूक्त'],
                'yajurveda': ['यजु', 'काण्ड', 'प्रपाठक'],
                'samaveda': ['साम', 'गान', 'आर्चिक'],
                'atharvaveda': ['अथर्व', 'काण्ड']
            }
            
            detected_markers = []
            for veda_name, markers in veda_markers.items():
                for marker in markers:
                    if marker in all_content:
                        detected_markers.append(f"{veda_name}:{marker}")
            
            if detected_markers:
                print(f"   Detected markers: {detected_markers}")
            
            # Store patterns for cross-comparison
            veda_patterns[veda].update(location_patterns)
            
            # Check for suspicious patterns
            suspicious = False
            if veda.lower() != 'rigveda' and any('ऋ' in pattern for pattern in location_patterns):
                print(f"   ⚠️  WARNING: Non-Rigveda file contains Rigveda markers!")
                suspicious = True
            
            if veda.lower() == 'samaveda' and not any('गान' in content or 'साम' in content or 'आर्चिक' in content for content in content_samples):
                print(f"   ⚠️  WARNING: Sāmaveda file lacks expected Sāmaveda content!")
                suspicious = True
            
            if not suspicious:
                print(f"   ✅ Content looks appropriate for {veda}")
            
            print()
            
        except Exception as e:
            print(f"   ❌ Error reading {file_path}: {e}")
            print()
    
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    print(f"Total unique content hashes: {len(content_hashes)}")
    print(f"Files analyzed: {len(data_files)}")
    
    print("\nVeda-specific patterns found:")
    for veda, patterns in veda_patterns.items():
        print(f"  {veda}: {len(patterns)} unique patterns")
        print(f"    Sample patterns: {list(patterns)[:3]}")
    
    # Check for cross-contamination
    print("\nCross-contamination check:")
    rigveda_patterns = veda_patterns.get('rigveda', set())
    other_vedas = {k: v for k, v in veda_patterns.items() if k != 'rigveda'}
    
    contamination_found = False
    for veda, patterns in other_vedas.items():
        overlap = rigveda_patterns.intersection(patterns)
        if overlap:
            print(f"  ⚠️  {veda} shares patterns with Rigveda: {list(overlap)[:3]}")
            contamination_found = True
        else:
            print(f"  ✅ {veda} has distinct patterns from Rigveda")
    
    if not contamination_found:
        print("  ✅ No cross-contamination detected!")
    
    print(f"\nValidation complete. Content diversity: {'GOOD' if len(content_hashes) > len(data_files) * 0.8 else 'POOR'}")

if __name__ == "__main__":
    validate_data_diversity()