# ✝ Church Bible Verse Presentation System

A production-grade voice-driven Bible verse display system for churches.
The pastor speaks a Bible reference, and it instantly appears on the projector screen.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PASTOR'S MICROPHONE                   │
│                   "John 3:16 in NIV"                     │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              WHISPER SPEECH RECOGNITION                  │
│              (runs locally — no internet)                │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  BIBLE REFERENCE PARSER                  │
│    Extracts: Book · Chapter · Verse · Translation        │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   SQLITE DATABASE                        │
│       book | chapter | verse | kjv | niv | msg | nlt    │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              FLASK + SSE (real-time push)                │
└──────────────┬─────────────────────────┬────────────────┘
               │                         │
               ▼                         ▼
    ┌─────────────────┐       ┌──────────────────────┐
    │  Control Panel  │       │   Projector Display  │
    │ localhost:5000  │       │  localhost:5000/display│
    │ (operator view) │       │  (large text screen) │
    └─────────────────┘       └──────────────────────┘
```

---

## Project Structure

```
church-bible-system/
├── backend/
│   ├── app.py          ← Flask server, SSE, Whisper loop
│   └── parser.py       ← Speech-to-reference parser
├── database/
│   ├── schema.sql      ← Database schema + book aliases
│   ├── seed.py         ← Sample verse loader
│   └── bible.db        ← Created on first run
├── frontend/
│   ├── display.html    ← Projector screen (large text)
│   └── control.html    ← Operator control panel
├── requirements.txt
└── README.md
```

---

## Quick Start

### Step 1 — Install Python dependencies

```bash
cd church-bible-system
pip install -r requirements.txt
```

> **macOS audio note:** You may need PortAudio for sounddevice:
> ```bash
> brew install portaudio
> ```

> **Linux audio note:**
> ```bash
> sudo apt-get install portaudio19-dev python3-pyaudio
> ```

### Step 2 — Initialize the database

```bash
python database/seed.py
```

This creates `database/bible.db` with ~30 commonly preached verses across 5 translations.

### Step 3 — Start the server

```bash
python backend/app.py
```

### Step 4 — Open the two windows

| Window | URL | Who opens it |
|--------|-----|--------------|
| **Control Panel** | `http://localhost:5000` | Operator / sound tech |
| **Display Screen** | `http://localhost:5000/display` | Projected on church screen |

### Step 5 — Start listening

In the Control Panel, click **"Start Listening"** — the system will
continuously listen to the pastor through the microphone.

---

## How the Pastor Uses It

The pastor simply speaks naturally:

| Spoken phrase | What happens |
|---------------|-------------|
| `"John 3:16"` | Displays John 3:16 in KJV (default) |
| `"Romans 8:28"` | Displays Romans 8:28 in KJV |
| `"John 3:16 in NIV"` | Switches to NIV translation |
| `"Show Psalm 23 in The Message"` | Displays in MSG translation |
| `"Philippians chapter 4 verse 13"` | Handles spoken format |
| `"First Corinthians 13:4"` | Handles ordinal book names |

### Supported translations

| Code | Full name |
|------|-----------|
| KJV | King James Version *(default)* |
| NIV | New International Version |
| MSG | The Message |
| NLT | New Living Translation |
| ESV | English Standard Version |

---

## Loading the Full Bible

The seed data includes ~30 key verses. To load the complete Bible:

1. Download a Bible dataset CSV (many are freely available for non-commercial church use, e.g. from [bible-corpus](https://github.com/christos-c/bible-corpus))

2. Import into the database:

```python
import sqlite3, csv

conn = sqlite3.connect('database/bible.db')
cursor = conn.cursor()

with open('full_bible.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cursor.execute("""
            INSERT OR REPLACE INTO verses (book, book_abbr, chapter, verse, kjv, niv, msg, nlt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (row['book'], row['abbr'], int(row['chapter']),
              int(row['verse']), row['kjv'], row['niv'], row['msg'], row['nlt']))

conn.commit()
conn.close()
```

---

## Network Setup (Projector on a Separate Computer)

If the display screen is on a different computer:

1. Find the server machine's local IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
2. Open on the display computer: `http://192.168.x.x:5000/display`
3. Both computers must be on the same Wi-Fi / church network

---

## Control Panel Features

- **Voice recognition toggle** — start/stop Whisper listening
- **Test speech input** — type a phrase and simulate voice recognition
- **Direct verse lookup** — manually select book/chapter/verse/translation
- **Quick reference buttons** — one-click most popular verses
- **Activity log** — real-time feed of all speech and display events
- **Display history** — last 20 verses shown with timestamps

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Microphone not detected | Check system audio input settings |
| Whisper model slow to load | First load downloads the model (~140MB) — subsequent loads are instant |
| Verse not found | Check the verse is in the database; run `seed.py` to verify |
| Display not updating | Ensure both windows are open to the same server |
| Book name not recognized | Try alternative spelling; check `book_aliases` table |

---

## Technical Notes

- Whisper runs entirely **locally** — no internet required during service
- SSE (Server-Sent Events) provides **real-time push** from server to display
- The display screen auto-reconnects if the connection drops
- All display events are logged to `display_log` table for record-keeping
- The system handles concurrent listeners (multiple operator devices)

---

*Built for church ministry — to God be the glory.*
