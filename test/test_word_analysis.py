#!/usr/bin/env python3

from backend.app.services.enhanced_dictionary import EnhancedDictionary

# Test word analysis with macronized text
ed = EnhancedDictionary()

# Test with macronized verse
macronized_verse = "In prīncipiō creāvit Deus caelum et terram"
original_verse = "In principio creavit Deus caelum et terram"

print("="*60)
print("TESTING WORD ANALYSIS WITH MACRONIZED TEXT")
print("="*60)

print(f"Original verse: {original_verse}")
print(f"Macronized verse: {macronized_verse}")
print()

# Analyze the macronized verse
result = ed.analyze_verse(macronized_verse, 'Genesis 1:1')

print("Word analysis results:")
print(f"Verse text in result: {result['verse_text']}")
print()

print("Individual words analyzed:")
for i, word in enumerate(result['word_analysis']):
    print(f"{i+1}. '{word['latin']}' - {word['definition']}")

print()
print("Cache status check:")
print("Checking what's actually in the cache...")

# Check cache for both forms
words_to_check = [
    ("In", "In"),
    ("principio", "prīncipiō"),
    ("creavit", "creāvit"),
    ("Deus", "Deus"),
    ("caelum", "caelum"),
    ("et", "et"),
    ("terram", "terram")
]

for original, macronized in words_to_check:
    original_cached = ed.get_from_cache(original)
    macronized_cached = ed.get_from_cache(macronized)
    
    print(f"  '{original}' in cache: {'✅' if original_cached else '❌'}")
    print(f"  '{macronized}' in cache: {'✅' if macronized_cached else '❌'}")
    print() 