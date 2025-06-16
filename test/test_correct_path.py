#!/usr/bin/env python3
"""Test the correct path calculation"""

import os
import sqlite3

# Simulate the API file path
api_file = "backend/app/api/api_v1/endpoints/dictionary.py"
main_project_root = os.path.abspath(os.path.join(os.path.dirname(api_file), "../../../../../"))
cache_db_path = os.path.join(main_project_root, "word_cache.db")

print('=== CORRECT PATH TEST ===')
print(f'API file: {api_file}')
print(f'Main project root: {main_project_root}')
print(f'Cache DB path: {cache_db_path}')
print(f'Cache DB exists: {os.path.exists(cache_db_path)}')

# Check if this matches the known correct path
expected_path = "/Users/guillermomolina/dev/vulgate/word_cache.db"
print(f'Expected path: {expected_path}')
print(f'Paths match: {cache_db_path == expected_path}')

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
            print(f'⚠️  Database has {count} records')
    except Exception as e:
        print(f'❌ Error reading database: {e}')
else:
    print('❌ Database file not found') 