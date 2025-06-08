# Morphosyntactic Analysis Feature

## Overview

The Vulgate project now includes advanced **morphosyntactic analysis** capabilities that provide detailed grammatical breakdown of Latin sentences. This feature explains not only WHAT each word is, but WHY it has its specific ending and HOW it relates to other words in the sentence.

## Features

### 🔍 **Detailed Word Analysis**
- **Complete morphological breakdown**: case, number, gender, tense, mood, voice, person
- **Declension/Conjugation identification**: 1st, 2nd, 3rd, 4th, 5th declensions and conjugations
- **Ending explanations**: Detailed reasoning for why each word has its specific ending
- **Grammatical function**: Subject, object, predicate, modifier, etc.

### 🔗 **Relationship Analysis**
- **Subject-verb agreement**: Shows how subjects agree with verbs in person and number
- **Case usage explanations**: Why accusative for objects, ablative with prepositions, etc.
- **Dependency relationships**: Which words modify or depend on which other words
- **Agreement patterns**: Adjective-noun, article-noun agreements

### 🏗️ **Sentence Structure**
- **Main verb identification** with full conjugation details
- **Subject analysis** with case and agreement explanations
- **Object classification** (direct, indirect, prepositional)
- **Prepositional phrase analysis** with case requirements

## API Endpoint

### `POST /api/v1/dictionary/analyze/grammar/relationships`

**Request Body:**
```json
{
  "sentence": "In princípio creávit Deus cǽlum et terram.",
  "reference": "Gn 1:1"
}
```

**Response:**
```json
{
  "success": true,
  "sentence": "In princípio creávit Deus cǽlum et terram.",
  "verse_reference": "Gn 1:1",
  "words": [
    {
      "word": "creávit",
      "lemma": "creo",
      "position": 2,
      "part_of_speech": "verb",
      "morphology": {
        "tense": "perfect",
        "mood": "indicative", 
        "voice": "active",
        "person": "3rd",
        "number": "singular",
        "conjugation": "3rd"
      },
      "grammatical_function": "main verb",
      "ending_explanation": "The -ávit ending is characteristic of the perfect tense in the 3rd conjugation",
      "relationships": [
        {
          "type": "agrees_with",
          "target_word": "Deus",
          "target_position": 3,
          "description": "Subject 'Deus' agrees with verb 'creávit' in person and number"
        }
      ]
    }
  ],
  "sentence_structure": {
    "main_verb": {
      "word": "creávit",
      "person": "3rd",
      "number": "singular",
      "subject": "Deus"
    },
    "subject": {
      "word": "Deus", 
      "case": "nominative",
      "agrees_with_verb": "Subject 'Deus' agrees with verb 'creávit' in person and number"
    },
    "objects": [
      {
        "word": "cǽlum",
        "case": "accusative",
        "function": "direct_object"
      }
    ]
  },
  "morphological_summary": "Complete grammatical explanation..."
}
```

## Example Analysis

### Input: "In princípio creávit Deus cǽlum et terram." (Genesis 1:1)

### Word-by-Word Breakdown:

1. **creávit** (main verb)
   - **Morphology**: 3rd person singular perfect indicative active
   - **Conjugation**: 3rd conjugation (-ávit perfect ending)
   - **Subject**: Deus (agrees in person and number)
   - **Explanation**: "The -ávit ending is characteristic of the perfect tense in the 3rd conjugation"

2. **Deus** (subject)
   - **Morphology**: Nominative singular masculine
   - **Declension**: 2nd declension (-us ending)
   - **Function**: Subject of creávit
   - **Agreement**: Agrees with verb in 3rd person singular
   - **Explanation**: "In the nominative case, 'Deus' is the subject of the sentence"

3. **cǽlum** (direct object)
   - **Morphology**: Accusative singular neuter
   - **Declension**: 2nd declension (-um ending)
   - **Function**: Direct object of creávit
   - **Explanation**: "In the accusative case, 'cǽlum' is the direct object. 2nd declension due to -um ending"

