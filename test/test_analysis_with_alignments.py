#!/usr/bin/env python3
"""
Test script to verify the analyze/verse/openai endpoint now includes word alignments
"""

import requests
import json
import sys

def test_analysis_with_alignments():
    """Test the updated analysis endpoint"""
    url = 'http://127.0.0.1:8000/api/v1/dictionary/analyze/verse/openai'
    
    test_data = {
        'verse': 'In princīpio creāvit Deus cælum, et terram.',
        'reference': 'Gn 1:1',
        'analysis_language': 'en',
        'include_translations': True
    }
    
    print("🧪 Testing analyze/verse/openai endpoint with word alignments...")
    print(f"📝 Verse: {test_data['verse']}")
    print(f"📍 Reference: {test_data['reference']}")
    print()
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('success', False)}")
            print(f"🔤 Source Language: {result.get('source_language', 'unknown')}")
            
            # Check for translations
            if 'literal_translation' in result:
                print(f"📖 Literal Translation: {result['literal_translation']}")
            if 'dynamic_translation' in result:
                print(f"🎭 Dynamic Translation: {result['dynamic_translation']}")
            
            # Check for word alignments
            if 'word_alignments' in result:
                alignments = result['word_alignments']
                print(f"🔗 Word Alignments Found: YES")
                print(f"   Method: {alignments.get('method', 'unknown')}")
                print(f"   Average Confidence: {alignments.get('average_confidence', 0.0):.3f}")
                print(f"   Literal Alignments: {len(alignments.get('literal', []))}")
                print(f"   Dynamic Alignments: {len(alignments.get('dynamic', []))}")
                
                # Show first few alignments
                literal_aligns = alignments.get('literal', [])
                if literal_aligns:
                    print(f"   Sample Literal Alignment: {literal_aligns[0]}")
                    
            else:
                print("❌ Word Alignments: NOT FOUND")
                if 'word_alignments_error' in result:
                    print(f"   Error: {result['word_alignments_error']}")
            
            # Check analysis data
            word_analysis = result.get('word_analysis', [])
            print(f"📚 Word Analysis Count: {len(word_analysis)}")
            
            theological = result.get('theological_layer', [])
            print(f"⛪ Theological Layer Count: {len(theological)}")
            
            return True
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Exception occurred: {e}")
        return False

if __name__ == "__main__":
    success = test_analysis_with_alignments()
    sys.exit(0 if success else 1) 