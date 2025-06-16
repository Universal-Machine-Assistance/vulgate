#!/usr/bin/env python3
"""
Step 2: Test PDF reading capability.
Ensure the Newton PDF can be opened with PyMuPDF.
"""
from pathlib import Path

PDF_PATH = "/Users/guillermomolina/dev/vulgate/source/Philosophiae Naturalis Principia Mathematica -- Isaac Newton -- 5a6ed3d91fb0e9f13484883ffae5e7c8.pdf"


def test_pdf_import():
    try:
        import fitz  # PyMuPDF
        print("✅ PyMuPDF imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ Cannot import PyMuPDF: {e}")
        print("Run step1_install_pdf_library.py first")
        return False


def test_pdf_exists():
    path = Path(PDF_PATH)
    if path.exists():
        print(f"✅ Newton PDF found: {path}")
        return True
    print(f"❌ Newton PDF not found at: {path}")
    return False


def test_pdf_reading():
    import fitz
    try:
        doc = fitz.open(PDF_PATH)
        print(f"✅ Opened PDF with {len(doc)} pages")
        if len(doc) > 0:
            text = doc[0].get_text()
            print(f"First page sample: {text[:100]}...")
        doc.close()
        return True
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        return False


if __name__ == "__main__":
    ok = test_pdf_import() and test_pdf_exists()
    if ok:
        ok = test_pdf_reading()
    if ok:
        print("🎉 Step 2 completed! Run further steps to load data.")
    else:
        print("❌ Step 2 failed. Fix the above issues.")
