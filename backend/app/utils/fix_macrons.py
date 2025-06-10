#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix Macrons Utility
Converts acute accents (´) to proper macrons (¯) in Latin text files.
"""

import re
from pathlib import Path

def fix_acute_to_macrons(text: str) -> str:
    """
    Convert acute accents to proper macrons in Latin text.
    
    Args:
        text: The text containing acute accents
        
    Returns:
        The text with proper macrons
    """
    # Map acute accented vowels to macronized vowels
    acute_to_macron = {
        # Lowercase
        'á': 'ā',
        'é': 'ē', 
        'í': 'ī',
        'ó': 'ō',
        'ú': 'ū',
        'ý': 'ȳ',
        # Uppercase
        'Á': 'Ā',
        'É': 'Ē',
        'Í': 'Ī', 
        'Ó': 'Ō',
        'Ú': 'Ū',
        'Ý': 'Ȳ',
        # Special cases for æ and œ ligatures
        'ǽ': 'ǣ',  # æ with acute to æ with macron
        'Ǽ': 'Ǣ',  # Æ with acute to Æ with macron
        'ǿ': 'ȭ',  # œ with acute to œ with macron  
        'Ǿ': 'Ȭ',  # Œ with acute to Œ with macron
    }
    
    # Apply all replacements
    for acute, macron in acute_to_macron.items():
        text = text.replace(acute, macron)
    
    return text

def fix_vulgate_source_file():
    """Fix the source Vulgate file to use proper macrons."""
    source_file = Path("/Users/guillermomolina/dev/vulgate/source/vulgate_with_accents.txt")
    backup_file = Path("/Users/guillermomolina/dev/vulgate/source/vulgate_with_accents_backup.txt")
    
    if not source_file.exists():
        print(f"Error: Source file not found at {source_file}")
        return False
    
    print(f"Reading source file: {source_file}")
    
    # Read the original file
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create backup
    print(f"Creating backup: {backup_file}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Fix the macrons
    print("Converting acute accents to proper macrons...")
    fixed_content = fix_acute_to_macrons(content)
    
    # Count changes made
    lines_changed = 0
    original_lines = content.split('\n')
    fixed_lines = fixed_content.split('\n')
    
    for i, (orig, fixed) in enumerate(zip(original_lines, fixed_lines)):
        if orig != fixed:
            lines_changed += 1
            if lines_changed <= 5:  # Show first 5 changes as examples
                print(f"  Line {i+1}: '{orig[:50]}...' -> '{fixed[:50]}...'")
    
    print(f"Total lines changed: {lines_changed}")
    
    # Write the fixed content
    print(f"Writing fixed content to: {source_file}")
    with open(source_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("✅ Macron fix completed successfully!")
    print("📝 Original file backed up as vulgate_with_accents_backup.txt")
    return True

def fix_text_sample(text: str) -> None:
    """Fix a sample text and show the changes."""
    print(f"Original: {text}")
    fixed = fix_acute_to_macrons(text)
    print(f"Fixed:    {fixed}")

if __name__ == "__main__":
    print("Latin Macron Fixer")
    print("=" * 50)
    
    # Test with the specific example from the user
    print("\nTesting with sample text:")
    fix_text_sample("In princípio creávit Deus cælum, et terram.")
    
    print("\n" + "=" * 50)
    print("Fixing source file...")
    
    if fix_vulgate_source_file():
        print("\n🎉 All done! The source file now uses proper macrons.")
        print("   You may need to re-run the database migration to update the stored verses.")
    else:
        print("\n❌ Failed to fix source file.") 