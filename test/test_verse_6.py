#!/usr/bin/env python3
"""
Simple test to check verse 6 issue
"""

import json
from pathlib import Path

def main():
    print("🔍 Checking verse 6 issue...")
    
    # Load JSON data
    json_path = Path("gita_verses.json")
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            verses = json.load(f)
        
        # Find verse 6
        for verse in verses:
            if verse.get('chapter_number') == 1 and verse.get('verse_number') == 6:
                print(f"✅ Found verse 6:")
                print(f"   Text: {verse['text']}")
                print(f"   Transliteration: {verse['transliteration']}")
                print(f"   Word meanings: {verse['word_meanings']}")
                
                # Check if transliteration is complete
                if 'yudhāmanyuśhcha' in verse['transliteration']:
                    print("✅ Transliteration is complete with both parts")
                else:
                    print("❌ Transliteration is missing first part")
                
                return
        
        print("❌ Verse 6 not found")
    else:
        print("❌ JSON file not found")

if __name__ == "__main__":
    main() 