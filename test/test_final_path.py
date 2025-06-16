#!/usr/bin/env python3
"""Test the final corrected path"""

import os
import sqlite3

# Test the corrected path (should go to main vulgate directory)
main_project_root = os.path.abspath(os.path.join(os.path.dirname("backend/app/api/api_v1/endpoints/dictionary.py"), "../../../../"))
cache_db_path = os.path.join(main_project_root, "word_cache.db")

print('=== FINAL PATH TEST ===')
print(f'Main project root: {main_project_root}')
print(f'Cache DB path: {cache_db_path}')
print(f'Cache DB exists: {os.path.exists(cache_db_path)}')

# This should be the database with 25 records
if os.path.exists(cache_db_path):
    try:
        conn = sqlite3.connect(cache_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM verse_analysis_cache")
        count = cursor.fetchone()[0]
        conn.close()
        print(f'Records in database: {count}')
        
        if count == 25:
            print('✅ SUCCESS: Found the correct database with existing cache!')
        else:
            print(f'⚠️  Database has {count} records (expected 25)')
    except Exception as e:
        print(f'❌ Error reading database: {e}')
else:
    print('❌ Database file not found') 