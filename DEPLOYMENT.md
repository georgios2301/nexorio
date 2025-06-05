# Deployment auf Render.com

Diese Anleitung erklärt, wie Sie das DZMetall Lieferschein System auf Render.com deployen.

## Voraussetzungen

- GitHub Account
- Render.com Account
- Git Repository mit dem Projekt

## Schritt 1: Repository vorbereiten

1. Erstellen Sie ein neues Git Repository oder nutzen Sie ein bestehendes
2. Pushen Sie alle Dateien zu GitHub/GitLab/Bitbucket

```bash
git init
git add .
git commit -m "Initial commit for DZMetall Lieferschein System"
git remote add origin https://github.com/IHR-USERNAME/dzmetall-lieferschein.git
git push -u origin main
```

## Schritt 2: Render.com Setup

1. Gehen Sie zu [render.com](https://render.com) und melden Sie sich an
2. Klicken Sie auf "New +" → "Web Service"
3. Verbinden Sie Ihr Git Repository
4. Render erkennt automatisch die `render.yaml` Datei

## Schritt 3: Umgebungsvariablen

Fügen Sie folgende Umgebungsvariablen in Render hinzu:

- `SUPABASE_URL`: https://hqxljqekbekkwmkqrtjo.supabase.co
- `SUPABASE_KEY`: Ihr Supabase Anonymous Key
- `GEMINI_API_KEY`: Ihr Google Gemini API Key (optional, aber empfohlen für OCR)

## Schritt 4: Deployment

1. Klicken Sie auf "Create Web Service"
2. Render wird automatisch:
   - Dependencies installieren
   - Das Build-Script ausführen
   - Die Services starten

## Schritt 5: Frontend konfigurieren

Nach dem Deployment:

1. Kopieren Sie die Backend-URL von Render (z.B. https://dzmetall-backend.onrender.com)
2. Aktualisieren Sie die `index.html` Datei:
   ```javascript
   // Ändern Sie die Backend-URL
   const BACKEND_URL = 'https://dzmetall-backend.onrender.com';
   ```
3. Deployen Sie das Frontend als Static Site auf Render

## Frontend als Static Site deployen

1. Klicken Sie auf "New +" → "Static Site"
2. Verbinden Sie dasselbe Repository
3. Konfigurieren Sie:
   - **Build Command**: `echo "No build needed"`
   - **Publish Directory**: `Lieferschein/Programm`
4. Klicken Sie auf "Create Static Site"

## URLs nach dem Deployment

- Backend API: `https://ihr-service-name.onrender.com`
- API Dokumentation: `https://ihr-service-name.onrender.com/docs`
- Frontend: `https://ihr-static-site-name.onrender.com`

## Wichtige Hinweise

### Kostenlose Tier Limitierungen

- Services auf dem kostenlosen Tier werden nach 15 Minuten Inaktivität heruntergefahren
- Der erste Request nach dem Herunterfahren kann 30-60 Sekunden dauern
- Für Production empfiehlt sich ein bezahlter Plan

### Datei-Uploads

- Render's ephemeres Filesystem bedeutet, dass hochgeladene Dateien nicht persistent sind
- Die OCR-Verarbeitung funktioniert trotzdem, da Dateien nur temporär benötigt werden

### Performance

- Die PDF-Generierung kann beim ersten Mal länger dauern
- Subsequent requests sind schneller durch Caching

## Troubleshooting

### Server startet nicht

1. Überprüfen Sie die Logs in Render Dashboard
2. Stellen Sie sicher, dass alle Umgebungsvariablen gesetzt sind
3. Überprüfen Sie die Python-Version (sollte 3.9+ sein)

### OCR funktioniert nicht

1. Stellen Sie sicher, dass `GEMINI_API_KEY` gesetzt ist
2. Überprüfen Sie die API-Key Gültigkeit
3. Schauen Sie in die Server-Logs für Fehlermeldungen

### PDF-Generierung schlägt fehl

1. Überprüfen Sie, ob alle Vorlagen-Dateien vorhanden sind
2. Stellen Sie sicher, dass die Schriftarten installiert sind
3. Überprüfen Sie die Logs für spezifische Fehler

## Lokale Entwicklung

Für lokale Tests mit Render-ähnlicher Umgebung:

```bash
# Environment variables setzen
export SUPABASE_URL=https://hqxljqekbekkwmkqrtjo.supabase.co
export SUPABASE_KEY=your-key-here
export GEMINI_API_KEY=your-gemini-key

# Server starten
python start_services.py
```

## Monitoring

1. Nutzen Sie Render's Dashboard für:
   - Service Logs
   - Metrics (CPU, Memory)
   - Deploy History

2. Health Check Endpoint:
   - `https://ihr-service-name.onrender.com/health`

## Sicherheit

1. Nutzen Sie Umgebungsvariablen für sensitive Daten
2. Aktivieren Sie HTTPS (automatisch bei Render)
3. Beschränken Sie CORS auf Ihre Frontend-Domain
4. Regelmäßige Updates der Dependencies

## Support

Bei Problemen:
1. Überprüfen Sie die [Render Dokumentation](https://render.com/docs)
2. Schauen Sie in die Service Logs
3. Kontaktieren Sie den Render Support