# Vulgate Word Lookup Implementation Guide

## Overview

This guide explains how to implement clickable word functionality in your Vulgate application, allowing users to click on any Latin word (like "deus") to get its definition and see all verse occurrences in the database.

## Features Implemented

✅ **Word Definition Lookup** - Get comprehensive word information including etymology, morphology, and pronunciation  
✅ **Verse Occurrence Search** - Find all verses containing a specific word  
✅ **Clickable Word Interface** - Interactive HTML/JS demo showing how to implement word clicking  
✅ **Database Relationships** - Word-verse relationship tracking  
✅ **API Endpoints** - RESTful endpoints for all word lookup functionality  

## Implementation Steps

### 1. Database Setup

Your database already has the necessary tables:
- `words` - Stores Latin words with definitions
- `verses` - Contains all biblical verses  
- `verse_words` - Junction table linking words to verses with position tracking
- `books` - Biblical books information

### 2. Populate Word-Verse Relationships

First, ensure your database has word-verse relationships populated:

```bash
# Run the population script
python populate_word_relationships.py

# Or just verify existing relationships
python populate_word_relationships.py --verify-only
```

This will:
- Extract all words from verse texts
- Create Word records for unique words
- Track word frequency across the corpus
- Link words to verses with position information

### 3. API Endpoints

The following endpoints are now available:

#### Comprehensive Word Information
```http
GET /api/v1/words/{word}
```
Returns complete word information including definition and verse occurrences.

**Parameters:**
- `include_verses` (bool, default: true) - Include verse occurrences
- `limit_verses` (int, default: 100) - Max verses to return

**Example:**
```bash
curl "http://localhost:8000/api/v1/words/deus?limit_verses=10"
```

**Response:**
```json
{
  "word": "deus",
  "latin": "Deus",
  "definition": "God, deity, divine being...",
  "part_of_speech": "noun",
  "morphology": "masculine, 2nd declension",
  "etymology": "From Proto-Indo-European *deiwos...",
  "source": "enhanced_dictionary",
  "confidence": 0.95,
  "verse_count": 1247,
  "verses": [
    {
      "verse_reference": "Genesis 1:1",
      "verse_text": "In principio creavit Deus caelum et terram",
      "position": 4,
      "book_name": "Genesis",
      "chapter": 1,
      "verse_number": 1
    }
  ]
}
```

#### Word Definition Only
```http
GET /api/v1/words/{word}/definition
```
Returns just the word definition for quick lookups.

#### Verse Occurrences with Pagination
```http
GET /api/v1/words/{word}/verses
```
Returns paginated verse occurrences.

**Parameters:**
- `skip` (int, default: 0) - Number of verses to skip
- `limit` (int, default: 100) - Max verses per page
- `book_filter` (str, optional) - Filter by book name

### 4. Frontend Implementation

#### HTML Structure
```html
<!-- Make words clickable -->
<span class="clickable-word" data-word="deus">Deus</span>

<!-- Word information panel -->
<div id="wordInfo" class="word-info">
    <div id="wordInfoContent"></div>
</div>
```

#### JavaScript Integration
```javascript
// Add click handlers to words
document.querySelectorAll('.clickable-word').forEach(word => {
    word.addEventListener('click', function() {
        const wordText = this.getAttribute('data-word');
        lookupWord(wordText);
    });
});

// Lookup word via API
async function lookupWord(word) {
    const response = await fetch(`/api/v1/words/${word}`);
    const data = await response.json();
    displayWordInfo(data);
}
```

#### CSS Styling
```css
.clickable-word {
    cursor: pointer;
    color: #8B4513;
    font-weight: bold;
    text-decoration: underline;
    transition: all 0.3s ease;
}

.clickable-word:hover {
    background-color: #FFE4B5;
    padding: 2px 4px;
    border-radius: 3px;
}

.word-info {
    background: #fff8dc;
    border: 2px solid #D2B48C;
    border-radius: 8px;
    padding: 20px;
}
```

### 5. Testing the Implementation

#### Test API Endpoints
```bash
# Test multiple words
python test_word_lookup.py deus verbum jesus

# Test single word
python test_word_lookup.py deus
```

#### Manual API Testing
```bash
# Get word info
curl "http://localhost:8000/api/v1/words/deus"

# Get definition only
curl "http://localhost:8000/api/v1/words/deus/definition"

# Get verses with pagination
curl "http://localhost:8000/api/v1/words/deus/verses?limit=5"
```

