# 🔑 Reddit API Setup - Developer Keys erhalten

## 📋 SCHRITT-FÜR-SCHRITT ANLEITUNG

### 1️⃣ Reddit Account vorbereiten

**Wichtig:** Du brauchst einen Reddit Account mit:
- ✅ Bestätigter Email
- ✅ Mindestens 7 Tage alt (für API-Zugriff)
- ✅ Karma > 10 (empfohlen, nicht zwingend)

**Falls noch kein Account:**
1. Gehe zu: https://www.reddit.com/register
2. Erstelle Account
3. Bestätige Email
4. Optional: Poste 1-2 Comments um etwas Karma zu sammeln

---

### 2️⃣ Reddit App erstellen (Developer Keys)

**Schritte:**

1. **Öffne Reddit Apps-Seite:**
   ```
   https://www.reddit.com/prefs/apps
   ```
   *(Du musst eingeloggt sein)*

2. **Scroll nach unten zu "Developed Applications"**

3. **Klicke auf "create another app..." Button**

4. **Fülle das Formular aus:**

   | Feld | Wert |
   |------|------|
   | **name** | `GENESIS-v10.1-Marketing` |
   | **App type** | ✅ `script` (WICHTIG: nicht "web app"!) |
   | **description** | `Automated marketing for GENESIS Sovereign AI OS` |
   | **about url** | `https://github.com/Alvoradozerouno/GENESIS-v10.1` |
   | **redirect uri** | `http://localhost:8080` |

5. **Klicke "create app"**

---

### 3️⃣ Credentials kopieren

**Nach Erstellung siehst du:**

```
┌─────────────────────────────────────────┐
│ GENESIS-v10.1-Marketing                 │
│ script app                               │
├─────────────────────────────────────────┤
│ client id:                               │
│ ┌─────────────────────┐                 │
│ │ ABC123xyz456        │ ← CLIENT_ID     │
│ └─────────────────────┘                 │
│                                          │
│ secret:                                  │
│ ┌──────────────────────────────────────┐│
│ │ xYz789-aBc123-dEf456-gHi789          ││ ← CLIENT_SECRET
│ └──────────────────────────────────────┘│
│                                          │
│ description: Automated marketing...      │
│ about url: https://github.com/...       │
│ redirect uri: http://localhost:8080     │
└─────────────────────────────────────────┘
```

**Kopiere diese 2 Werte:**
- ✅ **CLIENT_ID** (kurzer String, ca. 14 Zeichen)
- ✅ **CLIENT_SECRET** (langer String, ca. 27 Zeichen)

---

### 4️⃣ Credentials ins Terminal setzen

**Öffne PowerShell und führe aus:**

```powershell
# Reddit App Credentials (von Schritt 3)
$env:REDDIT_CLIENT_ID="ABC123xyz456"                    # ← Ersetze mit deinem CLIENT_ID
$env:REDDIT_CLIENT_SECRET="xYz789-aBc123-dEf456-gHi789" # ← Ersetze mit deinem CLIENT_SECRET

# Reddit Account Credentials
$env:REDDIT_USERNAME="dein_reddit_username"             # ← Dein Reddit Username (OHNE "u/")
$env:REDDIT_PASSWORD="dein_reddit_passwort"             # ← Dein Reddit Passwort

# User Agent (wichtig für Reddit API)
$env:REDDIT_USER_AGENT="GENESIS-v10.1-Launcher/1.0 by /u/dein_reddit_username"
```

**⚠️ WICHTIG:**
- `REDDIT_USERNAME` = Dein Reddit Login-Name (OHNE das "u/" davor)
- `REDDIT_PASSWORD` = Dein normales Reddit Passwort
- `REDDIT_USER_AGENT` = Im Format "AppName/Version by /u/username"

---

### 5️⃣ Validierung (Optional)

**Teste ob Credentials richtig gesetzt sind:**

```powershell
# Überprüfe ob alle Variablen gesetzt sind
Get-ChildItem Env:REDDIT* | Format-Table Name, Value -AutoSize
```

**Erwartete Ausgabe:**
```
Name                   Value
----                   -----
REDDIT_CLIENT_ID       ABC123xyz456
REDDIT_CLIENT_SECRET   xYz789-aBc123-dEf456-gHi789
REDDIT_PASSWORD        ******
REDDIT_USER_AGENT      GENESIS-v10.1-Launcher/1.0 by /u/...
REDDIT_USERNAME        dein_username
```

---

### 6️⃣ Reddit Automation starten

**Nach erfolgreicher Validierung:**

```powershell
C:\Python314\python.exe reddit-automation.py
```

**Erwartete Ausgabe:**
```
======================================================================
GENESIS v10.1 - Reddit Post Automation
======================================================================

[1/3] Connecting to Reddit...
✓ Logged in as: u/dein_username
  Karma: 123 link, 456 comment

[2/3] Posting to 2 subreddits...

Post 1/2: r/opensource
----------------------------------------------------------------------
  ✓ Posted successfully!
  URL: https://reddit.com/r/opensource/comments/...
  Post ID: abc123

Post 2/2: r/kubernetes
----------------------------------------------------------------------
  ⏳ Waiting 15.0 minutes before next post...
```

---

## 🔒 SICHERHEIT

**❌ NIE committen:**
- Reddit Credentials gehören NICHT ins Git Repository
- `.gitignore` enthält bereits `reddit-automation.py`

**✅ Best Practice:**
- Credentials nur als Environment-Variablen setzen
- Nach Abschluss: Token rotieren (alte löschen, neue erstellen)
- Bei Leak: Sofort auf https://www.reddit.com/prefs/apps löschen

---

## 📊 API LIMITS

**Reddit API Rate Limits:**
- 60 Requests pro Minute
- 600 Posts pro Stunde (Script posted nur 2 Posts mit 15-min Pause = safe)

**Spam Detection:**
- Nicht mehr als 1 Post pro 10 Minuten pro Subreddit
- User muss >7 Tage alt sein
- Empfohlen: Karma >10

**Unser Script:**
- ✅ 2 Posts mit 15-Minuten-Pause (safe)
- ✅ Verschiedene Subreddits (r/opensource, r/kubernetes)
- ✅ Technischer Content (kein Spam)

---

## ❓ TROUBLESHOOTING

**Problem: "invalid_client"**
- → CLIENT_ID oder CLIENT_SECRET falsch
- → Überprüfe auf https://www.reddit.com/prefs/apps
- → Achte auf Leerzeichen beim Copy-Paste

**Problem: "wrong_password"**
- → Reddit Passwort falsch
- → Teste Login auf reddit.com manuell
- → Falls 2FA aktiv: Nutze App-Passwort

**Problem: "USER_REQUIRED"**
- → Account zu neu (<7 Tage)
- → Warte einige Tage
- → Oder nutze älteren Account

**Problem: "RATELIMIT"**
- → Zu viele Requests
- → Warte 10 Minuten
- → Script hat automatische Delays eingebaut

---

## ✅ CHECKLISTE

- [ ] Reddit Account erstellt und Email bestätigt
- [ ] App auf https://www.reddit.com/prefs/apps erstellt
- [ ] CLIENT_ID kopiert
- [ ] CLIENT_SECRET kopiert
- [ ] Environment-Variablen im PowerShell gesetzt
- [ ] Validierung durchgeführt (`Get-ChildItem Env:REDDIT*`)
- [ ] **BEREIT FÜR: `python reddit-automation.py`**

---

**🎯 NÄCHSTER SCHRITT:** Nach Credentials-Setup → Reddit Automation ausführen
