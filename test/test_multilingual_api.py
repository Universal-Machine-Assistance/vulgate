#!/usr/bin/env python3
"""Test the enhanced multilingual API"""

import requests
import json

def test_multilingual_api():
    url = 'http://127.0.0.1:8000/api/v1/dictionary/analyze/verse/openai'
    
    # Test with all_languages parameter
    data = {
        'verse': 'In princīpio creāvit Deus cælum, et terram.',
        'reference': 'Gn 1:1',
        'analysis_language': 'es',
        'include_translations': True,
        'all_languages': True
    }
    
    print("=== TESTING MULTILINGUAL API ===")
    print(f"Request: {json.dumps(data, indent=2)}")
    print()
    
    try:
        response = requests.post(url, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            translations = result.get('translations', {})
            
            print('📝 Number of languages:', len(translations))
            print('📝 Translation keys:', list(translations.keys()))
            print()
            print('📝 Available translations:')
            for lang, trans in translations.items():
                print(f'  {lang}: {trans[:60]}...')
            
            # Check if we have the expected languages
            expected_languages = ["en", "es", "fr", "it", "pt", "de"]
            found_languages = list(translations.keys())
            
            print()
            print("=== LANGUAGE COVERAGE ===")
            for lang in expected_languages:
                status = "✅" if lang in found_languages else "❌"
                print(f"{status} {lang}")
            
            if len(found_languages) > 2:
                print("\n🎉 SUCCESS: Multiple languages returned!")
            else:
                print(f"\n🔄 Backend appears to only support {len(found_languages)} language(s)")
                
        else:
            print(f'❌ API Error: {response.status_code} - {response.text}')
            
    except Exception as e:
        print(f'❌ Request failed: {e}')

if __name__ == "__main__":
    test_multilingual_api() 