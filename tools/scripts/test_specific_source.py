#!/usr/bin/env python3
"""
Test specific source IDs to verify we get correct śākhā content
"""

import requests
import json
import time

def test_source(source_id, expected_veda, description):
    """Test a specific source ID"""
    print(f"\nTesting {description} ({source_id})")
    print(f"Expected: {expected_veda}")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://vaakya.vedanidhi.in/vedanidhi/browsedata/'
    })
    
    session.cookies.set('csrftoken', 'ROqhEXwodGWEmb5w3TZR6NjQUToZOZSlMjjpEjztXP3gHEssqNQVNbXEczGJRsYV')
    session.cookies.set('sessionid', 'o6nnni9emasigbnscvrqx7cfjrp26rl2')
    
    url = "https://vaakya.vedanidhi.in/browse_search_data_ajax/"
    
    params = {
        'value': source_id,
        'search_value': '',
        'draw': '1',
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
        'start': '0',
        'length': '5',
        'search[value]': '',
        'search[regex]': 'false',
        '_': str(int(time.time() * 1000))
    }
    
    try:
        response = session.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'data' in data and data['data']:
            texts = data['data']
            print(f"Total records: {data.get('recordsTotal', 0)}")
            print(f"Sample texts:")
            
            for i, text in enumerate(texts[:3]):
                location = text.get('location', [])
                content = text.get('vaakya_text', '')
                print(f"  {i+1}. Location: {location}")
                print(f"     Content: {content[:100]}...")
                
                # Check for Veda markers
                if expected_veda == 'rigveda':
                    if 'ऋ' in str(location) or 'मण्डल' in content:
                        print(f"     ✅ Contains expected Rigveda markers")
                    else:
                        print(f"     ⚠️  Missing Rigveda markers")
                        
                elif expected_veda == 'samaveda':
                    if 'साम' in content or 'गान' in content or 'आर्चिक' in content:
                        print(f"     ✅ Contains expected Sāmaveda markers")
                    else:
                        print(f"     ⚠️  Missing Sāmaveda markers")
                        
                elif expected_veda == 'atharvaveda':
                    if 'अथर्व' in content or 'काण्ड' in str(location):
                        print(f"     ✅ Contains expected Atharvaveda markers")
                    else:
                        print(f"     ⚠️  Missing Atharvaveda markers")
        else:
            print("No data returned")
            
    except Exception as e:
        print(f"Error: {e}")

def main():
    print("Testing specific source IDs to verify śākhā content")
    print("=" * 60)
    
    # Test known sources from our exploration
    test_cases = [
        ('010101', 'rigveda', 'Rigveda Śākala Saṃhitā'),
        ('030301', 'samaveda', 'Sāmaveda Kauthuma Ārchika'),
        ('040101', 'atharvaveda', 'Atharvaveda Śaunaka Saṃhitā'),
        ('020401', 'yajurveda', 'Yajurveda Taittirīya Saṃhitā')
    ]
    
    for source_id, expected_veda, description in test_cases:
        test_source(source_id, expected_veda, description)
        time.sleep(1)

if __name__ == "__main__":
    main()