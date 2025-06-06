#!/bin/bash

echo "DZMetall Local Development Setup"
echo "================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys:"
    echo "   - SUPABASE_URL"
    echo "   - SUPABASE_KEY" 
    echo "   - GEMINI_API_KEY (optional)"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if required variables are set
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    echo "❌ ERROR: SUPABASE_URL and SUPABASE_KEY must be set in .env file"
    exit 1
fi

echo "✅ Environment variables loaded"

# Create virtual environments if needed
if [ ! -d "Lieferschein/backend/venv" ]; then
    echo "Creating backend virtual environment..."
    cd Lieferschein/backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ../..
fi

if [ ! -d "Lieferschein/Programm/venv" ]; then
    echo "Creating frontend virtual environment..."
    cd Lieferschein/Programm
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ../..
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the servers:"
echo "1. Backend:  cd Lieferschein/backend && source venv/bin/activate && python simple_supabase_server.py"
echo "2. PDF:      cd Lieferschein/Programm && source venv/bin/activate && python pdf_server.py"
echo "3. Frontend: Open Lieferschein/Programm/index.html in browser"