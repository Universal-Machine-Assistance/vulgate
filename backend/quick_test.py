#!/usr/bin/env python3
"""Quick test of multilingual parameters"""

import requests
import json

def quick_test():
    url = 'http://127.0.0.1:8000/api/v1/dictionary/analyze/verse/openai'
    
    # Test with just 2 languages to avoid timeout
    data = {
        'verse': 'In princīpio creāvit Deus cælum, et terram.',
        'reference': 'Gn 1:1',
        'analysis_language': 'es',
        'include_translations': True,
        'languages': ['en', 'es'],  # Just 2 languages
        'multilingual': True
    }
    
    print("Testing with 2 languages...")
    
    try:
        response = requests.post(url, json=data, timeout=15)
        if response.status_code == 200:
            result = response.json()
            translations = result.get('translations', {})
            
            print(f'✅ Success! Languages: {list(translations.keys())}')
            print(f'📝 Number of languages: {len(translations)}')
            
            if len(translations) >= 2:
                print("🎉 Multiple languages working!")
            else:
                print("🔄 Still only single language")
                
        else:
            print(f'❌ Error: {response.status_code}')
            
    except Exception as e:
        print(f'❌ Failed: {e}')

if __name__ == "__main__":
    quick_test() 