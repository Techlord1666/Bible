-- ============================================================
-- Church Bible Verse Presentation System
-- Database Schema
-- ============================================================

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- Core Bible verses table
CREATE TABLE IF NOT EXISTS verses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    book        TEXT    NOT NULL,
    book_abbr   TEXT    NOT NULL,
    chapter     INTEGER NOT NULL,
    verse       INTEGER NOT NULL,
    kjv         TEXT,
    niv         TEXT,
    msg         TEXT,
    nlt         TEXT,
    esv         TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(book, chapter, verse)
);

-- Book aliases table for speech recognition flexibility
CREATE TABLE IF NOT EXISTS book_aliases (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    alias       TEXT    NOT NULL UNIQUE,
    book_name   TEXT    NOT NULL
);

-- Display history log
CREATE TABLE IF NOT EXISTS display_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    book        TEXT    NOT NULL,
    chapter     INTEGER NOT NULL,
    verse       INTEGER NOT NULL,
    version     TEXT    NOT NULL DEFAULT 'KJV',
    speech_text TEXT,
    displayed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fast lookup
CREATE INDEX IF NOT EXISTS idx_verses_ref ON verses(book, chapter, verse);
CREATE INDEX IF NOT EXISTS idx_verses_book ON verses(book);
CREATE INDEX IF NOT EXISTS idx_book_aliases ON book_aliases(alias);

-- ============================================================
-- Book Aliases (handles speech variations)
-- ============================================================
INSERT OR IGNORE INTO book_aliases (alias, book_name) VALUES
-- Old Testament
('gen', 'Genesis'), ('genesis', 'Genesis'),
('exo', 'Exodus'), ('exodus', 'Exodus'),
('lev', 'Leviticus'), ('leviticus', 'Leviticus'),
('num', 'Numbers'), ('numbers', 'Numbers'),
('deu', 'Deuteronomy'), ('deuteronomy', 'Deuteronomy'), ('deut', 'Deuteronomy'),
('josh', 'Joshua'), ('joshua', 'Joshua'),
('judg', 'Judges'), ('judges', 'Judges'),
('ruth', 'Ruth'),
('1sam', '1 Samuel'), ('1 samuel', '1 Samuel'), ('first samuel', '1 Samuel'),
('2sam', '2 Samuel'), ('2 samuel', '2 Samuel'), ('second samuel', '2 Samuel'),
('1ki', '1 Kings'), ('1 kings', '1 Kings'), ('first kings', '1 Kings'),
('2ki', '2 Kings'), ('2 kings', '2 Kings'), ('second kings', '2 Kings'),
('1chr', '1 Chronicles'), ('1 chronicles', '1 Chronicles'), ('first chronicles', '1 Chronicles'),
('2chr', '2 Chronicles'), ('2 chronicles', '2 Chronicles'), ('second chronicles', '2 Chronicles'),
('ezra', 'Ezra'),
('neh', 'Nehemiah'), ('nehemiah', 'Nehemiah'),
('esth', 'Esther'), ('esther', 'Esther'),
('job', 'Job'),
('ps', 'Psalms'), ('psa', 'Psalms'), ('psalm', 'Psalms'), ('psalms', 'Psalms'),
('prov', 'Proverbs'), ('proverbs', 'Proverbs'),
('eccl', 'Ecclesiastes'), ('ecclesiastes', 'Ecclesiastes'),
('song', 'Song of Solomon'), ('songs', 'Song of Solomon'), ('song of solomon', 'Song of Solomon'),
('isa', 'Isaiah'), ('isaiah', 'Isaiah'),
('jer', 'Jeremiah'), ('jeremiah', 'Jeremiah'),
('lam', 'Lamentations'), ('lamentations', 'Lamentations'),
('ezek', 'Ezekiel'), ('ezekiel', 'Ezekiel'),
('dan', 'Daniel'), ('daniel', 'Daniel'),
('hos', 'Hosea'), ('hosea', 'Hosea'),
('joel', 'Joel'),
('amos', 'Amos'),
('obad', 'Obadiah'), ('obadiah', 'Obadiah'),
('jonah', 'Jonah'),
('mic', 'Micah'), ('micah', 'Micah'),
('nah', 'Nahum'), ('nahum', 'Nahum'),
('hab', 'Habakkuk'), ('habakkuk', 'Habakkuk'),
('zeph', 'Zephaniah'), ('zephaniah', 'Zephaniah'),
('hag', 'Haggai'), ('haggai', 'Haggai'),
('zech', 'Zechariah'), ('zechariah', 'Zechariah'),
('mal', 'Malachi'), ('malachi', 'Malachi'),
-- New Testament
('matt', 'Matthew'), ('matthew', 'Matthew'),
('mark', 'Mark'),
('luke', 'Luke'),
('john', 'John'),
('acts', 'Acts'),
('rom', 'Romans'), ('romans', 'Romans'),
('1cor', '1 Corinthians'), ('1 corinthians', '1 Corinthians'), ('first corinthians', '1 Corinthians'),
('2cor', '2 Corinthians'), ('2 corinthians', '2 Corinthians'), ('second corinthians', '2 Corinthians'),
('gal', 'Galatians'), ('galatians', 'Galatians'),
('eph', 'Ephesians'), ('ephesians', 'Ephesians'),
('phil', 'Philippians'), ('philippians', 'Philippians'),
('col', 'Colossians'), ('colossians', 'Colossians'),
('1thess', '1 Thessalonians'), ('1 thessalonians', '1 Thessalonians'), ('first thessalonians', '1 Thessalonians'),
('2thess', '2 Thessalonians'), ('2 thessalonians', '2 Thessalonians'), ('second thessalonians', '2 Thessalonians'),
('1tim', '1 Timothy'), ('1 timothy', '1 Timothy'), ('first timothy', '1 Timothy'),
('2tim', '2 Timothy'), ('2 timothy', '2 Timothy'), ('second timothy', '2 Timothy'),
('titus', 'Titus'),
('phlm', 'Philemon'), ('philemon', 'Philemon'),
('heb', 'Hebrews'), ('hebrews', 'Hebrews'),
('jas', 'James'), ('james', 'James'),
('1pet', '1 Peter'), ('1 peter', '1 Peter'), ('first peter', '1 Peter'),
('2pet', '2 Peter'), ('2 peter', '2 Peter'), ('second peter', '2 Peter'),
('1john', '1 John'), ('1 john', '1 John'), ('first john', '1 John'),
('2john', '2 John'), ('2 john', '2 John'), ('second john', '2 John'),
('3john', '3 John'), ('3 john', '3 John'), ('third john', '3 John'),
('jude', 'Jude'),
('rev', 'Revelation'), ('revelation', 'Revelation'), ('revelations', 'Revelation');
