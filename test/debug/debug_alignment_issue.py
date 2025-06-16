#!/usr/bin/env python3
"""Debug script to investigate word alignment issues"""

import sys
import os
sys.path.append('.')

from app.services.word_alignment import get_word_aligner

def debug_alignment():
    aligner = get_word_aligner()
    
    # Test the problematic verse
    source_text = "In princīpio creāvit Deus cælum, et terram."
    literal_target = "En principio creó Dios cielo, y tierra."
    dynamic_target = "Al principio, Dios creó el cielo y la tierra."
    
    print("=== DEBUGGING WORD ALIGNMENT ===")
    print(f"Source: {source_text}")
    print(f"Literal: {literal_target}")
    print(f"Dynamic: {dynamic_target}")
    print()
    
    # Check tokenization
    source_tokens = aligner._tokenize_text(source_text, "latin")
    literal_tokens = aligner._tokenize_text(literal_target, "target")
    dynamic_tokens = aligner._tokenize_text(dynamic_target, "target")
    
    print("=== TOKENIZATION ===")
    print(f"Source tokens ({len(source_tokens)}): {source_tokens}")
    print(f"Literal tokens ({len(literal_tokens)}): {literal_tokens}")
    print(f"Dynamic tokens ({len(dynamic_tokens)}): {dynamic_tokens}")
    print()
    
    # Test alignments
    print("=== LITERAL ALIGNMENT ===")
    literal_result = aligner.align_words(source_text, literal_target, "latin")
    literal_formatted = aligner.format_alignment_response(literal_result)
    
    for i, alignment in enumerate(literal_formatted["alignments"]):
        print(f"Word {i}: {alignment['source_word']} -> {alignment['target_words']} (conf: {alignment['confidence']:.3f})")
    
    print()
    print("=== DYNAMIC ALIGNMENT ===")
    dynamic_result = aligner.align_words(source_text, dynamic_target, "latin")
    dynamic_formatted = aligner.format_alignment_response(dynamic_result)
    
    for i, alignment in enumerate(dynamic_formatted["alignments"]):
        print(f"Word {i}: {alignment['source_word']} -> {alignment['target_words']} (conf: {alignment['confidence']:.3f})")
    
    print()
    print("=== FRONTEND FORMAT ===")
    frontend_format = aligner.format_alignment_for_frontend(literal_formatted, dynamic_formatted, source_text)
    
    for i in range(len(source_tokens)):
        literal_align = frontend_format["literal"][i] if i < len(frontend_format["literal"]) else {}
        dynamic_align = frontend_format["dynamic"][i] if i < len(frontend_format["dynamic"]) else {}
        print(f"Word {i} ({source_tokens[i]}):")
        print(f"  Literal: {literal_align}")
        print(f"  Dynamic: {dynamic_align}")

if __name__ == "__main__":
    debug_alignment() 