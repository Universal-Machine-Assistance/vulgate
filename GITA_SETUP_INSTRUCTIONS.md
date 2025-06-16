# Bhagavad Gita Integration Setup

This document provides instructions for integrating Bhagavad Gita data into your Vulgate application using the dependency downloader script.

## Overview

The integration includes:
- **Automated downloader** that fetches data from the official [Bhagavad Gita GitHub repository](https://github.com/gita/BhagavadGita)
- **Database schema fixes** to ensure compatibility
- **Sample verses** with Sanskrit, transliteration, and English translations
- **Unified API structure** consistent with Bible endpoints

## Quick Setup

### Option 1: Automated Script (Recommended)

```bash
# Run the comprehensive downloader script
python download_gita_dependency.py
```

This script will:
1. 🔧 Fix database schema automatically
2. 📥 Download data from the official Gita repository
3. 🌐 Try multiple API sources as fallback
4. 💾 Integrate data into your existing database
5. ✅ Verify the integration

### Option 2: Manual Database Setup

If the automated script doesn't work due to environment issues:

```bash
# Open SQLite database
sqlite3 db/vulgate.db

# Run the manual setup commands
.read manual_gita_setup.sql

# Exit SQLite
.quit
```

## What Gets Installed

### Database Changes
- **Books table**: Adds `abbreviation`, `updated_at`, `source`, `source_id` columns
- **Cache tables**: Adds `language_code` column (fixes server startup error)
- **Bhagavad Gita book**: Added with abbreviation "a" and source "gita"
- **Sample verses**: Key verses from Chapters 1-4 with Sanskrit, transliteration, and translations

### API Endpoints Available After Setup

```bash
# List all text sources (should include "gita")
curl http://localhost:8000/api/v1/texts/sources

# Get Gita chapter 2 (all verses)
curl http://localhost:8000/api/v1/texts/gita/a/2

# Get specific verse (Chapter 2, Verse 47 - famous karma yoga verse)
curl http://localhost:8000/api/v1/texts/gita/a/2/47

# Get Chapter 4, Verse 7-8 (Krishna's incarnation promise)
curl http://localhost:8000/api/v1/texts/gita/a/4/7
curl http://localhost:8000/api/v1/texts/gita/a/4/8
```

## Unified API Structure

The integration maintains consistency with your existing Bible API:

- **Bible**: `/api/v1/texts/bible/Gn/1/1` (Genesis 1:1)
- **Gita**: `/api/v1/texts/gita/a/1/1` (Bhagavad Gita Chapter 1, Verse 1)

Both use the same response format and error handling.

## Sample Verses Included

The setup includes these key verses:

1. **Chapter 1, Verses 1-2**: Dhritarashtra's opening question
2. **Chapter 2, Verses 1-2**: Sanjaya's description of Arjuna's distress  
3. **Chapter 2, Verse 11**: Krishna's first teaching about wisdom
4. **Chapter 2, Verse 47**: The famous karma yoga verse
5. **Chapter 3, Verses 1-2**: Arjuna's confusion about action vs knowledge
6. **Chapter 4, Verses 7-8**: Krishna's promise to incarnate when dharma declines

Each verse includes:
- **Sanskrit text** (Devanagari script)
- **Transliteration** (Roman script with diacritics)
- **English translation**

## Troubleshooting

### Server Startup Errors
If you see "Error setting up cache database: no such column: language_code":
- Run the manual SQL setup to add missing columns
- Restart your server

### Missing Dependencies
The downloader script requires:
- `requests` for API calls
- `sqlite3` (built into Python)
- `git` for repository cloning

### Database Permissions
Ensure your application has write permissions to the database file:
```bash
chmod 664 db/vulgate.db
```

## Extending the Integration

### Adding More Verses
To add complete chapters or more verses:

1. **Use the downloader script** - it will attempt to fetch complete data
2. **Modify the sample data** in `download_gita_dependency.py`
3. **Import from external sources** using the script's API integration features

### Custom Translations
The database structure supports multiple translations. You can:
- Add translation columns to the verses table
- Store different language versions
- Implement translation switching in the frontend

## Frontend Integration

Update your frontend to handle the new Gita endpoints:

```typescript
// Fetch available text sources
const sources = await fetch('/api/v1/texts/sources').then(r => r.json());
// Should return: ["bible", "gita"]

// Fetch Gita chapter
const gitaChapter = await fetch('/api/v1/texts/gita/a/2').then(r => r.json());

// Handle both Bible and Gita in unified way
const getVerses = async (source: string, book: string, chapter: number) => {
  return fetch(`/api/v1/texts/${source}/${book}/${chapter}`).then(r => r.json());
};
```

## Benefits of This Integration

✅ **No external API dependencies** - all data stored locally  
✅ **Consistent with existing Bible structure** - same endpoints and responses  
✅ **Authentic Sanskrit text** - includes proper Devanagari and transliteration  
✅ **Offline capability** - works without internet connection  
✅ **Fast performance** - no network latency for verse lookups  
✅ **Extensible** - easy to add more chapters and translations  

## Next Steps

After successful setup:
1. Test the API endpoints to ensure they're working
2. Update your frontend to include Gita text selection
3. Consider adding more chapters using the downloader script
4. Implement text search across both Bible and Gita content

For questions or issues, refer to the main project documentation or check the server logs for specific error messages. 