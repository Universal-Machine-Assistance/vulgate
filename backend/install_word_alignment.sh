#!/bin/bash

# Advanced Word Alignment Setup Script
# Sets up SimAlign and BERT dependencies for semantic word alignment

echo "🚀 Setting up Advanced Word Alignment Dependencies..."
echo "=================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found."
    echo "Please install Python 3.7+ and try again."
    exit 1
fi

# Check if pip is available
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip is required but not found."
    echo "Please install pip and try again."
    exit 1
fi

# Use pip3 if available, otherwise pip
PIP_CMD="pip3"
if ! command -v pip3 &> /dev/null; then
    PIP_CMD="pip"
fi

echo "📦 Installing core dependencies..."
echo "This will install:"
echo "  - simalign (word alignment library)"
echo "  - torch (PyTorch for BERT)"
echo "  - transformers (Hugging Face)"
echo "  - Additional NLP libraries"
echo ""

# Install dependencies
$PIP_CMD install -r requirements_alignment.txt

# Check installation success
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. The BERT model (~500MB) will download automatically on first use"
    echo "2. Restart your backend server to load the new dependencies"
    echo "3. Word alignment will now use semantic BERT-based matching"
    echo ""
    echo "🧪 Testing installation..."
    
    # Test import
    python3 -c "
try:
    import simalign
    import torch
    import transformers
    print('✅ All imports successful!')
    print('🎯 SimAlign version:', simalign.__version__)
    print('🔥 PyTorch version:', torch.__version__)
    print('🤗 Transformers version:', transformers.__version__)
except ImportError as e:
    print('❌ Import failed:', e)
    exit(1)
" 2>/dev/null

    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 Word Alignment setup complete!"
        echo "📖 See backend/docs/WORD_ALIGNMENT_FEATURE.md for full documentation"
    else
        echo ""
        echo "⚠️  Installation completed but imports failed."
        echo "You may need to restart your Python environment."
    fi
    
else
    echo "❌ Installation failed!"
    echo "Please check the error messages above and try again."
    echo ""
    echo "🛠️  Common solutions:"
    echo "1. Update pip: $PIP_CMD install --upgrade pip"
    echo "2. Use virtual environment: python3 -m venv venv && source venv/bin/activate"
    echo "3. Install with user flag: $PIP_CMD install --user -r requirements_alignment.txt"
    exit 1
fi

echo ""
echo "📊 Resource requirements:"
echo "  - Disk space: ~500MB for BERT model (downloaded on first use)"
echo "  - RAM: ~500MB when model is loaded"
echo "  - First alignment: ~2-5 seconds (model loading)"
echo "  - Subsequent alignments: ~200-500ms"
echo ""
echo "🔧 If you encounter issues:"
echo "  - Check backend logs for detailed error messages"
echo "  - The system will gracefully fall back to pattern-based alignment"
echo "  - See troubleshooting section in the documentation" 