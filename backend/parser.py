"""
Bible Reference Parser
Extracts book, chapter, verse and translation from speech text.
"""

import re
import sqlite3
import os
import logging
from dataclasses import dataclass
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "bible.db")

# ── Translation keyword map ────────────────────────────────────────────────────
TRANSLATION_MAP = {
    # KJV variants
    "kjv": "kjv", "king james": "kjv", "king james version": "kjv",
    "authorized": "kjv", "authorized version": "kjv",
    # NIV variants
    "niv": "niv", "new international": "niv", "new international version": "niv",
    # The Message variants
    "msg": "msg", "message": "msg", "the message": "msg",
    # NLT variants
    "nlt": "nlt", "new living": "nlt", "new living translation": "nlt",
    # ESV variants
    "esv": "esv", "english standard": "esv", "english standard version": "esv",
}

# ── Number word to digit map ───────────────────────────────────────────────────
NUMBER_WORDS = {
    "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
    "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
    "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14",
    "fifteen": "15", "sixteen": "16", "seventeen": "17", "eighteen": "18",
    "nineteen": "19", "twenty": "20", "thirty": "30", "forty": "40",
    "fifty": "50", "sixty": "60", "seventy": "70", "eighty": "80",
    "ninety": "90", "hundred": "100",
    # Ordinals
    "first": "1", "second": "2", "third": "3",
}

# ── Book name normalization ────────────────────────────────────────────────────
BOOK_PREFIX_MAP = {
    "first": "1", "second": "2", "third": "3",
    "1st": "1", "2nd": "2", "3rd": "3",
}


@dataclass
class BibleReference:
    book: str
    chapter: int
    verse: int
    translation: str = "kjv"
    raw_text: str = ""

    def display_ref(self) -> str:
        return f"{self.book} {self.chapter}:{self.verse}"

    def translation_upper(self) -> str:
        return self.translation.upper()


def _normalize_numbers(text: str) -> str:
    """Replace spoken number words with digits."""
    words = text.split()
    result = []
    i = 0
    while i < len(words):
        w = words[i].lower().rstrip(".,;:!?")
        # Handle "twenty one" style compound numbers
        if w in NUMBER_WORDS and i + 1 < len(words):
            next_w = words[i + 1].lower().rstrip(".,;:!?")
            if next_w in NUMBER_WORDS and int(NUMBER_WORDS[w]) >= 20:
                combined = int(NUMBER_WORDS[w]) + int(NUMBER_WORDS[next_w])
                result.append(str(combined))
                i += 2
                continue
        if w in NUMBER_WORDS:
            result.append(NUMBER_WORDS[w])
        else:
            result.append(words[i])
        i += 1
    return " ".join(result)


def _detect_translation(text: str) -> Tuple[str, str]:
    """
    Detect the requested translation from speech text.
    Returns (translation_code, cleaned_text_with_version_phrase_removed)
    """
    text_lower = text.lower()
    detected = "kjv"

    # Look for version markers: "in NIV", "in the Message", "NIV version"
    patterns = [
        r"\b(?:in\s+the\s+|in\s+|show\s+in\s+)?({versions})\b".format(
            versions="|".join(re.escape(k) for k in sorted(TRANSLATION_MAP.keys(), key=len, reverse=True))
        ),
        r"\b({versions})\s+(?:version|translation|bible)\b".format(
            versions="|".join(re.escape(k) for k in sorted(TRANSLATION_MAP.keys(), key=len, reverse=True))
        ),
    ]

    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            found = match.group(1).strip()
            detected = TRANSLATION_MAP.get(found, "kjv")
            # Remove the matched phrase from text to clean up reference parsing
            text = text[:match.start()] + text[match.end():]
            break

    return detected, text.strip()


def _load_book_aliases(conn: sqlite3.Connection) -> dict:
    """Load book alias map from database."""
    cursor = conn.cursor()
    cursor.execute("SELECT alias, book_name FROM book_aliases")
    return {row[0].lower(): row[1] for row in cursor.fetchall()}


def _resolve_book(raw_book: str, aliases: dict) -> Optional[str]:
    """Resolve a raw book string to canonical book name."""
    raw = raw_book.lower().strip()

    # Direct alias match
    if raw in aliases:
        return aliases[raw]

    # Normalize "first/second/third" prefixes
    for prefix, num in BOOK_PREFIX_MAP.items():
        if raw.startswith(prefix + " "):
            normalized = num + " " + raw[len(prefix) + 1:]
            if normalized in aliases:
                return aliases[normalized]

    # Partial match fallback
    for alias, book in aliases.items():
        if raw.startswith(alias) or alias.startswith(raw):
            return book

    return None


