#!/usr/bin/env python3
"""Debug translation and alignment issues"""

import requests
import json

def test_translations_and_alignments():
    url = 'http://127.0.0.1:8000/api/v1/dictionary/analyze/verse/openai'
    verse = "In princīpio creāvit Deus cælum, et terram."
    
    # Test different languages
    languages = ['en', 'es', 'fr']
    
    for lang in languages:
        print(f"\n=== TESTING LANGUAGE: {lang.upper()} ===")
        
        data = {
            'verse': verse,
            'reference': 'Gn 1:1',
            'analysis_language': lang,
            'include_translations': True
        }
        
        try:
            response = requests.post(url, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                
                # Check translations
                translations = result.get('translations', {})
                print(f"Available languages: {list(translations.keys())}")
                print(f"Translation for {lang}: {translations.get(lang, 'NOT FOUND')}")
                
                # Check word alignments for cælum (word 4)
                wa = result.get('word_alignments', {})
                literal_array = wa.get('literal', [])
                dynamic_array = wa.get('dynamic', [])
                
                if len(literal_array) > 4:
                    print(f"Word 4 (cælum) literal: {literal_array[4]}")
                if len(dynamic_array) > 4:
                    print(f"Word 4 (cælum) dynamic: {dynamic_array[4]}")
                
                # Show all word alignments for this language
                print(f"\nAll word alignments for {lang}:")
                source_words = verse.replace(',', '').replace('.', '').split()
                for i, word in enumerate(source_words):
                    if i < len(literal_array):
                        lit_align = literal_array[i]
                        dyn_align = dynamic_array[i] if i < len(dynamic_array) else {}
                        print(f"  {i}: {word} -> Lit: {lit_align.get('target_words', [])} | Dyn: {dyn_align.get('target_words', [])}")
                
            else:
                print(f"Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    test_translations_and_alignments() 