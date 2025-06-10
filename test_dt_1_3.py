#!/usr/bin/env python3

from backend.app.services.latin_macronizer import LatinMacronizer

# Test the specific verse from Deuteronomy 1:3
original_text = "Quadragesimo anno, undecimo mense, prima die mensis, locutus est Moyses ad filios Israel omnia quae praeceperat illi Dominus, ut diceret eis:"

print("="*80)
print("TESTING DEUTERONOMY 1:3 MACRONIZATION")
print("="*80)
print()

print("Original text:")
print(original_text)
print()

# Test macronization
macronizer = LatinMacronizer()

if macronizer.is_available():
    print("✅ Macronizer is available")
    macronized = macronizer.macronize_text(original_text)
    print(f"Macronized text:")
    print(macronized)
    print()
    
    print("Expected text:")
    expected = "Quadragésimoanno, undécimomense, primadīemēnsis, locútusest Móyses ad fílios Isrāēl ómnīaquæ præcéperat illī Dóminus, ut dícerēteis:"
    print(expected)
    print()
    
    print("Differences analysis:")
    # Split into words and compare
    original_words = original_text.replace(',', '').replace(':', '').split()
    macronized_words = macronized.replace(',', '').replace(':', '').split()
    expected_words = expected.replace(',', '').replace(':', '').split()
    
    print(f"{'Original':<20} {'Macronized':<20} {'Expected':<20} {'Match'}")
    print("-" * 80)
    
    max_len = max(len(original_words), len(macronized_words), len(expected_words))
    for i in range(max_len):
        orig = original_words[i] if i < len(original_words) else ""
        macr = macronized_words[i] if i < len(macronized_words) else ""
        exp = expected_words[i] if i < len(expected_words) else ""
        match = "✅" if macr == exp else "❌"
        print(f"{orig:<20} {macr:<20} {exp:<20} {match}")
        
else:
    print("❌ Macronizer is not available")

print()
print("Testing with different meter hints:")
meters = ['prose', 'dactylic', 'elegiac']
for meter in meters:
    print(f"\nWith meter='{meter}':")
    result = macronizer.macronize_text(original_text, meter=meter)
    print(result) 