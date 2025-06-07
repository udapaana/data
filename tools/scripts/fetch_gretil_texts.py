#!/usr/bin/env python3
"""
Fetch Vedic texts from GRETIL with proper academic annotation
"""

import requests
import re
import json
from pathlib import Path
from datetime import datetime
import time

class GRETILFetcher:
    def __init__(self):
        self.base_url = "http://gretil.sub.uni-goettingen.de/"
        self.output_dir = Path("data/academic_sources/gretil")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Known GRETIL Vedic text URLs
        self.vedic_texts = {
            "rigveda": {
                "sakala_samhita": {
                    "url": "gretil/corpustei/sa_Rgveda-edAufrecht.xml",
                    "description": "Rigveda Śākala Saṃhitā (Aufrecht edition)",
                    "format": "xml",
                    "modifications": ["critical_edition", "normalized_sandhi"]
                },
                "padapatha": {
                    "url": "gretil/corpustei/sa_RgvedasaMhitApadapATha.xml",
                    "description": "Rigveda Padapāṭha",
                    "format": "xml", 
                    "modifications": ["word_separation"]
                }
            },
            "atharvaveda": {
                "saunaka_unaccented": {
                    "url": "gretil/1_sanskr/1_veda/1_sam/avs___u.htm",
                    "description": "Atharvaveda Śaunaka (unaccented)",
                    "format": "htm",
                    "modifications": ["critical_edition", "accents_removed"]
                },
                "saunaka_accented": {
                    "url": "gretil/1_sanskr/1_veda/1_sam/avs_acu.htm",
                    "description": "Atharvaveda Śaunaka (accented)",
                    "format": "htm",
                    "modifications": ["critical_edition", "vedic_accents"]
                }
            }
        }
    
    def fetch_text(self, veda, shakha, info):
        """Fetch a single text from GRETIL"""
        print(f"\nFetching {info['description']}...")
        
        url = self.base_url + info['url']
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Save raw HTML
            raw_dir = self.output_dir / veda / shakha / "raw"
            raw_dir.mkdir(parents=True, exist_ok=True)
            
            file_ext = 'xml' if info['format'] == 'xml' else 'html'
            raw_file = raw_dir / f"{shakha}_gretil.{file_ext}"
            with open(raw_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(f"  Saved raw HTML to {raw_file}")
            
            # Parse the HTML to extract text
            parsed_data = self.parse_gretil_html(response.text, veda, shakha, info)
            
            # Save parsed data with metadata
            parsed_dir = self.output_dir / veda / shakha / "parsed"
            parsed_dir.mkdir(parents=True, exist_ok=True)
            
            parsed_file = parsed_dir / f"{shakha}_parsed.json"
            
            metadata = {
                "source": {
                    "name": "GRETIL",
                    "url": url,
                    "fetched_at": datetime.now().isoformat(),
                    "type": "academic",
                    "modifications": info['modifications'],
                    "suitable_for": ["research", "comparison"],
                    "adhyayana_suitable": False,
                    "notes": "Academic critical edition with editorial modifications"
                },
                "text_info": info,
                "statistics": {
                    "total_verses": len(parsed_data)
                },
                "data": parsed_data
            }
            
            with open(parsed_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            print(f"  Parsed {len(parsed_data)} verses/sections")
            print(f"  Saved to {parsed_file}")
            
            return True
            
        except requests.RequestException as e:
            print(f"  ERROR fetching: {e}")
            return False
        except Exception as e:
            print(f"  ERROR parsing: {e}")
            return False
    
    def parse_gretil_html(self, html_content, veda, shakha, info):
        """Parse GRETIL HTML format to extract structured text"""
        parsed_data = []
        
        # Remove HTML tags but preserve structure markers
        # GRETIL uses specific patterns for verse numbers
        
        # Basic HTML cleanup
        text = re.sub(r'<[^>]+>', '', html_content)
        
        # Split into lines
        lines = text.strip().split('\n')
        
        current_section = None
        current_verse = None
        verse_text = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for verse markers (e.g., "1.1.1", "01.001.01", etc.)
            verse_match = re.match(r'^(\d+\.[\d.]+)\s*(.*)', line)
            if verse_match:
                # Save previous verse if exists
                if current_verse and verse_text:
                    parsed_data.append({
                        "id": current_verse,
                        "text": ' '.join(verse_text),
                        "veda": veda,
                        "shakha": shakha
                    })
                
                # Start new verse
                current_verse = verse_match.group(1)
                remainder = verse_match.group(2).strip()
                verse_text = [remainder] if remainder else []
            else:
                # Continue current verse
                if current_verse:
                    verse_text.append(line)
        
        # Save last verse
        if current_verse and verse_text:
            parsed_data.append({
                "id": current_verse,
                "text": ' '.join(verse_text),
                "veda": veda,
                "shakha": shakha
            })
        
        return parsed_data
    
    def fetch_all(self):
        """Fetch all configured Vedic texts from GRETIL"""
        print("Starting GRETIL Vedic text collection...")
        print("=" * 50)
        
        total_fetched = 0
        
        for veda, shakhas in self.vedic_texts.items():
            for shakha, info in shakhas.items():
                if self.fetch_text(veda, shakha, info):
                    total_fetched += 1
                    # Be respectful - wait between requests
                    time.sleep(2)
        
        print("\n" + "=" * 50)
        print(f"Total texts fetched: {total_fetched}")
        
        # Create summary
        summary = {
            "source": "GRETIL",
            "fetched_at": datetime.now().isoformat(),
            "total_texts": total_fetched,
            "texts": self.vedic_texts,
            "notes": [
                "Academic critical editions",
                "May contain metric restoration",
                "Suitable for research, not traditional recitation",
                "Requires annotation when used in adhyayana context"
            ]
        }
        
        summary_file = self.output_dir / "gretil_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"\nSummary saved to {summary_file}")

def main():
    fetcher = GRETILFetcher()
    fetcher.fetch_all()

if __name__ == "__main__":
    main()