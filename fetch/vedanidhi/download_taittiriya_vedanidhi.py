#!/usr/bin/env python3
"""
Download Taittirīya texts from Vedanidhi
Focused on texts we know exist with accent marks
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime
import logging

class TaittiriyaVedanidhiDownloader:
    def __init__(self):
        self.base_url = "https://vaakya.vedanidhi.in"
        self.download_dir = Path("data/vedanidhi_taittiriya")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
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
        
        # Taittirīya text types discovered
        self.taittiriya_texts = [
            {'id': '020401', 'name': 'तैत्तिरीयसंहिता', 'desc': 'Taittirīya Saṃhitā'},
            {'id': '020402', 'name': 'तैत्तिरीयब्राह्मणम्', 'desc': 'Taittirīya Brāhmaṇa'},
            {'id': '020403', 'name': 'तैत्तरीयारण्यकम्', 'desc': 'Taittirīya Āraṇyaka'},
            {'id': '020405', 'name': 'पदम्', 'desc': 'Taittirīya Padapāṭha'}
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
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get texts: {e}")
            return None
    
    def download_text_type(self, text_info):
        """Download a specific Taittirīya text type"""
        self.logger.info(f"\nDownloading {text_info['desc']} ({text_info['id']})")
        
        all_texts = []
        start = 0
        draw = 1
        batch_size = 1000
        
        # First, get total count
        self.logger.info("  Getting total count...")
        data = self.get_texts_ajax(text_info['id'], start=0, length=1, draw=1)
        
        if not data:
            self.logger.error("  Failed to get initial data")
            return False
            
        total_records = data.get('recordsTotal', 0)
        self.logger.info(f"  Total records: {total_records}")
        
        if total_records == 0:
            self.logger.warning("  No records found")
            return False
        
        # Download in batches
        while start < total_records:
            self.logger.info(f"  Fetching records {start} to {min(start + batch_size, total_records)}...")
            data = self.get_texts_ajax(text_info['id'], start=start, length=batch_size, draw=draw)
            
            if not data or 'data' not in data:
                self.logger.error("  No data received")
                break
            
            texts = data['data']
            if not texts:
                break
            
            all_texts.extend(texts)
            self.logger.info(f"    Got {len(texts)} texts")
            
            start += len(texts)
            draw += 1
            
            # Be respectful
            time.sleep(0.5)
        
        if all_texts:
            # Analyze accent coverage
            accent_count = 0
            sample_texts = []
            
            for i, text in enumerate(all_texts):
                if 'vaakya_text' in text:
                    text_content = text['vaakya_text']
                    # Check for Vedic accent marks
                    if any(m in text_content for m in ['॒', '॑', '᳚', '᳛']):
                        accent_count += 1
                        if len(sample_texts) < 5:  # Collect samples
                            sample_texts.append({
                                'location': text.get('location', ''),
                                 'text': text_content[:100] + '...' if len(text_content) > 100 else text_content
                            })
            
            # Save the data
            save_path = self.download_dir / f"{text_info['id']}_{text_info['name']}.json"
            
            save_data = {
                'metadata': {
                    'source': 'vedanidhi',
                    'veda': 'yajurveda',
                    'shakha': 'taittiriya',
                    'text_type': text_info['desc'],
                    'value_code': text_info['id'],
                    'total_texts': len(all_texts),
                    'texts_with_accents': accent_count,
                    'accent_percentage': round(accent_count / len(all_texts) * 100, 2) if all_texts else 0,
                    'downloaded_at': datetime.now().isoformat(),
                    'sample_accented_texts': sample_texts
                },
                'texts': all_texts
            }
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"  ✓ Saved {len(all_texts)} texts to: {save_path.name}")
            self.logger.info(f"  ✓ Accent coverage: {accent_count}/{len(all_texts)} ({save_data['metadata']['accent_percentage']}%)")
            
            return True
        
        return False
    
    def run(self):
        """Download all Taittirīya texts"""
        self.logger.info("Taittirīya Texts Downloader from Vedanidhi")
        self.logger.info("=" * 60)
        
        success_count = 0
        
        for text_info in self.taittiriya_texts:
            if self.download_text_type(text_info):
                success_count += 1
            time.sleep(2)  # Pause between different text types
        
        self.logger.info("\n" + "=" * 60)
        self.logger.info(f"Download complete! Successfully downloaded {success_count}/{len(self.taittiriya_texts)} text types")
        
        # Create summary
        summary = {
            'downloaded_at': datetime.now().isoformat(),
            'veda': 'Yajurveda',
            'shakha': 'Taittirīya',
            'source': 'Vedanidhi',
            'total_text_types': len(self.taittiriya_texts),
            'successful_downloads': success_count,
            'text_types': []
        }
        
        # Add info about each downloaded file
        for json_file in self.download_dir.glob('*.json'):
            if not json_file.name.startswith('summary'):
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    if 'metadata' in data:
                        summary['text_types'].append({
                            'file': json_file.name,
                            'text_type': data['metadata']['text_type'],
                            'total_texts': data['metadata']['total_texts'],
                            'accent_percentage': data['metadata']['accent_percentage'],
                            'samples': data['metadata'].get('sample_accented_texts', [])
                        })
        
        summary_path = self.download_dir / 'summary.json'
        with open(summary_path, 'w') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"\nSummary saved to: {summary_path}")

def main():
    downloader = TaittiriyaVedanidhiDownloader()
    downloader.run()

if __name__ == "__main__":
    main()