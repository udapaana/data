#!/usr/bin/env python3
"""
Vedanidhi Hierarchical Downloader
Follows the actual Vedanidhi browsing structure
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime
import logging
from urllib.parse import urlencode

class VedanidhiHierarchicalDownloader:
    def __init__(self):
        self.base_url = "https://vaakya.vedanidhi.in"
        self.download_dir = Path("data/vedanidhi_hierarchical")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
        
        # Session with cookies
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://vaakya.vedanidhi.in/vedanidhi/browsedata/'
        })
        
        # Set cookies
        self.session.cookies.set('csrftoken', 'ROqhEXwodGWEmb5w3TZR6NjQUToZOZSlMjjpEjztXP3gHEssqNQVNbXEczGJRsYV')
        self.session.cookies.set('sessionid', 'o6nnni9emasigbnscvrqx7cfjrp26rl2')
        
        self.download_log = []
        self.hierarchy_cache = {}
    
    def get_browse_data(self, level, value):
        """Get browse data for a specific level"""
        url = f"{self.base_url}/browsedata/"
        params = {
            'id': level,
            'value': value
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get browse data for level {level}, value {value}: {e}")
            return []
    
    def get_texts_ajax(self, value, start=0, length=10, draw=1):
        """Get actual text data via AJAX"""
        url = f"{self.base_url}/browse_search_data_ajax/"
        
        # Build the complex query parameters
        params = {
            'value': value,
            'search_value': '',
            'draw': str(draw),
            'columns[0][data]': 'location',
            'columns[0][name]': '',
            'columns[0][searchable]': 'true',
            'columns[0][orderable]': 'false',
            'columns[0][search][value]': '',
            'columns[0][search][regex]': 'false',
            'columns[1][data]': 'vaakya_text',
            'columns[1][name]': '',
            'columns[1][searchable]': 'true',
            'columns[1][orderable]': 'false',
            'columns[1][search][value]': '',
            'columns[1][search][regex]': 'false',
            'start': str(start),
            'length': str(length),
            'search[value]': '',
            'search[regex]': 'false',
            '_': str(int(time.time() * 1000))  # timestamp
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except Exception as e:
            self.logger.error(f"Failed to get texts for value {value}: {e}")
            return None
    
    def download_all_texts(self, value, name, save_path):
        """Download all texts for a given value"""
        all_texts = []
        start = 0
        batch_size = 1000  # Get 1000 at a time for efficiency
        draw = 1
        
        while True:
            self.logger.info(f"  Fetching batch starting at {start}...")
            data = self.get_texts_ajax(value, start=start, length=batch_size, draw=draw)
            
            if not data or 'data' not in data:
                break
            
            texts = data['data']
            if not texts:
                break
            
            all_texts.extend(texts)
            self.logger.info(f"    Got {len(texts)} texts (total: {len(all_texts)})")
            
            # Check if we got all
            total_records = data.get('recordsTotal', 0)
            if start + len(texts) >= total_records:
                self.logger.info(f"    Completed! Total records: {total_records}")
                break
            
            start += len(texts)
            draw += 1
            time.sleep(0.5)  # Shorter pause since server seems responsive
        
        if all_texts:
            # Save the data
            save_data = {
                'metadata': {
                    'source': 'vedanidhi',
                    'value_code': value,
                    'name': name,
                    'total_texts': len(all_texts),
                    'downloaded_at': datetime.now().isoformat()
                },
                'texts': all_texts
            }
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"  Saved {len(all_texts)} texts to {save_path}")
            return len(all_texts)
        
        return 0
    
    def explore_vedas(self):
        """Explore and download all Vedas hierarchically"""
        # Start with level 1 - Get all Vedas
        vedas = [
            {'id': '01', 'name': 'rigveda'},
            {'id': '02', 'name': 'yajurveda'},
            {'id': '03', 'name': 'samaveda'},
            {'id': '04', 'name': 'atharvaveda'}
        ]
        
        for veda in vedas:
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Processing {veda['name'].upper()}")
            self.logger.info(f"{'='*60}")
            
            # Get śākhās for this Veda
            shakhas = self.get_browse_data(1, veda['id'])
            self.logger.info(f"Found {len(shakhas)} śākhās")
            
            for shakha in shakhas:
                shakha_id = shakha['id']
                shakha_name = shakha['value'].strip()
                self.logger.info(f"\n  Śākhā: {shakha_name} ({shakha_id})")
                
                # Get text types for this śākhā
                text_types = self.get_browse_data(2, shakha_id)
                self.logger.info(f"  Found {len(text_types)} text types")
                
                for text_type in text_types:
                    text_id = text_type['id']
                    text_name = text_type['value'].strip()
                    self.logger.info(f"\n    Text type: {text_name} ({text_id})")
                    
                    # Create save path
                    save_dir = self.download_dir / veda['name'] / shakha_name / text_name
                    save_dir.mkdir(parents=True, exist_ok=True)
                    save_path = save_dir / 'texts.json'
                    
                    # Download all texts
                    count = self.download_all_texts(text_id, text_name, save_path)
                    
                    # Log the download
                    self.download_log.append({
                        'veda': veda['name'],
                        'veda_id': veda['id'],
                        'shakha': shakha_name,
                        'shakha_id': shakha_id,
                        'text_type': text_name,
                        'text_id': text_id,
                        'count': count,
                        'path': str(save_path),
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    time.sleep(2)  # Pause between text types
                
                time.sleep(3)  # Pause between śākhās
        
        # Save download log
        log_path = self.download_dir / 'download_log.json'
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(self.download_log, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Download complete!")
        self.logger.info(f"Total downloads: {len(self.download_log)}")
        self.logger.info(f"Log saved to: {log_path}")

def main():
    downloader = VedanidhiHierarchicalDownloader()
    
    # Test with a single text type first
    print("Testing with Rigveda Śākala Saṃhitā...")
    test_count = downloader.download_all_texts('010101', 'शाकलसंहिता', Path('test_rigveda.json'))
    
    if test_count > 0:
        print(f"\nTest successful! Downloaded {test_count} texts.")
        response = input("\nProceed with full download? (y/n): ")
        if response.lower() == 'y':
            downloader.explore_vedas()
    else:
        print("Test failed. Please check the connection and cookies.")

if __name__ == "__main__":
    main()