#!/usr/bin/env python3
"""
Step 4: Extract text from the first few pages of Newton's PDF.
Stores the sample data in newton_test_data/extracted_sections.json.
"""

import json
from pathlib import Path

def extract_sample():
    import fitz  # PyMuPDF

    pdf_path = "/Users/guillermomolina/dev/vulgate/source/" \
               "Philosophiae Naturalis Principia Mathematica -- Isaac Newton -- " \
               "5a6ed3d91fb0e9f13484883ffae5e7c8.pdf"

    path = Path(pdf_path)
    if not path.exists():
        print(f"❌ PDF not found: {path}")
        return False

    doc = fitz.open(pdf_path)
    print(f"📖 Pages in PDF: {len(doc)}")

    samples = []
    for page_num in range(min(10, len(doc))):
        page = doc[page_num]
        text = page.get_text()
        if len(text.strip()) > 50:
            title = text.splitlines()[0][:100]
            samples.append({
                "page_number": page_num + 1,
                "title": title,
                "content": text.strip()[:1000],
                "book_number": 1,
                "section_number": page_num + 1,
                "section_type": "text"
            })
            print(f"✅ Extracted page {page_num + 1}: {title}")

    doc.close()

    output_dir = Path("newton_test_data")
    output_dir.mkdir(exist_ok=True)
    with open(output_dir / "extracted_sections.json", "w", encoding="utf-8") as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)

    print(f"🎉 Saved {len(samples)} sample sections to {output_dir}/extracted_sections.json")
    return True

if __name__ == "__main__":
    extract_sample() 