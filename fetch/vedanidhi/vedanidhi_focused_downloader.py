#!/usr/bin/env python3
"""
Focused Vedanidhi Downloader
Downloads specific high-priority texts with accent marks
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime
import logging

class VedanidhiFocusedDownloader:
    def __init__(self):
        self.base_url = "https://vaakya.vedanidhi.in"
        self.download_dir = Path("data/vedanidhi_focused")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
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
        
        # Priority targets - texts most likely to have accent marks
        self.priority_targets = [
            {
                'veda': 'rigveda',
                'veda_id': '01',
                'targets': [
                    {'id': '010101', 'name': 'शाकलसंहिता', 'desc': 'Śākala Saṃhitā'},
                    {'id': '010105', 'name': 'पदम्', 'desc': 'Padapāṭha'}
                ]
            },
            {
                'veda': 'yajurveda',
                'veda_id': '02',
                'targets': [
                    # We need to discover the IDs for Taittirīya texts
                    # Will explore programmatically
                ]
            }
        ]
    
    def get_texts_ajax(self, value, start=0, length=1000, draw=1):
        """Get actual text data via AJAX"""
        url = f"{self.base_url}/browse_search_data_ajax/"
        
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
            '_': str(int(time.time() * 1000))
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get texts: {e}")
            return None
    
    def download_text_type(self, value, name, veda, desc):
        """Download a specific text type"""
        self.logger.info(f"\nDownloading {veda} - {desc} ({value})")
        
        all_texts = []
        start = 0
        draw = 1
        batch_size = 1000
        
        while True:
            self.logger.info(f"  Fetching records {start} to {start + batch_size}...")
            data = self.get_texts_ajax(value, start=start, length=batch_size, draw=draw)
            
            if not data or 'data' not in data:
                self.logger.error("  No data received")
                break
            
            texts = data['data']
            if not texts:
                break
            
            # Quick check for accent marks in first few texts
            has_accents = False
            for i, text in enumerate(texts[:10]):
                if 'vaakya_text' in text:
                    # Look for common accent markers
                    if any(marker in text['vaakya_text'] for marker in ['॒', '॑', 'ः', '।', '॥']):
                        has_accents = True
                        break
            
            if has_accents:
                self.logger.info(f"  ✓ Found accent marks! Continuing download...")
            else:
                self.logger.warning(f"  ⚠ No accent marks found in sample. Checking more...")
            
            all_texts.extend(texts)
            self.logger.info(f"  Got {len(texts)} texts (total: {len(all_texts)})")
            
            total_records = data.get('recordsTotal', 0)
            if start + len(texts) >= total_records:
                self.logger.info(f"  Completed! Total: {total_records} texts")
                break
            
            start += len(texts)
            draw += 1
            time.sleep(0.5)
        
        if all_texts:
            # Save the data
            save_dir = self.download_dir / veda / name
            save_dir.mkdir(parents=True, exist_ok=True)
            save_path = save_dir / f'{value}_texts.json'
            
            # Analyze accent coverage
            accent_count = 0
            for text in all_texts:
                if 'vaakya_text' in text and any(m in text['vaakya_text'] for m in ['॒', '॑']):
                    accent_count += 1
            
            save_data = {
                'metadata': {
                    'source': 'vedanidhi',
                    'veda': veda,
                    'text_type': desc,
                    'value_code': value,
                    'total_texts': len(all_texts),
                    'texts_with_accents': accent_count,
                    'accent_percentage': round(accent_count / len(all_texts) * 100, 2) if all_texts else 0,
                    'downloaded_at': datetime.now().isoformat()
                },
                'texts': all_texts
            }
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"  Saved to: {save_path}")
            self.logger.info(f"  Accent coverage: {accent_count}/{len(all_texts)} ({save_data['metadata']['accent_percentage']}%)")
            
            return save_data['metadata']['accent_percentage'] > 50  # Return True if good accent coverage
        
        return False
    
    def explore_yajurveda_shakhas(self):
        """Explore Yajurveda śākhās to find Taittirīya"""
        self.logger.info("\nExploring Yajurveda śākhās...")
        
        url = f"{self.base_url}/browsedata/"
        params = {'id': 1, 'value': '02'}  # Yajurveda
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            shakhas = response.json()
            
            self.logger.info(f"Found {len(shakhas)} Yajurveda śākhās:")
            for shakha in shakhas:
                self.logger.info(f"  {shakha['id']}: {shakha['value']}")
                
                # Look for Taittirīya
                if 'तैत्तिरीय' in shakha['value'] or 'taittir' in shakha['value'].lower():
                    self.logger.info(f"  → Found Taittirīya! Exploring text types...")
                    
                    # Get text types for Taittirīya
                    params = {'id': 2, 'value': shakha['id']}
                    response = self.session.get(url, params=params)
                    text_types = response.json()
                    
                    for text_type in text_types:
                        self.logger.info(f"    {text_type['id']}: {text_type['value']}")
                        
            return shakhas
            
        except Exception as e:
            self.logger.error(f"Failed to explore: {e}")
            return []
    
    def run(self):
        """Run the focused download"""
        self.logger.info("Starting focused Vedanidhi download...")
        self.logger.info("Looking for texts with accent marks (svara)")
        self.logger.info("=" * 60)
        
        # First explore Yajurveda to find Taittirīya
        self.explore_yajurveda_shakhas()
        
        # Download priority Rigveda texts
        for veda_info in self.priority_targets:
            if veda_info['targets']:  # Only if we have specific targets
                for target in veda_info['targets']:
                    success = self.download_text_type(
                        target['id'], 
                        target['name'],
                        veda_info['veda'],
                        target['desc']
                    )
                    
                    if success:
                        self.logger.info(f"✓ {target['desc']} has good accent coverage!")
                    else:
                        self.logger.warning(f"✗ {target['desc']} lacks accent marks")
                    
                    time.sleep(2)
        
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Download complete!")
        
        # Summary
        summary_path = self.download_dir / 'download_summary.json'
        summary = {
            'downloaded_at': datetime.now().isoformat(),
            'focus': 'Texts with accent marks for adhyayana',
            'results': []
        }
        
        # Analyze downloaded files
        for json_file in self.download_dir.rglob('*.json'):
            if json_file.name != 'download_summary.json':
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    if 'metadata' in data:
                        summary['results'].append({
                            'file': str(json_file.relative_to(self.download_dir)),
                            'veda': data['metadata']['veda'],
                            'text_type': data['metadata']['text_type'],
                            'total_texts': data['metadata']['total_texts'],
                            'accent_percentage': data['metadata']['accent_percentage']
                        })
        
        with open(summary_path, 'w') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"\nSummary saved to: {summary_path}")

def main():
    downloader = VedanidhiFocusedDownloader()
    downloader.run()

if __name__ == "__main__":
    main()