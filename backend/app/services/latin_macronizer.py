#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Latin Macronizer Service
Wrapper for the latin-macronizer to integrate with the Vulgate analysis system.
"""

import os
import sys
import re
import tempfile
import sqlite3
from typing import Optional

# Add the latin-macronizer directory to path
MACRONIZER_DIR = os.path.join(os.path.dirname(__file__), 'latin-macronizer')
sys.path.insert(0, MACRONIZER_DIR)

# Import the macronizer classes
try:
    from latin_macronizer.macronizer import Macronizer as MacronizerCore
except ImportError:
    try:
        # Try direct import if the module is in the path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'latin-macronizer'))
        from macronizer import Macronizer as MacronizerCore
    except ImportError:
        # Fallback if we can't import the macronizer
        MacronizerCore = None


class LatinMacronizer:
    """Service wrapper for the latin-macronizer tool"""
    
    def __init__(self, database_path: Optional[str] = None):
        """Initialize the macronizer service"""
        self.database_path = database_path or "macronizer.db"
        self.macronizer = None
        self._initialize_macronizer()
    
    def _initialize_macronizer(self):
        """Initialize the macronizer core if available"""
        if MacronizerCore is None:
            print("Warning: Latin macronizer core not available")
            return
        
        try:
            self.macronizer = MacronizerCore()
        except Exception as e:
            print(f"Warning: Could not initialize macronizer: {e}")
            self.macronizer = None
    
    def macronize_text(self, latin_text: str, 
                      perform_utov: bool = False, 
                      perform_itoj: bool = False,
                      scan_meter: int = 0) -> str:
        """
        Macronize Latin text with proper long vowel markings
        
        Args:
            latin_text: The Latin text to macronize
            perform_utov: Convert u to v where appropriate
            perform_itoj: Convert i to j where appropriate  
            scan_meter: Meter type for scanning (0 = prose, 1 = dactylic hexameter, etc.)
        
        Returns:
            The macronized Latin text with proper macrons
        """
        if not self.macronizer or not latin_text.strip():
            return latin_text
        
        try:
            # Clean the input text
            text = latin_text.strip()
            
            # Set the text in the macronizer
            self.macronizer.settext(text)
            
            # Apply meter scanning if requested
            if scan_meter > 0:
                scansions = [
                    [],  # prose
                    [MacronizerCore.dactylichexameter],  # dactylic hexameters
                    [MacronizerCore.dactylichexameter, MacronizerCore.dactylicpentameter],  # elegiac distichs
                    [MacronizerCore.hendecasyllable],  # hendecasyllables
                    [MacronizerCore.iambictrimeter, MacronizerCore.iambicdimeter]  # iambic trimeter + dimeter
                ]
                if scan_meter < len(scansions):
                    self.macronizer.scan(scansions[scan_meter])
            
            # Get the macronized text
            macronized = self.macronizer.gettext(
                domacronize=True,
                alsomaius=False,
                performutov=perform_utov,
                performitoj=perform_itoj,
                markambigs=False
            )
            
            return macronized.strip()
            
        except Exception as e:
            print(f"Error macronizing text '{latin_text[:50]}...': {e}")
            return latin_text
    
    def macronize_verse(self, verse_text: str, meter_hint: Optional[str] = None) -> str:
        """
        Macronize a verse with optional meter detection
        
        Args:
            verse_text: The verse text to macronize
            meter_hint: Optional hint about the meter (prose, hexameter, elegiac, etc.)
        
        Returns:
            The macronized verse text
        """
        # Determine scan type based on meter hint
        scan_type = 0  # Default to prose
        
        if meter_hint:
            meter_lower = meter_hint.lower()
            if 'hexameter' in meter_lower or 'epic' in meter_lower:
                scan_type = 1
            elif 'elegiac' in meter_lower or 'distich' in meter_lower:
                scan_type = 2
            elif 'hendecasyllab' in meter_lower:
                scan_type = 3
            elif 'iambic' in meter_lower:
                scan_type = 4
        
        return self.macronize_text(verse_text, scan_meter=scan_type)
    
    def is_available(self) -> bool:
        """Check if the macronizer is available and working"""
        return self.macronizer is not None
    
    def test_macronizer(self) -> bool:
        """Test the macronizer with a simple example"""
        if not self.is_available():
            return False
        
        try:
            test_text = "In principio creavit Deus caelum et terram"
            result = self.macronize_text(test_text)
            return len(result) > 0 and result != test_text
        except Exception:
            return False 