# Vulgate Bible Translation App

A comprehensive digital research tool for analyzing the Latin Vulgate Bible with word-by-word analysis, multi-layered interpretations, and interactive features.

## 🎯 Project Overview

This research application provides:
- **Complete Vulgate text** with verse-by-verse navigation
- **Word-by-word Latin analysis** with morphology, etymology, and pronunciation
- **Multi-layered interpretation**:
  - Theological analysis
  - Jungian/symbolic interpretation  
  - Cosmological/historical context
- **Multi-language translations** (English, Spanish, French, Portuguese, Italian)
- **Interactive features**: Audio playback, word highlighting, grammar color-coding
- **URL-based navigation** with persistence on refresh
- **Embedded SQLite database** storing all analyses for research continuity

## 🗄️ Database-Driven Architecture

The app uses an embedded SQLite database (`word_cache.db`) that stores:
- **Individual word analyses** with full morphological data
- **Complete verse analyses** with all interpretation layers
- **Translations and theological insights**

This ensures:
- ✅ **Instant loading** of previously analyzed verses
- ✅ **Research continuity** - all work is preserved
- ✅ **Offline capability** once verses are analyzed
- ✅ **Complete Vulgate coverage** as analysis progresses

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+
- OpenAI API key (for new verse analysis)

### Backend Setup
```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Start the backend server
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend Setup
```bash
# Install dependencies
cd frontend
npm install

# Start the development server
npm start
```

The app will be available at `http://localhost:3000`

## 🔗 URL Structure

- **Root**: `/` → Redirects to Genesis 1:1
- **Book/Chapter/Verse**: `/Gn/1/1` → Genesis Chapter 1, Verse 1  
- **Direct navigation**: Type any URL like `/Mt/5/3` for Matthew 5:3

Examples:
- `/Gn/1/1` - Genesis 1:1 (Creation)
- `/Mt/5/3` - Matthew 5:3 (Beatitudes)
- `/Jo/3/16` - John 3:16 
- `/Ps/23/1` - Psalm 23:1

## 📊 Database Schema

### Word Cache (`word_cache`)
- Individual Latin words with morphological analysis
- Etymology, part of speech, pronunciation
- Source tracking (dictionary, AI analysis)

### Verse Analysis Cache (`verse_analysis_cache`)
- Complete verse analyses with all layers
- Multi-language translations
- Theological, Jungian, and cosmological interpretations
- JSON format for structured data storage

## 🎨 Features

### Interactive Word Analysis
- **Hover highlighting** with grammar color-coding
- **Click for details** - etymology, morphology, pronunciation
- **Grammar legend** showing part-of-speech colors
- **Synchronized selection** across verse text and breakdown

### Audio Integration
- **Word-by-word audio** playback (when available)
- **Sequential highlighting** as audio plays
- **Recording capability** for verse pronunciation

### Multi-Layered Interpretation
- **Theological Layer**: Traditional biblical scholarship
- **Jungian Layer**: Psychological and symbolic analysis
- **Cosmological Layer**: Historical and scientific context

### Smart Caching
- **Cache-first architecture** - no unnecessary API calls
- **Rate limiting protection** - built-in retry logic
- **Progressive enhancement** - analyze as you explore

## 🔧 Development

### Project Structure
```
vulgate/
├── backend/           # FastAPI Python backend
│   ├── app/          # API endpoints and core logic
│   └── enhanced_dictionary.py  # AI analysis engine
├── frontend/         # React TypeScript frontend
│   └── src/App.tsx   # Main application component
├── word_cache.db     # Embedded SQLite database
└── README.md         # This file
```

### Key Technologies
- **Backend**: FastAPI, SQLite, OpenAI GPT-4
- **Frontend**: React, TypeScript, React Router
- **Database**: SQLite with JSON fields for structured data
- **AI**: OpenAI for morphological analysis and interpretation

## 📈 Research Progress

The database grows progressively as you explore verses:
- Each analyzed verse is permanently cached
- Word-level analysis builds a comprehensive Latin dictionary
- Multi-layered interpretations create a rich theological resource

Track progress with: `GET /api/v1/dictionary/cache/verse-stats`

## 🤝 Contributing

This is a research project focused on building a complete digital interpretation of the Vulgate Bible. Contributions welcome for:
- Enhanced morphological analysis
- Additional interpretation layers
- UI/UX improvements
- Database optimizations

## 📝 License

Research/Educational use - Building a comprehensive digital Vulgate resource.

---

**Goal**: Create the most comprehensive digital analysis of the Latin Vulgate Bible, combining traditional scholarship with modern AI analysis and interactive technology. 