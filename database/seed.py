"""
Church Bible Verse Presentation System
Database initialization and seeding script
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "bible.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

# ============================================================
# Sample verse dataset — expand this with a full Bible import
# These are the most commonly preached verses as a starter set
# ============================================================
SAMPLE_VERSES = [
    # (book, book_abbr, chapter, verse, kjv, niv, msg, nlt)
    ("John", "Jn", 3, 16,
     "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.",
     "For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life.",
     "This is how much God loved the world: He gave his Son, his one and only Son. And this is why: so that no one need be destroyed; by believing in him, anyone can have a whole and lasting life.",
     "For this is how God loved the world: He gave his one and only Son, so that everyone who believes in him will not perish but have eternal life."),

    ("John", "Jn", 3, 17,
     "For God sent not his Son into the world to condemn the world; but that the world through him might be saved.",
     "For God did not send his Son into the world to condemn the world, but to save the world through him.",
     "God didn't go to all the trouble of sending his Son merely to point an accusing finger, telling the world how bad it was. He came to help, to put the world right again.",
     "God sent his Son into the world not to judge the world, but to save the world through him."),

    ("Romans", "Rom", 8, 28,
     "And we know that all things work together for good to them that love God, to them who are the called according to his purpose.",
     "And we know that in all things God works for the good of those who love him, who have been called according to his purpose.",
     "That's why we can be so sure that every detail in our lives of love for God is worked into something good.",
     "And we know that God causes everything to work together for the good of those who love God and are called according to his purpose for them."),

    ("Psalms", "Ps", 23, 1,
     "The LORD is my shepherd; I shall not want.",
     "The Lord is my shepherd, I lack nothing.",
     "God, my shepherd! I don't need a thing.",
     "The Lord is my shepherd; I have all that I need."),

    ("Psalms", "Ps", 23, 2,
     "He maketh me to lie down in green pastures: he leadeth me beside the still waters.",
     "He makes me lie down in green pastures, he leads me beside quiet waters,",
     "You have bedded me down in lush meadows, you find me quiet pools to drink from.",
     "He lets me rest in green meadows; he leads me beside peaceful streams."),

    ("Psalms", "Ps", 23, 3,
     "He restoreth my soul: he leadeth me in the paths of righteousness for his name's sake.",
     "he refreshes my soul. He guides me along the right paths for his name's sake.",
     "True to your word, you let me catch my breath and send me in the right direction.",
     "He renews my strength. He guides me along right paths, bringing honor to his name."),

    ("Psalms", "Ps", 23, 4,
     "Yea, though I walk through the valley of the shadow of death, I will fear no evil: for thou art with me; thy rod and thy staff they comfort me.",
     "Even though I walk through the darkest valley, I will fear no evil, for you are with me; your rod and your staff, they comfort me.",
     "Even when the way goes through Death Valley, I'm not afraid when you walk at my side. Your trusty shepherd's crook makes me feel secure.",
     "Even when I walk through the darkest valley, I will not be afraid, for you are close beside me. Your rod and your staff protect and comfort me."),

    ("Psalms", "Ps", 23, 5,
     "Thou preparest a table before me in the presence of mine enemies: thou anointest my head with oil; my cup runneth over.",
     "You prepare a table before me in the presence of my enemies. You anoint my head with oil; my cup overflows.",
     "You serve me a six-course dinner right in front of my enemies. You revive my drooping head; my cup brims with blessing.",
     "You prepare a feast for me in the presence of my enemies. You honor me by anointing my head with oil. My cup overflows with blessings."),

    ("Psalms", "Ps", 23, 6,
     "Surely goodness and mercy shall follow me all the days of my life: and I will dwell in the house of the LORD for ever.",
     "Surely your goodness and love will follow me all the days of my life, and I will dwell in the house of the Lord forever.",
     "Your beauty and love chase after me every day of my life. I'm back home in the house of God for the rest of my life.",
     "Surely your goodness and unfailing love will pursue me all the days of my life, and I will live in the house of the Lord forever."),

    ("Jeremiah", "Jer", 29, 11,
     "For I know the thoughts that I think toward you, saith the LORD, thoughts of peace, and not of evil, to give you an expected end.",
     "For I know the plans I have for you, declares the Lord, plans to prosper you and not to harm you, plans to give you hope and a future.",
     "I know what I'm doing. I have it all planned out—plans to take care of you, not abandon you, plans to give you the future you hope for.",
     "For I know the plans I have for you, says the Lord. They are plans for good and not for disaster, to give you a future and a hope."),

    ("Philippians", "Phil", 4, 13,
     "I can do all things through Christ which strengtheneth me.",
     "I can do all this through him who gives me strength.",
     "Whatever I have, wherever I am, I can make it through anything in the One who makes me who I am.",
     "For I can do everything through Christ, who gives me strength."),

    ("Philippians", "Phil", 4, 6,
     "Be careful for nothing; but in every thing by prayer and supplication with thanksgiving let your requests be made known unto God.",
     "Do not be anxious about anything, but in every situation, by prayer and petition, with thanksgiving, present your requests to God.",
     "Don't fret or worry. Instead of worrying, pray. Let petitions and praises shape your worries into prayers, letting God know your concerns.",
     "Don't worry about anything; instead, pray about everything. Tell God what you need, and thank him for all he has done."),

    ("Philippians", "Phil", 4, 7,
     "And the peace of God, which passeth all understanding, shall keep your hearts and minds through Christ Jesus.",
     "And the peace of God, which transcends all understanding, will guard your hearts and your minds in Christ Jesus.",
     "Before you know it, a sense of God's wholeness, everything coming together for good, will come and settle you down. It's wonderful what happens when Christ displaces worry at the center of your life.",
     "Then you will experience God's peace, which exceeds anything we can understand. His peace will guard your hearts and minds as you live in Christ Jesus."),

    ("Proverbs", "Prov", 3, 5,
     "Trust in the LORD with all thine heart; and lean not unto thine own understanding.",
     "Trust in the Lord with all your heart and lean not on your own understanding;",
     "Trust God from the bottom of your heart; don't try to figure out everything on your own.",
     "Trust in the Lord with all your heart; do not depend on your own understanding."),

    ("Proverbs", "Prov", 3, 6,
     "In all thy ways acknowledge him, and he shall direct thy paths.",
     "in all your ways submit to him, and he will make your paths straight.",
     "Listen for God's voice in everything you do, everywhere you go; he's the one who will keep you on track.",
     "Seek his will in all you do, and he will show you which path to take."),

    ("Isaiah", "Isa", 40, 31,
     "But they that wait upon the LORD shall renew their strength; they shall mount up with wings as eagles; they shall run, and not be weary; and they shall walk, and not faint.",
     "but those who hope in the Lord will renew their strength. They will soar on wings like eagles; they will run and not grow weary, they will walk and not be faint.",
     "But those who wait upon God get fresh strength. They spread their wings and soar like eagles, They run and don't get tired, they walk and don't lag behind.",
     "But those who trust in the Lord will find new strength. They will soar high on wings like eagles. They will run and not grow weary. They will walk and not faint."),

    ("Matthew", "Matt", 6, 33,
     "But seek ye first the kingdom of God, and his righteousness; and all these things shall be added unto you.",
     "But seek first his kingdom and his righteousness, and all these things will be given to you as well.",
     "Steep your life in God-reality, God-initiative, God-provisions. Don't worry about missing out. You'll find all your everyday human concerns will be met.",
     "Seek the Kingdom of God above all else, and live righteously, and he will give you everything you need."),

    ("Matthew", "Matt", 11, 28,
     "Come unto me, all ye that labour and are heavy laden, and I will give you rest.",
     "Come to me, all you who are weary and burdened, and I will give you rest.",
     "Are you tired? Worn out? Burned out on religion? Come to me. Get away with me and you'll recover your life.",
     "Then Jesus said, Come to me, all of you who are weary and carry heavy burdens, and I will give you rest."),

    ("Genesis", "Gen", 1, 1,
     "In the beginning God created the heaven and the earth.",
     "In the beginning God created the heavens and the earth.",
     "First this: God created the Heavens and Earth—all you see, all you don't see.",
     "In the beginning God created the heavens and the earth."),

    ("Ephesians", "Eph", 2, 8,
     "For by grace are ye saved through faith; and that not of yourselves: it is the gift of God:",
     "For it is by grace you have been saved, through faith—and this is not from yourselves, it is the gift of God—",
     "Saving is all his idea, and all his work. All we do is trust him enough to let him do it. It's God's gift from start to finish!",
     "God saved you by his grace when you believed. And you can't take credit for this; it is a gift from God."),

    ("Ephesians", "Eph", 2, 9,
     "Not of works, lest any man should boast.",
     "not by works, so that no one can boast.",
     "We don't play the major role. If we did, we'd probably go around bragging that we'd done the whole thing!",
     "Salvation is not a reward for the good things we have done, so none of us can boast about it."),

    ("2 Timothy", "2Tim", 3, 16,
     "All scripture is given by inspiration of God, and is profitable for doctrine, for reproof, for correction, for instruction in righteousness:",
     "All Scripture is God-breathed and is useful for teaching, rebuking, correcting and training in righteousness,",
     "Every part of Scripture is God-breathed and useful one way or another—showing us truth, exposing our rebellion, correcting our mistakes, training us to live God's way.",
     "All Scripture is inspired by God and is useful to teach us what is true and to make us realize what is wrong in our lives. It corrects us when we are wrong and teaches us to do what is right."),

    ("1 John", "1Jn", 4, 8,
     "He that loveth not knoweth not God; for God is love.",
     "Whoever does not love does not know God, because God is love.",
     "If you don't love, you don't know the first thing about God, because God is love—so you can't know him if you don't love.",
     "But anyone who does not love others does not know God, for God is love."),

    ("Galatians", "Gal", 5, 22,
     "But the fruit of the Spirit is love, joy, peace, longsuffering, gentleness, goodness, faith,",
     "But the fruit of the Spirit is love, joy, peace, forbearance, kindness, goodness, faithfulness,",
     "But what happens when we live God's way? He brings gifts into our lives, much the same way that fruit appears in an orchard—things like affection for others, exuberance about life, serenity.",
     "But the Holy Spirit produces this kind of fruit in our lives: love, joy, peace, patience, kindness, goodness, faithfulness,"),

    ("Hebrews", "Heb", 11, 1,
     "Now faith is the substance of things hoped for, the evidence of things not seen.",
     "Now faith is confidence in what we hope for and assurance about what we do not see.",
     "The fundamental fact of existence is that this trust in God, this faith, is the firm foundation under everything that makes life worth living. It's our handle on what we can't see.",
     "Faith shows the reality of what we hope for; it is the evidence of things we cannot see."),

    ("Romans", "Rom", 3, 23,
     "For all have sinned, and come short of the glory of God;",
     "for all have sinned and fall short of the glory of God,",
     "Since we've compiled this long and sorry record as sinners and proved that we are utterly incapable of living the glorious lives God wills for us,",
     "For everyone has sinned; we all fall short of God's glorious standard."),

    ("Romans", "Rom", 6, 23,
     "For the wages of sin is death; but the gift of God is eternal life through Jesus Christ our Lord.",
     "For the wages of sin is death, but the gift of God is eternal life in Christ Jesus our Lord.",
     "Work hard for sin your whole life and your pension is death. But God's gift is real life, eternal life, delivered by Jesus, our Master.",
     "For the wages of sin is death, but the free gift of God is eternal life through Christ Jesus our Lord."),

    ("Joshua", "Josh", 1, 9,
     "Have not I commanded thee? Be strong and of a good courage; be not afraid, neither be thou dismayed: for the LORD thy God is with thee whithersoever thou goest.",
     "Have I not commanded you? Be strong and courageous. Do not be afraid; do not be discouraged, for the Lord your God will be with you wherever you go.",
     "Haven't I commanded you? Strength! Courage! Don't be timid; don't get discouraged. God, your God, is with you every step you take.",
     "This is my command—be strong and courageous! Do not be afraid or discouraged. For the Lord your God is with you wherever you go."),

    ("Psalm", "Ps", 119, 105,
     "Thy word is a lamp unto my feet, and a light unto my path.",
     "Your word is a lamp for my feet, a light on my path.",
     "By your words I can see where I'm going; they throw a beam of light on my dark path.",
     "Your word is a lamp to guide my feet and a light for my path."),

    ("Matthew", "Matt", 28, 19,
     "Go ye therefore, and teach all nations, baptizing them in the name of the Father, and of the Son, and of the Holy Ghost:",
     "Therefore go and make disciples of all nations, baptizing them in the name of the Father and of the Son and of the Holy Spirit,",
     "Go out and train everyone you meet, far and near, in this way of life, marking them by baptism in the threefold name: Father, Son, and Holy Spirit.",
     "Therefore, go and make disciples of all the nations, baptizing them in the name of the Father and the Son and the Holy Spirit."),

    ("Romans", "Rom", 10, 9,
     "That if thou shalt confess with thy mouth the Lord Jesus, and shalt believe in thine heart that God hath raised him from the dead, thou shalt be saved.",
     "If you declare with your mouth, Jesus is Lord, and believe in your heart that God raised him from the dead, you will be saved.",
     "Say the welcoming word to God—Jesus is my Master—embracing, body and soul, God's work of doing in us what he did in raising Jesus from the dead. That's it.",
     "If you openly declare that Jesus is Lord and believe in your heart that God raised him from the dead, you will be saved."),
]


def init_database():
    """Initialize the database with schema and sample data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Execute schema
    with open(SCHEMA_PATH, "r") as f:
        cursor.executescript(f.read())

    # Insert sample verses
    for verse_data in SAMPLE_VERSES:
        book, book_abbr, chapter, verse, kjv, niv, msg, nlt = verse_data
        cursor.execute("""
            INSERT OR REPLACE INTO verses (book, book_abbr, chapter, verse, kjv, niv, msg, nlt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (book, book_abbr, chapter, verse, kjv, niv, msg, nlt))

    conn.commit()
    conn.close()
    print(f"✅ Database initialized at: {DB_PATH}")
    print(f"✅ {len(SAMPLE_VERSES)} sample verses loaded")
    print("\nTo add the full Bible, import a complete Bible dataset CSV into the verses table.")
    print("Format: book, book_abbr, chapter, verse, kjv, niv, msg, nlt")


if __name__ == "__main__":
    init_database()
