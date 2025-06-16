#!/usr/bin/env python3
"""Test the new format_alignment_for_frontend method"""

from app.services.word_alignment import get_word_aligner
import json

def test_format_method():
    aligner = get_word_aligner()
    verse = 'In princīpio creāvit Deus cælum'
    
    # Create mock alignment data
    literal_data = {
        'alignments': [
            {'source_word': 'In', 'source_index': 0, 'target_words': ['In'], 'target_indices': [0], 'confidence': 0.8},
            {'source_word': 'princīpio', 'source_index': 1, 'target_words': ['beginning'], 'target_indices': [1], 'confidence': 0.7}
        ], 
        'method': 'test', 
        'average_confidence': 0.75
    }
    
    dynamic_data = {
        'alignments': [
            {'source_word': 'In', 'source_index': 0, 'target_words': ['In', 'the'], 'target_indices': [0, 1], 'confidence': 0.7},
            {'source_word': 'princīpio', 'source_index': 1, 'target_words': ['beginning'], 'target_indices': [2], 'confidence': 0.6}
        ], 
        'method': 'test', 
        'average_confidence': 0.65
    }
    
    # Test the new format method
    result = aligner.format_alignment_for_frontend(literal_data, dynamic_data, verse)
    
    print('Frontend format result:')
    print(json.dumps(result, indent=2))
    print(f'Literal type: {type(result["literal"])}')
    print(f'Dynamic type: {type(result["dynamic"])}')
    print(f'Literal length: {len(result["literal"])}')
    print(f'Dynamic length: {len(result["dynamic"])}')
    
    if isinstance(result["literal"], list) and isinstance(result["dynamic"], list):
        print("✅ Format is correct: Arrays created")
    else:
        print("❌ Format is incorrect")

if __name__ == "__main__":
    test_format_method() 