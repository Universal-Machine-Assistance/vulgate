# Update Directory

This directory contains all update scripts for the Vulgate project database and content.

## Contents

- **update_all_books.py** - Updates all books in the database
- **update_major_books.py** - Updates major books with enhanced features
- **update_matthew.py** - Specific updates for the Book of Matthew
- **update_verse_6.py** - Updates for specific verse 6 issues

## Usage

To run update scripts, navigate to the project root and run:

```bash
python update/<script_name>.py
```

⚠️ **Warning**: Always backup your database before running update scripts as they modify existing data.

## Notes

- These scripts typically require database access
- Some scripts may take considerable time to complete for large datasets
- Check script documentation for specific requirements and usage instructions 