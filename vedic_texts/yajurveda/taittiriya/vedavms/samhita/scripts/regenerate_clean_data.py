#!/usr/bin/env python3
"""
Regenerate all data formats using cleaned data
"""

import os
import shutil
import subprocess
import sys

def backup_original_data():
    """Backup original parsed data before replacing with cleaned versions."""
    print("Creating backup of original data...")
    
    if not os.path.exists('parsed_original'):
        os.makedirs('parsed_original')
        
    # Backup all original JSON files
    for filename in os.listdir('parsed'):
        if filename.endswith('.json') and not filename.endswith('_clean.json'):
            src = os.path.join('parsed', filename)
            dst = os.path.join('parsed_original', filename)
            shutil.copy2(src, dst)
            print(f"  Backed up: {filename}")

def replace_with_clean_data():
    """Replace original files with cleaned versions."""
    print("\nReplacing original files with cleaned versions...")
    
    for filename in os.listdir('parsed'):
        if filename.endswith('_clean.json'):
            clean_file = os.path.join('parsed', filename)
            original_file = clean_file.replace('_clean.json', '.json')
            
            # Replace original with clean version
            shutil.copy2(clean_file, original_file)
            print(f"  Replaced: {os.path.basename(original_file)}")
            
            # Remove the _clean.json file to avoid confusion
            os.remove(clean_file)

def run_parsing_scripts():
    """Run the parsing scripts to regenerate all formats."""
    print("\n=== Regenerating Enhanced Samhita Data ===")
    subprocess.run([sys.executable, 'enhanced_parser.py'], check=True)
    
    print("\n=== Regenerating Brahmana/Aranyaka Data ===")
    subprocess.run([sys.executable, 'brahmana_aranyaka_parser.py'], check=True)
    
    print("\n=== Creating Complete Dataset ===")
    subprocess.run([sys.executable, 'create_complete_dataset.py'], check=True)
    
    print("\n=== Creating Enhanced Web Format ===")
    subprocess.run([sys.executable, 'create_enhanced_web_format.py'], check=True)
    
    print("\n=== Creating Brahmana/Aranyaka Web Format ===")
    subprocess.run([sys.executable, 'create_brahmana_aranyaka_web_format.py'], check=True)

def verify_results():
    """Verify that all expected files were created."""
    print("\n=== Verifying Results ===")
    
    expected_files = {
        'parsed': [
            'samhita_complete.json',
            'taittiriya_complete_enhanced.json',
            'taittiriya_brahmana_aranyaka_complete.json',
            'taittiriya_complete_corpus.json'
        ],
        'web_enhanced': [
            'taittiriya_enhanced_minified.json',
            'statistics_enhanced.json',
            'search_data_enhanced.json'
        ],
        'web_brahmana_aranyaka': [
            'brahmana_aranyaka_minified.json',
            'statistics.json',
            'search_data.json'
        ],
        'web_complete': [
            'taittiriya_complete_corpus.json',
            'taittiriya_corpus_minified.json',
            'corpus_statistics.json'
        ]
    }
    
    all_good = True
    for directory, files in expected_files.items():
        for file in files:
            filepath = os.path.join(directory, file)
            if os.path.exists(filepath):
                print(f"  ✓ {filepath}")
            else:
                print(f"  ✗ {filepath} - MISSING!")
                all_good = False
                
    return all_good

def main():
    """Main function to coordinate the regeneration process."""
    print("=== Regenerating Clean Data ===\n")
    
    # Step 1: Backup original data
    backup_original_data()
    
    # Step 2: Replace with clean data
    replace_with_clean_data()
    
    # Step 3: Run parsing scripts
    try:
        run_parsing_scripts()
    except subprocess.CalledProcessError as e:
        print(f"\nError running parsing scripts: {e}")
        print("You may need to run the individual scripts manually.")
        return
    
    # Step 4: Verify results
    if verify_results():
        print("\n✅ All data successfully regenerated with cleaned content!")
    else:
        print("\n⚠️  Some files may be missing. Check the output above.")
        
    print("\nNext steps:")
    print("1. Test the cleaned data in the web applications")
    print("2. Run add_static_transliterations.py if transliterations are needed")
    print("3. Commit the changes once verified")

if __name__ == '__main__':
    main()