def parse_reference(text: str, db_path: str = DB_PATH) -> Optional[BibleReference]:
    """
    Parse a Bible reference from speech text.

    Handles formats like:
      - "John 3:16"
      - "Romans chapter 8 verse 28"
      - "Psalm 23 verse 1"
      - "John 3 16" (no colon)
      - "Show John 3:16 in NIV"
      - "Romans 8:28 New International Version"
    """
    if not text or not text.strip():
        return None

    original_text = text
    text = _normalize_numbers(text)
    translation, text = _detect_translation(text)

    # Strip common verbal prefixes: "Show", "Read", "Display", "Turn to", "Open to", etc.
    text = re.sub(r"^\s*(?:show|read|display|open\s+to|turn\s+to|go\s+to|let(?:'s|\s+us)?\s+(?:look\s+at|read|go\s+to)?)\s+", "", text, flags=re.IGNORECASE).strip()

    # ── Reference patterns (ordered most specific → least) ─────────────────
    REF_PATTERNS = [
        # "John 3:16" or "John 3 : 16"
        r"(?P<book>[1-3]?\s*[A-Za-z]+(?:\s+[A-Za-z]+)?)\s+(?P<ch>\d+)\s*[:\-]\s*(?P<vs>\d+)",
        # "John chapter 3 verse 16"
        r"(?P<book>[1-3]?\s*[A-Za-z]+(?:\s+[A-Za-z]+)?)\s+chapter\s+(?P<ch>\d+)\s+verse\s+(?P<vs>\d+)",
        # "John 3 verse 16"
        r"(?P<book>[1-3]?\s*[A-Za-z]+(?:\s+[A-Za-z]+)?)\s+(?P<ch>\d+)\s+verse\s+(?P<vs>\d+)",
        # "John 3 16" (ambiguous but common in speech)
        r"(?P<book>[1-3]?\s*[A-Za-z]+(?:\s+[A-Za-z]+)?)\s+(?P<ch>\d+)\s+(?P<vs>\d+)",
    ]

    try:
        conn = sqlite3.connect(db_path)
        aliases = _load_book_aliases(conn)
        conn.close()
    except Exception as e:
        logger.error(f"Database error loading aliases: {e}")
        aliases = {}

    for pattern in REF_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            continue

        raw_book = match.group("book").strip()
        chapter = int(match.group("ch"))
        verse = int(match.group("vs"))

        book = _resolve_book(raw_book, aliases)
        if not book:
            continue

        return BibleReference(
            book=book,
            chapter=chapter,
            verse=verse,
            translation=translation,
            raw_text=original_text,
        )

    return None


def fetch_verse(ref: BibleReference, db_path: str = DB_PATH) -> Optional[dict]:
    """Fetch a verse from the database given a BibleReference."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Allow Psalms/Psalm interchangeably
        book_variants = [ref.book]
        if ref.book.lower() == "psalms":
            book_variants.append("Psalm")
        elif ref.book.lower() == "psalm":
            book_variants.append("Psalms")

        placeholders = ",".join("?" * len(book_variants))
        cursor.execute(f"""
            SELECT book, chapter, verse, kjv, niv, msg, nlt, esv
            FROM verses
            WHERE book IN ({placeholders}) AND chapter = ? AND verse = ?
        """, (*book_variants, ref.chapter, ref.verse))

        row = cursor.fetchone()

        if row:
            translation = ref.translation.lower()
            translation_col_map = {
                "kjv": row[3], "niv": row[4], "msg": row[5], "nlt": row[6], "esv": row[7]
            }
            verse_text = translation_col_map.get(translation) or row[3]  # fallback to KJV

            # Log the display
            cursor.execute("""
                INSERT INTO display_log (book, chapter, verse, version, speech_text)
                VALUES (?, ?, ?, ?, ?)
            """, (row[0], row[1], row[2], translation.upper(), ref.raw_text))
            conn.commit()

            result = {
                "book": row[0],
                "chapter": row[1],
                "verse": row[2],
                "text": verse_text,
                "translation": translation.upper(),
                "reference": f"{row[0]} {row[1]}:{row[2]}",
                "available_translations": {
                    "KJV": bool(row[3]),
                    "NIV": bool(row[4]),
                    "MSG": bool(row[5]),
                    "NLT": bool(row[6]),
                    "ESV": bool(row[7]),
                }
            }
            conn.close()
            return result

        conn.close()
        return None

    except Exception as e:
        logger.error(f"Database error fetching verse: {e}")
        return None
