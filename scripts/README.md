# Scripts Directory

This directory contains utility scripts, setup scripts, and other tools for the Vulgate project.

## Categories

### Newton Integration Scripts
- **step1_install_pdf_library.py** - Installs PDF processing dependencies
- **step3_add_newton_support.py** - Adds Newton support to the database
- **step4_extract_newton_text.py** - Extracts text from Newton's Principia
- **step5_load_newton_sections.py** - Loads Newton sections into the database
- **step6_proper_newton_structure.py** - Sets up proper Newton data structure
- **step7_newton_frontend_integration.py** - Integrates Newton with frontend
- **step8_newton_api_integration.py** - Sets up Newton API endpoints

### Database Scripts
- **fix_database.py** - Database repair utilities
- **fix_database_schema.py** - Schema fixes and updates
- **fix_schema_now.py** - Immediate schema fixes
- **create_gita_database.py** - Creates Bhagavad Gita database
- **add_gita_data.py** - Adds Gita data to database

### Data Population Scripts
- **populate_gita_from_json.py** - Populates Gita from JSON data
- **populate_word_relationships.py** - Populates word relationship data
- **fetch_complete_gita.py** - Fetches complete Gita data
- **download_gita_dependency.py** - Downloads Gita dependencies

### Setup and Initialization
- **setup_gita_integration.py** - Sets up Gita integration
- **initialize_macronizer.py** - Initializes the Latin macronizer

### Utility Scripts
- **simple_fix.py** - Simple database fixes
- **quick_fix.py** - Quick fixes for common issues
- **check_verses_simple.py** - Simple verse checking
- **debug_chapter_1.py** - Debug tools for Chapter 1
- **complete_chapter_1.py** - Chapter 1 completion script
- **verify_gita_integration.py** - Verifies Gita integration
- **add_missing_verse.py** - Adds missing verses
- **fix_verse_1_1.py** - Fixes specific verse issues

## Usage

Navigate to the project root and run scripts as needed:

```bash
python scripts/<script_name>.py
```

⚠️ **Note**: Many scripts require specific setup or database access. Check individual script documentation for requirements. 