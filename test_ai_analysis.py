# -*- coding: utf-8 -*-
import os
import sys
import json
import tempfile
from openai import OpenAI

# Ensure backend package is importable when script run from project root
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    from backend.app.services.enhanced_dictionary import EnhancedDictionary
except ImportError as e:
    print("Failed to import EnhancedDictionary – run from project root. Error:", e)
    sys.exit(1)


def analyze_verse_directly(verse_text: str, verse_reference: str) -> dict:
    """Direct OpenAI analysis without any caching"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = f"""Analyze this Latin Vulgate verse with comprehensive interpretive layers:\n\nVerse: \"{verse_text}\"\nReference: {verse_reference}\n\nProvide a detailed JSON response with:\n    \"translations\": {{\n        \"spanish\": \"Spanish translation of the verse\",\n        \"english\": \"English translation of the verse\", \n        \"french\": \"French translation of the verse\",\n        \"portuguese\": \"Portuguese translation of the verse\",\n        \"italian\": \"Italian translation of the verse\",\n        \"russian\": \"Russian translation of the verse\"\n    }},\n\n1. WORD_ANALYSIS: For each word, provide:\n   - latin: the exact word as it appears\n   - definition: clear English definition\n   - etymology: word origin and development\n   - part_of_speech: grammatical category\n   - morphology: detailed grammatical analysis (case, number, tense, etc.)\n\n2. THEOLOGICAL_LAYER: 3-4 key theological insights about this verse\n\n3. SYMBOLIC_LAYER: 3-4 symbolic (e.g., Jungian or archetypal) insights drawing connections to the human psyche and inner life\n\n4. COSMOLOGICAL_HISTORICAL_LAYER: 3-4 insights comparing this verse with ancient Near-Eastern cosmologies or mythic motifs (e.g., creation out of chaos, combat myths), emphasizing how the biblical text re-frames them\n\nFormat as valid JSON:\n{{\n    \"word_analysis\": [\n        {{\n            \"latin\": \"word\",\n            \"definition\": \"meaning\",\n            \"etymology\": \"origin\",\n            \"part_of_speech\": \"noun/verb/etc\",\n            \"morphology\": \"detailed grammar\"\n        }}\n    ],\n    \"translations\": {{\n        \"spanish\": \"En el principio creó Dios los cielos y la tierra\",\n        \"english\": \"In the beginning God created the heaven and the earth\",\n        \"french\": \"Au commencement, Dieu créa le ciel et la terre\",\n        \"portuguese\": \"No princípio, Deus criou o céu e a terra\",\n        \"italian\": \"In principio Dio creò il cielo e la terra\",\n        \"russian\": \"В начале сотворил Бог небо и землю\"\n    }},\n    \"theological_layer\": [\n        \"theological insight 1\",\n        \"theological insight 2\",\n        \"theological insight 3\"\n    ],\n    \"symbolic_layer\": [\n        \"symbolic insight 1\",\n        \"symbolic insight 2\",\n        \"symbolic insight 3\"\n    ],\n    \"cosmological_historical_layer\": [\n        \"cosmological insight 1\",\n        \"cosmological insight 2\",\n        \"cosmological insight 3\"\n    ]\n}}"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a Latin scholar and theologian. Provide detailed, accurate analysis."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    
    result = json.loads(response.choices[0].message.content)
    return {
        "success": True,
        "word_analysis": result.get("word_analysis", []),
        "translations": result.get("translations", {}),
        "theological_layer": result.get("theological_layer", []),
        "symbolic_layer": result.get("symbolic_layer", []),
        "cosmological_historical_layer": result.get("cosmological_historical_layer", []),
        "source": "direct_openai"
    }


def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌  Please set the OPENAI_API_KEY environment variable.")
        sys.exit(1)

    # Get verse text from CLI or default to Genesis 1:1
    verse_text = " ".join(sys.argv[1:]).strip() if len(sys.argv) > 1 else "In principio creavit Deus caelum et terram"
    verse_reference = "Gn 1:1" if len(sys.argv) == 1 else "CLI_INPUT"

    print(f"🔍  Requesting analysis for: '{verse_text}' ({verse_reference})")

    # Get direct analysis without any caching
    result = analyze_verse_directly(verse_text, verse_reference)

    # Pretty-print key parts of the response
    if result.get("success"):
        print("\n=== Word Analysis ===")
        print(json.dumps(result.get("word_analysis", []), ensure_ascii=False, indent=2))

        if result.get("theological_layer"):
            print("\n=== Theological Layer ===")
            print("\n".join(result["theological_layer"]))
            
        if result.get("symbolic_layer"):
            print("\n=== Symbolic Layer (Jungian & Campbell) ===")
            print("\n".join(result["symbolic_layer"]))

        if result.get("cosmological_historical_layer"):
            print("\n=== Cosmological-Historical Layer ===")
            print("\n".join(result["cosmological_historical_layer"]))
            
        if result.get("source"):
            print(f"\n=== Source ===")
            print(f"Analysis source: {result['source']}")

        if result.get("translations"):
            print("\n=== Translations ===")
            for lang, txt in result["translations"].items():
                print(f"{lang.capitalize()}: {txt}")
    else:
        print("Analysis failed:", result.get("error", "Unknown error"))


if __name__ == "__main__":
    main() 