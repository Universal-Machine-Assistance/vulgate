#!/usr/bin/env python3
"""
Test script for word lookup functionality.
Tests the API endpoints for word definitions and verse occurrences.
"""

import requests
import json
import sys
from typing import Dict, Any

# Configuration
API_BASE = "http://localhost:8000/api/v1"
HEADERS = {"Content-Type": "application/json"}

def test_word_definition(word: str) -> Dict[str, Any]:
    """Test getting word definition"""
    print(f"\n🔍 Testing word definition for: '{word}'")
    
    try:
        response = requests.get(f"{API_BASE}/words/{word}/definition", headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Definition found:")
            print(f"   📝 Latin: {data.get('latin', 'N/A')}")
            print(f"   📖 Definition: {data.get('definition', 'N/A')[:100]}...")
            print(f"   🏷️  Part of Speech: {data.get('part_of_speech', 'N/A')}")
            print(f"   📚 Source: {data.get('source', 'N/A')} (Confidence: {data.get('confidence', 0):.2f})")
            return data
        else:
            print(f"   ❌ Error {response.status_code}: {response.text}")
            return {}
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection error - make sure the server is running at {API_BASE}")
        return {}
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {}

def test_word_occurrences(word: str) -> Dict[str, Any]:
    """Test getting word occurrences"""
    print(f"\n📖 Testing verse occurrences for: '{word}'")
    
    try:
        response = requests.get(f"{API_BASE}/words/{word}/verses?limit=5", headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            verses = data.get('verses', [])
            total_count = data.get('total_count', 0)
            
            print(f"   ✅ Found {total_count} total occurrences (showing first {len(verses)}):")
            
            for verse in verses[:3]:  # Show first 3
                print(f"   📜 {verse.get('verse_reference', 'Unknown')}")
                print(f"      {verse.get('verse_text', 'No text')[:80]}...")
                print()
            
            if len(verses) > 3:
                print(f"   ... and {len(verses) - 3} more in this response")
            
            return data
        else:
            print(f"   ❌ Error {response.status_code}: {response.text}")
            return {}
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection error - make sure the server is running at {API_BASE}")
        return {}
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {}

def test_comprehensive_word_info(word: str) -> Dict[str, Any]:
    """Test getting comprehensive word information"""
    print(f"\n🎯 Testing comprehensive word info for: '{word}'")
    
    try:
        response = requests.get(f"{API_BASE}/words/{word}?limit_verses=5", headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"   ✅ Comprehensive data retrieved:")
            print(f"   📝 Word: {data.get('word', 'N/A')}")
            print(f"   🏛️  Latin: {data.get('latin', 'N/A')}")
            print(f"   📖 Definition: {data.get('definition', 'N/A')[:100]}...")
            print(f"   🏷️  Part of Speech: {data.get('part_of_speech', 'N/A')}")
            print(f"   📊 Verse Count: {data.get('verse_count', 0)}")
            print(f"   📚 Source: {data.get('source', 'N/A')} (Confidence: {data.get('confidence', 0):.2f})")
            
            verses = data.get('verses', [])
            if verses:
                print(f"   📜 Sample verses ({len(verses)} shown):")
                for verse in verses[:2]:
                    print(f"      • {verse.get('verse_reference', 'Unknown')}: {verse.get('verse_text', 'No text')[:60]}...")
            
            return data
        else:
            print(f"   ❌ Error {response.status_code}: {response.text}")
            return {}
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection error - make sure the server is running at {API_BASE}")
        return {}
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {}

def test_api_health():
    """Test if the API is responding"""
    print(f"🏥 Testing API health at {API_BASE}")
    
    try:
        response = requests.get(f"{API_BASE.replace('/api/v1', '')}/", headers=HEADERS)
        
        if response.status_code == 200:
            print(f"   ✅ API is responding")
            return True
        else:
            print(f"   ⚠️  API responded with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection error - make sure the server is running")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 VULGATE WORD LOOKUP API TESTS")
    print("=" * 50)
    
    # Test API health first
    if not test_api_health():
        print("\n❌ Cannot continue - API is not responding")
        print("💡 Make sure your FastAPI server is running:")
        print("   cd backend && uvicorn app.main:app --reload --port 8000")
        sys.exit(1)
    
    # Test words
    test_words = ["deus", "et", "in", "dominus", "verbum", "jesus"]
    
    if len(sys.argv) > 1:
        test_words = sys.argv[1:]
    
    for word in test_words:
        print(f"\n{'='*60}")
        print(f"🔬 TESTING WORD: '{word.upper()}'")
        print(f"{'='*60}")
        
        # Test each endpoint
        definition_data = test_word_definition(word)
        occurrences_data = test_word_occurrences(word)
        comprehensive_data = test_comprehensive_word_info(word)
        
        # Summary for this word
        print(f"\n📊 SUMMARY for '{word}':")
        if comprehensive_data:
            print(f"   ✅ Definition: {'Found' if comprehensive_data.get('definition') else 'Not found'}")
            print(f"   ✅ Occurrences: {comprehensive_data.get('verse_count', 0)} verses")
            print(f"   ✅ Source: {comprehensive_data.get('source', 'Unknown')}")
        else:
            print(f"   ❌ No data available")
    
    print(f"\n🎉 TESTING COMPLETE!")
    print("\n💡 USAGE TIPS:")
    print("   • Use the comprehensive endpoint: GET /api/v1/words/{word}")
    print("   • For just definitions: GET /api/v1/words/{word}/definition")
    print("   • For paginated verses: GET /api/v1/words/{word}/verses")
    print("   • Example: curl http://localhost:8000/api/v1/words/deus")

if __name__ == "__main__":
    main() 