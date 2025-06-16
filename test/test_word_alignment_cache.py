#!/usr/bin/env python3
"""Test word alignment caching functionality"""

import sys
import os
sys.path.append('.')

from app.api.api_v1.endpoints.dictionary import cache_word_alignments, get_cached_word_alignments
import json

def test_caching():
    print("=== TESTING WORD ALIGNMENT CACHING ===")
    
    # Test data
    verse_reference = "Gn 1:1"
    language_code = "es"
    literal_translation = "En principio creó Dios cielo, y tierra."
    dynamic_translation = "Al principio, Dios creó el cielo y la tierra."
    
    word_alignments = {
        "literal": [
            {"target_words": ["En"], "target_indices": [0], "confidence": 0.8},
            {"target_words": ["principio"], "target_indices": [1], "confidence": 0.543}
        ],
        "dynamic": [
            {"target_words": ["Al"], "target_indices": [0], "confidence": 0.8},
            {"target_words": ["principio"], "target_indices": [1], "confidence": 0.533}
        ],
        "method": "simalign_bert",
        "average_confidence": 0.5245
    }
    
    print("1. Testing cache storage...")
    cache_word_alignments(verse_reference, language_code, literal_translation, dynamic_translation, word_alignments)
    
    print("2. Testing cache retrieval...")
    cached_result = get_cached_word_alignments(verse_reference, language_code)
    
    if cached_result:
        print("✅ Cache retrieval successful!")
        print(f"   Method: {cached_result.get('alignment_method', 'unknown')}")
        print(f"   Confidence: {cached_result.get('alignment_confidence', 0.0)}")
        print(f"   Literal translation: {cached_result.get('literal_translation', 'None')}")
        print(f"   Dynamic translation: {cached_result.get('dynamic_translation', 'None')}")
        print(f"   Word alignments count: {len(cached_result.get('word_alignments', {}).get('literal', []))}")
    else:
        print("❌ Cache retrieval failed!")
    
    print("3. Testing cache retrieval for non-existent entry...")
    non_existent = get_cached_word_alignments("Non 1:1", "fr")
    if non_existent is None:
        print("✅ Correctly returned None for non-existent entry")
    else:
        print("❌ Should have returned None for non-existent entry")

if __name__ == "__main__":
    test_caching() 