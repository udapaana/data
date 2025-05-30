#!/usr/bin/env python3
"""
Download Atharvaveda texts specifically
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime
import logging

class AtharvavedaDownloader:
    def __init__(self):
        self.base_url = "https://vaakya.vedanidhi.in"
        self.download_dir = Path("data/vedanidhi_complete")
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Session with cookies
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://vaakya.vedanidhi.in/vedanidhi/browsedata/'
        })
        
        # Set cookies
        self.session.cookies.set('csrftoken', 'ROqhEXwodGWEmb5w3TZR6NjQUToZOZSlMjjpEjztXP3gHEssqNQVNbXEczGJRsYV')
        self.session.cookies.set('sessionid', 'o6nnni9emasigbnscvrqx7cfjrp26rl2')
        
        # Atharvaveda sources (manually extracted from our exploration)
        self.atharvaveda_sources = [
            {'id': '040101', 'text': 'शौनकसंहिता', 'shakha': 'शौनकशाखा'},
            {'id': '04010101', 'text': 'शौनकसंहिता - (04010101) काण्डम्', 'shakha': 'शौनकशाखा'},
            {'id': '04010102', 'text': 'शौनकसंहिता - (04010102) काण्डम्', 'shakha': 'शौनकशाखा'},
            {'id': '04010103', 'text': 'शौनकसंहिता - (04010103) काण्डम्', 'shakha': 'शौनकशाखा'},
            {'id': '04010104', 'text': 'शौनकसंहिता - (04010104) काण्डम्', 'shakha': 'शौनकशाखा'},
            {'id': '04010105', 'text': 'शौनकसंहिता - (04010105) काण्डम्', 'shakha': 'शौनकशाखा'}
        ]
    
    def get_texts_ajax(self, value, start=0, length=1000, draw=1):
        """Get text data via AJAX"""
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
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Request failed: {e}")
            return None
    
    def download_source(self, source):
        """Download a single Atharvaveda source"""
        source_id = source['id']
        source_text = source['text']
        source_shakha = source['shakha']
        
        self.logger.info(f"Downloading Atharvaveda - {source_text} ({source_id})")
        
        # Get total count
        data = self.get_texts_ajax(source_id, start=0, length=1, draw=1)
        
        if not data:
            self.logger.warning(f"  No response for {source_id}")
            return False
        
        total_records = data.get('recordsTotal', 0)
        if total_records == 0:
            self.logger.warning(f"  No records found for {source_id}")
            return False
        
        self.logger.info(f"  Total records: {total_records}")
        
        # Download all data
        all_texts = []
        start = 0
        draw = 1
        batch_size = 1000
        
        while start < total_records:
            data = self.get_texts_ajax(source_id, start=start, length=batch_size, draw=draw)
            
            if not data or 'data' not in data:
                self.logger.error(f"  Failed to get batch at {start}")
                break
            
            texts = data['data']
            if not texts:
                break
            
            all_texts.extend(texts)
            start += len(texts)
            draw += 1
            
            progress_pct = round(start / total_records * 100, 1)
            self.logger.info(f"  Progress: {start}/{total_records} ({progress_pct}%)")
            
            time.sleep(0.2)
        
        if all_texts:
            # Accent analysis
            accent_count = 0
            for text in all_texts[:100]:  # Sample
                if 'vaakya_text' in text and any(m in text['vaakya_text'] for m in ['॒', '॑', '।', '॥']):
                    accent_count += 1
            
            accent_percentage = round(accent_count / min(100, len(all_texts)) * 100, 1)
            
            # Save the data
            save_dir = self.download_dir / 'atharvaveda' / source_shakha
            save_dir.mkdir(parents=True, exist_ok=True)
            
            clean_text = source_text.replace('/', '_').replace(' ', '_')
            save_path = save_dir / f"{source_id}_{clean_text}.json"
            
            save_data = {
                'metadata': {
                    'source': 'vedanidhi',
                    'veda': 'atharvaveda',
                    'shakha': source_shakha,
                    'text_type': source_text,
                    'source_id': source_id,
                    'total_texts': len(all_texts),
                    'accent_percentage_sample': accent_percentage,
                    'downloaded_at': datetime.now().isoformat()
                },
                'texts': all_texts
            }
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            file_size_mb = save_path.stat().st_size / (1024 * 1024)
            self.logger.info(f"  ✓ Saved {len(all_texts)} texts ({file_size_mb:.1f}MB)")
            self.logger.info(f"  ✓ Accent marks: {accent_percentage}% (sample)")
            
            return True
        
        return False
    
    def run(self):
        """Download Atharvaveda sources"""
        self.logger.info("Downloading Atharvaveda texts from Vedanidhi")
        self.logger.info("=" * 60)
        
        for i, source in enumerate(self.atharvaveda_sources, 1):
            self.logger.info(f"\n[{i}/{len(self.atharvaveda_sources)}]")
            
            if self.download_source(source):
                self.logger.info("✓ Success")
            else:
                self.logger.warning("✗ Failed")
            
            time.sleep(1)
        
        self.logger.info(f"\nAtharvaveda download complete!")

def main():
    downloader = AtharvavedaDownloader()
    downloader.run()

if __name__ == "__main__":
    main()