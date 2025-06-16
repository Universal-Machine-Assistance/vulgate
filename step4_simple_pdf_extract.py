#!/usr/bin/env python3
"""
Step 4: Simple PDF text extraction
Extract text from first 10 pages of the Newton PDF for testing.
"""

import json
from pathlib import Path

PDF_PATH = "/Users/guillermomolina/dev/vulgate/source/Philosophiae Naturalis Principia Mathematica -- Isaac Newton -- 5a6ed3d91fb0e9f13484883ffae5e7c8.pdf"


def simple_pdf_extract() -> bool:
    try:
        import fitz
    except ImportError:
        print("❌ PyMuPDF not installed. Run step1_install_pdf_library.py first")
        return False

    if not Path(PDF_PATH).exists():
        print(f"❌ PDF not found: {PDF_PATH}")
        return False

    doc = fitz.open(PDF_PATH)
    print(f"📄 Total pages: {len(doc)}")
    extracted = []
    for page_num in range(min(10, len(doc))):
        text = doc[page_num].get_text().strip()
        if len(text) < 50:
            continue
        title = text.split('\n')[0][:100]
        extracted.append({
            "page_number": page_num + 1,
            "title": title,
            "content": text[:1000],
            "book_number": 1,
            "section_number": page_num + 1,
            "section_type": "text",
        })
        print(f"✅ Extracted page {page_num+1}: {title[:50]}...")
    doc.close()
    out_dir = Path("newton_test_data")
    out_dir.mkdir(exist_ok=True)
    with open(out_dir / "extracted_sections.json", "w", encoding="utf-8") as f:
        json.dump(extracted, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(extracted)} sections to {out_dir}/extracted_sections.json")
    return True


if __name__ == "__main__":
    if simple_pdf_extract():
        print("🎉 Step 4 completed! Run step5_load_test_data.py next")
    else:
        print("❌ Step 4 failed")