#### Demo Page
Open `word_lookup_demo.html` in your browser to see a working example of clickable words with definition popups and verse occurrences.

## Integration with Your Frontend

### React/Vue.js Integration
```javascript
// Example React component
const ClickableWord = ({ word, children }) => {
    const [wordInfo, setWordInfo] = useState(null);
    const [showInfo, setShowInfo] = useState(false);
    
    const handleClick = async () => {
        const response = await fetch(`/api/v1/words/${word}`);
        const data = await response.json();
        setWordInfo(data);
        setShowInfo(true);
    };
    
    return (
        <>
            <span 
                className="clickable-word" 
                onClick={handleClick}
            >
                {children}
            </span>
            {showInfo && <WordInfoModal word={wordInfo} onClose={() => setShowInfo(false)} />}
        </>
    );
};
```

### Server-Side Rendering
For SSR frameworks, make sure to:
1. Generate verse HTML with `data-word` attributes on each word
2. Add client-side JavaScript for click handling
3. Use progressive enhancement for better UX

## Advanced Features

### 1. Word Highlighting in Verses
When showing occurrences, highlight the searched word:
```javascript
function highlightWordInText(text, word) {
    const regex = new RegExp(`\\b${word}\\b`, 'gi');
    return text.replace(regex, match => 
        `<span class="highlighted-word">${match}</span>`
    );
}
```

### 2. Related Words
Extend the API to include related words (synonyms, word family):
```sql
-- Query related words
SELECT rw.latin_text, wr.relationship_type 
FROM word_relationships wr
JOIN words rw ON wr.related_word_id = rw.id
WHERE wr.word_id = (SELECT id FROM words WHERE latin_text = 'deus');
```

### 3. Word Statistics
Show frequency and difficulty metrics:
```json
{
    "word": "deus",
    "frequency": 1247,
    "difficulty_level": 2,
    "books_count": 66,
    "most_common_book": "Psalms"
}
```

### 4. Search Suggestions
Implement fuzzy matching for misspelled words:
```python
# Use difflib or Levenshtein distance
import difflib

def suggest_words(input_word, all_words, limit=5):
    matches = difflib.get_close_matches(input_word, all_words, limit)
    return matches
```

## Performance Considerations

### Database Optimization
- Index `word_latin_text` for fast word lookups
- Index `verse_id, word_id` for relationship queries
- Consider full-text search for complex queries

### Caching
- Cache frequent word definitions in memory
- Use Redis for API response caching
- Implement browser-side caching for definitions

### Pagination
- Always use pagination for verse occurrences
- Default to 50-100 verses per page
- Implement infinite scroll for better UX

## Troubleshooting

### Common Issues

1. **No word occurrences found**
   - Run `populate_word_relationships.py` to ensure database is populated
   - Check word normalization (case sensitivity, punctuation)

2. **API connection errors**
   - Verify backend server is running on correct port
   - Check CORS settings for frontend integration

3. **Slow word lookup**
   - Add database indexes on frequently queried columns
   - Implement caching for common words

4. **Memory issues during population**
   - Process verses in smaller batches
   - Use database transactions wisely

### Database Checks
```sql
-- Check word-verse relationships
SELECT COUNT(*) FROM verse_words;

-- Check word frequencies
SELECT latin_text, frequency FROM words ORDER BY frequency DESC LIMIT 10;

-- Check verse coverage
SELECT COUNT(DISTINCT verse_id) FROM verse_words;
```

## Next Steps

1. **Integrate with your main application** - Replace the demo HTML with your actual verse display components
2. **Add authentication** - Protect API endpoints if needed
3. **Implement caching** - Add Redis or in-memory caching for performance
4. **Add analytics** - Track which words users look up most
5. **Enhance UI** - Add loading states, animations, and better error handling
6. **Mobile optimization** - Ensure touch-friendly interactions on mobile devices

## API Documentation

Full API documentation is available at `/docs` when your FastAPI server is running. This includes interactive testing capabilities and detailed parameter descriptions.

---

*Haec implementatio auxilium dat ad verba Latina melius intelligenda et contextum biblicum explorandum.* 

This implementation helps in better understanding Latin words and exploring biblical context. 