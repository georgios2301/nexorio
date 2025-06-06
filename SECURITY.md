# Security Configuration Guide

## ⚠️ WICHTIG: API Keys und Sicherheit

### Lokale Entwicklung

1. **Erstellen Sie eine `.env` Datei** (basierend auf `.env.example`):
   ```bash
   cp .env.example .env
   ```

2. **Fügen Sie Ihre API Keys in `.env` ein**:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   GEMINI_API_KEY=your-gemini-key
   ```

3. **Starten Sie Server mit Umgebungsvariablen**:
   ```bash
   # Backend Server
   source .env && python simple_supabase_server.py
   
   # Oder mit python-dotenv
   pip install python-dotenv
   ```

### Wichtige Sicherheitsregeln

❌ **NIEMALS**:
- API Keys im Code hardcoden
- `.env` Datei committen
- Echte Keys in Beispieldateien verwenden
- Keys in Frontend-Code einbinden

✅ **IMMER**:
- Umgebungsvariablen verwenden
- `.env` in `.gitignore` aufnehmen
- API Keys regelmäßig rotieren
- Separate Keys für Entwicklung/Produktion

### Deployment (Render.com)

Die `render.yaml` ist bereits korrekt konfiguriert:
- Verwendet Umgebungsvariablen mit `sync: false`
- Keys werden sicher im Render Dashboard gesetzt

### API Keys rotieren

Falls Keys kompromittiert wurden:

1. **Supabase**:
   - Dashboard → Settings → API
   - Regenerate anon key
   - Update in allen Umgebungen

2. **Google Gemini**:
   - Google Cloud Console → APIs & Services
   - Create new API key
   - Delete old key

### Checklist vor Deployment

- [ ] Alle hardcodierten Keys entfernt
- [ ] `.env` in `.gitignore`
- [ ] Umgebungsvariablen in Hosting-Platform gesetzt
- [ ] Alte/kompromittierte Keys deaktiviert
- [ ] CORS korrekt konfiguriert (nur erlaubte Domains)