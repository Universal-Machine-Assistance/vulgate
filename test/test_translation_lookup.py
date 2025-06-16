#!/usr/bin/env python3
"""Test the new translation word lookup endpoint"""

import requests
import json

def test_translation_lookup():
    print("=== TESTING TRANSLATION WORD LOOKUP ===")
    
    url = 'http://127.0.0.1:8000/api/v1/dictionary/lookup/translation'
    
    # Test the Portuguese word that's causing issues
    test_word = {
        'word': 'escuridão',
        'language': 'pt'
    }
    
    print(f"1. Testing Portuguese word: {test_word['word']}")
    
    try:
        response = requests.post(url, json=test_word, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ API call successful!")
            print(f"   Word: {result.get('word')}")
            print(f"   Language: {result.get('language')}")
            print(f"   Found: {result.get('found')}")
            print(f"   Definition: {result.get('definition', 'N/A')}")
            print(f"   Part of Speech: {result.get('partOfSpeech', 'N/A')}")
            print(f"   Etymology: {result.get('etymology', 'N/A')}")
            print(f"   Source: {result.get('source', 'N/A')}")
            print(f"   Confidence: {result.get('confidence', 'N/A')}")
            
            if 'examples' in result and result['examples']:
                print(f"   Examples: {result['examples']}")
            
            if 'note' in result:
                print(f"   Note: {result['note']}")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test second call to see if it's cached
    print("\n2. Testing cache (second call)...")
    try:
        response = requests.post(url, json=test_word, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Cached result: {result.get('source', 'N/A')}")
            print(f"   Definition: {result.get('definition', 'N/A')[:50]}...")
        else:
            print(f"❌ Cache test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Cache test failed: {e}")

if __name__ == "__main__":
    test_translation_lookup() 