#!/usr/bin/env python3
"""
Continuous Vedanidhi Downloader
Runs in background to complete all downloads
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime
import logging

class ContinuousDownloader:
    def __init__(self):
        self.base_url = "https://vaakya.vedanidhi.in"
        self.download_dir = Path("data/vedanidhi_complete")
        
        # Setup logging to file
        log_file = self.download_dir / 'continuous_download.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
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
        
        # Load sources and progress
        self.sources = self.load_sources()
        self.progress_file = self.download_dir / 'download_progress.json'
        
    def load_sources(self):
        """Load all sources in priority order"""
        summary_file = Path("data/vedanidhi_exploration/vedanidhi_sources_summary.json")
        with open(summary_file, 'r') as f:
            data = json.load(f)
        
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
        """Load current progress"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {'completed': [], 'failed': [], 'last_index': 0}
    
    def save_progress(self, progress):
        """Save progress"""
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
    
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
    
    def download_source(self, source, index, progress):
        """Download a single source"""
        source_id = source['id']
        
        # Skip if already completed
        if source_id in progress['completed']:
            return True
        
        veda_name = source['veda']
        source_text = source['text']
        source_shakha = source['shakha']
        
        self.logger.info(f"[{index+1}/{len(self.sources)}] {veda_name} - {source_shakha} - {source_text} ({source_id})")
        
        # Check if file exists
        save_dir = self.download_dir / veda_name.lower() / source_shakha
        clean_text = source_text.replace('/', '_').replace(' ', '_')
        save_path = save_dir / f"{source_id}_{clean_text}.json"
        
        if save_path.exists():
            self.logger.info(f"  File exists: {save_path.name}")
            progress['completed'].append(source_id)
            return True
        
        # Get total count
        data = self.get_texts_ajax(source_id, start=0, length=1, draw=1)
        if not data or data.get('recordsTotal', 0) == 0:
            self.logger.warning(f"  No data for {source_id}")
            progress['failed'].append(source_id)
            return False
        
        total_records = data['recordsTotal']
        self.logger.info(f"  Total records: {total_records}")
        
        # Download all data
        all_texts = []
        start = 0
        draw = 1
        batch_size = 1000
        
        while start < total_records:
            data = self.get_texts_ajax(source_id, start=start, length=batch_size, draw=draw)
            
            if not data or 'data' not in data:
                break
            
            texts = data['data']
            if not texts:
                break
            
            all_texts.extend(texts)
            start += len(texts)
            draw += 1
            
            # Log progress every 1000 records
            if len(all_texts) % 1000 == 0 or start >= total_records:
                progress_pct = round(start / total_records * 100, 1)
                self.logger.info(f"  Progress: {start}/{total_records} ({progress_pct}%)")
            
            time.sleep(0.1)  # Faster for large files
        
        if all_texts and len(all_texts) >= total_records * 0.9:
            # Quick accent analysis
            accent_count = sum(1 for text in all_texts[:50] 
                             if 'vaakya_text' in text and any(m in text['vaakya_text'] for m in ['॒', '॑', '।', '॥']))
            accent_pct = round(accent_count / min(50, len(all_texts)) * 100, 1)
            
            # Save data
            save_dir.mkdir(parents=True, exist_ok=True)
            save_data = {
                'metadata': {
                    'source': 'vedanidhi',
                    'veda': veda_name.lower(),
                    'shakha': source_shakha,
                    'text_type': source_text,
                    'source_id': source_id,
                    'total_texts': len(all_texts),
                    'accent_percentage_sample': accent_pct,
                    'downloaded_at': datetime.now().isoformat()
                },
                'texts': all_texts
            }
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            file_size_mb = save_path.stat().st_size / (1024 * 1024)
            self.logger.info(f"  ✓ Saved {len(all_texts)} texts ({file_size_mb:.1f}MB, {accent_pct}% accents)")
            
            progress['completed'].append(source_id)
            return True
        else:
            self.logger.error(f"  Download incomplete: {len(all_texts)}/{total_records}")
            progress['failed'].append(source_id)
            return False
    
    def run_continuous(self):
        """Run continuous download until all sources complete"""
        self.logger.info("Starting continuous Vedanidhi download")
        self.logger.info(f"Total sources: {len(self.sources)}")
        
        while True:
            progress = self.load_progress()
            start_index = progress['last_index']
            
            if start_index >= len(self.sources):
                self.logger.info("🎉 ALL DOWNLOADS COMPLETE!")
                break
            
            self.logger.info(f"Progress: {len(progress['completed'])}/{len(self.sources)} completed")
            self.logger.info(f"Continuing from index {start_index}")
            
            # Download next batch
            batch_size = 5
            for i in range(start_index, min(start_index + batch_size, len(self.sources))):
                source = self.sources[i]
                
                try:
                    success = self.download_source(source, i, progress)
                    progress['last_index'] = i + 1
                    self.save_progress(progress)
                    
                    if success:
                        self.logger.info(f"  ✓ Success")
                    else:
                        self.logger.warning(f"  ✗ Failed")
                    
                    time.sleep(0.5)
                    
                except KeyboardInterrupt:
                    self.logger.info("Download interrupted by user")
                    return
                except Exception as e:
                    self.logger.error(f"Error: {e}")
                    continue
            
            # Brief pause between batches
            time.sleep(2)
        
        # Generate final summary
        self.generate_final_summary()
    
    def generate_final_summary(self):
        """Generate final download summary"""
        total_files = len(list(self.download_dir.rglob('*.json'))) - 2  # Exclude progress files
        total_size = sum(f.stat().st_size for f in self.download_dir.rglob('*.json') if 'progress' not in f.name)
        total_size_mb = total_size / (1024 * 1024)
        
        summary = {
            'completed_at': datetime.now().isoformat(),
            'total_files': total_files,
            'total_size_mb': round(total_size_mb, 1),
            'status': 'COMPLETE'
        }
        
        with open(self.download_dir / 'final_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.logger.info(f"📊 Final Summary:")
        self.logger.info(f"   Files downloaded: {total_files}")
        self.logger.info(f"   Total size: {total_size_mb:.1f}MB")
        self.logger.info(f"   Summary saved to: final_summary.json")

def main():
    downloader = ContinuousDownloader()
    downloader.run_continuous()

if __name__ == "__main__":
    main()