4. **terram** (direct object)
   - **Morphology**: Accusative singular feminine
   - **Declension**: 1st declension (-am ending)
   - **Function**: Direct object of creávit
   - **Explanation**: "1st declension due to -am ending. Accusative for direct object"

## Usage Examples

### Command Line Testing
```bash
# Test with curl
curl -X POST http://localhost:8000/api/v1/dictionary/analyze/grammar/relationships \
  -H "Content-Type: application/json" \
  -d '{"sentence": "In princípio creávit Deus cǽlum et terram.", "reference": "Gn 1:1"}'

# Test with Python script
python test_grammar_relationships.py
```

### Web Interface
Open `grammar_relationships_demo.html` in a browser (when served by the web server) for an interactive interface.

## Integration

### Backend Integration
```python
from backend.app.services.enhanced_dictionary import EnhancedDictionary

enhanced_dict = EnhancedDictionary()
result = enhanced_dict.analyze_grammatical_relationships(
    "In princípio creávit Deus cǽlum et terram.",
    "Gn 1:1"
)
```

### Frontend Integration
```javascript
const response = await fetch('/api/v1/dictionary/analyze/grammar/relationships', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    sentence: "In princípio creávit Deus cǽlum et terram.",
    reference: "Gn 1:1"
  })
});
const analysis = await response.json();
```

## Technical Details

### AI Model
- **Primary Model**: GPT-4 with specialized Latin morphosyntax expertise
- **System Prompt**: Emphasizes detailed grammatical analysis and ending explanations
- **Temperature**: 0.2 (low for consistency)
- **Max Tokens**: 2000 (sufficient for detailed analysis)

### Response Structure
- **Structured morphology**: Organized by grammatical category
- **Relationship mapping**: Shows dependencies between words
- **Ending explanations**: Explains the "why" behind each grammatical form
- **Agreement analysis**: Details subject-verb, adjective-noun agreements

### Error Handling
- **Rate limiting**: Integrated with existing OpenAI rate limiting
- **Fallback handling**: Graceful degradation if AI analysis fails
- **Input validation**: Sentence length and format validation

## Benefits

### For Students
- **Learning tool**: Understand WHY Latin words have specific endings
- **Pattern recognition**: See how declensions and conjugations work in context
- **Relationship understanding**: Visualize grammatical dependencies

### For Scholars
- **Research tool**: Detailed morphosyntactic breakdown for academic work
- **Cross-referencing**: Compare grammatical patterns across verses
- **Validation**: Verify grammatical interpretations

### For Developers
- **Structured data**: JSON format for easy integration
- **Comprehensive**: All grammatical information in one response
- **Extensible**: Easy to add new analysis features

## Implementation Files

### Backend
- `backend/app/services/enhanced_dictionary.py`: Core analysis logic
- `backend/app/api/api_v1/endpoints/dictionary.py`: API endpoint

### Frontend
- `grammar_relationships_demo.html`: Web interface demo
- `test_grammar_relationships.py`: Command-line testing tool

### Dependencies
- `requirements.txt`: Updated with `requests==2.31.0` for testing

## Future Enhancements

### Planned Features
- **Syntax tree visualization**: Graphical representation of dependencies
- **Comparative analysis**: Side-by-side grammatical comparisons
- **Historical linguistics**: Etymology and semantic evolution
- **Scansion analysis**: Metrical analysis for poetry

### Integration Possibilities
- **Enhanced symbolic layer**: Combine with Jungian/Campbell analysis
- **Cross-linguistic**: Compare with Greek, Hebrew grammatical structures
- **Educational modules**: Interactive Latin grammar lessons

---

**Status**: ✅ **COMPLETE AND WORKING**

The morphosyntactic analysis feature is fully implemented, tested, and ready for production use. It provides comprehensive grammatical analysis that explains both the structure and reasoning behind Latin grammatical forms. 