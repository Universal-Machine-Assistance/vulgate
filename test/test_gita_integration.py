#!/usr/bin/env python3
"""
Test script for Bhagavad Gita integration
"""

import requests
import json
import time

def test_endpoints():
    """Test the new text endpoints"""
    base_url = "http://localhost:8000/api/v1/texts"
    
    print("🧪 Testing Bhagavad Gita Integration")
    print("=" * 50)
    
    # Test 1: Get available sources
    print("1. Testing available sources...")
    try:
        response = requests.get(f"{base_url}/sources", timeout=10)
        if response.status_code == 200:
            sources = response.json()
            print(f"✅ Available sources: {sources}")
        else:
            print(f"❌ Status: {response.status_code}, Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Get source info for Gita
    print("\n2. Testing Gita source info...")
    try:
        response = requests.get(f"{base_url}/sources/gita/info", timeout=10)
        if response.status_code == 200:
            info = response.json()
            print(f"✅ Gita info: {json.dumps(info, indent=2)}")
        else:
            print(f"❌ Status: {response.status_code}, Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Get a Gita verse
    print("\n3. Testing Gita verse (Chapter 1, Verse 1)...")
    try:
        response = requests.get(f"{base_url}/gita/1/1", timeout=30)
        if response.status_code == 200:
            verse = response.json()
            print(f"✅ Gita verse fetched successfully!")
            print(f"   Chapter: {verse.get('chapter')}")
            print(f"   Verse: {verse.get('verse_number')}")
            print(f"   Text preview: {verse.get('text', '')[:100]}...")
            print(f"   Translation preview: {verse.get('translation', '')[:100]}...")
        else:
            print(f"❌ Status: {response.status_code}, Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Get a Bible verse (should still work)
    print("\n4. Testing Bible verse (Genesis 1:1)...")
    try:
        response = requests.get(f"{base_url}/bible/Gn/1/1", timeout=10)
        if response.status_code == 200:
            verse = response.json()
            print(f"✅ Bible verse fetched successfully!")
            print(f"   Chapter: {verse.get('chapter')}")
            print(f"   Verse: {verse.get('verse_number')}")
            print(f"   Text preview: {verse.get('text', '')[:100]}...")
        else:
            print(f"❌ Status: {response.status_code}, Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Integration test complete!")

def test_api_directly():
    """Test the RapidAPI directly"""
    print("\n🔌 Testing RapidAPI directly...")
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("RAPIDAPI_KEY")
    
    if not api_key:
        print("❌ RAPIDAPI_KEY not found in environment")
        return
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "bhagavad-gita3.p.rapidapi.com"
    }
    
    try:
        response = requests.get(
            "https://bhagavad-gita3.p.rapidapi.com/v2/chapters/1/verses/1/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Direct API test successful!")
            print(f"   Verse: {data.get('chapter_number')}.{data.get('verse_number')}")
            print(f"   Sanskrit text preview: {data.get('text', '')[:50]}...")
        else:
            print(f"❌ Direct API test failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Direct API error: {e}")

if __name__ == "__main__":
    # Wait a moment for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(3)
    
    # Test direct API first
    test_api_directly()
    
    # Test our endpoints
    test_endpoints() 