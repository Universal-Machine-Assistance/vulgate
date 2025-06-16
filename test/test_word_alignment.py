#!/usr/bin/env python3
"""
Test Script for Advanced Word Alignment Feature
Demonstrates semantic word alignment between Latin/Sanskrit and target languages
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
    # If not in the right directory structure, try relative import
    sys.path.append(os.path.join(backend_path, "app"))
    from services.word_alignment import get_word_aligner

def test_latin_alignment():
    """Test Latin to Spanish alignment"""
    print("🏛️  Testing Latin → Spanish Alignment")
    print("=" * 50)
    
    # Sample Latin verse (Genesis 1:1)
    latin_text = "In principio creavit Deus caelum et terram"
    spanish_text = "En el principio creó Dios los cielos y la tierra"
    
    print(f"Latin:   {latin_text}")
    print(f"Spanish: {spanish_text}")
    print()
    
    # Get word aligner
    aligner = get_word_aligner()
    
    # Perform alignment
    result = aligner.align_words(latin_text, spanish_text, "latin")
    formatted = aligner.format_alignment_response(result)
    
    # Display results
    print("🎯 Alignment Results:")
    print(f"Method: {formatted.get('method', 'unknown')}")
    print(f"Average Confidence: {formatted.get('average_confidence', 0.0):.3f}")
    print()
    
    print("📋 Word Alignments:")
    for alignment in formatted['literal']:
        confidence_icon = "🟢" if alignment['confidence'] > 0.8 else "🟡" if alignment['confidence'] > 0.6 else "🔴"
        print(f"{confidence_icon} {alignment['source_word']:12} → {', '.join(alignment['target_words']):20} (conf: {alignment['confidence']:.3f})")
    
    print()

def test_sanskrit_alignment():
    """Test Sanskrit to English alignment"""
    print("🕉️  Testing Sanskrit → English Alignment")
    print("=" * 50)
    
    # Sample Sanskrit verse (Bhagavad Gita 2.47)
    sanskrit_text = "karmaṇy evādhikāras te mā phaleṣu kadācana"
    english_text = "You have a right to perform actions, but never to the fruits of actions"
    
    print(f"Sanskrit: {sanskrit_text}")
    print(f"English:  {english_text}")
    print()
    
    # Get word aligner
    aligner = get_word_aligner()
    
    # Perform alignment
    result = aligner.align_words(sanskrit_text, english_text, "sanskrit")
    formatted = aligner.format_alignment_response(result)
    
    # Display results
    print("🎯 Alignment Results:")
    print(f"Method: {formatted.get('method', 'unknown')}")
    print(f"Average Confidence: {formatted.get('average_confidence', 0.0):.3f}")
    print()
    
    print("📋 Word Alignments:")
    for alignment in formatted['literal']:
        confidence_icon = "🟢" if alignment['confidence'] > 0.8 else "🟡" if alignment['confidence'] > 0.6 else "🔴"
        print(f"{confidence_icon} {alignment['source_word']:15} → {', '.join(alignment['target_words']):25} (conf: {alignment['confidence']:.3f})")
    
    print()

def test_literal_vs_dynamic():
    """Test different translation styles"""
    print("📚 Testing Literal vs Dynamic Translations")
    print("=" * 50)
    
    # Sample Latin verse
    latin_text = "Vocavītque Deus firmamēntum Caelum"
    literal_spanish = "Y llamó Dios al firmamento Cielo"
    dynamic_spanish = "Dios nombró al firmamento Cielo"
    
    print(f"Latin:           {latin_text}")
    print(f"Literal Spanish: {literal_spanish}")
    print(f"Dynamic Spanish: {dynamic_spanish}")
    print()
    
    aligner = get_word_aligner()
    
    # Test literal alignment
    literal_result = aligner.align_words(latin_text, literal_spanish, "latin")
    literal_formatted = aligner.format_alignment_response(literal_result)
    
    # Test dynamic alignment  
    dynamic_result = aligner.align_words(latin_text, dynamic_spanish, "latin")
    dynamic_formatted = aligner.format_alignment_response(dynamic_result)
    
    print("🎯 Literal Translation Alignment:")
    for alignment in literal_formatted['literal']:
        print(f"  {alignment['source_word']:12} → {', '.join(alignment['target_words']):20}")
    
    print()
    print("🎯 Dynamic Translation Alignment:")
    for alignment in dynamic_formatted['literal']:
        print(f"  {alignment['source_word']:12} → {', '.join(alignment['target_words']):20}")
    
    print()

def test_api_response_format():
    """Test the complete API response format"""
    print("📡 Testing Complete API Response Format")
    print("=" * 50)
    
    # Simulate complete translation response
    latin_text = "Terra autem erat inānis et vācua"
    literal = "La tierra, sin embargo, estaba vacía y desolada"
    dynamic = "Pero la tierra estaba vacía y desolada"
    
    aligner = get_word_aligner()
    
    # Generate alignments
    literal_result = aligner.align_words(latin_text, literal, "latin")
    dynamic_result = aligner.align_words(latin_text, dynamic, "latin")
    
    literal_formatted = aligner.format_alignment_response(literal_result)
    dynamic_formatted = aligner.format_alignment_response(dynamic_result)
    
    # Create complete API response
    api_response = {
        "success": True,
        "literal": literal,
        "dynamic": dynamic,
        "source_language": "latin",
        "word_alignments": {
            "literal": literal_formatted["literal"],
            "dynamic": dynamic_formatted["literal"],
            "method": literal_formatted.get("method", "fallback"),
            "average_confidence": literal_formatted.get("average_confidence", 0.0)
        }
    }
    
    print("📋 Complete API Response:")
    print(json.dumps(api_response, indent=2, ensure_ascii=False))
    print()

def main():
    """Run all alignment tests"""
    print("🚀 Advanced Word Alignment Test Suite")
    print("=" * 60)
    print()
    
    try:
        # Test different language pairs
        test_latin_alignment()
        test_sanskrit_alignment()
        test_literal_vs_dynamic()
        test_api_response_format()
        
        print("✅ All tests completed successfully!")
        print()
        print("📖 For more information, see:")
        print("   - backend/docs/WORD_ALIGNMENT_FEATURE.md")
        print("   - backend/requirements_alignment.txt")
        print("   - backend/install_word_alignment.sh")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print()
        print("🛠️  To install dependencies:")
        print("   cd backend && bash install_word_alignment.sh")
        print("   OR")
        print("   pip install -r backend/requirements_alignment.txt")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("🔍 Check the error message above for details.")
        print("The system should gracefully fall back to pattern-based alignment.")

if __name__ == "__main__":
    main() 