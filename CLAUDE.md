# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the DZMetall Lieferschein (Delivery Note) System - a comprehensive document management system for creating delivery notes, invoices, and work cards for a German metal processing company. The system consists of:
- A frontend interface for order management and document generation
- A standalone FastAPI backend server for data operations and AI-powered OCR
- Dual PDF generation servers (Python and Node.js)

## Common Development Commands

### Backend Server (Supabase API)
```bash
cd Lieferschein/backend
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
pip install -r requirements.txt
python simple_supabase_server.py
```

### Python PDF Server (Preferred)
```bash
cd Lieferschein/Programm
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
python pdf_server.py
```

### Node.js PDF Server (Alternative)
```bash
cd Lieferschein/Programm
npm install
node pdfServer.js
```

### Running Tests
```bash
cd Lieferschein/Programm
python test_pdf_generation.py
```

### Starting the System
1. Start the Backend API server: `python simple_supabase_server.py` (port 8001)
2. Start the PDF server (Python or Node.js) on port 4000
3. Open `Lieferschein/Programm/index.html` in a browser
4. Configure environment variable `GEMINI_API_KEY` for AI-powered OCR (optional)

## Architecture Overview

### Component Interaction
- **Frontend** (`index.html`) → **FastAPI Backend** (port 8001) → Supabase Database
- **Frontend** → **PDF Server** (port 4000) → PDF generation
- **Backend** → **Google Gemini AI** or **Local OCR** → Data extraction

### Backend API Details
The FastAPI backend (`simple_supabase_server.py`) provides the following endpoints:

#### API Endpoints
- **`GET /health`**: Health check endpoint
- **`GET /api/orders`**: Fetch all order numbers (newest first)
- **`GET /api/positions?bestellnummer=XXX`**: Fetch positions for a specific order
- **`PUT /api/positions/batch`**: Update multiple position records
- **`POST /api/extract`**: OCR extraction from uploaded delivery note images
- **`DELETE /api/orders/{bestellnummer}`**: Delete an order and all its positions

#### Database Integration
- **Supabase**: `https://hqxljqekbekkwmkqrtjo.supabase.co`
- **Tables**:
  - `bestellungen`: Orders table
  - `positionen`: Position items table

### OCR Processing
The system supports two OCR methods:
1. **Google Gemini AI** (preferred): Set `GEMINI_API_KEY` environment variable
   - Uses Gemini 1.5 Pro for accurate text extraction
   - Automatically extracts structured data in JSON format
2. **Local OCR** (fallback): Uses Tesseract OCR
   - Pattern-based extraction from delivery notes
   - Supports German language documents

### Key API Endpoints
- **Backend API**: `http://localhost:8001/api/*`
- **PDF Server**: `POST http://localhost:4000/generate-pdf` with `{docType, data}`

### PDF Generation Flow
1. User selects order in frontend
2. Clicks document type button (Lieferschein/Laufkarte/Rechnung)
3. Frontend sends order data to PDF server
4. Server generates PDF using template
5. PDF opens in new browser window

### Important Files
- **Backend Server**: `backend/simple_supabase_server.py` - Main API server
- **OCR Module**: `backend/app/ocr.py` - OCR processing logic
- **PDF Templates**: `Vorlagen/ls2.pdf` (Python), HTML templates (Node.js)
- **Coordinate Definitions**: `Vorlagen/lieferschein_generator.py`
- **Frontend**: `Programm/index.html` - Main user interface
- **PDF Servers**: `Programm/pdf_server.py`, `Programm/pdfServer.js`

## Development Notes

### Environment Variables
- `GEMINI_API_KEY`: Google Gemini API key for AI-powered OCR (optional)
- `PORT`: Backend server port (default: 8001)

### PDF Coordinate System
The Python PDF generator uses precise coordinate positioning. To adjust field positions:
1. Use `test_pdf_generation.py` to visualize coordinates
2. Modify positions in `lieferschein_generator.py`
3. Coordinates are in points (1/72 inch)

### Data Structure
Orders contain:
- `bestellnummer`: Order number
- `positionen`: Array of order positions with fields:
  - `pos_nr`: Position number
  - `auftrag`: Order/job number
  - `beschreibung`: Description
  - `vorgang`: Process/operation
  - `preis`: Price
  - `menge`: Quantity
  - `modellnummer`: Model number
  - `fv`: Process code (F/V/P)
  - `werkstoff`: Material specification

### Dual Implementation
The system supports two PDF generation methods:
- **Python**: Direct PDF manipulation with PyPDF/ReportLab
- **Node.js**: HTML rendering with Puppeteer
Both can run simultaneously on the same port.

### OCR Processing Details
- Supports image formats: JPEG, PNG, PDF
- Extracts structured data from German delivery notes
- Pattern matching for order numbers (BL-prefix), positions (FL-prefix)
- Automatic field detection for quantities, prices, materials
- Falls back to local OCR if Gemini API is unavailable