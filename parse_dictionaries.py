#!/usr/bin/env python3
"""
Dictionary Parser for Latin XDXF Files

This script parses all XDXF dictionary files and creates a structured
database of Latin words with their definitions, etymologies, and
grammatical information.
"""

import xml.etree.ElementTree as ET
import json
import glob
import re
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class WordEntry:
    """Structure for a dictionary word entry"""
    latin: str
    definition: str
    etymology: str = ""
    part_of_speech: str = ""
    morphology: str = ""
    pronunciation: str = ""
    source_dictionary: str = ""
    raw_definition: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class XDXFParser:
    """Parser for XDXF dictionary files"""
    
    def __init__(self):
        self.word_database: Dict[str, WordEntry] = {}
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'total_entries': 0,
            'valid_entries': 0,
            'errors': 0
        }
    
    def clean_text(self, text: str) -> str:
        """Clean text by removing XML tags and normalizing whitespace"""
        if not text:
            return ""
        
        # Remove XML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # Remove special markers
        text = re.sub(r'⟪[^⟫]*⟫', '', text)
        return text
    
    def extract_part_of_speech(self, definition: str) -> str:
        """Extract part of speech from definition"""
        pos_patterns = [
            r'\b(noun|verb|adjective|adverb|preposition|conjunction|pronoun|interjection)\b',
            r'\b(substantive|verbum|nomen|adjectivum)\b',
            r'\(([^)]*(?:noun|verb|adj|adv|prep|conj|pron|interj)[^)]*)\)',
        ]
        
        for pattern in pos_patterns:
            match = re.search(pattern, definition, re.IGNORECASE)
            if match:
                return match.group(1).lower()
        
        return ""
    
    def extract_etymology(self, definition: str) -> str:
        """Extract etymology information from definition"""
        etymology_patterns = [
            r'from\s+([^;.,]+)',
            r'etymology[:\s]+([^;.,]+)',
            r'\(from\s+([^)]+)\)',
            r'<i>([^<]*(?:from|derives?|origin)[^<]*)</i>',
        ]
        
        for pattern in etymology_patterns:
            match = re.search(pattern, definition, re.IGNORECASE)
            if match:
                return self.clean_text(match.group(1))
        
        return ""
    
    def parse_xdxf_content(self, content: str, source_dict: str) -> List[WordEntry]:
        """Parse XDXF content and extract word entries"""
        entries = []
        
        try:
            # Find all article entries
            article_pattern = r'<ar>(.*?)</ar>'
            articles = re.findall(article_pattern, content, re.DOTALL)
            
            for article in articles:
                try:
                    # Extract key words (headwords)
                    key_pattern = r'<k[^>]*>([^<]+)</k>'
                    keys = re.findall(key_pattern, article, re.IGNORECASE)
                    
                    if not keys:
                        continue
                    
                    # Extract definition
                    def_pattern = r'<def[^>]*>(.*?)</def>'
                    definitions = re.findall(def_pattern, article, re.DOTALL)
                    
                    if not definitions:
                        # Try alternative patterns
                        def_pattern = r'<deftext[^>]*>(.*?)</deftext>'
                        definitions = re.findall(def_pattern, article, re.DOTALL)
                    
                    if not definitions:
                        continue
                    
                    # Process each key (headword) in this article
                    for key in keys:
                        key = self.clean_text(key).lower()
                        if not key or len(key) < 2:
                            continue
                        
                        # Combine all definitions for this entry
                        full_definition = " ".join(definitions)
                        clean_definition = self.clean_text(full_definition)
                        
                        if not clean_definition or len(clean_definition) < 3:
                            continue
                        
                        # Extract grammatical information
                        part_of_speech = self.extract_part_of_speech(clean_definition)
                        etymology = self.extract_etymology(clean_definition)
                        
                        # Create word entry
                        entry = WordEntry(
                            latin=key,
                            definition=clean_definition[:500],  # Limit length
                            etymology=etymology[:200],  # Limit length
                            part_of_speech=part_of_speech,
                            source_dictionary=source_dict,
                            raw_definition=full_definition[:1000]  # Keep some raw data
                        )
                        
                        entries.append(entry)
                        
                except Exception as e:
                    logger.warning(f"Error parsing article in {source_dict}: {e}")
                    self.stats['errors'] += 1
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing XDXF content from {source_dict}: {e}")
            self.stats['errors'] += 1
        
        return entries
    
    def parse_dictionary_file(self, file_path: str) -> List[WordEntry]:
        """Parse a single XDXF dictionary file"""
        entries = []
        dict_name = os.path.basename(os.path.dirname(file_path))
        
        try:
            logger.info(f"Parsing {dict_name}...")
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            entries = self.parse_xdxf_content(content, dict_name)
            logger.info(f"Extracted {len(entries)} entries from {dict_name}")
            
            self.stats['processed_files'] += 1
            self.stats['total_entries'] += len(entries)
            
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            self.stats['errors'] += 1
        
        return entries
    
    def merge_entries(self, entries: List[WordEntry]) -> Dict[str, WordEntry]:
        """Merge entries, preferring more detailed definitions"""
        merged = {}
        
        for entry in entries:
            key = entry.latin.lower()
            
            if key not in merged:
                merged[key] = entry
                self.stats['valid_entries'] += 1
            else:
                # Merge with existing entry, keeping the most detailed information
                existing = merged[key]
                
                # Prefer longer, more detailed definitions
                if len(entry.definition) > len(existing.definition):
                    existing.definition = entry.definition
                
                # Merge etymology if missing
                if not existing.etymology and entry.etymology:
                    existing.etymology = entry.etymology
                
                # Merge part of speech if missing
                if not existing.part_of_speech and entry.part_of_speech:
                    existing.part_of_speech = entry.part_of_speech
                
                # Add source dictionary info
                if entry.source_dictionary not in existing.source_dictionary:
                    existing.source_dictionary += f", {entry.source_dictionary}"
        
        return merged
    
    def parse_all_dictionaries(self, dictionaries_dir: str = "source/dictionaries") -> Dict[str, WordEntry]:
        """Parse all XDXF dictionary files in the directory"""
        all_entries = []
        
        # Find all XDXF files
        xdxf_files = glob.glob(os.path.join(dictionaries_dir, "*/dict.xdxf"))
        self.stats['total_files'] = len(xdxf_files)
        
        logger.info(f"Found {len(xdxf_files)} dictionary files")
        
        for file_path in xdxf_files:
            entries = self.parse_dictionary_file(file_path)
            all_entries.extend(entries)
        
        # Merge all entries
        logger.info("Merging entries...")
        self.word_database = self.merge_entries(all_entries)
        
        logger.info(f"Parsing complete. Statistics:")
        logger.info(f"  Total files: {self.stats['total_files']}")
        logger.info(f"  Processed files: {self.stats['processed_files']}")
        logger.info(f"  Total entries extracted: {self.stats['total_entries']}")
        logger.info(f"  Unique valid entries: {self.stats['valid_entries']}")
        logger.info(f"  Errors: {self.stats['errors']}")
        
        return self.word_database
    
    def save_to_json(self, output_file: str = "latin_dictionary.json"):
        """Save the parsed dictionary to JSON format"""
        logger.info(f"Saving dictionary to {output_file}...")
        
        # Convert to serializable format
        serializable_db = {
            word: entry.to_dict() 
            for word, entry in self.word_database.items()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_db, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Dictionary saved with {len(serializable_db)} entries")
    
    def save_for_frontend(self, output_file: str = "frontend/src/dictionary.json"):
        """Save dictionary in format optimized for frontend use"""
        logger.info(f"Saving frontend dictionary to {output_file}...")
        
        # Create simplified format for frontend
        frontend_db = {}
        for word, entry in self.word_database.items():
            frontend_db[word] = {
                "latin": entry.latin,
                "definition": entry.definition,
                "etymology": entry.etymology or "Etymology not available",
                "partOfSpeech": entry.part_of_speech or "unknown",
                "morphology": entry.morphology or "Analysis not available",
                "pronunciation": entry.pronunciation or ""
            }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(frontend_db, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Frontend dictionary saved with {len(frontend_db)} entries")
    
    def get_sample_entries(self, count: int = 10) -> List[WordEntry]:
        """Get a sample of parsed entries for inspection"""
        return list(self.word_database.values())[:count]

def main():
    """Main function to parse dictionaries"""
    parser = XDXFParser()
    
    # Parse all dictionaries
    word_db = parser.parse_all_dictionaries()
    
    # Save results
    parser.save_to_json()
    parser.save_for_frontend()
    
    # Show sample entries
    print("\nSample entries:")
    for entry in parser.get_sample_entries(5):
        print(f"\nWord: {entry.latin}")
        print(f"Definition: {entry.definition[:100]}...")
        print(f"Etymology: {entry.etymology}")
        print(f"Part of Speech: {entry.part_of_speech}")
        print(f"Source: {entry.source_dictionary}")

if __name__ == "__main__":
    main() 