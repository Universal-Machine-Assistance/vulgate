# Bhagavad Gita Integration Guide

## Overview

This integration adds support for the Bhagavad Gita alongside the existing Vulgate Bible, using the same database structure and providing unified API endpoints. The system fetches data from the [Bhagavad Gita RapidAPI](https://rapidapi.com/bhagavad-gita-bhagavad-gita-default/api/bhagavad-gita3) and caches it locally for performance.

## 🙏 Acknowledgments

This integration would not be possible without the incredible work of the **Ved Vyas Foundation** and their amazing open-source contributions:

### Special Thanks to [@gita](https://github.com/gita) Organization

The [@gita](https://github.com/gita) organization (Ved Vyas Foundation) is a non-profit project dedicated to making the transcendental wisdom from Indian scriptures accessible to anyone, anywhere, anytime. Their mission aligns perfectly with our goal of providing global access to sacred texts.

### Special Thanks to [@gita/BhagavadGita](https://github.com/gita/BhagavadGita)

The [@gita/BhagavadGita](https://github.com/gita/BhagavadGita) project is "A non-profit initiative to help spread the transcendental wisdom from the Bhagavad Gita to people around the world." This project has been instrumental in:

- **Creating Open APIs**: Their [bhagavad-gita-api](https://github.com/gita/bhagavad-gita-api) provides the foundation for programmatic access to Bhagavad Gita text
- **JSON Data Formats**: Their [gita](https://github.com/gita/gita) repository provides Bhagavad Gita in structured JSON format
- **Modern Applications**: Projects like [Bhagavad-Gita-AI](https://github.com/gita/Bhagavad-Gita-AI) (GitaGPT) and [Bhagavad-Gita-App](https://github.com/gita/Bhagavad-Gita-App) show innovative ways to make ancient wisdom accessible
- **Web Platform**: [BhagavadGita.io](https://bhagavadgita.io) provides a beautiful, accessible interface to the sacred text

### Why This Project is Amazing

The [@gita](https://github.com/gita) organization has created an entire ecosystem around making sacred texts accessible:

- **🌍 Global Accessibility**: Making ancient wisdom available to anyone, anywhere, anytime
- **💻 Developer-Friendly**: Open APIs and JSON data formats for easy integration
- **🤖 AI Integration**: ChatGPT-style interfaces for interactive learning
- **📱 Multi-Platform**: Web, mobile, and API access
- **🔓 Open Source**: All projects are open-source under permissive licenses
- **🎯 Non-Profit Mission**: Purely focused on spreading wisdom, not profit

**Without their foundational work in digitizing, structuring, and providing API access to the Bhagavad Gita, this integration would not be possible.** We are deeply grateful for their service to the global community.

---

## Setup

### 1. Environment Configuration

You need to configure your RapidAPI key in the `.env` file:

```bash
# Add to your .env file
RAPIDAPI_KEY=your_rapidapi_key_here
```

Get your RapidAPI key from: https://rapidapi.com/bhagavad-gita-bhagavad-gita-default/api/bhagavad-gita3

### 2. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 3. Run Database Migration

```bash
# Run the migration to add source fields to books table
alembic upgrade head
```

### 4. Automated Setup

Alternatively, use the setup script:

```bash
python setup_gita_integration.py
```

## API Endpoints

### Unified Structure Philosophy

This integration follows a **consistent URL structure** for all sacred texts: `/{source}/{book_abbr}/{chapter}/{verse}`. This unified approach:

- **🎯 Simplifies Logic**: No special cases or different handling needed
- **🔄 Maintains Consistency**: All texts follow the same pattern
- **🚀 Enables Expansion**: Easy to add other texts in the future
- **🧹 Reduces Complexity**: One data model, one set of endpoints

The Bhagavad Gita uses **"a"** as its book abbreviation to maintain this consistent structure, treating it as a single "book" within the gita source.

### Unified Text API

#### Bible Endpoints

- **Get Bible Chapter**: `GET /api/v1/texts/bible/{abbr}/{chapter}`
  - Example: `/api/v1/texts/bible/Gn/1` (Genesis Chapter 1)
  
- **Get Bible Verse**: `GET /api/v1/texts/bible/{abbr}/{chapter}/{verse}`
  - Example: `/api/v1/texts/bible/Gn/1/1` (Genesis 1:1)

#### Bhagavad Gita Endpoints (Unified Structure)

- **Get Gita Chapter**: `GET /api/v1/texts/gita/a/{chapter}`
  - Example: `/api/v1/texts/gita/a/1` (Bhagavad Gita Chapter 1)
  
- **Get Gita Verse**: `GET /api/v1/texts/gita/a/{chapter}/{verse}`
  - Example: `/api/v1/texts/gita/a/1/1` (Bhagavad Gita Chapter 1, Verse 1)

**Note**: The "a" in the Gita URLs represents the single "book" of the Bhagavad Gita, maintaining the consistent `/{source}/{book}/{chapter}/{verse}` pattern.

#### Utility Endpoints

- **Get Available Sources**: `GET /api/v1/texts/sources`
  - Returns: `["bible", "gita"]`

- **Get Source Info**: `GET /api/v1/texts/sources/{source}/info`
  - Example: `/api/v1/texts/sources/gita/info`

## Database Schema Changes

### Books Table

Added new fields to support multiple text sources:

```sql
-- New columns added to books table
source VARCHAR(50) DEFAULT 'bible' NOT NULL  -- 'bible' or 'gita'
source_id VARCHAR(50) NULL                   -- external API identifier
```

### Data Flow

1. **Bible Data**: Continues to work as before, sourced from local database
2. **Gita Data**: 
   - First checks local cache
   - If not cached, fetches from RapidAPI
   - Caches locally for future requests
   - Uses same verse/book structure as Bible

## Usage Examples

### Fetch Genesis 1:1 (Bible)
```bash
curl "http://localhost:8000/api/v1/texts/bible/Gn/1/1"
```

### Fetch Bhagavad Gita Chapter 1, Verse 1 (Unified Structure)
```bash
curl "http://localhost:8000/api/v1/texts/gita/a/1/1"
```

### Get All Verses from Bhagavad Gita Chapter 2 (Unified Structure)
```bash
curl "http://localhost:8000/api/v1/texts/gita/a/2"
```

### Get Available Text Sources
```bash
curl "http://localhost:8000/api/v1/texts/sources"
```

### Comparison: Consistent URL Patterns
```bash
# Bible: Genesis 1:1
curl "http://localhost:8000/api/v1/texts/bible/Gn/1/1"

# Gita: Chapter 1, Verse 1 (note the "a" book abbreviation)
curl "http://localhost:8000/api/v1/texts/gita/a/1/1"

# Both follow: /{source}/{book_abbr}/{chapter}/{verse}
```

## Frontend Integration

The unified structure makes frontend development incredibly simple - the same components work for both texts:

```javascript
// Bible verse
const bibleVerse = await fetch('/api/v1/texts/bible/Gn/1/1');

// Gita verse (note the "a" book abbreviation)
const gitaVerse = await fetch('/api/v1/texts/gita/a/1/1');

// Both return the same verse structure:
// {
//   "id": number,
//   "book_id": number,
//   "chapter": number,
//   "verse_number": number,
//   "text": "string",
//   "translation": "string",
//   "created_at": "datetime",
//   "updated_at": "datetime"
// }
```

### Frontend Code Example

```javascript
// Generic function that works for both Bible and Gita
async function getVerse(source, bookAbbr, chapter, verse) {
  const response = await fetch(`/api/v1/texts/${source}/${bookAbbr}/${chapter}/${verse}`);
  return response.json();
}

// Usage examples
const genesis = await getVerse('bible', 'Gn', 1, 1);
const gita = await getVerse('gita', 'a', 1, 1);  // "a" is the Gita book abbreviation

// Same function, same structure, no special cases needed!
```

## Caching Strategy

- **Bible**: Served from local database (no API calls)
- **Gita**: 
  - First request: Fetches from RapidAPI and caches locally
  - Subsequent requests: Served from local cache
  - Cache is persistent across server restarts

## Error Handling

The system gracefully handles:
- Missing RapidAPI configuration
- API timeouts and failures
- Invalid chapter/verse numbers
- Network connectivity issues

## Configuration

### Environment Variables

```bash
# Required for Bhagavad Gita integration
RAPIDAPI_KEY=your_rapidapi_key_here

# Existing configuration
DATABASE_URL=sqlite:///./app.db
OPENAI_API_KEY=your_openai_key_here
```

### RapidAPI Limits

Be aware of your RapidAPI subscription limits. The free tier typically allows a limited number of requests per month.

## Monitoring

The system logs all API interactions and caching activities. Monitor your logs for:
- API call frequency
- Cache hit/miss ratios
- Error rates
- Response times

## Future Enhancements

Possible extensions to this integration:
- Support for additional text sources
- Batch caching of entire Gita at startup
- Multilingual support for Gita translations
- Cross-referencing between Bible and Gita verses
- Unified search across both texts 