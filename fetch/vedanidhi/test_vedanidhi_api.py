#!/usr/bin/env python3
"""
Test Vedanidhi API with different request formats
"""

import requests
import json

# Test different endpoints and formats
def test_api():
    cookies = {
        'csrftoken': 'ROqhEXwodGWEmb5w3TZR6NjQUToZOZSlMjjpEjztXP3gHEssqNQVNbXEczGJRsYV',
        'sessionid': 'o6nnni9emasigbnscvrqx7cfjrp26rl2'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9',
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': 'ROqhEXwodGWEmb5w3TZR6NjQUToZOZSlMjjpEjztXP3gHEssqNQVNbXEczGJRsYV',
        'Referer': 'https://vaakya.vedanidhi.in/vedanidhi/browsedata/',
        'Origin': 'https://vaakya.vedanidhi.in'
    }
    
    # Test 1: Try the manage-vaakya endpoint
    print("Test 1: API manage-vaakya endpoint")
    url = "https://vaakya.vedanidhi.in/api/manage-vaakya/"
    
    data = {
        'draw': '1',
        'start': '0', 
        'length': '10',
        'browse_id1': '01',
        'browse_id2': '0101',
        'browse_id3': '010101',
        'filter_mode': 'samhita'
    }
    
    try:
        response = requests.post(url, data=data, headers=headers, cookies=cookies)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Try the browsedata endpoint with different params
    print("Test 2: browsedata endpoint")
    url = "https://vaakya.vedanidhi.in/browsedata/"
    
    params = {
        'lang': 'dv',
        'vedam': '01',
        'shakha': '0101', 
        'text': '010101'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, cookies=cookies)
        print(f"Status: {response.status_code}")
        print(f"Response length: {len(response.text)}")
        
        # Look for AJAX endpoints in the response
        if "ajax" in response.text.lower():
            import re
            ajax_urls = re.findall(r'url["\']?\s*:\s*["\']([^"\']+ajax[^"\']+)', response.text)
            print(f"Found AJAX URLs: {ajax_urls}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: Try the api/browse endpoint
    print("Test 3: API browse endpoint")
    url = "https://vaakya.vedanidhi.in/api/browse/"
    
    data = {
        'browse_id1': '01',
        'browse_id2': '0101',
        'browse_id3': '010101'
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, cookies=cookies)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()