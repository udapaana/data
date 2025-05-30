#!/usr/bin/env python3
"""
Batch Vedanidhi Downloader
Downloads in manageable batches with resume capability
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime
import logging
import sys

class VedanidhiBatchDownloader:
    def __init__(self):
        self.base_url = "https://vaakya.vedanidhi.in"
        self.download_dir = Path("data/vedanidhi_complete")
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
        
        # Load sources and setup progress tracking
        self.sources = self.load_available_sources()
        self.progress_file = self.download_dir / 'download_progress.json'
        self.progress = self.load_progress()
    
    def load_available_sources(self):
        """Load sources organized by priority"""
        summary_file = Path("data/vedanidhi_exploration/vedanidhi_sources_summary.json")
        
        with open(summary_file, 'r') as f:
            data = json.load(f)
        
        # Flatten and prioritize
        all_sources = []
        priority_order = ['Samaveda', 'Atharvaveda', 'Yajurveda', 'Rigveda']
        
        for veda_name in priority_order:
            for veda_info in data['sources_by_veda']:
                if veda_info['veda'] == veda_name:
                    for source in veda_info['sources']:
                        source['veda'] = veda_name
                        all_sources.append(source)
        
        return all_sources
    
    def load_progress(self):
        """Load download progress"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {'completed': [], 'failed': [], 'last_index': 0}
    
    def save_progress(self):
        """Save download progress"""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
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
    
    def download_source(self, source, index):
        """Download a single source"""
        source_id = source['id']
        
        # Check if already completed
        if source_id in self.progress['completed']:
            self.logger.info(f"  [{index+1}] {source_id} - Already completed, skipping")
            return True
        
        if source_id in self.progress['failed']:
            self.logger.info(f"  [{index+1}] {source_id} - Previously failed, retrying")
        
        veda_name = source['veda']
        source_text = source['text']
        source_shakha = source['shakha']
        
        self.logger.info(f"  [{index+1}/{len(self.sources)}] {veda_name} - {source_shakha} - {source_text} ({source_id})")
        
        # Check if file already exists
        save_dir = self.download_dir / veda_name.lower() / source_shakha
        clean_text = source_text.replace('/', '_').replace(' ', '_')
        save_path = save_dir / f"{source_id}_{clean_text}.json"
        
        if save_path.exists():
            self.logger.info(f"    File already exists: {save_path.name}")
            self.progress['completed'].append(source_id)
            return True
        
        # Get total count
        data = self.get_texts_ajax(source_id, start=0, length=1, draw=1)
        
        if not data:
            self.logger.warning(f"    No response for {source_id}")
            self.progress['failed'].append(source_id)
            return False
        
        total_records = data.get('recordsTotal', 0)
        if total_records == 0:
            self.logger.warning(f"    No records found for {source_id}")
            self.progress['failed'].append(source_id)
            return False
        
        self.logger.info(f"    Total records: {total_records}")
        
        # Download all data
        all_texts = []
        start = 0
        draw = 1
        batch_size = 1000
        
        while start < total_records:
            try:
                data = self.get_texts_ajax(source_id, start=start, length=batch_size, draw=draw)
                
                if not data or 'data' not in data:
                    self.logger.error(f"    Failed to get batch at {start}")
                    break
                
                texts = data['data']
                if not texts:
                    break
                
                all_texts.extend(texts)
                start += len(texts)
                draw += 1
                
                # Progress indicator
                progress_pct = round(start / total_records * 100, 1)
                self.logger.info(f"    Progress: {start}/{total_records} ({progress_pct}%)")
                
                time.sleep(0.2)  # Be respectful
                
            except Exception as e:
                self.logger.error(f"    Error in batch download: {e}")
                break
        
        if all_texts and len(all_texts) > total_records * 0.9:  # At least 90% downloaded
            # Quick accent analysis
            accent_count = 0
            for text in all_texts[:50]:  # Sample
                if 'vaakya_text' in text and any(m in text['vaakya_text'] for m in ['॒', '॑', '।', '॥']):
                    accent_count += 1
            
            accent_percentage = round(accent_count / min(50, len(all_texts)) * 100, 1)
            
            # Save the data
            save_dir.mkdir(parents=True, exist_ok=True)
            
            save_data = {
                'metadata': {
                    'source': 'vedanidhi',
                    'veda': veda_name.lower(),
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
            self.logger.info(f"    ✓ Saved {len(all_texts)} texts ({file_size_mb:.1f}MB)")
            self.logger.info(f"    ✓ Accent marks: {accent_percentage}% (sample)")
            
            self.progress['completed'].append(source_id)
            return True
        else:
            self.logger.error(f"    Download incomplete: {len(all_texts)}/{total_records}")
            self.progress['failed'].append(source_id)
            return False
    
    def run_batch(self, batch_size=10):
        """Run download in batches"""
        start_index = self.progress['last_index']
        
        self.logger.info(f"Starting batch download from index {start_index}")
        self.logger.info(f"Total sources: {len(self.sources)}")
        self.logger.info(f"Completed: {len(self.progress['completed'])}")
        self.logger.info(f"Failed: {len(self.progress['failed'])}")
        self.logger.info("=" * 80)
        
        for i in range(start_index, min(start_index + batch_size, len(self.sources))):
            source = self.sources[i]
            
            try:
                self.download_source(source, i)
                self.progress['last_index'] = i + 1
                self.save_progress()
                
                # Pause between sources
                time.sleep(1)
                
            except KeyboardInterrupt:
                self.logger.info(f"\nInterrupted at index {i}")
                self.progress['last_index'] = i
                self.save_progress()
                break
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                continue
        
        # Summary
        self.logger.info(f"\nBatch complete!")
        self.logger.info(f"Completed: {len(self.progress['completed'])}/{len(self.sources)}")
        self.logger.info(f"Next batch starts at index: {self.progress['last_index']}")
        
        if self.progress['last_index'] >= len(self.sources):
            self.logger.info("🎉 ALL DOWNLOADS COMPLETE!")

def main():
    downloader = VedanidhiBatchDownloader()
    
    # Allow command line batch size
    batch_size = 10
    if len(sys.argv) > 1:
        try:
            batch_size = int(sys.argv[1])
        except ValueError:
            pass
    
    downloader.run_batch(batch_size)

if __name__ == "__main__":
    main()