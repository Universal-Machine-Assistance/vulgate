# -*- coding: utf-8 -*-
import os
import sys
import json
import requests
from datetime import datetime

def test_grammatical_relationships():
    """Test the new grammatical relationships analysis endpoint"""
    
    # Example Latin sentences for testing
    test_sentences = [
        {
            "sentence": "Plantáverat autem Dóminus Deus paradísum voluptátis a princípio: in quo pósuit hóminem quem formáverat.",
            "reference": "Gn 2:8",
            "description": "Genesis 2:8 - Complex sentence with relative clause"
        },
        {
            "sentence": "In princípio creávit Deus cǽlum et terram.",
            "reference": "Gn 1:1", 
            "description": "Genesis 1:1 - Simple sentence structure"
        },
        {
            "sentence": "Et dixit Deus: Fiat lux. Et facta est lux.",
            "reference": "Gn 1:3",
            "description": "Genesis 1:3 - Multiple clauses with direct speech"
        }
    ]
    
    # API endpoint
    url = "http://localhost:8000/api/v1/dictionary/analyze/grammar/relationships"
    
    print("🔍 Testing Grammatical Relationships Analysis")
    print("=" * 80)
    
    for i, test_case in enumerate(test_sentences, 1):
        print(f"\n📖 Test {i}: {test_case['description']}")
        print(f"Latin: {test_case['sentence']}")
        print(f"Reference: {test_case['reference']}")
        print("-" * 60)
        
        # Prepare request data
        payload = {
            "sentence": test_case["sentence"],
            "reference": test_case["reference"]
        }
        
        try:
            # Make API request
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    print("✅ Analysis successful!")
                    
                    # Display sentence structure overview
                    if "sentence_structure" in data:
                        structure = data["sentence_structure"]
                        print(f"\n🏗️  Sentence Structure:")
                        print(f"   Main Verb: {structure.get('main_verb', 'N/A')}")
                        print(f"   Subject: {structure.get('subject', 'N/A')}")
                        print(f"   Objects: {', '.join(structure.get('objects', []))}")
                        
                        if structure.get('clauses'):
                            print(f"   Clauses: {len(structure['clauses'])}")
                            for j, clause in enumerate(structure['clauses'], 1):
                                print(f"     {j}. {clause.get('type', 'unknown')} clause - {clause.get('description', 'no description')}")
                    
                    # Display syntax tree
                    if data.get("syntax_tree"):
                        print(f"\n🌳 Syntax Tree:")
                        print(f"   {data['syntax_tree']}")
                    
                    # Display word relationships
                    if "words" in data and data["words"]:
                        print(f"\n🔗 Word Relationships:")
                        for word_data in data["words"]:
                            word = word_data.get("word", "")
                            lemma = word_data.get("lemma", "")
                            function = word_data.get("grammatical_function", "")
                            pos = word_data.get("part_of_speech", "")
                            morphology = word_data.get("morphology", "")
                            
                            print(f"\n   📝 {word} ({lemma}) - {pos}")
                            print(f"      Function: {function}")
                            print(f"      Morphology: {morphology}")
                            
                            if word_data.get("relationships"):
                                print(f"      Relationships:")
                                for rel in word_data["relationships"]:
                                    rel_type = rel.get("type", "")
                                    target = rel.get("target_word", "")
                                    description = rel.get("description", "")
                                    print(f"        • {rel_type} → {target}: {description}")
                    
                    print(f"\n📊 Source: {data.get('source', 'unknown')}")
                    
                else:
                    print(f"❌ Analysis failed: {data.get('error', 'Unknown error')}")
            
            elif response.status_code == 429:
                print("⏱️  Rate limit exceeded. Please wait and try again.")
                
            else:
                print(f"❌ API Error {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            print("⏱️  Request timed out")
        except requests.exceptions.ConnectionError:
            print("🔌 Connection error - is the server running?")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "=" * 80)

def test_specific_sentence():
    """Test with a specific sentence provided by user"""
    sentence = input("\nEnter a Latin sentence to analyze: ").strip()
    if not sentence:
        print("No sentence provided.")
        return
    
    reference = input("Enter verse reference (optional): ").strip()
    
    url = "http://localhost:8000/api/v1/dictionary/analyze/grammar/relationships"
    
    payload = {
        "sentence": sentence,
        "reference": reference
    }
    
    print(f"\n🔍 Analyzing: {sentence}")
    print("-" * 60)
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Grammatical Relationships Analysis Test")
    print("Choose an option:")
    print("1. Run predefined test cases")
    print("2. Test specific sentence")
    print("3. Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        test_grammatical_relationships()
    elif choice == "2":
        test_specific_sentence()
    elif choice == "3":
        test_grammatical_relationships()
        test_specific_sentence()
    else:
        print("Invalid choice. Running predefined tests...")
        test_grammatical_relationships() 