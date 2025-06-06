# Vulgate Translation Project

A comprehensive digital platform for analyzing and translating the Latin Vulgate Bible using AI-powered linguistic analysis.

## Project Vision

This project aims to create a complete, intelligent translation system for the Vulgate Clementina (Latin Bible) that combines:

- **Morphological Analysis**: Deep grammatical breakdown of Latin words and their forms
- **AI-Enhanced Definitions**: OpenAI-powered word analysis with etymological insights
- **Multi-layered Interpretation**: Theological, Jungian/symbolic, and cosmological analysis layers
- **Complete Translation Coverage**: Working towards translating the entire Vulgate corpus
- **Persistent Data Storage**: All analyses are cached and stored for future reference

## Current Features

### 🔍 Word Analysis
- **Morphological Recognition**: Identifies Latin conjugations, declensions, and word forms
- **AI-Powered Definitions**: Fallback to OpenAI GPT-4 for unknown words
- **Etymology Tracking**: Word origins and linguistic development
- **Part of Speech Classification**: Automatic grammatical categorization
- **Smart Caching**: Local SQLite database prevents repeated API calls

### 📖 Verse Analysis
- **Complete Verse Processing**: Single API call for comprehensive analysis
- **Multi-language Translations**: English, Spanish, French, Portuguese, Italian
- **Theological Layer**: Religious and doctrinal interpretations
- **Jungian Layer**: Archetypal and psychological symbolism analysis
- **Cosmological Layer**: Historical context and ancient worldview insights

### 🎨 Interactive UI
- **Word Highlighting**: Visual grammar breakdown with color-coded parts of speech
- **Click-to-Define**: Interactive word lookup and selection
- **Grammar Legend**: Visual guide for grammatical categories
- **Hover Effects**: Real-time word highlighting and tooltips
- **Synchronized Selection**: Words selected in grammar breakdown highlight in verse text

### 💾 Data Persistence
- **Verse Analysis Cache**: Complete analyses stored in SQLite database
- **Word Definition Cache**: Individual word lookups cached for reuse
- **Progress Tracking**: Monitoring translation coverage across the entire Vulgate
- **API Rate Limiting**: Intelligent request management to prevent quota exhaustion

## Database Schema

### Word Cache
- Stores individual word definitions, etymologies, and morphological analysis
- Prevents redundant API calls for previously analyzed words

### Verse Analysis Cache
- Complete verse analyses including word breakdowns, translations, and interpretation layers
- Tracks analysis source (cache vs. fresh API call)
- Enables offline browsing of previously analyzed verses

### Progress Tracking
- Monitors which verses have been analyzed
- Tracks translation completion percentage
- Provides statistics on dictionary coverage

## API Architecture

### Consolidated Endpoints
- `/analyze/verse/complete` - Single call for complete verse analysis
- `/lookup/batch` - Efficient bulk word lookup
- `/cache/verse-stats` - Progress tracking and statistics

### Rate Limiting
- Exponential backoff retry logic
- Minimum time delays between API calls
- Error handling for quota limits
- Graceful degradation to cached data

## Technical Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLite**: Lightweight database for caching
- **OpenAI API**: GPT-4 for linguistic analysis
- **Pydantic**: Data validation and serialization

### Frontend
- **React + TypeScript**: Modern UI framework
- **Tailwind CSS**: Utility-first styling
- **FontAwesome**: Icon library for visual enhancement

### Data Processing
- **Unicode Normalization**: Handles Latin diacritical marks
- **Morphological Analysis**: Custom Latin grammar processing
- **JSON Caching**: Structured data storage for complex analyses

## Project Goals

### Immediate Objectives
1. **Complete Vulgate Coverage**: Analyze all 73 books of the Vulgate
2. **Multi-language Support**: Expand translation languages
3. **Audio Integration**: Pronunciation and audio playbook features
4. **Advanced Search**: Cross-reference and concordance features

### Long-term Vision
1. **Scholarly Resource**: Become a comprehensive tool for biblical scholarship
2. **Educational Platform**: Support Latin language learning and biblical studies
3. **Open Source Community**: Enable collaborative translation improvement
4. **Academic Integration**: Partner with theological institutions and universities

## Data Analysis Progress

The system tracks analysis progress across multiple dimensions:

- **Word Coverage**: Percentage of unique Vulgate words analyzed
- **Verse Coverage**: Number of verses with complete analysis
- **Book Completion**: Progress through all 73 biblical books
- **Translation Quality**: Confidence scores and source tracking

## Usage Statistics

Current implementation provides detailed statistics on:
- Total dictionary entries (main + cached)
- OpenAI API usage and rate limiting
- Cache hit ratios and performance metrics
- Recent analysis activity

## Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- OpenAI API key

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Environment Variables
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

## Contributing

This project welcomes contributions in:
- Latin linguistic expertise
- Biblical scholarship
- Software development
- UI/UX design
- Translation accuracy
- Performance optimization

## License

[License information to be added]

---

*"In principio erat Verbum"* - Working towards making the Word accessible through technology and scholarship. 