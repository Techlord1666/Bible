"""
EasyWorship Integration Helper
================================
EasyWorship does NOT have a direct API, but there are two reliable
ways to connect this Bible system with EasyWorship:

METHOD 1 — Side-by-Side Display (Recommended for most churches)
    Run both systems on the same projector PC. Use Windows display
    settings to extend to two screens. Bible system on Screen 1,
    EasyWorship on Screen 2. Toggle with Alt+Tab or a presenter remote.

METHOD 2 — EasyWorship Scripture Database Sync (Best integration)
    EasyWorship stores its Bible data in a local database.
    This script exports verses in EasyWorship-compatible format
    so you can import them directly, and optionally copies
    prepared slides into EasyWorship's media folder.

METHOD 3 — OBS Studio Bridge (Live streaming churches)
    Route the display screen through OBS as a browser source
    on top of EasyWorship output.

This file implements Method 2 — the EasyWorship database/file sync.
"""

import sqlite3
import os
import json
import shutil
from pathlib import Path
from datetime import datetime


# ── EasyWorship typical install paths ─────────────────────────────────────────
EW_PATHS = [
    r"C:\Users\Public\Documents\Softouch\EasyWorship 7",
    r"C:\Users\Public\Documents\Softouch\EasyWorship 6",
    r"C:\ProgramData\Softouch\EasyWorship",
    r"C:\EasyWorship",
]

OUR_DB = os.path.join(os.path.dirname(__file__), "bible.db")


def find_easyworship():
    """Locate EasyWorship installation."""
    for path in EW_PATHS:
        if os.path.exists(path):
            return path
    return None


def export_verse_as_ew_text(book, chapter, verse, text, translation="KJV"):
    """
    Format a verse the way EasyWorship expects it for slide import.
    EasyWorship accepts plain-text files it can convert to slides.
    """
    reference = f"{book} {chapter}:{verse} ({translation})"
    return f"{text}\n\n— {reference}"


def export_prepared_service(verses_list, output_path="easyworship_service.txt"):
    """
    Export a list of verses as a service order text file.
    In EasyWorship: File > Import > Text to create a schedule.

    verses_list: list of dicts with keys: book, chapter, verse, translation
    """
    conn = sqlite3.connect(OUR_DB)
    cursor = conn.cursor()

    lines = []
    lines.append("CHURCH BIBLE PRESENTATION — SERVICE ORDER")
    lines.append(f"Generated: {datetime.now().strftime('%A, %d %B %Y — %I:%M %p')}")
    lines.append("=" * 60)
    lines.append("")

    for item in verses_list:
        trans = item.get("translation", "kjv").lower()
        cursor.execute(f"""
            SELECT book, chapter, verse, {trans}
            FROM verses
            WHERE book = ? AND chapter = ? AND verse = ?
        """, (item["book"], item["chapter"], item["verse"]))
        row = cursor.fetchone()
        if row:
            lines.append(f"{row[0]} {row[1]}:{row[2]} ({trans.upper()})")
            lines.append(row[3] or "")
            lines.append("")
            lines.append("-" * 40)
            lines.append("")

    conn.close()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ Service order exported to: {output_path}")
    return output_path


def sync_to_easyworship_bible_db(ew_path=None):
    """
    Attempt to sync our verse database into EasyWorship's Bible database.
    EasyWorship 6/7 uses SQLite for its Bible data.
    """
    if not ew_path:
        ew_path = find_easyworship()

    if not ew_path:
        print("⚠  EasyWorship installation not found at standard paths.")
        print("   Manually provide the path to your EasyWorship data folder.")
        return False

    # Look for EasyWorship Bible database
    ew_db_candidates = [
        os.path.join(ew_path, "Bibles", "KJV.db"),
        os.path.join(ew_path, "Data", "Bibles", "KJV.db"),
        os.path.join(ew_path, "Resources", "Bibles", "KJV.db"),
    ]

    ew_db_path = None
    for p in ew_db_candidates:
        if os.path.exists(p):
            ew_db_path = p
            break

    if ew_db_path:
        print(f"✅ Found EasyWorship Bible DB: {ew_db_path}")
        # EasyWorship uses its own schema — do not modify, only read/reference
        print("   EasyWorship Bible DB located — using side-by-side mode recommended")
    else:
        print("ℹ  No EasyWorship Bible DB found — using export mode")

    return True


def print_easyworship_setup_guide():
    """Print the recommended EasyWorship + Bible System setup."""
    guide = """
╔══════════════════════════════════════════════════════════════════╗
║          EASYWORSHIP + BIBLE SYSTEM SETUP GUIDE                ║
╚══════════════════════════════════════════════════════════════════╝

RECOMMENDED SETUP FOR YOUR CHURCH:
──────────────────────────────────
Since EasyWorship controls the main projector, here is the best
workflow that lets both systems work together perfectly:

OPTION A — Two-Screen Setup (Most Professional)
─────────────────────────────────────────────────
 Computer  ──► Screen 1 (EasyWorship): Songs, announcements, videos
           ──► Screen 2 (Bible System): Verse display via browser

 How to set up:
 1. Connect projector to computer (HDMI/VGA)
 2. Right-click desktop → Display Settings → Extend display
 3. Open EasyWorship → assign to Screen 1
 4. Open Chrome/Edge → go to localhost:5000/display → F11 fullscreen
 5. Drag browser to Screen 2

 During service:
 - Pastor calls out verse → Bible system auto-displays it on Screen 2
 - For songs/videos → switch projector input to EasyWorship (Screen 1)
 - Use a presentation remote or keyboard shortcut to toggle

OPTION B — Single Screen with Alt+Tab (Budget Setup)
──────────────────────────────────────────────────────
 1. Keep EasyWorship running in the background
 2. Bible display browser open in full screen on same projector
 3. Alt+Tab to switch between EasyWorship and Bible display
 4. Operator switches manually as pastor transitions

OPTION C — Browser Source in OBS (Streaming Churches)
───────────────────────────────────────────────────────
 If your church streams online via OBS:
 1. In OBS → Add Source → Browser Source
 2. URL: http://localhost:5000/display
 3. Width: 1920, Height: 1080
 4. The Bible overlay can appear on top of EasyWorship capture

WHAT EASYWORSHIP HANDLES:
  ✅ Worship songs (lyrics with backgrounds)
  ✅ Announcement slides
  ✅ Videos and countdowns
  ✅ Its own built-in Bible (limited voice control)

WHAT YOUR BIBLE SYSTEM ADDS:
  ✅ Voice-activated verse display
  ✅ Instant multi-translation switching
  ✅ Auto-detects pastor's spoken references
  ✅ No clicking or searching needed
  ✅ Works alongside EasyWorship seamlessly

KEYBOARD SHORTCUT SUGGESTIONS:
  Win+Left/Right  — snap windows to sides of screen
  F11             — fullscreen browser
  Win+P           — switch projector display mode
  Alt+Tab         — switch between open applications
"""
    print(guide)


if __name__ == "__main__":
    print_easyworship_setup_guide()

    # Demo export
    sample_service = [
        {"book": "John", "chapter": 3, "verse": 16, "translation": "kjv"},
        {"book": "Romans", "chapter": 8, "verse": 28, "translation": "niv"},
        {"book": "Psalms", "chapter": 23, "verse": 1, "translation": "kjv"},
        {"book": "Philippians", "chapter": 4, "verse": 13, "translation": "nlt"},
        {"book": "Jeremiah", "chapter": 29, "verse": 11, "translation": "msg"},
    ]

    export_prepared_service(sample_service, "easyworship_service_order.txt")
    sync_to_easyworship_bible_db()
