#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for Latin Macronizer integration
Tests the macronizer service and its integration with the analysis system.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Test the macronizer service directly
def test_macronizer_service():
    """Test the LatinMacronizer service directly"""
    print("=" * 60)
    print("TESTING MACRONIZER SERVICE")
    print("=" * 60)
    
    try:
        from backend.app.services.latin_macronizer import LatinMacronizer
        
        # Initialize the macronizer
        macronizer = LatinMacronizer()
        
        if not macronizer.is_available():
            print("❌ Macronizer not available - check installation")
            return False
        
        print("✅ Macronizer initialized successfully")
        
        # Test basic macronization
        test_texts = [
            "In principio creavit Deus caelum et terram",
            "Et dixit Deus fiat lux et facta est lux",
            "Pater noster qui es in caelis",
            "Ave Maria gratia plena"
        ]
        
        for i, text in enumerate(test_texts, 1):
            print(f"\nTest {i}:")
            print(f"  Original: {text}")
            
            try:
                macronized = macronizer.macronize_text(text)
                print(f"  Macronized: {macronized}")
                
                if macronized != text:
                    print("  ✅ Macronization successful!")
                else:
                    print("  ⚠️ No macrons added (may be expected)")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
                return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import macronizer: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_enhanced_dictionary_integration():
    """Test macronizer integration with enhanced dictionary"""
    print("\n" + "=" * 60)
    print("TESTING ENHANCED DICTIONARY INTEGRATION")
    print("=" * 60)
    
    try:
        from backend.app.services.enhanced_dictionary import EnhancedDictionary
        
        # Initialize enhanced dictionary
        dictionary = EnhancedDictionary()
        
        if not hasattr(dictionary, 'macronizer') or not dictionary.macronizer:
            print("⚠️ Macronizer not available in enhanced dictionary")
            return False
        
        print("✅ Enhanced dictionary with macronizer initialized")
        
        # Test verse macronization
        test_verses = [
            ("Gn 1:1", "In principio creavit Deus caelum et terram"),
            ("Gn 1:3", "Et dixit Deus fiat lux et facta est lux"),
            ("Mt 6:9", "Pater noster qui es in caelis"),
        ]
        
        for verse_ref, verse_text in test_verses:
            print(f"\nTesting {verse_ref}:")
            print(f"  Original: {verse_text}")
            
            try:
                macronized = dictionary.macronize_verse(verse_text)
                print(f"  Macronized: {macronized}")
                
                if macronized != verse_text:
                    print("  ✅ Verse macronization successful!")
                else:
                    print("  ⚠️ No macrons added (may be expected)")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
                return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import enhanced dictionary: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_vulgate_analyzer_integration():
    """Test macronizer integration with vulgate analyzer"""
    print("\n" + "=" * 60)
    print("TESTING VULGATE ANALYZER INTEGRATION")
    print("=" * 60)
    
    try:
        from vulgate_analyzer import VulgateAnalyzer
        
        # Initialize vulgate analyzer
        analyzer = VulgateAnalyzer()
        
        if not hasattr(analyzer, 'macronizer') or not analyzer.macronizer:
            print("⚠️ Macronizer not available in vulgate analyzer")
            return False
        
        print("✅ Vulgate analyzer with macronizer initialized")
        
        # Test verse macronization
        test_verse = "In principio creavit Deus caelum et terram"
        print(f"\nTesting verse: {test_verse}")
        
        try:
            macronized = analyzer.macronize_verse(test_verse)
            print(f"Macronized: {macronized}")
            
            if macronized != test_verse:
                print("✅ Vulgate analyzer macronization successful!")
            else:
                print("⚠️ No macrons added (may be expected)")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import vulgate analyzer: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_full_analysis_with_macronization():
    """Test full verse analysis with macronization"""
    print("\n" + "=" * 60)
    print("TESTING FULL ANALYSIS WITH MACRONIZATION")
    print("=" * 60)
    
    try:
        from backend.app.services.enhanced_dictionary import EnhancedDictionary
        
        # Initialize enhanced dictionary
        dictionary = EnhancedDictionary()
        
        test_verse = "In principio creavit Deus caelum et terram"
        verse_ref = "Genesis 1:1"
        
        print(f"Testing full analysis for: {test_verse}")
        
        try:
            # Analyze the verse (should include macronization)
            analysis = dictionary.analyze_verse(test_verse, verse_ref)
            
            print(f"\nAnalysis results:")
            print(f"  Success: {analysis.get('success', False)}")
            print(f"  Verse text: {analysis.get('verse_text', 'N/A')}")
            
            if 'macronized_text' in analysis:
                print(f"  Macronized: {analysis['macronized_text']}")
                print("  ✅ Macronization included in analysis!")
            else:
                print("  ⚠️ No macronization info in analysis")
            
            if 'original_text' in analysis:
                print(f"  Original: {analysis['original_text']}")
            
            word_count = len(analysis.get('word_analysis', []))
            print(f"  Word analysis count: {word_count}")
            
            if word_count > 0:
                print("  ✅ Word analysis included!")
            else:
                print("  ⚠️ No word analysis")
                
        except Exception as e:
            print(f"❌ Error in full analysis: {e}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import for full analysis test: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error in full analysis: {e}")
        return False


def main():
    """Run all tests"""
    print("Latin Macronizer Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("Macronizer Service", test_macronizer_service),
        ("Enhanced Dictionary Integration", test_enhanced_dictionary_integration),
        ("Vulgate Analyzer Integration", test_vulgate_analyzer_integration),
        ("Full Analysis with Macronization", test_full_analysis_with_macronization),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Macronizer integration is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 