#!/usr/bin/env python3
"""
Step 7: Add Newton frontend integration.
Updates the frontend to display Newton alongside Bible and Gita.
"""

import os
from pathlib import Path

def update_frontend():
    """Add Newton support to frontend components."""
    
    # 1. Update the main book selection in static/index.html
    index_path = Path("static/index.html")
    if index_path.exists():
        print("🔄 Updating book selection in index.html...")
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for book selection dropdown and add Newton
        if 'Newton' not in content and 'option value="newton"' not in content:
            # Find the book selection section and add Newton option
            gita_option = '<option value="gita">Bhagavad Gita</option>'
            if gita_option in content:
                newton_option = '<option value="newton">Newton - Principia</option>'
                content = content.replace(gita_option, gita_option + '\n        ' + newton_option)
                
                with open(index_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print("✅ Added Newton to book selection")
            else:
                print("ℹ️  Book selection format not recognized")
    else:
        print("ℹ️  static/index.html not found")

    # 2. Create Newton-specific CSS styling
    css_path = Path("static/css/newton.css")
    css_path.parent.mkdir(exist_ok=True)
    
    newton_css = """/* Newton-specific styling for Principia Mathematica */
.newton-content {
    font-family: 'Times New Roman', serif;
    line-height: 1.6;
    color: #2c3e50;
}

.newton-title {
    text-align: center;
    font-size: 1.4em;
    font-weight: bold;
    color: #8b4513;
    margin: 20px 0;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.newton-preface {
    font-style: italic;
    background-color: #f8f9fa;
    padding: 15px;
    border-left: 4px solid #6c757d;
    margin: 15px 0;
}

.newton-poetry {
    font-style: italic;
    text-align: center;
    background-color: #e8f4f8;
    padding: 20px;
    border-radius: 8px;
    margin: 15px 0;
    color: #1a5490;
}

.newton-definition {
    background-color: #fff8dc;
    padding: 15px;
    border: 2px solid #daa520;
    border-radius: 5px;
    margin: 15px 0;
}

.newton-definition strong {
    color: #b8860b;
}

.newton-chapter-header {
    font-size: 1.2em;
    font-weight: bold;
    color: #8b4513;
    text-align: center;
    margin: 25px 0 15px 0;
    text-transform: uppercase;
}

.newton-verse-ref {
    font-size: 0.9em;
    color: #6c757d;
    margin-bottom: 10px;
}
"""
    
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(newton_css)
    print("✅ Created Newton CSS styling")

    # 3. Update VerseBridge.js to handle Newton references
    verse_bridge_path = Path("static/js/VerseBridge.js")
    if verse_bridge_path.exists():
        print("🔄 Updating VerseBridge.js for Newton support...")
        with open(verse_bridge_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add Newton reference detection
        if 'newton' not in content.lower():
            # Find the detectSource function and add Newton pattern
            detect_pattern = "// Newton references: Newton 1:1, N 3:2"
            newton_detection = '''
        // Newton references: Newton 1:1, N 3:2, Pr 0:1 (Principia)
        if (/^(Newton|N|Pr)\\s+\\d+:\\d+$/i.test(reference.trim())) {
            return { source: 'newton', language: 'latin' };
        }'''
            
            # Insert Newton detection logic
            if 'detectSource' in content:
                # Add after Gita detection
                gita_pattern = 'return { source: \'gita\', language: \'sanskrit\' };'
                if gita_pattern in content:
                    content = content.replace(gita_pattern, gita_pattern + newton_detection)
                    
                    with open(verse_bridge_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print("✅ Updated VerseBridge.js with Newton support")
    else:
        print("ℹ️  VerseBridge.js not found")

    print("🎉 Newton frontend integration complete!")

if __name__ == "__main__":
    update_frontend() 