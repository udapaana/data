#!/usr/bin/env python3
"""
Explore the full Vedanidhi hierarchy to list all available sources
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime

class VedanidhiExplorer:
    def __init__(self):
        self.base_url = "https://vaakya.vedanidhi.in"
        self.output_dir = Path("data/vedanidhi_exploration")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Session with cookies
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest'
        })
        
        # Set cookies
        self.session.cookies.set('csrftoken', 'ROqhEXwodGWEmb5w3TZR6NjQUToZOZSlMjjpEjztXP3gHEssqNQVNbXEczGJRsYV')
        self.session.cookies.set('sessionid', 'o6nnni9emasigbnscvrqx7cfjrp26rl2')
        
        self.hierarchy = {}
    
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
            print(f"Error fetching level {level}, value {value}: {e}")
            return []
    
    def check_data_exists(self, value):
        """Quick check if data exists for a value"""
        url = f"{self.base_url}/browse_search_data_ajax/"
        params = {
            'value': value,
            'draw': '1',
            'start': '0',
            'length': '1',
            'columns[0][data]': 'location',
            'columns[1][data]': 'vaakya_text',
            '_': str(int(time.time() * 1000))
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('recordsTotal', 0) > 0
        except:
            pass
        return False
    
    def explore_all(self):
        """Explore the entire hierarchy"""
        print("Exploring Vedanidhi hierarchy...")
        print("=" * 80)
        
        # Level 1: Vedas
        vedas = [
            {'id': '01', 'name': 'Rigveda'},
            {'id': '02', 'name': 'Yajurveda'},
            {'id': '03', 'name': 'Samaveda'},
            {'id': '04', 'name': 'Atharvaveda'}
        ]
        
        full_hierarchy = []
        
        for veda in vedas:
            print(f"\n{veda['name']} ({veda['id']})")
            print("-" * 40)
            
            veda_data = {
                'id': veda['id'],
                'name': veda['name'],
                'shakhas': []
            }
            
            # Level 2: Śākhās
            shakhas = self.get_browse_data(1, veda['id'])
            
            for shakha in shakhas:
                shakha_id = shakha['id']
                shakha_name = shakha['value'].strip()
                print(f"  {shakha_name} ({shakha_id})")
                
                shakha_data = {
                    'id': shakha_id,
                    'name': shakha_name,
                    'texts': []
                }
                
                # Level 3: Text types
                text_types = self.get_browse_data(2, shakha_id)
                
                for text_type in text_types:
                    text_id = text_type['id']
                    text_name = text_type['value'].strip()
                    
                    # Check if data exists
                    has_data = self.check_data_exists(text_id)
                    status = "✓" if has_data else "✗"
                    
                    print(f"    {status} {text_name} ({text_id})")
                    
                    text_data = {
                        'id': text_id,
                        'name': text_name,
                        'has_data': has_data
                    }
                    
                    # Check for sub-levels (some texts have further divisions)
                    sub_items = self.get_browse_data(3, text_id)
                    if sub_items:
                        text_data['sub_items'] = []
                        for sub_item in sub_items:
                            sub_id = sub_item['id']
                            sub_name = sub_item['value'].strip()
                            sub_has_data = self.check_data_exists(sub_id)
                            sub_status = "✓" if sub_has_data else "✗"
                            
                            print(f"      {sub_status} {sub_name} ({sub_id})")
                            
                            text_data['sub_items'].append({
                                'id': sub_id,
                                'name': sub_name,
                                'has_data': sub_has_data
                            })
                    
                    shakha_data['texts'].append(text_data)
                    time.sleep(0.2)  # Be respectful
                
                veda_data['shakhas'].append(shakha_data)
                time.sleep(0.5)
            
            full_hierarchy.append(veda_data)
        
        # Save the complete hierarchy
        output_file = self.output_dir / 'vedanidhi_complete_hierarchy.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'explored_at': datetime.now().isoformat(),
                'source': 'vedanidhi',
                'hierarchy': full_hierarchy
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'=' * 80}")
        print(f"Complete hierarchy saved to: {output_file}")
        
        # Generate summary
        self.generate_summary(full_hierarchy)
    
    def generate_summary(self, hierarchy):
        """Generate a summary of available texts"""
        summary = []
        total_with_data = 0
        total_without_data = 0
        
        print("\n\nSUMMARY OF AVAILABLE TEXTS")
        print("=" * 80)
        
        for veda in hierarchy:
            print(f"\n{veda['name']}")
            veda_summary = {'veda': veda['name'], 'sources': []}
            
            for shakha in veda['shakhas']:
                for text in shakha['texts']:
                    if text['has_data']:
                        entry = f"{shakha['name']} - {text['name']} ({text['id']})"
                        print(f"  ✓ {entry}")
                        veda_summary['sources'].append({
                            'shakha': shakha['name'],
                            'text': text['name'],
                            'id': text['id'],
                            'has_data': True
                        })
                        total_with_data += 1
                    else:
                        total_without_data += 1
                    
                    # Check sub-items
                    if 'sub_items' in text:
                        for sub in text['sub_items']:
                            if sub['has_data']:
                                entry = f"{shakha['name']} - {text['name']} - {sub['name']} ({sub['id']})"
                                print(f"    ✓ {entry}")
                                veda_summary['sources'].append({
                                    'shakha': shakha['name'],
                                    'text': f"{text['name']} - {sub['name']}",
                                    'id': sub['id'],
                                    'has_data': True
                                })
                                total_with_data += 1
                            else:
                                total_without_data += 1
            
            summary.append(veda_summary)
        
        print(f"\n{'=' * 80}")
        print(f"Total sources with data: {total_with_data}")
        print(f"Total sources without data: {total_without_data}")
        
        # Save summary
        summary_file = self.output_dir / 'vedanidhi_sources_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump({
                'generated_at': datetime.now().isoformat(),
                'total_with_data': total_with_data,
                'total_without_data': total_without_data,
                'sources_by_veda': summary
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\nSummary saved to: {summary_file}")

def main():
    explorer = VedanidhiExplorer()
    explorer.explore_all()

if __name__ == "__main__":
    main()