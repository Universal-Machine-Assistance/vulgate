#!/usr/bin/env python3
"""Debug API alignment issue by replicating the exact API flow"""

import sys
import os
sys.path.append('.')

from app.services.word_alignment import get_word_aligner
from app.services.enhanced_dictionary import EnhancedDictionary
import json

def test_api_flow():
    print("=== TESTING API FLOW ===")
    
    # Same data as API call
    verse_text = "In princīpio creāvit Deus cælum, et terram."
    target_language = "es"
    
    # Create enhanced dictionary (like API does)
    enhanced_dict = EnhancedDictionary()
    
    # Get translations (like API does)
    print("1. Getting translations...")
    translation_result = enhanced_dict.translate_verse(verse_text, target_language)
    
    if isinstance(translation_result, str):
        try:
            translation_data = json.loads(translation_result)
        except json.JSONDecodeError:
            translation_data = {
                "literal": "Translation not available",
                "dynamic": "Translation not available",
                "source_language": "latin"
            }
    else:
        translation_data = translation_result
    
    literal_translation = translation_data.get("literal", "")
    dynamic_translation = translation_data.get("dynamic", "")
    source_language = translation_data.get("source_language", "latin")
    
    print(f"   Literal: {literal_translation}")
    print(f"   Dynamic: {dynamic_translation}")
    print(f"   Source language: {source_language}")
    
    # Generate alignments (like API does)
    print("\n2. Generating alignments...")
    word_aligner = get_word_aligner()
    
    literal_alignments_data = word_aligner.align_words(verse_text, literal_translation, source_language)
    dynamic_alignments_data = word_aligner.align_words(verse_text, dynamic_translation, source_language)
    
    print(f"   Literal alignments type: {type(literal_alignments_data)}")
    print(f"   Dynamic alignments type: {type(dynamic_alignments_data)}")
    
    # Format alignments (like API does)
    print("\n3. Formatting alignments...")
    literal_formatted = word_aligner.format_alignment_response(literal_alignments_data)
    dynamic_formatted = word_aligner.format_alignment_response(dynamic_alignments_data)
    
    print(f"   Literal formatted type: {type(literal_formatted)}")
    print(f"   Dynamic formatted type: {type(dynamic_formatted)}")
    print(f"   Literal alignments count: {len(literal_formatted.get('alignments', []))}")
    print(f"   Dynamic alignments count: {len(dynamic_formatted.get('alignments', []))}")
    
    # Show word 2 before frontend formatting
    literal_aligns = literal_formatted.get('alignments', [])
    dynamic_aligns = dynamic_formatted.get('alignments', [])
    
    if len(literal_aligns) > 2:
        print(f"   Word 2 literal before frontend format: {literal_aligns[2]}")
    if len(dynamic_aligns) > 2:
        print(f"   Word 2 dynamic before frontend format: {dynamic_aligns[2]}")
    
    # Format for frontend (like API does)
    print("\n4. Frontend formatting...")
    frontend_alignments = word_aligner.format_alignment_for_frontend(
        literal_formatted, dynamic_formatted, verse_text
    )
    
    print(f"   Frontend format type: {type(frontend_alignments)}")
    print(f"   Literal array length: {len(frontend_alignments.get('literal', []))}")
    print(f"   Dynamic array length: {len(frontend_alignments.get('dynamic', []))}")
    
    # Check word 2 after frontend formatting
    literal_array = frontend_alignments.get('literal', [])
    dynamic_array = frontend_alignments.get('dynamic', [])
    
    if len(literal_array) > 2:
        print(f"   Word 2 literal after frontend format: {literal_array[2]}")
    if len(dynamic_array) > 2:
        print(f"   Word 2 dynamic after frontend format: {dynamic_array[2]}")

if __name__ == "__main__":
    test_api_flow() 