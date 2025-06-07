#!/usr/bin/env bash
# Build script for Render deployment

set -e  # Exit on error

echo "Starting build process..."

# Install system dependencies
echo "Installing system dependencies..."
apt-get update
apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-deu \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget

# Install additional fonts
echo "Installing fonts..."
apt-get install -y fonts-liberation

# Create necessary directories
echo "Creating directories..."
mkdir -p Lieferschein/backend
mkdir -p Lieferschein/Programm
mkdir -p Lieferschein/Vorlagen

# Copy files from the repository structure
echo "Copying application files..."
# Backend files
if [ -f "Lieferschein/backend/simple_supabase_server.py" ]; then
    cp Lieferschein/backend/simple_supabase_server.py .
fi

if [ -d "Lieferschein/backend/app" ]; then
    cp -r Lieferschein/backend/app .
fi

# PDF server
if [ -f "Lieferschein/Programm/pdf_server.py" ]; then
    cp Lieferschein/Programm/pdf_server.py .
fi

# Template processor
if [ -f "Lieferschein/Programm/templateProcessor.js" ]; then
    cp Lieferschein/Programm/templateProcessor.js .
fi

# Counter file
if [ -f "Lieferschein/backend/lieferschein_counter.txt" ]; then
    cp Lieferschein/backend/lieferschein_counter.txt .
else
    echo "907" > lieferschein_counter.txt
fi

# Copy Vorlagen files (PDF templates and Python modules)
echo "Copying Vorlagen files..."
if [ -d "Lieferschein/Vorlagen" ]; then
    # Copy Python modules
    for file in Lieferschein/Vorlagen/*.py; do
        if [ -f "$file" ]; then
            cp "$file" .
        fi
    done
    
    # Copy PDF templates
    for file in Lieferschein/Vorlagen/*.pdf; do
        if [ -f "$file" ]; then
            cp "$file" .
        fi
    done
    
    # Also keep the Vorlagen directory structure for any remaining files
    cp -r Lieferschein/Vorlagen .
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Build completed successfully!"