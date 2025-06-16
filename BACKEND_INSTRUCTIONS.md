# Vulgate Backend Instructions

## Overview
The Vulgate backend is a FastAPI-based REST API that provides services for Bible and Bhagavad Gita text analysis, dictionary lookups, audio generation, and verse analysis. It supports both Latin Bible (Vulgate) and Sanskrit Bhagavad Gita texts with advanced linguistic analysis capabilities.

## Project Structure
```
backend/
├── app/
│   ├── api/
│   │   └── api_v1/
│   │       ├── endpoints/          # API endpoint definitions
│   │       │   ├── analysis.py     # Verse analysis endpoints
│   │       │   ├── audio.py        # Audio generation/playback
│   │       │   ├── books.py        # Book management
│   │       │   ├── dictionary.py   # Dictionary and translation
│   │       │   ├── images.py       # Image generation/management
│   │       │   ├── texts.py        # Text retrieval (Bible/Gita)
│   │       │   ├── themes.py       # Theme analysis
│   │       │   ├── verses.py       # Verse-specific operations
│   │       │   ├── words.py        # Word analysis
│   │       │   └── users.py        # User management
│   │       └── api.py              # API router configuration
│   ├── core/
│   │   └── config.py               # Application configuration
│   ├── crud/                       # Database operations
│   ├── db/                         # Database models and setup
│   ├── models/                     # SQLAlchemy models
│   ├── schemas/                    # Pydantic schemas
│   ├── services/                   # Business logic services
│   ├── utils/                      # Utility functions
│   └── main.py                     # FastAPI application entry point
├── static/                         # Static file storage
├── requirements.txt                # Python dependencies
├── word_cache.db                   # Word analysis cache database
└── app.db                          # Main application database
```

## Prerequisites
- Python 3.9 or higher
- Virtual environment (recommended)
- SQLite (included with Python)
- OpenAI API key (optional, for enhanced analysis)

## Installation & Setup

### 1. Environment Setup
```bash
# Navigate to project root
cd /path/to/vulgate

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the project root:
```env
# OpenAI Configuration (optional)
OPENAI_API_KEY=your_openai_api_key_here

# RapidAPI Configuration (optional, for external Gita API)
RAPIDAPI_KEY=your_rapidapi_key_here

# Database Configuration (optional, uses defaults if not set)
SQLITE_DB_PATH=db/vulgate.db

# Security (change in production)
SECRET_KEY=your-secret-key-here
```

### 3. Database Initialization
```bash
# Initialize the main database
python backend/init_database.py

# The application will automatically create required tables on first run
```

## Running the Server

### Development Mode
```bash
# From project root
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

# Alternative with auto-reload
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
# Without auto-reload
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

# With multiple workers (for production)
gunicorn backend.app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Server Management
```bash
# Kill existing server processes
pkill -f uvicorn

# Start server in background
nohup python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &

# Check if server is running
curl http://localhost:8000/
```

## API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

### Main API Endpoints

#### Text Sources
- `GET /api/v1/texts/sources` - Get available text sources (bible, gita)
- `GET /api/v1/texts/{source}/{book}/{chapter}` - Get chapter verses
- `GET /api/v1/texts/{source}/{book}/{chapter}/{verse}` - Get specific verse

#### Books Management
- `GET /api/v1/books/` - List all books
- `GET /api/v1/books/abbr/{abbreviation}` - Get book by abbreviation
- `GET /api/v1/books/{book_id}` - Get book by ID

#### Dictionary & Translation
- `POST /api/v1/dictionary/translate` - Translate text
- `GET /api/v1/dictionary/stats` - Get dictionary statistics
- `POST /api/v1/dictionary/lookup` - Look up word definitions

#### Analysis
- `GET /api/v1/verses/analysis/{book}/{chapter}/{verse}` - Get verse analysis
- `POST /api/v1/analysis/queue` - Queue analysis job
- `GET /api/v1/analysis/queue` - Get analysis queue status

#### Audio
- `GET /api/v1/audio/{book}/{chapter}/{verse}` - Get verse audio
- `HEAD /api/v1/audio/{book}/{chapter}/{verse}` - Check audio availability

