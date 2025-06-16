"""
Advanced Word Alignment Service using SimAlign and BERT embeddings
Provides semantic-based word alignment between source and target texts
"""

import re
import json
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

# Initialize availability flag
SIMALIGN_AVAILABLE = False

try:
    import torch
    from transformers import AutoTokenizer, AutoModel
    from simalign import SentenceAligner
    SIMALIGN_AVAILABLE = True
except ImportError:
    SIMALIGN_AVAILABLE = False
    logging.warning("SimAlign not available. Install with: pip install simalign torch transformers")

@dataclass
class WordAlignment:
    source_word: str
    source_index: int
    target_words: List[str]
    target_indices: List[int]
    confidence: float = 0.0

class AdvancedWordAligner:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.aligner = None
        self.tokenizer = None
        self.model = None
        
        if SIMALIGN_AVAILABLE:
            try:
                # Initialize SimAlign with multilingual BERT
                self.aligner = SentenceAligner(
                    model="bert",
                    token_type="bpe",
                    matching_methods="mai"  # Maximum Alignment Inference
                )
                self.logger.info("SimAlign initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize SimAlign: {e}")

    def align_words(self, source_text: str, target_text: str, source_language: str = "latin") -> Dict[str, List[WordAlignment]]:
        """
        Align words between source and target texts using semantic understanding
        
        Args:
            source_text: Original text (Latin/Sanskrit)
            target_text: Translated text
            source_language: Source language ("latin" or "sanskrit")
            
        Returns:
            Dictionary with alignment results for literal and dynamic translations
        """
        
        if not SIMALIGN_AVAILABLE:
            self.logger.warning("SimAlign not available, falling back to basic alignment")
            return self._fallback_alignment(source_text, target_text, source_language)
        
        try:
            # Clean and tokenize texts
            source_tokens = self._tokenize_text(source_text, source_language)
            target_tokens = self._tokenize_text(target_text, "target")
            
            # Get alignments using SimAlign
            alignments = self.aligner.get_word_aligns(source_tokens, target_tokens)
            
            # Convert to our format
            word_alignments = self._convert_alignments(
                source_tokens, target_tokens, alignments['mwmf']  # Many-to-many forward
            )
            
            return {
                "alignments": word_alignments,
                "method": "simalign_bert",
                "confidence": self._calculate_average_confidence(word_alignments)
            }
            
        except Exception as e:
            self.logger.error(f"SimAlign failed: {e}")
            return self._fallback_alignment(source_text, target_text, source_language)

    def _tokenize_text(self, text: str, language: str) -> List[str]:
        """Tokenize text considering language-specific characteristics"""
        
        # Remove punctuation and normalize
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Language-specific tokenization
        if language == "latin":
            # Handle Latin diacritics and compounds
            tokens = self._tokenize_latin(text)
        elif language == "sanskrit":
            # Handle Sanskrit transliteration
            tokens = self._tokenize_sanskrit(text)
        else:
            # Standard tokenization for target languages
            tokens = text.split()
        
        return [token for token in tokens if token.strip()]

    def _tokenize_latin(self, text: str) -> List[str]:
        """Latin-specific tokenization handling enclitics and compounds"""
        # Handle common Latin enclitics
        text = re.sub(r'(\w+)(que|ve|ne)(\s|$)', r'\1 \2\3', text)
        
        # Split on whitespace
        tokens = text.split()
        
        # Further processing for compound words if needed
        processed_tokens = []
        for token in tokens:
            # Handle specific Latin patterns
            if len(token) > 8 and any(x in token.lower() for x in ['ibus', 'orum', 'arum']):
                # Potential compound - keep as is for now
                processed_tokens.append(token)
            else:
                processed_tokens.append(token)
                
        return processed_tokens

    def _tokenize_sanskrit(self, text: str) -> List[str]:
        """Sanskrit-specific tokenization handling transliteration"""
        # Handle Sanskrit compounds and diacritics
        text = re.sub(r'([aeiouāīūēō])([kgṅcjñṭḍṇtdnpbmyrlvśṣsh])', r'\1 \2', text)
        
        return text.split()

    def _convert_alignments(self, source_tokens: List[str], target_tokens: List[str], 
                          alignments: List[Tuple[int, int]]) -> List[WordAlignment]:
        """Convert SimAlign output to our WordAlignment format"""
        
        # Group alignments by source word
        source_to_target = {}
        for src_idx, tgt_idx in alignments:
            if src_idx not in source_to_target:
                source_to_target[src_idx] = []
            source_to_target[src_idx].append(tgt_idx)
        
        word_alignments = []
        for src_idx in range(len(source_tokens)):
            target_indices = source_to_target.get(src_idx, [])
            target_words = [target_tokens[i] for i in target_indices if i < len(target_tokens)]
            
            # Calculate confidence based on alignment consistency
            confidence = self._calculate_alignment_confidence(src_idx, target_indices, len(target_tokens))
            
            word_alignments.append(WordAlignment(
                source_word=source_tokens[src_idx],
                source_index=src_idx,
                target_words=target_words,
                target_indices=target_indices,
                confidence=confidence
            ))
        
        return word_alignments

    def _calculate_alignment_confidence(self, src_idx: int, tgt_indices: List[int], tgt_len: int) -> float:
        """Calculate confidence score for an alignment"""
        if not tgt_indices:
            return 0.0
        
        # Factors affecting confidence:
        # 1. Number of target words (1-to-1 is most confident)
        # 2. Position consistency (closer positions are more likely)
        # 3. Word length similarity
        
        base_confidence = 1.0 / (1 + len(tgt_indices))  # Prefer 1-to-1 alignments
        
        # Position consistency bonus
        if tgt_indices:
            avg_tgt_pos = sum(tgt_indices) / len(tgt_indices)
            expected_pos = (src_idx / len(tgt_indices)) * tgt_len if tgt_len > 0 else 0
            position_diff = abs(avg_tgt_pos - expected_pos) / max(tgt_len, 1)
            position_bonus = max(0, 1 - position_diff)
            base_confidence += position_bonus * 0.3
        
        return min(1.0, base_confidence)

    def _calculate_average_confidence(self, alignments: List[WordAlignment]) -> float:
        """Calculate average confidence across all alignments"""
        if not alignments:
            return 0.0
        return sum(a.confidence for a in alignments) / len(alignments)

    def _fallback_alignment(self, source_text: str, target_text: str, source_language: str) -> Dict[str, Any]:
        """Fallback alignment when SimAlign is not available"""
        
        source_tokens = self._tokenize_text(source_text, source_language)
        target_tokens = self._tokenize_text(target_text, "target")
        
        # Simple position-based alignment with improvements
        alignments = []
        
        for i, source_word in enumerate(source_tokens):
            # Try to find semantic matches first
            target_matches = self._find_semantic_matches(source_word, target_tokens, source_language)
            
            if target_matches:
                target_words = [target_tokens[idx] for idx in target_matches]
                confidence = 0.7  # Medium confidence for semantic matches
            else:
                # Fall back to position-based alignment
                ratio = len(target_tokens) / len(source_tokens) if source_tokens else 1
                target_idx = min(int(i * ratio), len(target_tokens) - 1)
                target_matches = [target_idx] if target_idx >= 0 else []
                target_words = [target_tokens[target_idx]] if target_matches else []
                confidence = 0.3  # Low confidence for position-based
            
            alignments.append(WordAlignment(
                source_word=source_word,
                source_index=i,
                target_words=target_words,
                target_indices=target_matches,
                confidence=confidence
            ))
        
        return {
            "alignments": alignments,
            "method": "fallback_semantic",
            "confidence": self._calculate_average_confidence(alignments)
        }

    def _find_semantic_matches(self, source_word: str, target_tokens: List[str], source_language: str) -> List[int]:
        """Find potential semantic matches using heuristics"""
        
        matches = []
        source_lower = source_word.lower()
        
        # Common Latin-to-Spanish/English patterns
        if source_language == "latin":
            latin_patterns = {
                'deus': ['dios', 'god', 'divine'],
                'terra': ['tierra', 'earth', 'ground'],
                'caelum': ['cielo', 'heaven', 'sky'],
                'aqua': ['agua', 'water'],
                'ignis': ['fuego', 'fire'],
                'homo': ['hombre', 'man', 'human'],
                'femina': ['mujer', 'woman'],
                'rex': ['rey', 'king'],
                'regina': ['reina', 'queen']
            }
            
            # Check for direct matches
            for target_idx, target_word in enumerate(target_tokens):
                target_lower = target_word.lower()
                
                # Direct semantic mapping
                if source_lower in latin_patterns:
                    if any(pattern in target_lower for pattern in latin_patterns[source_lower]):
                        matches.append(target_idx)
                
                # Cognate detection (similar spelling)
                if self._is_likely_cognate(source_lower, target_lower):
                    matches.append(target_idx)
        
        return matches

    def _is_likely_cognate(self, word1: str, word2: str) -> bool:
        """Simple cognate detection based on string similarity"""
        if len(word1) < 3 or len(word2) < 3:
            return False
        
        # Calculate simple edit distance ratio
        from difflib import SequenceMatcher
        similarity = SequenceMatcher(None, word1, word2).ratio()
        
        return similarity > 0.6  # 60% similarity threshold

    def format_alignment_response(self, alignments_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format alignment data for API response"""
        
        alignments = alignments_data.get("alignments", [])
        
        formatted = []
        for alignment in alignments:
            formatted.append({
                "source_word": alignment.source_word,
                "source_index": alignment.source_index,
                "target_words": alignment.target_words,
                "target_indices": alignment.target_indices,
                "confidence": round(alignment.confidence, 3)
            })
        
        return {
            "alignments": formatted,
            "method": alignments_data.get("method", "unknown"),
            "average_confidence": round(alignments_data.get("confidence", 0.0), 3)
        }

    def format_alignment_for_frontend(self, literal_alignments: Dict[str, Any], 
                                    dynamic_alignments: Dict[str, Any],
                                    source_text: str) -> Dict[str, Any]:
        """Format alignments for frontend consumption as position-indexed arrays"""
        
        # Tokenize source text to get word count
        source_tokens = self._tokenize_text(source_text, "latin")
        word_count = len(source_tokens)
        
        # Initialize arrays for each word position with empty alignment objects
        literal_array = [{"target_words": [], "target_indices": [], "confidence": 0.0} for _ in range(word_count)]
        dynamic_array = [{"target_words": [], "target_indices": [], "confidence": 0.0} for _ in range(word_count)]
        
        # Fill literal alignments
        literal_aligns = literal_alignments.get("alignments", [])
        for alignment in literal_aligns:
            source_idx = alignment.get("source_index", 0)
            if 0 <= source_idx < word_count:
                literal_array[source_idx] = {
                    "target_words": alignment.get("target_words", []),
                    "target_indices": alignment.get("target_indices", []),
                    "confidence": alignment.get("confidence", 0.0)
                }
        
        # Fill dynamic alignments
        dynamic_aligns = dynamic_alignments.get("alignments", [])
        for alignment in dynamic_aligns:
            source_idx = alignment.get("source_index", 0)
            if 0 <= source_idx < word_count:
                dynamic_array[source_idx] = {
                    "target_words": alignment.get("target_words", []),
                    "target_indices": alignment.get("target_indices", []),
                    "confidence": alignment.get("confidence", 0.0)
                }
        
        return {
            "literal": literal_array,
            "dynamic": dynamic_array,
            "method": literal_alignments.get("method", "unknown"),
            "literal_confidence": literal_alignments.get("average_confidence", 0.0),
            "dynamic_confidence": dynamic_alignments.get("average_confidence", 0.0),
            "average_confidence": (
                (literal_alignments.get("average_confidence", 0.0) + 
                 dynamic_alignments.get("average_confidence", 0.0)) / 2
            )
        }

# Global instance
word_aligner = AdvancedWordAligner()

def get_word_aligner() -> AdvancedWordAligner:
    """Get the global word aligner instance"""
    return word_aligner 