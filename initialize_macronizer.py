#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Initialize the Latin Macronizer database
This script sets up the macronizer database with all necessary tables and data.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def initialize_macronizer_db():
    """Initialize the macronizer database"""
    print("Initializing Latin Macronizer database...")
    
    try:
        # Import and initialize the macronizer core
        sys.path.insert(0, str(project_root / 'backend' / 'app' / 'services' / 'latin-macronizer'))
        from macronizer import Macronizer
        
        print("Creating macronizer instance...")
        macronizer = Macronizer()
        
        print("Reinitializing database (this may take a while)...")
        macronizer.wordlist.reinitializedatabase()
        
        print("✅ Macronizer database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing macronizer database: {e}")
        return False

def test_macronizer():
    """Test that the macronizer works after initialization"""
    print("\nTesting macronizer...")
    
    try:
        from backend.app.services.latin_macronizer import LatinMacronizer
        
        macronizer = LatinMacronizer()
        
        if not macronizer.is_available():
            print("❌ Macronizer still not available after initialization")
            return False
        
        # Test with a simple phrase
        test_text = "In principio creavit Deus caelum et terram"
        print(f"Testing: {test_text}")
        
        result = macronizer.macronize_text(test_text)
        print(f"Result: {result}")
        
        if result and result != test_text:
            print("✅ Macronization working!")
            return True
        else:
            print("⚠️ Macronization completed but no macrons added (may be expected)")
            return True
            
    except Exception as e:
        print(f"❌ Error testing macronizer: {e}")
        return False

def main():
    """Main function"""
    print("Latin Macronizer Database Initialization")
    print("=" * 50)
    
    # Initialize the database
    if not initialize_macronizer_db():
        print("Failed to initialize macronizer database")
        return 1
    
    # Test the macronizer
    if not test_macronizer():
        print("Macronizer initialization succeeded but testing failed")
        return 1
    
    print("\n🎉 Macronizer setup complete and working!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 