#### Images
- `GET /api/v1/images/{book}/{chapter}/{verse}` - Get verse images
- `POST /api/v1/images/generate` - Generate new images

## Database Management

### Database Files
- `app.db` - Main application database (books, verses, users)
- `word_cache.db` - Word analysis and translation cache
- `macronizer.db` - Latin macronization data

### Common Database Operations
```bash
# Check database contents
sqlite3 app.db ".tables"
sqlite3 app.db "SELECT * FROM books LIMIT 5;"

# Check Gita verses
sqlite3 app.db "SELECT COUNT(*) FROM verses WHERE book_id = 55;"

# Clear cache
rm word_cache.db  # Will be recreated automatically
```

### Adding New Texts

#### Bible Books
Books are automatically loaded from the database. To add new books, insert into the `books` table with appropriate abbreviations.

#### Bhagavad Gita
The Gita is stored as book ID 55 with abbreviation "a". Verses are stored in the standard `verses` table.

```bash
# Add Gita data (if not already present)
python download_gita_dependency.py
```

## Configuration

### Core Settings (backend/app/core/config.py)
- `API_V1_STR`: API version prefix ("/api/v1")
- `SQLITE_DB_PATH`: Database file location
- `AUDIO_STORAGE_PATH`: Audio files storage
- `OPENAI_API_KEY`: OpenAI integration
- `BACKEND_CORS_ORIGINS`: CORS allowed origins

### CORS Configuration
The server allows requests from:
- `http://localhost:3000` (React frontend)
- `http://127.0.0.1:3000`
- `http://localhost:3001`
- All origins in development (remove `"*"` in production)

## Services

### Enhanced Dictionary
Provides advanced Latin-English translation with:
- Word lookup and caching
- Morphological analysis
- Context-aware translations
- OpenAI-powered enhancements (optional)

### Audio Generation
- Text-to-speech for Latin verses
- Audio file caching
- Multiple voice options

### Analysis Engine
- Grammatical analysis
- Thematic analysis
- Symbolic/mythological insights
- Jungian psychological analysis

## Troubleshooting

### Common Issues

#### Server Won't Start
```bash
# Check if port is in use
lsof -i :8000

# Kill processes using the port
pkill -f uvicorn

# Check for Python path issues
which python
python --version
```

#### Database Errors
```bash
# Check database file permissions
ls -la *.db

# Recreate database
rm app.db word_cache.db
python backend/init_database.py
```

#### CORS Errors
- Ensure frontend URL is in CORS origins
- Check that requests include proper headers
- Verify API endpoints are correctly prefixed

#### Missing Dependencies
```bash
# Reinstall requirements
pip install -r backend/requirements.txt --force-reinstall

# Check for missing system dependencies
# On macOS: brew install ffmpeg
# On Ubuntu: apt-get install ffmpeg
```

### Logging
The server logs all requests and errors to the console. For production, configure proper logging:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Performance Optimization
- Use database connection pooling for high traffic
- Implement Redis caching for frequently accessed data
- Use CDN for static audio files
- Enable gzip compression for API responses

## Development

### Adding New Endpoints
1. Create endpoint function in appropriate file under `endpoints/`
2. Add route to `api.py`
3. Create corresponding CRUD operations in `crud/`
4. Define Pydantic schemas in `schemas/`
5. Update database models if needed in `models/`

### Testing
```bash
# Run basic API tests
curl http://localhost:8000/api/v1/texts/sources
curl http://localhost:8000/api/v1/books/

# Test specific endpoints
python test_api_verses.py
```

### Code Style
- Follow PEP 8 conventions
- Use type hints
- Document functions with docstrings
- Keep files under 800 lines (split if larger)

## Security Considerations

### Production Deployment
- Change default `SECRET_KEY`
- Remove `"*"` from CORS origins
- Use environment variables for sensitive data
- Enable HTTPS
- Implement rate limiting
- Add authentication for sensitive endpoints

### Database Security
- Use proper file permissions for database files
- Implement backup strategies
- Consider encryption for sensitive data

## Support

### API Documentation
Visit http://localhost:8000/docs for interactive API documentation.

### Error Codes
- `200`: Success
- `404`: Resource not found
- `422`: Validation error
- `500`: Internal server error

### Contact
For issues or questions, check the project repository or contact the development team. 