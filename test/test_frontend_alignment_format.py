#!/usr/bin/env python3
"""
Test script to verify the analyze/verse/openai endpoint returns word alignments 
in the correct frontend format (position-indexed arrays)
"""

import requests
import json
import sys

def test_frontend_alignment_format():
    """Test the updated analysis endpoint with frontend-compatible alignment format"""
    url = 'http://127.0.0.1:8000/api/v1/dictionary/analyze/verse/openai'
    
    test_data = {
        'verse': 'In princīpio creāvit Deus cælum, et terram.',
        'reference': 'Gn 1:1',
        'analysis_language': 'en',
        'include_translations': True
    }
    
    print("🧪 Testing frontend alignment format...")
    print(f"📝 Verse: {test_data['verse']}")
    print(f"📍 Reference: {test_data['reference']}")
    print()
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('success', False)}")
            
            # Check for word alignments
            if 'word_alignments' in result:
                alignments = result['word_alignments']
                print(f"🔗 Word Alignments Found: YES")
                print(f"   Type: {type(alignments)}")
                
                # Check structure
                if 'literal' in alignments and 'dynamic' in alignments:
                    literal = alignments['literal']
                    dynamic = alignments['dynamic']
                    
                    print(f"   Literal Type: {type(literal)}")
                    print(f"   Dynamic Type: {type(dynamic)}")
                    print(f"   Literal Length: {len(literal) if isinstance(literal, list) else 'Not a list'}")
                    print(f"   Dynamic Length: {len(dynamic) if isinstance(dynamic, list) else 'Not a list'}")
                    
                    # Show first few entries
                    if isinstance(literal, list) and len(literal) > 0:
                        print(f"   Sample Literal[0]: {literal[0]}")
                        print(f"   Sample Literal[1]: {literal[1] if len(literal) > 1 else 'N/A'}")
                    
                    if isinstance(dynamic, list) and len(dynamic) > 0:
                        print(f"   Sample Dynamic[0]: {dynamic[0]}")
                        print(f"   Sample Dynamic[1]: {dynamic[1] if len(dynamic) > 1 else 'N/A'}")
                    
                    # Check metadata
                    print(f"   Method: {alignments.get('method', 'unknown')}")
                    print(f"   Average Confidence: {alignments.get('average_confidence', 0.0):.3f}")
                    
                    # Validate format
                    if isinstance(literal, list) and isinstance(dynamic, list):
                        print("✅ Format is correct: Arrays indexed by word position")
                        return True
                    else:
                        print("❌ Format is incorrect: Expected arrays")
                        return False
                else:
                    print("❌ Missing literal/dynamic keys in word_alignments")
                    return False
            else:
                print("❌ Word Alignments: NOT FOUND")
                return False
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Exception occurred: {e}")
        return False

if __name__ == "__main__":
    success = test_frontend_alignment_format()
    sys.exit(0 if success else 1) 