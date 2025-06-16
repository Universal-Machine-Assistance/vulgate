#!/usr/bin/env python3
"""
Step 1: Install PDF processing library for Newton integration.
Run this script to install PyMuPDF and update requirements.txt.
"""
import subprocess
import sys
from pathlib import Path

def install_pdf_library() -> bool:
    print('📦 Installing PyMuPDF...')
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'PyMuPDF==1.23.14'], capture_output=True, text=True)
        if result.returncode == 0:
            print('✅ PyMuPDF installed successfully!')
            return True
        print(f'❌ Installation failed: {result.stderr}')
        return False
    except Exception as exc:
        print(f'❌ Error: {exc}')
        return False

def update_requirements():
    req_file = Path('backend/requirements.txt')
    try:
        text = req_file.read_text()
        if 'PyMuPDF' not in text:
            req_file.write_text(text.rstrip() + '\nPyMuPDF==1.23.14\n')
            print('✅ Added PyMuPDF to requirements.txt')
        else:
            print('ℹ️ PyMuPDF already listed in requirements.txt')
    except Exception as exc:
        print(f'❌ Failed to update requirements: {exc}')

if __name__ == '__main__':
    if install_pdf_library():
        update_requirements()
        print('🎉 Step 1 completed! Run step2_test_pdf.py next')
    else:
        print('❌ Step 1 failed. Please install PyMuPDF manually: pip install PyMuPDF')
