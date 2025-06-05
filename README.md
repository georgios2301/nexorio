# DZMetall Lieferschein System

Ein umfassendes Dokumentenverwaltungssystem für die Erstellung von Lieferscheinen, Rechnungen und Laufkarten für DZ Metall.

## Features

- 📄 **OCR-Erkennung**: Automatische Extraktion von Lieferscheindaten mit Google Gemini AI
- 📊 **Datenbankverwaltung**: Speicherung und Verwaltung von Bestellungen in Supabase
- 🖨️ **PDF-Generierung**: Erstellung von Lieferscheinen, Laufkarten und Rechnungen
- 🌐 **Web-Interface**: Modernes, responsives Frontend mit Tailwind CSS
- 🚀 **Cloud-Ready**: Vorbereitet für Deployment auf Render.com

## Technologie-Stack

- **Backend**: Python FastAPI
- **PDF-Server**: Python Flask
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **Datenbank**: Supabase (PostgreSQL)
- **OCR**: Google Gemini AI
- **PDF-Verarbeitung**: PyPDF2, ReportLab

## Installation

### Voraussetzungen

- Python 3.9+
- Node.js (optional, für Frontend-Entwicklung)
- Tesseract OCR
- Poppler Utils

### Lokale Installation

1. Repository klonen:
```bash
git clone https://github.com/georgios2301/Lieferschein.git
cd Lieferschein
```

2. Python-Umgebung einrichten:
```bash
python -m venv venv
source venv/bin/activate  # Auf Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Umgebungsvariablen setzen:
```bash
cp .env.example .env
# Bearbeiten Sie .env und fügen Sie Ihre API-Keys ein
```

4. Services starten:
```bash
# Backend starten
cd Lieferschein/backend
python simple_supabase_server.py

# PDF-Server starten (in neuem Terminal)
cd Lieferschein/Programm
python pdf_server.py
```

5. Frontend öffnen:
- Öffnen Sie `Lieferschein/Programm/index.html` in Ihrem Browser

## Deployment auf Render.com

Siehe [DEPLOYMENT.md](DEPLOYMENT.md) für detaillierte Anweisungen.

## Verwendung

1. **Lieferschein hochladen**: 
   - Klicken Sie auf "Lieferschein hochladen"
   - Wählen Sie eine PDF- oder Bilddatei
   - Die KI extrahiert automatisch alle relevanten Daten

2. **Bestellungen verwalten**:
   - Ansicht aller Bestellungen
   - Bearbeiten von Positionen
   - Löschen von Bestellungen

3. **Dokumente erstellen**:
   - Wählen Sie eine Bestellung
   - Klicken Sie auf das gewünschte Dokument (Lieferschein, Laufkarte, Rechnung)
   - Das PDF wird automatisch generiert und geöffnet

## API-Dokumentation

Nach dem Start ist die API-Dokumentation verfügbar unter:
- Lokal: `http://localhost:8001/docs`
- Produktion: `https://ihr-service.onrender.com/docs`

## Lizenz

Proprietär - Alle Rechte vorbehalten

## Support

Bei Fragen oder Problemen erstellen Sie bitte ein Issue im GitHub Repository.