#!/usr/bin/env python3
"""Test script to identify API issues"""

import requests
import json

def test_api_issues():
    print("=== TESTING API ISSUES ===")
    
    url = 'http://127.0.0.1:8000/api/v1/dictionary/analyze/verse/openai'
    
    # Test data
    test_data = {
        'verse': 'In princīpio creāvit Deus cælum, et terram.',
        'reference': 'Gn 1:1',
        'analysis_language': 'en',
        'include_translations': True,
        'languages': ['en', 'es'],
        'multilingual': True
    }
    
    print("1. Making API request...")
    print(f"   Request: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            print("2. Checking response structure...")
            print(f"   ✅ Success: {result.get('success', False)}")
            print(f"   ✅ Has translations: {'translations' in result}")
            print(f"   ✅ Has word_alignments: {'word_alignments' in result}")
            print(f"   ✅ Has literal_translation: {'literal_translation' in result}")
            print(f"   ✅ Has dynamic_translation: {'dynamic_translation' in result}")
            
            if 'translations' in result:
                translations = result['translations']
                print(f"   📝 Translation languages: {list(translations.keys())}")
                for lang, trans in translations.items():
                    print(f"      {lang}: {trans[:50]}...")
            
            if 'word_alignments' in result:
                wa = result['word_alignments']
                print(f"   🔗 Word alignments type: {type(wa)}")
                if isinstance(wa, dict):
                    print(f"      Keys: {list(wa.keys())}")
                    if 'literal' in wa:
                        print(f"      Literal alignments count: {len(wa['literal'])}")
                        if wa['literal']:
                            print(f"      First alignment: {wa['literal'][0]}")
            
            if 'literal_translation' in result:
                print(f"   📖 Literal: {result['literal_translation'][:50]}...")
            
            if 'dynamic_translation' in result:
                print(f"   📖 Dynamic: {result['dynamic_translation'][:50]}...")
            
            # Check for errors
            if 'word_alignments_error' in result:
                print(f"   ❌ Word alignment error: {result['word_alignments_error']}")
            
        else:
            print(f"   ❌ API Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")

if __name__ == "__main__":
    test_api_issues() 