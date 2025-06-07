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

# Copy start_services.py first (main entry point)
if [ -f "start_services.py" ]; then
    cp start_services.py .
    echo "Copied start_services.py"
fi

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

# Copy backend files (including PDF generation modules)
echo "Copying backend modules..."
if [ -d "Lieferschein/backend" ]; then
    # Copy all Python modules from backend
    for file in Lieferschein/backend/*.py; do
        if [ -f "$file" ]; then
            basename=$(basename "$file")
            if [ "$basename" != "simple_supabase_server.py" ]; then
                cp "$file" .
                echo "Copied $basename"
            fi
        fi
    done
    
    # Copy PDF templates from backend
    for file in Lieferschein/backend/*.pdf; do
        if [ -f "$file" ]; then
            cp "$file" .
            echo "Copied $(basename "$file")"
        fi
    done
fi

# Copy remaining Vorlagen files (but not Python modules or PDFs)
echo "Copying other Vorlagen files..."
if [ -d "Lieferschein/Vorlagen" ]; then
    # Create Vorlagen directory
    mkdir -p Vorlagen
    
    # Copy non-Python, non-PDF files
    for file in Lieferschein/Vorlagen/*; do
        if [ -f "$file" ]; then
            ext="${file##*.}"
            if [ "$ext" != "py" ] && [ "$ext" != "pdf" ]; then
                cp "$file" Vorlagen/
            fi
        fi
    done
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Build completed successfully!"