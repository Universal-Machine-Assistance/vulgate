#!/bin/bash
# Install RFTagger for Latin Macronizer
# Based on the INSTALL.txt instructions from the latin-macronizer project

set -e  # Exit on any error

echo "Installing RFTagger for Latin Macronizer..."
echo "============================================="

# Change to the latin-macronizer directory
cd latin-macronizer

# Download RFTagger
echo "Downloading RFTagger..."
if [ ! -f "RFTagger.zip" ]; then
    wget https://www.cis.uni-muenchen.de/~schmid/tools/RFTagger/data/RFTagger.zip
else
    echo "RFTagger.zip already exists, skipping download."
fi

# Extract RFTagger
echo "Extracting RFTagger..."
if [ ! -d "RFTagger" ]; then
    unzip RFTagger.zip
else
    echo "RFTagger directory already exists, skipping extraction."
fi

# Compile RFTagger
echo "Compiling RFTagger..."
cd RFTagger/src

# Check if we need to compile
if [ ! -f "../bin/rft-annotate" ] || [ ! -f "../bin/rft-train" ]; then
    echo "Compiling RFTagger binaries..."
    make clean || true
    make
    
    # Create bin directory if it doesn't exist
    mkdir -p ../bin
    
    # Copy the compiled binaries to the bin directory
    cp rft-annotate ../bin/
    cp rft-train ../bin/
    
    echo "RFTagger compiled successfully!"
else
    echo "RFTagger binaries already exist, skipping compilation."
fi

# Go back to the latin-macronizer directory
cd ../..

# Check if RFTagger binaries are working
echo "Testing RFTagger installation..."
if [ -f "RFTagger/bin/rft-annotate" ]; then
    echo "✅ RFTagger installed successfully!"
    echo "RFTagger binaries are located at: $(pwd)/RFTagger/bin/"
    
    # Update the macronizer configuration
    echo "Updating macronizer configuration..."
    RFTAGGER_BIN_DIR="$(pwd)/RFTagger/bin"
    
    # Create a patch for the macronizer.py file to use the local RFTagger
    cat > rftagger_config.patch << EOF
--- macronizer.py.orig
+++ macronizer.py
@@ -29,7 +29,7 @@
 
 USE_DB = True
 DB_NAME = 'macronizer.db'
-RFTAGGER_DIR = '/usr/local/bin'
+RFTAGGER_DIR = '$RFTAGGER_BIN_DIR'
 MORPHEUS_DIR = os.path.join(os.path.dirname(__file__), 'morpheus')
 MACRONS_FILE = os.path.join(os.path.dirname(__file__), 'macrons.txt')
 
EOF
    
    # Apply the patch (backup original first)
    if [ ! -f "macronizer.py.orig" ]; then
        cp macronizer.py macronizer.py.orig
    fi
    
    # Use sed to update the RFTAGGER_DIR
    sed -i '' "s|RFTAGGER_DIR = '/usr/local/bin'|RFTAGGER_DIR = '$RFTAGGER_BIN_DIR'|" macronizer.py
    
    echo "✅ Configuration updated!"
    echo "RFTagger directory set to: $RFTAGGER_BIN_DIR"
    
else
    echo "❌ RFTagger compilation failed!"
    exit 1
fi

# Go back to the project root
cd ..

echo ""
echo "🎉 RFTagger installation complete!"
echo ""
echo "Next steps:"
echo "1. The macronizer should now work with RFTagger support"
echo "2. Test with: python test_macronizer_integration.py"
echo "" 