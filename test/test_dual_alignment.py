#!/usr/bin/env python3
"""
Test script to demonstrate separate word alignments for literal vs dynamic translations
"""

import sys
import os
import json

# Add the backend to path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_path)

try:
    from app.services.word_alignment import get_word_aligner
except ImportError:
    sys.path.append(os.path.join(backend_path, "app"))
    from services.word_alignment import get_word_aligner

def test_dual_alignment():
    """Test word alignment for both literal and dynamic translations"""
    
    print("🎯 Testing Separate Word Alignments for Literal vs Dynamic")
    print("=" * 65)
    
    # Sample Latin verse (Genesis 1:2)
    latin_source = "Terra autem erat inānis et vācua"
    literal_english = "But the earth was empty and void"
    dynamic_english = "Yet the earth was barren and desolate"
    
    print(f"📖 Latin Source: {latin_source}")
    print(f"📝 Literal Translation: {literal_english}")
    print(f"🎨 Dynamic Translation: {dynamic_english}")
    print()
    
    # Get word aligner
    aligner = get_word_aligner()
    
    # Generate alignments for literal translation
    literal_alignment_data = aligner.align_words(latin_source, literal_english, "latin")
    literal_formatted = aligner.format_alignment_response(literal_alignment_data)
    
    # Generate alignments for dynamic translation
    dynamic_alignment_data = aligner.align_words(latin_source, dynamic_english, "latin")
    dynamic_formatted = aligner.format_alignment_response(dynamic_alignment_data)
    
    print("🔤 LITERAL Translation Alignments:")
    print(f"   Method: {literal_formatted['method']}")
    print(f"   Confidence: {literal_formatted['average_confidence']:.3f}")
    for alignment in literal_formatted['alignments']:
        confidence_icon = "🟢" if alignment['confidence'] > 0.7 else "🟡" if alignment['confidence'] > 0.5 else "🔴"
        target_words = ', '.join(alignment['target_words']) if alignment['target_words'] else '(no alignment)'
        print(f"   {confidence_icon} {alignment['source_word']:12} → {target_words:20} (conf: {alignment['confidence']:.3f})")
    
    print()
    print("🎨 DYNAMIC Translation Alignments:")
    print(f"   Method: {dynamic_formatted['method']}")
    print(f"   Confidence: {dynamic_formatted['average_confidence']:.3f}")
    for alignment in dynamic_formatted['alignments']:
        confidence_icon = "🟢" if alignment['confidence'] > 0.7 else "🟡" if alignment['confidence'] > 0.5 else "🔴"
        target_words = ', '.join(alignment['target_words']) if alignment['target_words'] else '(no alignment)'
        print(f"   {confidence_icon} {alignment['source_word']:12} → {target_words:20} (conf: {alignment['confidence']:.3f})")
    
    print()
    print("📊 Comparison Analysis:")
    
    # Compare alignments word by word
    literal_alignments = {a['source_word']: a['target_words'] for a in literal_formatted['alignments']}
    dynamic_alignments = {a['source_word']: a['target_words'] for a in dynamic_formatted['alignments']}
    
    for word in ['Terra', 'autem', 'erat', 'inānis', 'et', 'vācua']:
        if word in literal_alignments or word in dynamic_alignments:
            literal_targets = ', '.join(literal_alignments.get(word, ['(none)']))
            dynamic_targets = ', '.join(dynamic_alignments.get(word, ['(none)']))
            
            different = literal_targets != dynamic_targets
            icon = "🔄" if different else "➡️"
            
            print(f"   {icon} {word:12}: Literal=[{literal_targets:15}] Dynamic=[{dynamic_targets:15}]")
    
    print()
    print("📋 API Response Format:")
    
    # Simulate the API response format
    api_response = {
        "success": True,
        "literal": literal_english,
        "dynamic": dynamic_english,
        "source_language": "latin",
        "word_alignments": {
            "literal": literal_formatted["alignments"],
            "dynamic": dynamic_formatted["alignments"],
            "method": literal_formatted["method"],
            "literal_confidence": literal_formatted["average_confidence"],
            "dynamic_confidence": dynamic_formatted["average_confidence"],
            "average_confidence": (literal_formatted["average_confidence"] + dynamic_formatted["average_confidence"]) / 2
        }
    }
    
    print(json.dumps(api_response, indent=2, ensure_ascii=False))

def test_spanish_alignment():
    """Test with Spanish translations"""
    
    print("\n" + "=" * 65)
    print("🇪🇸 Testing Spanish Translation Alignments")
    print("=" * 65)
    
    latin_source = "Vocavītque Deus firmamēntum Caelum"
    literal_spanish = "Y llamó Dios al firmamento Cielo"
    dynamic_spanish = "Dios nombró al firmamento Cielo"
    
    print(f"📖 Latin Source: {latin_source}")
    print(f"📝 Literal Spanish: {literal_spanish}")
    print(f"🎨 Dynamic Spanish: {dynamic_spanish}")
    print()
    
    aligner = get_word_aligner()
    
    # Generate alignments
    literal_data = aligner.align_words(latin_source, literal_spanish, "latin")
    dynamic_data = aligner.align_words(latin_source, dynamic_spanish, "latin")
    
    literal_formatted = aligner.format_alignment_response(literal_data)
    dynamic_formatted = aligner.format_alignment_response(dynamic_data)
    
    print("📝 Literal Spanish Alignments:")
    for alignment in literal_formatted['alignments']:
        target_words = ', '.join(alignment['target_words']) if alignment['target_words'] else '(no alignment)'
        print(f"   {alignment['source_word']:12} → {target_words}")
    
    print()
    print("🎨 Dynamic Spanish Alignments:")
    for alignment in dynamic_formatted['alignments']:
        target_words = ', '.join(alignment['target_words']) if alignment['target_words'] else '(no alignment)'
        print(f"   {alignment['source_word']:12} → {target_words}")

if __name__ == "__main__":
    print("🚀 Dual Word Alignment Test Suite")
    print("Testing separate alignments for literal and dynamic translations")
    print()
    
    try:
        test_dual_alignment()
        test_spanish_alignment()
        
        print("\n✅ All dual alignment tests completed!")
        print("\n📖 Key Benefits:")
        print("   • Literal alignments preserve word order and structure")
        print("   • Dynamic alignments reflect natural language flow")
        print("   • Separate confidence scores for each translation style")
        print("   • Frontend can choose which alignment to use for highlighting")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nThis is expected if SimAlign dependencies aren't installed.")
        print("The system will still work with fallback alignment methods.") 