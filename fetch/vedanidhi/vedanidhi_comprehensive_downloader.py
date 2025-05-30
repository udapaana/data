#!/usr/bin/env python3
"""
Comprehensive Vedanidhi Downloader
- Fetches ALL available data from Vedanidhi
- Validates to ensure we're getting the right content
- Saves raw data for later organization
"""

import requests
import json
import os
import time
import logging
from datetime import datetime
from pathlib import Path
import hashlib

class VedanidhiDownloader:
    def __init__(self):
        self.base_url = "https://vaakya.vedanidhi.in/vedanidhi/getVakyaList"
        self.session = requests.Session()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
        self.download_dir = Path("data/vedanidhi_raw_v2")
        self.log_file = self.download_dir / "download_log.json"
        self.validation_log = self.download_dir / "validation_log.json"
        self.download_log = []
        self.validation_issues = []
        
        # Known Veda codes
        self.veda_codes = {
            "01": "rigveda",
            "02": "yajurveda", 
            "03": "samaveda",
            "04": "atharvaveda"
        }
        
        # Known structure patterns (for validation)
        self.expected_patterns = {
            "rigveda": ["ऋ", "अष्ट", "अध्या", "सू"],
            "yajurveda_krishna": ["यजु", "काण्ड", "प्र", "अनु"],
            "yajurveda_shukla": ["यजु", "अध्या"],
            "samaveda": ["साम", "आर्चिक", "गान"],
            "atharvaveda": ["अथर्व", "काण्ड", "सू"]
        }
        
    def setup_directories(self):
        """Create directory structure"""
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
    def get_hierarchy_info(self):
        """First, let's discover what's actually available"""
        print("Discovering Vedanidhi hierarchy...")
        
        hierarchy = {}
        
        # Level 1: Vedas
        for veda_code, veda_name in self.veda_codes.items():
            print(f"\nExploring {veda_name} ({veda_code})...")
            
            # Get shakhas for this Veda
            shakhas = self.get_options(level=2, parent_value=veda_code)
            
            if not shakhas:
                print(f"  No shakhas found for {veda_name}")
                continue
                
            hierarchy[veda_code] = {
                "name": veda_name,
                "shakhas": {}
            }
            
            for shakha in shakhas:
                shakha_code = shakha["id"]
                shakha_name = shakha["value"].strip()
                print(f"  Found shakha: {shakha_name} ({shakha_code})")
                
                # Get text types for this shakha
                text_types = self.get_options(level=3, parent_value=shakha_code)
                
                hierarchy[veda_code]["shakhas"][shakha_code] = {
                    "name": shakha_name,
                    "text_types": {}
                }
                
                for text_type in text_types:
                    text_code = text_type["id"]
                    text_name = text_type["value"].strip()
                    print(f"    Text type: {text_name} ({text_code})")
                    
                    hierarchy[veda_code]["shakhas"][shakha_code]["text_types"][text_code] = text_name
        
        # Save hierarchy
        hierarchy_file = self.download_dir / "vedanidhi_hierarchy.json"
        with open(hierarchy_file, 'w', encoding='utf-8') as f:
            json.dump(hierarchy, f, ensure_ascii=False, indent=2)
        
        print(f"\nHierarchy saved to {hierarchy_file}")
        return hierarchy
        
    def get_options(self, level, parent_value):
        """Get options for a given hierarchy level"""
        try:
            url = f"https://vaakya.vedanidhi.in/vedanidhi/browse.htm"
            params = {
                "id": level,
                "value": parent_value
            }
            
            response = self.session.get(url, params=params)
            
            # This returns HTML, we need to parse it
            # For now, returning empty - we'll need to implement HTML parsing
            # or find the actual API endpoint
            return []
            
        except Exception as e:
            print(f"Error getting options: {e}")
            return []
    
    def fetch_texts(self, veda_code, shakha_code, text_type_code, start=0, length=1000):
        """Fetch texts for a specific combination"""
        try:
            params = {
                "draw": 1,
                "start": start,
                "length": length,
                "id_": f"{veda_code}{shakha_code}{text_type_code}"
            }
            
            response = self.session.post(self.base_url, data=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error fetching texts: {e}")
            return None
    
    def validate_response(self, data, veda_code, shakha_code, text_type_code):
        """Validate that we got the right data"""
        if not data or "data" not in data or not data["data"]:
            return False, "Empty response"
        
        # Check first few items
        sample_items = data["data"][:5]
        
        for item in sample_items:
            if "location" not in item:
                return False, "No location array"
            
            location = item["location"]
            if not location:
                return False, "Empty location array"
            
            # Check Veda code
            first_element = location[0]
            
            # Rigveda check
            if veda_code == "01" and "ऋ" not in first_element:
                return False, f"Expected Rigveda marker, got {first_element}"
            
            # Non-Rigveda check - should NOT have Rigveda marker
            if veda_code != "01" and "ऋ" in first_element:
                return False, f"Got Rigveda data for Veda code {veda_code}"
            
            # More specific checks based on Veda
            if veda_code == "02" and "यजु" not in str(location):
                return False, "Expected Yajurveda markers"
            
            if veda_code == "03" and "साम" not in str(location):
                return False, "Expected Samaveda markers"
                
            if veda_code == "04" and "अथर्व" not in str(location):
                return False, "Expected Atharvaveda markers"
        
        return True, "Validation passed"
    
    def save_batch(self, data, veda_name, shakha_name, text_type, batch_num):
        """Save a batch of data"""
        # Create directory structure
        save_dir = self.download_dir / veda_name / shakha_name / text_type
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Save with batch number
        filename = f"batch_{batch_num:04d}.json"
        filepath = save_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def fetch_texts(self, veda_code, shakha_code, text_code, filter_mode="samhita", start=0, length=-1):
        """Fetch texts from Vedanidhi API"""
        try:
            # Prepare the request
            url = "https://vaakya.vedanidhi.in/browse_search_data_ajax/"
            
            # DataTables-style request data
            data = {
                "draw": "1",
                "columns[0][data]": "0",
                "columns[0][name]": "",
                "columns[0][searchable]": "true",
                "columns[0][orderable]": "true",
                "columns[0][search][value]": "",
                "columns[0][search][regex]": "false",
                "columns[1][data]": "1",
                "columns[1][name]": "",
                "columns[1][searchable]": "true",
                "columns[1][orderable]": "true",
                "columns[1][search][value]": "",
                "columns[1][search][regex]": "false",
                "columns[2][data]": "2",
                "columns[2][name]": "",
                "columns[2][searchable]": "true",
                "columns[2][orderable]": "true",
                "columns[2][search][value]": "",
                "columns[2][search][regex]": "false",
                "order[0][column]": "2",
                "order[0][dir]": "asc",
                "start": str(start),
                "length": str(length),
                "search[value]": "",
                "search[regex]": "false",
                "browse_id1": veda_code,
                "browse_id2": shakha_code,
                "browse_id3": text_code,
                "filter_mode": filter_mode,
                "csrfmiddlewaretoken": "ROqhEXwodGWEmb5w3TZR6NjQUToZOZSlMjjpEjztXP3gHEssqNQVNbXEczGJRsYV"
            }
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Cookie": "csrftoken=ROqhEXwodGWEmb5w3TZR6NjQUToZOZSlMjjpEjztXP3gHEssqNQVNbXEczGJRsYV; sessionid=o6nnni9emasigbnscvrqx7cfjrp26rl2",
                "X-CSRFToken": "ROqhEXwodGWEmb5w3TZR6NjQUToZOZSlMjjpEjztXP3gHEssqNQVNbXEczGJRsYV",
                "Referer": "https://vaakya.vedanidhi.in/vedanidhi/browsedata/"
            }
            
            self.logger.info(f"Making POST request to {url}")
            self.logger.info(f"Parameters: browse_id1={veda_code}, browse_id2={shakha_code}, browse_id3={text_code}, filter_mode={filter_mode}")
            
            response = requests.post(url, data=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse response: {e}")
            return None
    
    def download_all(self):
        """Main download function"""
        self.setup_directories()
        
        print("Starting comprehensive Vedanidhi download...")
        print("=" * 50)
        
        # First, discover what's available
        # For now, we'll use known codes
        test_targets = [
            # Rigveda
            ("01", "0101", "010101", "rigveda", "shakala", "samhita"),
            ("01", "0101", "010102", "rigveda", "shakala", "pada"),
            
            # Yajurveda - Krishna
            ("02", "0201", "020101", "yajurveda", "taittiriya", "samhita"),
            ("02", "0201", "020102", "yajurveda", "taittiriya", "pada"),
            ("02", "0203", "020301", "yajurveda", "maitrayani", "samhita"),
            
            # Yajurveda - Shukla  
            ("02", "0204", "020401", "yajurveda", "madhyandina", "samhita"),
            ("02", "0205", "020501", "yajurveda", "kanva", "samhita"),
            
            # Samaveda
            ("03", "0301", "030101", "samaveda", "kauthuma", "samhita"),
            ("03", "0302", "030201", "samaveda", "jaiminiya", "samhita"),
            
            # Atharvaveda
            ("04", "0401", "040101", "atharvaveda", "shaunaka", "samhita"),
            ("04", "0402", "040201", "atharvaveda", "paippalada", "samhita"),
        ]
        
        for veda_code, shakha_code, text_code, veda_name, shakha_name, text_type in test_targets:
            print(f"\nDownloading {veda_name} > {shakha_name} > {text_type}")
            print("-" * 40)
            
            batch_num = 0
            start = 0
            total_fetched = 0
            
            while True:
                print(f"  Fetching batch {batch_num + 1} (start: {start})...")
                
                # Fetch data
                data = self.fetch_texts(veda_code, shakha_code, text_code, start=start)
                
                if not data:
                    print("    No data received")
                    break
                
                # Validate
                is_valid, message = self.validate_response(data, veda_code, shakha_code, text_code)
                
                if not is_valid:
                    print(f"    VALIDATION FAILED: {message}")
                    self.validation_issues.append({
                        "target": f"{veda_name}/{shakha_name}/{text_type}",
                        "issue": message,
                        "timestamp": datetime.now().isoformat()
                    })
                    break
                
                # Check if we have data
                if "data" not in data or not data["data"]:
                    print("    No more data")
                    break
                
                # Save batch
                filepath = self.save_batch(data, veda_name, shakha_name, text_type, batch_num)
                print(f"    Saved {len(data['data'])} items to {filepath}")
                
                # Log
                self.download_log.append({
                    "veda": veda_name,
                    "shakha": shakha_name,
                    "text_type": text_type,
                    "batch": batch_num,
                    "count": len(data["data"]),
                    "file": str(filepath),
                    "timestamp": datetime.now().isoformat()
                })
                
                # Update counters
                total_fetched += len(data["data"])
                batch_num += 1
                start += len(data["data"])
                
                # Check if we've fetched all
                total_records = data.get("recordsTotal", 0)
                if start >= total_records:
                    print(f"    Fetched all {total_records} records")
                    break
                
                # Rate limiting
                time.sleep(2)
            
            print(f"  Total fetched: {total_fetched} items in {batch_num} batches")
            
            # Longer pause between different texts
            time.sleep(5)
        
        # Save logs
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.download_log, f, ensure_ascii=False, indent=2)
        
        with open(self.validation_log, 'w', encoding='utf-8') as f:
            json.dump(self.validation_issues, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 50)
        print("Download complete!")
        print(f"Downloaded: {len(self.download_log)} batches")
        print(f"Validation issues: {len(self.validation_issues)}")
        print(f"Logs saved to: {self.download_dir}")

def main():
    downloader = VedanidhiDownloader()
    downloader.download_all()

if __name__ == "__main__":
    main()