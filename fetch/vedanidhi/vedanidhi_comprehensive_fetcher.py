#!/usr/bin/env python3
"""
Comprehensive Vedanidhi Fetcher
Downloads all 107 available sources with accent mark validation
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime
import logging

class VedanidhiComprehensiveFetcher:
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
        
        # Load the available sources from our exploration
        self.sources = self.load_available_sources()
        
        # Priority order: Sāmaveda, Atharvaveda, Yajurveda, Rigveda
        self.download_order = ['Samaveda', 'Atharvaveda', 'Yajurveda', 'Rigveda']
    
    def load_available_sources(self):
        """Load the available sources from our exploration"""
        summary_file = Path("data/vedanidhi_exploration/vedanidhi_sources_summary.json")
        
        if not summary_file.exists():
            self.logger.error(f"Summary file not found: {summary_file}")
            return {}
        
        with open(summary_file, 'r') as f:
            data = json.load(f)
        
        # Organize by veda for easier access
        sources_by_veda = {}
        for veda_info in data['sources_by_veda']:
            veda_name = veda_info['veda']
            sources_by_veda[veda_name] = veda_info['sources']
        
        return sources_by_veda
    
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
            self.logger.error(f"Failed to get texts for {value}: {e}")
            return None
    
    def download_source(self, source, veda_name):
        """Download a single source"""
        source_id = source['id']
        source_text = source['text']
        source_shakha = source['shakha']
        
        self.logger.info(f"  Downloading {source_text} ({source_id})")
        
        # Get total count first
        data = self.get_texts_ajax(source_id, start=0, length=1, draw=1)
        
        if not data:
            self.logger.warning(f"    No response for {source_id}")
            return False
        
        total_records = data.get('recordsTotal', 0)
        if total_records == 0:
            self.logger.warning(f"    No records found for {source_id}")
            return False
        
        self.logger.info(f"    Total records: {total_records}")
        
        # Download all data
        all_texts = []
        start = 0
        draw = 1
        batch_size = 1000
        
        while start < total_records:
            batch_end = min(start + batch_size, total_records)
            self.logger.info(f"    Fetching {start}-{batch_end}/{total_records}...")
            
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
            
            # Be respectful to the server
            time.sleep(0.3)
        
        if all_texts:
            # Analyze accent coverage
            accent_count = 0
            sample_accented = []
            
            for text in all_texts[:100]:  # Sample first 100
                if 'vaakya_text' in text:
                    text_content = text['vaakya_text']
                    # Check for Vedic accent marks
                    if any(m in text_content for m in ['॒', '॑', '᳚', '᳛', '।', '॥']):
                        accent_count += 1
                        if len(sample_accented) < 3:
                            sample_accented.append({
                                'location': text.get('location', ''),
                                'text': text_content[:150] + '...' if len(text_content) > 150 else text_content
                            })
            
            # Calculate accent percentage (from sample)
            accent_percentage = round(accent_count / min(100, len(all_texts)) * 100, 2) if all_texts else 0
            
            # Save the data
            save_dir = self.download_dir / veda_name.lower() / source_shakha
            save_dir.mkdir(parents=True, exist_ok=True)
            
            # Clean filename
            clean_text = source_text.replace('/', '_').replace(' ', '_')
            save_path = save_dir / f"{source_id}_{clean_text}.json"
            
            save_data = {
                'metadata': {
                    'source': 'vedanidhi',
                    'veda': veda_name.lower(),
                    'shakha': source_shakha,
                    'text_type': source_text,
                    'source_id': source_id,
                    'total_texts': len(all_texts),
                    'accent_percentage_sample': accent_percentage,
                    'downloaded_at': datetime.now().isoformat(),
                    'sample_accented_texts': sample_accented
                },
                'texts': all_texts
            }
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            file_size_mb = save_path.stat().st_size / (1024 * 1024)
            self.logger.info(f"    ✓ Saved {len(all_texts)} texts ({file_size_mb:.1f}MB)")
            self.logger.info(f"    ✓ Accent marks: {accent_percentage}% (sample)")
            
            return True
        
        return False
    
    def download_veda(self, veda_name):
        """Download all sources for a specific Veda"""
        if veda_name not in self.sources:
            self.logger.warning(f"No sources found for {veda_name}")
            return
        
        sources = self.sources[veda_name]
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"DOWNLOADING {veda_name.upper()}")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Total sources: {len(sources)}")
        
        success_count = 0
        
        for i, source in enumerate(sources, 1):
            self.logger.info(f"\n[{i}/{len(sources)}] {source['shakha']} - {source['text']}")
            
            if self.download_source(source, veda_name):
                success_count += 1
            
            # Longer pause between sources
            time.sleep(1)
        
        self.logger.info(f"\n{veda_name} complete: {success_count}/{len(sources)} sources downloaded")
    
    def run(self):
        """Run the comprehensive download"""
        self.logger.info("Starting comprehensive Vedanidhi download")
        self.logger.info(f"Total available sources: {sum(len(sources) for sources in self.sources.values())}")
        self.logger.info("=" * 80)
        
        # Download in priority order
        for veda_name in self.download_order:
            if veda_name in self.sources:
                self.download_veda(veda_name)
                
                # Longer pause between Vedas
                time.sleep(5)
        
        self.logger.info("\n" + "=" * 80)
        self.logger.info("DOWNLOAD COMPLETE!")
        
        # Generate final summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate final download summary"""
        summary = {
            'download_completed_at': datetime.now().isoformat(),
            'total_downloaded': 0,
            'vedas': {}
        }
        
        for veda_dir in self.download_dir.iterdir():
            if veda_dir.is_dir():
                veda_name = veda_dir.name
                veda_files = list(veda_dir.rglob('*.json'))
                
                veda_summary = {
                    'files_downloaded': len(veda_files),
                    'total_size_mb': sum(f.stat().st_size for f in veda_files) / (1024 * 1024),
                    'sources': []
                }
                
                for json_file in veda_files:
                    try:
                        with open(json_file, 'r') as f:
                            data = json.load(f)
                            metadata = data.get('metadata', {})
                            veda_summary['sources'].append({
                                'file': str(json_file.relative_to(self.download_dir)),
                                'shakha': metadata.get('shakha', ''),
                                'text_type': metadata.get('text_type', ''),
                                'total_texts': metadata.get('total_texts', 0),
                                'accent_percentage': metadata.get('accent_percentage_sample', 0)
                            })
                    except:
                        pass
                
                summary['vedas'][veda_name] = veda_summary
                summary['total_downloaded'] += len(veda_files)
        
        summary_path = self.download_dir / 'download_summary.json'
        with open(summary_path, 'w') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"\nFinal summary saved to: {summary_path}")
        self.logger.info(f"Total files downloaded: {summary['total_downloaded']}")

def main():
    fetcher = VedanidhiComprehensiveFetcher()
    fetcher.run()

if __name__ == "__main__":
    main()