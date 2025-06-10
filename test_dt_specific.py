#!/usr/bin/env python3

from backend.app.services.latin_macronizer import LatinMacronizer

# Test the specific Deuteronomy verse
macronizer = LatinMacronizer()

# The verse you're analyzing
dt_verse = "Quadragesimo anno, undecimo mense, prima die mensis, locutus est Moyses ad filios Israel omnia quae praeceperat illi Dominus, ut diceret eis"

print("="*80)
print("TESTING DEUTERONOMY 1:3 MACRONIZATION")
print("="*80)

print(f"Original: {dt_verse}")
print()

try:
    # Test macronization
    macronized = macronizer.macronize_verse(dt_verse)
    print(f"Macronized: {macronized}")
    print()
    
    # Your desired result for comparison
    desired = "Quadragésimoanno, undécimomense, primadīemēnsis, locútusest Móyses ad fílios Isrāēl ómnīaquæ præcéperat illī Dóminus, ut dícerēteis"
    print(f"Desired:    {desired}")
    print()
    
    # Check if service is available
    if macronizer.is_available():
        print("✅ Macronizer service is available")
    else:
        print("❌ Macronizer service is NOT available")
        
except Exception as e:
    print(f"❌ Error: {e}") 