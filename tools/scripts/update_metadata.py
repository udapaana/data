#!/usr/bin/env python3
"""Update metadata files in the reorganized structure."""

import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_metadata_from_file(json_path):
    """Extract metadata from the actual JSON file."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Extract metadata
        meta = {
            'source_id': json_path.stem,
            'file_name': json_path.name,
            'total_records': len(data.get('data', [])) if 'data' in data else 0
        }
        
        # Try to infer from data structure
        if 'data' in data and len(data['data']) > 0:
            first_item = data['data'][0]
            if 'location' in first_item:
                location = first_item['location']
                if len(location) > 0:
                    # Map abbreviations to full names
                    veda_map = {'ऋ': 'Rigveda', 'सा': 'Samaveda', 'य': 'Yajurveda', 'अ': 'Atharvaveda'}
                    meta['veda'] = veda_map.get(location[0], location[0])
                if len(location) > 1:
                    meta['shakha'] = location[1]
            
            # Get text type from first few items
            for item in data['data'][:10]:
                if 'vaakya_text' in item and item['vaakya_text']:
                    # Look for text type indicators
                    text = item['vaakya_text']
                    if 'संहिता' in text:
                        meta['text_type'] = 'संहिता'
                        break
                    elif 'ब्राह्मण' in text:
                        meta['text_type'] = 'ब्राह्मण'
                        break
                    elif 'आरण्यक' in text or 'आरण्ह्यक' in text:
                        meta['text_type'] = 'आरण्यक'
                        break
                    elif 'उपनिषत्' in text or 'उपनिषद्' in text:
                        meta['text_type'] = 'उपनिषद्'
                        break
            
            # Check for accents
            sample_text = ' '.join(str(item.get('vaakya_text', '')) for item in data['data'][:100])
            has_accents = any(char in sample_text for char in ['॑', '॒'])
            meta['has_accents'] = has_accents
            
            if has_accents:
                # Calculate accent coverage on larger sample
                larger_sample = ' '.join(str(item.get('vaakya_text', '')) for item in data['data'][:500])
                words = larger_sample.split()
                accented_words = sum(1 for word in words if any(char in word for char in ['॑', '॒']))
                meta['accent_coverage'] = round(accented_words / len(words), 3) if words else 0.0
            else:
                meta['accent_coverage'] = 0.0
        
        # Add 'meta' to the original file if it doesn't exist
        if 'meta' not in data:
            data['meta'] = meta
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"  Added meta to {json_path.name}")
                
        return meta
        
    except Exception as e:
        logger.error(f"Error processing {json_path}: {e}")
        return None

def update_all_metadata():
    """Update all metadata files in the reorganized structure."""
    base_dir = Path("data/vedic_texts_by_sakha")
    
    for sakha_dir in base_dir.iterdir():
        if sakha_dir.is_dir() and not sakha_dir.name.startswith('.'):
            logger.info(f"\nProcessing {sakha_dir.name}:")
            
            for source_dir in sakha_dir.iterdir():
                if source_dir.is_dir():
                    # Find the JSON data file
                    json_files = list(source_dir.glob("*.json"))
                    data_files = [f for f in json_files if f.name != 'metadata.json']
                    
                    if data_files:
                        json_path = data_files[0]
                        meta = extract_metadata_from_file(json_path)
                        
                        if meta:
                            # Write updated metadata
                            meta_path = source_dir / "metadata.json"
                            with open(meta_path, 'w', encoding='utf-8') as f:
                                json.dump(meta, f, ensure_ascii=False, indent=2)
                            
                            logger.info(f"  {source_dir.name}: {meta.get('total_records', 0)} texts, "
                                      f"{meta.get('accent_coverage', 0)*100:.1f}% accents")

if __name__ == "__main__":
    logger.info("Updating metadata files...")
    update_all_metadata()
    logger.info("\nMetadata update complete!")