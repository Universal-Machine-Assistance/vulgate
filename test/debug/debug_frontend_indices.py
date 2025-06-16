#!/usr/bin/env python3
"""Debug frontend target indices calculation"""

import requests
import json

def debug_target_indices():
    url = 'http://127.0.0.1:8000/api/v1/dictionary/analyze/verse/openai'
    
    data = {
        'verse': 'In princīpio creāvit Deus cælum, et terram.',
        'reference': 'Gn 1:1',
        'analysis_language': 'es',
        'include_translations': True
    }
    
    print("=== DEBUGGING TARGET INDICES ===")
    
    response = requests.post(url, json=data, timeout=30)
    if response.status_code == 200:
        result = response.json()
        
        # Get the translations
        translations = result.get('translations', {})
        spanish_translation = translations.get('es', '')
        english_translation = translations.get('en', '')
        
        print(f"Spanish translation: {spanish_translation}")
        print(f"English translation: {english_translation}")
        print()
        
        # Tokenize translations
        spanish_words = spanish_translation.split()
        english_words = english_translation.split()
        
        print(f"Spanish words ({len(spanish_words)}): {spanish_words}")
        print(f"English words ({len(english_words)}): {english_words}")
        print()
        
        # Show word alignments
        wa = result.get('word_alignments', {})
        literal_alignments = wa.get('literal', [])
        dynamic_alignments = wa.get('dynamic', [])
        
        source_words = data['verse'].replace(',', '').replace('.', '').split()
        
        print("=== WORD ALIGNMENT ANALYSIS ===")
        for i, word in enumerate(source_words):
            if i < len(literal_alignments):
                lit_align = literal_alignments[i]
                dyn_align = dynamic_alignments[i] if i < len(dynamic_alignments) else {}
                
                print(f"Word {i}: '{word}'")
                print(f"  Literal: target_words={lit_align.get('target_words', [])} | target_indices={lit_align.get('target_indices', [])}")
                print(f"  Dynamic: target_words={dyn_align.get('target_words', [])} | target_indices={dyn_align.get('target_indices', [])}")
                
                # Show what those indices point to
                lit_indices = lit_align.get('target_indices', [])
                dyn_indices = dyn_align.get('target_indices', [])
                
                if lit_indices:
                    lit_words = [spanish_words[idx] if idx < len(spanish_words) else f"OUT_OF_BOUNDS({idx})" for idx in lit_indices]
                    print(f"  Literal indices {lit_indices} → {lit_words}")
                
                if dyn_indices:
                    dyn_words = [spanish_words[idx] if idx < len(spanish_words) else f"OUT_OF_BOUNDS({idx})" for idx in dyn_indices]
                    print(f"  Dynamic indices {dyn_indices} → {dyn_words}")
                
                print()
        
        # Special focus on word 1 (princīpio)
        print("=== WORD 1 (princīpio) DETAILED ANALYSIS ===")
        if len(literal_alignments) > 1:
            word1_align = literal_alignments[1]
            target_indices = word1_align.get('target_indices', [])
            target_words = word1_align.get('target_words', [])
            
            print(f"Backend says: target_indices = {target_indices}")
            print(f"Backend says: target_words = {target_words}")
            print(f"Spanish translation: '{spanish_translation}'")
            print(f"Spanish words: {spanish_words}")
            
            if target_indices:
                for idx in target_indices:
                    if idx < len(spanish_words):
                        print(f"Index {idx} → '{spanish_words[idx]}'")
                    else:
                        print(f"Index {idx} → OUT_OF_BOUNDS (max index: {len(spanish_words)-1})")
    
    else:
        print(f"API Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    debug_target_indices() 