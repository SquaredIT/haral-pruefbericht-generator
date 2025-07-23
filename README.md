# HARAL Prüfbericht Generator

Eine moderne, responsive Webanwendung zur Erstellung und Verwaltung von Prüfberichten für die Firma HARAL.

## 🚀 Features

- **Benutzerauthentifizierung** - Sicheres Login-System mit Rollen (Admin, Auditor)
- **Kundenverwaltung** - Vollständige CRUD-Operationen für Kunden
- **Prüfberichte** - Erstellen, bearbeiten und PDF-Export von Prüfberichten
- **Mobile-responsive** - Optimiert für Desktop, Tablet und Smartphone
- **PDF-Generierung** - Automatische PDF-Erstellung basierend auf Original-Layout

## 🛠️ Technologie-Stack

### Backend
- **Flask** - Python Web Framework
- **SQLAlchemy** - ORM für Datenbankoperationen
- **ReportLab** - PDF-Generierung
- **Flask-CORS** - Cross-Origin Resource Sharing

### Frontend
- **React** - Moderne UI-Bibliothek
- **React Router** - Client-side Routing
- **CSS3** - Responsive Design mit Flexbox/Grid

## 📦 Installation & Setup

### Lokale Entwicklung

1. **Repository klonen**
   ```bash
   git clone https://github.com/ihr-username/haral-backend.git
   cd haral-backend
   ```

2. **Python-Umgebung einrichten**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # oder
   venv\Scripts\activate     # Windows
   ```

3. **Abhängigkeiten installieren**
   ```bash
   pip install -r requirements.txt
   ```

4. **Anwendung starten**
   ```bash
   python src/main.py
   ```

5. **Browser öffnen**
   ```
   http://localhost:5000
   ```

### Docker Deployment

1. **Docker Container bauen**
   ```bash
   docker build -t haral-pruefbericht .
   ```

2. **Container starten**
   ```bash
   docker run -p 5000:5000 haral-pruefbericht
   ```

3. **Mit Docker Compose**
   ```bash
   docker-compose up -d
   ```

## 🌐 Deployment-Optionen

### 1. Render.com (Kostenlos)
- Einfachstes Deployment
- Automatische SSL-Zertifikate
- GitHub-Integration

### 2. Railway.app (~5€/Monat)
- Keine Sleep-Modi
- Bessere Performance
- Einfache Skalierung

### 3. DigitalOcean (ab 6€/Monat)
- Volle Server-Kontrolle
- Professionelle Infrastruktur
- Skalierbar

Detaillierte Anleitungen finden Sie in der [Hosting-Anleitung](hosting-guide.md).

## 👥 Standard-Benutzer

Nach der ersten Installation werden automatisch Standard-Benutzer erstellt:

| Benutzername | Passwort | Rolle | Beschreibung |
|-------------|----------|-------|--------------|
| admin | admin123 | Admin | Vollzugriff auf alle Funktionen |
| ralf.hartmann | auditor123 | Auditor | Kann Berichte erstellen und verwalten |

⚠️ **Wichtig:** Ändern Sie diese Passwörter in der Produktion!

## 📱 Mobile Optimierung

Die Anwendung ist vollständig responsive und optimiert für:
- **Desktop** - Vollständige Funktionalität
- **Tablet** - Touch-optimierte Bedienung
- **Smartphone** - Hamburger-Menü, große Touch-Targets

## 🔧 Konfiguration

### Umgebungsvariablen

```bash
FLASK_ENV=production
SECRET_KEY=ihr-sicherer-secret-key
DATABASE_URL=sqlite:///app.db  # oder PostgreSQL URL
```

### Produktions-Setup

1. **Gunicorn verwenden**
   ```bash
   gunicorn --bind 0.0.0.0:5000 src.main:app
   ```

2. **Nginx Reverse Proxy** (optional)
   ```nginx
   server {
       listen 80;
       server_name ihre-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 📊 API-Endpunkte

### Authentifizierung
- `POST /api/auth/login` - Benutzer anmelden
- `POST /api/auth/logout` - Benutzer abmelden
- `GET /api/auth/me` - Aktueller Benutzer

### Kunden
- `GET /api/customers` - Alle Kunden abrufen
- `POST /api/customers` - Neuen Kunden erstellen
- `PUT /api/customers/{id}` - Kunde aktualisieren
- `DELETE /api/customers/{id}` - Kunde löschen

### Berichte
- `GET /api/reports` - Alle Berichte abrufen
- `POST /api/reports` - Neuen Bericht erstellen
- `PUT /api/reports/{id}` - Bericht aktualisieren
- `GET /api/reports/{id}/pdf` - PDF herunterladen

## 🔒 Sicherheit

- **Session-basierte Authentifizierung**
- **CSRF-Schutz** durch SameSite Cookies
- **SQL-Injection-Schutz** durch SQLAlchemy ORM
- **XSS-Schutz** durch Input-Validierung

## 🐛 Troubleshooting

### Häufige Probleme

1. **Port bereits in Verwendung**
   ```bash
   lsof -ti:5000 | xargs kill -9
   ```

2. **Datenbankfehler**
   ```bash
   rm src/database/app.db
   python src/main.py  # Erstellt neue DB
   ```

3. **CORS-Fehler**
   - Überprüfen Sie die CORS-Konfiguration in `main.py`

## 📞 Support

Bei Fragen oder Problemen:
1. Überprüfen Sie die Logs
2. Konsultieren Sie die Hosting-Anleitung
3. Kontaktieren Sie den Entwickler

## 📄 Lizenz

© 2025 HARAL - Alle Rechte vorbehalten

---

**Entwickelt für die Firma HARAL zur effizienten Erstellung von Prüfberichten.**

