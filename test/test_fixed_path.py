#!/usr/bin/env python3
"""Test the fixed path resolution"""

import os

# Test the fixed path
project_root = os.path.abspath(os.path.join(os.path.dirname('backend/app/api/api_v1/endpoints/dictionary.py'), '../../../../'))
cache_db_path = os.path.join(project_root, 'word_cache.db')

print('Fixed project root:', project_root)
print('Fixed cache DB path:', cache_db_path)
print('Fixed cache DB exists:', os.path.exists(cache_db_path))

# Check record count in the correct database
import sqlite3
try:
    conn = sqlite3.connect(cache_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM verse_analysis_cache")
    count = cursor.fetchone()[0]
    conn.close()
    print(f'Records in correct database: {count}')
except Exception as e:
    print(f'Error reading correct database: {e}') 