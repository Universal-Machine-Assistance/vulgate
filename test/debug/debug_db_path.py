#!/usr/bin/env python3
"""Debug database path resolution"""

import os

# Simulate the path resolution from dictionary.py
current_file = "backend/app/api/api_v1/endpoints/dictionary.py"
project_root = os.path.abspath(os.path.join(os.path.dirname(current_file), "../../../../../"))
cache_db_path = os.path.join(project_root, "word_cache.db")

print("=== DATABASE PATH DEBUG ===")
print(f"Current file: {current_file}")
print(f"Project root: {project_root}")
print(f"Cache DB path: {cache_db_path}")
print(f"Cache DB exists: {os.path.exists(cache_db_path)}")
print(f"Current dir word_cache.db exists: {os.path.exists('word_cache.db')}")
print(f"Current working directory: {os.getcwd()}")

# Check if there are multiple word_cache.db files
print("\n=== SEARCHING FOR ALL word_cache.db FILES ===")
for root, dirs, files in os.walk("."):
    for file in files:
        if file == "word_cache.db":
            full_path = os.path.join(root, file)
            print(f"Found: {full_path}")
            
# Check the actual path the API is using
print("\n=== ACTUAL API PATH ===")
api_file_path = os.path.abspath("backend/app/api/api_v1/endpoints/dictionary.py")
if os.path.exists(api_file_path):
    api_project_root = os.path.abspath(os.path.join(os.path.dirname(api_file_path), "../../../../../"))
    api_cache_db_path = os.path.join(api_project_root, "word_cache.db")
    print(f"API project root: {api_project_root}")
    print(f"API cache DB path: {api_cache_db_path}")
    print(f"API cache DB exists: {os.path.exists(api_cache_db_path)}") 