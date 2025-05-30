#!/usr/bin/env python3
"""
Validated Continuous Vedanidhi Downloader
Validates content at each step to ensure correct śākhā-specific data
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime
import logging
import hashlib

class ValidatedContinuousDownloader:
    def __init__(self):
        self.base_url = "https://vaakya.vedanidhi.in"
        self.download_dir = Path("data/vedanidhi_complete")
        
        # Setup logging
        log_file = self.download_dir / 'validated_download.log'
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
        
        # Content validation patterns
        self.veda_markers = {
            'rigveda': {
                'location': ['ऋ', 'अष्ट', 'मण्डल'],
                'content': ['ऋच्', 'सूक्त', 'मण्डल'],
                'reject': []  # Should not contain other Veda markers
            },
            'yajurveda': {
                'location': ['य', 'काण्ड', 'प्रपा'],
                'content': ['यजु', 'काण्ड', 'प्रपाठक', 'अनुवाक'],
                'reject': ['ऋ', 'साम', 'अथर्व']
            },
            'samaveda': {
                'location': ['सा', 'काण्ड'],
                'content': ['साम', 'गान', 'आर्चिक', 'ऊह', 'प्रकृति'],
                'reject': []  # Sāmaveda can contain Rigvedic mantras
            },
            'atharvaveda': {
                'location': ['अ', 'काण्ड'],
                'content': ['अथर्व', 'काण्ड', 'सूक्त'],
                'reject': ['ऋ', 'साम', 'यजु']
            }
        }
        
        # Track content hashes to detect duplicates
        self.content_hashes = set()
    
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
    
    def validate_content(self, texts, veda_name, source_id):
        """Validate that content matches expected Veda"""
        veda_lower = veda_name.lower()
        
        if veda_lower not in self.veda_markers:
            self.logger.warning(f"No validation rules for {veda_name}")
            return True, "No validation rules"
        
        markers = self.veda_markers[veda_lower]
        
        # Sample texts for validation
        sample_size = min(20, len(texts))
        sample_texts = texts[:sample_size]
        
        # Check location patterns
        location_matches = 0
        content_matches = 0
        reject_matches = 0
        
        for text in sample_texts:
            location = text.get('location', [])
            content = text.get('vaakya_text', '')
            
            # Convert location to string for checking
            location_str = ' '.join(str(l) for l in location if l)
            
            # Check for expected markers
            for marker in markers['location']:
                if marker in location_str:
                    location_matches += 1
                    break
            
            for marker in markers['content']:
                if marker in content:
                    content_matches += 1
                    break
            
            # Check for rejected markers
            for marker in markers['reject']:
                if marker in location_str or marker in content:
                    reject_matches += 1
                    break
        
        # Calculate content hash to detect duplicates
        content_sample = ''.join(t.get('vaakya_text', '')[:50] for t in sample_texts[:5])
        content_hash = hashlib.md5(content_sample.encode()).hexdigest()
        
        # Validation logic
        location_percent = (location_matches / sample_size) * 100 if sample_size > 0 else 0
        content_percent = (content_matches / sample_size) * 100 if sample_size > 0 else 0
        reject_percent = (reject_matches / sample_size) * 100 if sample_size > 0 else 0
        
        # Log validation results
        self.logger.info(f"  Validation for {veda_name} ({source_id}):")
        self.logger.info(f"    Location markers: {location_percent:.1f}% match")
        self.logger.info(f"    Content markers: {content_percent:.1f}% match")
        self.logger.info(f"    Rejected markers: {reject_percent:.1f}% found")
        self.logger.info(f"    Content hash: {content_hash[:8]}")
        
        # Check for duplicate content
        if content_hash in self.content_hashes:
            self.logger.error(f"    ❌ DUPLICATE CONTENT DETECTED!")
            return False, "Duplicate content"
        
        self.content_hashes.add(content_hash)
        
        # Determine if valid
        is_valid = True
        reason = ""
        
        # For Sāmaveda, be more lenient since it contains Rigvedic verses
        if veda_lower == 'samaveda':
            if location_percent < 50 and content_percent < 10:
                is_valid = False
                reason = f"Too few Sāmaveda markers (loc: {location_percent}%, content: {content_percent}%)"
        else:
            # For other Vedas, be stricter
            if location_percent < 70:
                is_valid = False
                reason = f"Too few location markers ({location_percent}%)"
            elif reject_percent > 20:
                is_valid = False
                reason = f"Too many rejected markers ({reject_percent}%)"
        
        if is_valid:
            self.logger.info(f"    ✅ Content validated for {veda_name}")
        else:
            self.logger.error(f"    ❌ VALIDATION FAILED: {reason}")
        
        return is_valid, reason
    
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
        """Download a single source with validation"""
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
        
        # Get initial data for validation
        initial_data = self.get_texts_ajax(source_id, start=0, length=20, draw=1)
        if not initial_data or initial_data.get('recordsTotal', 0) == 0:
            self.logger.warning(f"  No data for {source_id}")
            progress['failed'].append(source_id)
            return False
        
        total_records = initial_data['recordsTotal']
        self.logger.info(f"  Total records: {total_records}")
        
        # Validate initial sample
        sample_texts = initial_data.get('data', [])
        is_valid, validation_reason = self.validate_content(sample_texts, veda_name, source_id)
        
        if not is_valid:
            self.logger.error(f"  ❌ STOPPING DOWNLOAD: {validation_reason}")
            progress['failed'].append(source_id)
            
            # Save validation failure report
            failure_dir = self.download_dir / 'validation_failures'
            failure_dir.mkdir(exist_ok=True)
            failure_file = failure_dir / f"{source_id}_failure.json"
            
            with open(failure_file, 'w') as f:
                json.dump({
                    'source_id': source_id,
                    'veda': veda_name,
                    'shakha': source_shakha,
                    'text_type': source_text,
                    'failure_reason': validation_reason,
                    'sample_texts': sample_texts,
                    'timestamp': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            return False
        
        # If validation passed, download all data
        all_texts = list(sample_texts)  # Start with validated sample
        start = len(sample_texts)
        draw = 2
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
            
            # Periodic validation during download
            if len(all_texts) % 5000 == 0:
                recent_texts = texts[:10]
                is_still_valid, _ = self.validate_content(recent_texts, veda_name, source_id)
                if not is_still_valid:
                    self.logger.error(f"  ❌ Validation failed during download at {len(all_texts)} texts")
                    progress['failed'].append(source_id)
                    return False
            
            if len(all_texts) % 1000 == 0 or start >= total_records:
                progress_pct = round(start / total_records * 100, 1)
                self.logger.info(f"  Progress: {start}/{total_records} ({progress_pct}%)")
            
            time.sleep(0.1)
        
        if all_texts and len(all_texts) >= total_records * 0.9:
            # Final validation
            final_sample = all_texts[-20:]
            is_final_valid, _ = self.validate_content(final_sample, veda_name, source_id)
            
            if not is_final_valid:
                self.logger.error(f"  ❌ Final validation failed")
                progress['failed'].append(source_id)
                return False
            
            # Calculate accent percentage
            accent_count = sum(1 for text in all_texts[:100] 
                             if 'vaakya_text' in text and any(m in text['vaakya_text'] for m in ['॒', '॑', '।', '॥']))
            accent_pct = round(accent_count / min(100, len(all_texts)) * 100, 1)
            
            # Save validated data
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
                    'validation_passed': True,
                    'downloaded_at': datetime.now().isoformat()
                },
                'texts': all_texts
            }
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            file_size_mb = save_path.stat().st_size / (1024 * 1024)
            self.logger.info(f"  ✅ Saved {len(all_texts)} texts ({file_size_mb:.1f}MB, {accent_pct}% accents)")
            self.logger.info(f"  ✅ Content validation PASSED")
            
            progress['completed'].append(source_id)
            return True
        else:
            self.logger.error(f"  Download incomplete: {len(all_texts)}/{total_records}")
            progress['failed'].append(source_id)
            return False
    
    def run_continuous(self):
        """Run continuous download with validation"""
        self.logger.info("Starting VALIDATED continuous Vedanidhi download")
        self.logger.info(f"Total sources: {len(self.sources)}")
        self.logger.info("Validation enabled at each step")
        
        while True:
            progress = self.load_progress()
            start_index = progress['last_index']
            
            if start_index >= len(self.sources):
                self.logger.info("🎉 ALL DOWNLOADS COMPLETE!")
                break
            
            self.logger.info(f"\nProgress: {len(progress['completed'])}/{len(self.sources)} completed, {len(progress['failed'])} failed")
            self.logger.info(f"Continuing from index {start_index}")
            
            # Download next batch
            batch_size = 3  # Smaller batches for better validation
            for i in range(start_index, min(start_index + batch_size, len(self.sources))):
                source = self.sources[i]
                
                try:
                    success = self.download_source(source, i, progress)
                    progress['last_index'] = i + 1
                    self.save_progress(progress)
                    
                    if not success:
                        self.logger.warning(f"  ⚠️  Failed - check validation_failures directory")
                    
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
        progress = self.load_progress()
        
        summary = {
            'completed_at': datetime.now().isoformat(),
            'total_sources': len(self.sources),
            'completed': len(progress['completed']),
            'failed': len(progress['failed']),
            'validation_enabled': True,
            'unique_content_hashes': len(self.content_hashes)
        }
        
        with open(self.download_dir / 'validated_download_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.logger.info(f"\n📊 Final Summary:")
        self.logger.info(f"   Completed: {summary['completed']}/{summary['total_sources']}")
        self.logger.info(f"   Failed: {summary['failed']}")
        self.logger.info(f"   Unique content patterns: {summary['unique_content_hashes']}")

def main():
    downloader = ValidatedContinuousDownloader()
    downloader.run_continuous()

if __name__ == "__main__":
    main()