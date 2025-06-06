#!/usr/bin/env python3
"""
Dictionary Search Tool

Simple tool to search the comprehensive Latin dictionary for specific words
"""

import json
import sys
from typing import Dict, Any

def load_dictionary(filename: str = "frontend/public/dictionary.json") -> Dict[str, Any]:
    """Load the dictionary from JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading dictionary: {e}")
        return {}

def search_word(dictionary: Dict[str, Any], word: str) -> None:
    """Search for a specific word in the dictionary"""
    word_lower = word.lower()
    
    if word_lower in dictionary:
        entry = dictionary[word_lower]
        print(f"\n✓ Found: {word}")
        print("-" * 50)
        print(f"Latin: {entry['latin']}")
        print(f"Definition: {entry['definition'][:200]}{'...' if len(entry['definition']) > 200 else ''}")
        print(f"Part of Speech: {entry['partOfSpeech']}")
        print(f"Etymology: {entry['etymology'][:150]}{'...' if len(entry['etymology']) > 150 else ''}")
        if entry.get('pronunciation'):
            print(f"Pronunciation: {entry['pronunciation']}")
    else:
        print(f"\n✗ Not found: {word}")
        
        # Try to find similar words
        similar = [w for w in dictionary.keys() if word_lower in w or w in word_lower]
        if similar:
            print(f"Similar words found: {', '.join(similar[:10])}")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python search_dictionary.py <word1> [word2] [word3] ...")
        print("Example: python search_dictionary.py principium deus terra")
        return
    
    dictionary = load_dictionary()
    if not dictionary:
        return
    
    print(f"Dictionary loaded with {len(dictionary)} entries")
    
    for word in sys.argv[1:]:
        search_word(dictionary, word)

if __name__ == "__main__":
    main() 