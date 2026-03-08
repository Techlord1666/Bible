"""
Church Bible Verse Presentation System
Main Flask Backend — handles voice recognition, verse lookup, and SSE streaming
"""

import os
import sys
import json
import time
import queue
import logging
import threading
import subprocess
from pathlib import Path

from flask import Flask, render_template, jsonify, request, Response, send_from_directory
from flask_cors import CORS

# ── Path setup ─────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "database" / "bible.db"
FRONTEND_DIR = BASE_DIR / "frontend"

sys.path.insert(0, str(BASE_DIR / "backend"))
from parser import parse_reference, fetch_verse, BibleReference

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Flask app ──────────────────────────────────────────────────────────────────
app = Flask(__name__, template_folder=str(FRONTEND_DIR), static_folder=str(FRONTEND_DIR / "static"))
CORS(app)

# ── State ──────────────────────────────────────────────────────────────────────
current_verse = {
    "reference": None,
    "text": None,
    "translation": "KJV",
    "book": None,
    "chapter": None,
    "verse": None,
    "available_translations": {},
    "status": "idle",  # idle | listening | displaying | error
    "last_speech": "",
    "error": None,
}

verse_event_queue = queue.Queue()
is_listening = False
listen_thread = None


# ── SSE helpers ────────────────────────────────────────────────────────────────
def push_event(event_type: str, data: dict):
    """Push an event to all SSE subscribers."""
    verse_event_queue.put({"type": event_type, "data": data})


# ── Routes ─────────────────────────────────────────────────────────────────────
@app.route("/")
def control_panel():
    return send_from_directory(str(FRONTEND_DIR), "control.html")


@app.route("/display")
def display():
    return send_from_directory(str(FRONTEND_DIR), "display.html")


@app.route("/api/status")
def api_status():
    return jsonify({
        "listening": is_listening,
        "current_verse": current_verse,
        "db_path": str(DB_PATH),
        "db_exists": DB_PATH.exists(),
    })


@app.route("/api/verse", methods=["POST"])
def api_verse():
    """Manually trigger a verse display — for testing or manual entry."""
    data = request.get_json()
    speech_text = data.get("text", "").strip()

    if not speech_text:
        return jsonify({"error": "No text provided"}), 400

    return _process_speech(speech_text)


@app.route("/api/verse/manual", methods=["POST"])
def api_verse_manual():
    """Direct verse lookup — book/chapter/verse/translation."""
    data = request.get_json()
    try:
        ref = BibleReference(
            book=data["book"],
            chapter=int(data["chapter"]),
            verse=int(data["verse"]),
            translation=data.get("translation", "kjv").lower(),
            raw_text="Manual entry",
        )
        result = fetch_verse(ref, db_path=str(DB_PATH))
        if result:
            _update_display(result)
            return jsonify({"success": True, "verse": result})
        return jsonify({"error": "Verse not found"}), 404
    except (KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/listen/start", methods=["POST"])
def api_listen_start():
    """Start the Whisper voice recognition listener."""
    global is_listening, listen_thread
    if is_listening:
        return jsonify({"status": "already_listening"})

    is_listening = True
    listen_thread = threading.Thread(target=_whisper_listen_loop, daemon=True)
    listen_thread.start()
    logger.info("🎤 Whisper listener started")
    push_event("status", {"listening": True, "message": "Listening started"})
    return jsonify({"status": "started"})


@app.route("/api/listen/stop", methods=["POST"])
def api_listen_stop():
    """Stop the voice recognition listener."""
    global is_listening
    is_listening = False
    push_event("status", {"listening": False, "message": "Listening stopped"})
    logger.info("⏹  Whisper listener stopped")
    return jsonify({"status": "stopped"})


@app.route("/api/clear", methods=["POST"])
def api_clear():
    """Clear the display screen."""
    current_verse.update({
        "reference": None, "text": None, "status": "idle",
        "error": None, "last_speech": "",
    })
    push_event("clear", {})
    return jsonify({"status": "cleared"})


@app.route("/api/history")
def api_history():
    """Fetch recent display history."""
    import sqlite3
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT book, chapter, verse, version, speech_text, displayed_at
        FROM display_log
        ORDER BY displayed_at DESC
        LIMIT 20
    """)
    rows = cursor.fetchall()
    conn.close()
    history = [
        {"book": r[0], "chapter": r[1], "verse": r[2], "version": r[3],
         "speech": r[4], "time": r[5]}
        for r in rows
    ]
    return jsonify(history)


@app.route("/api/stream")
def api_stream():
    """Server-Sent Events stream for real-time updates to display screen."""
    def event_generator():
        # Send current state on connect
        yield f"data: {json.dumps({'type': 'init', 'data': current_verse})}\n\n"

        while True:
            try:
                event = verse_event_queue.get(timeout=30)
                yield f"data: {json.dumps(event)}\n\n"
            except queue.Empty:
                yield "data: {\"type\": \"ping\"}\n\n"

    return Response(
        event_generator(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# ── Core logic ─────────────────────────────────────────────────────────────────
def _process_speech(text: str):
    """Parse speech text and display matching verse."""
    logger.info(f"🗣  Speech: {text}")
    current_verse["last_speech"] = text

    ref = parse_reference(text, db_path=str(DB_PATH))
    if not ref:
        msg = f"No Bible reference detected in: '{text}'"
        logger.warning(msg)
        current_verse["status"] = "error"
        current_verse["error"] = msg
        push_event("error", {"message": msg, "speech": text})
        return jsonify({"error": msg}), 422

    logger.info(f"📖 Parsed: {ref.display_ref()} [{ref.translation_upper()}]")

    result = fetch_verse(ref, db_path=str(DB_PATH))
    if not result:
        msg = f"Verse not found: {ref.display_ref()}"
        logger.warning(msg)
        current_verse["status"] = "error"
        current_verse["error"] = msg
        push_event("error", {"message": msg, "reference": ref.display_ref()})
        return jsonify({"error": msg}), 404

    _update_display(result)
    return jsonify({"success": True, "verse": result})


def _update_display(result: dict):
    """Update state and push display event to all connected screens."""
    current_verse.update({
        "reference": result["reference"],
        "text": result["text"],
        "translation": result["translation"],
        "book": result["book"],
        "chapter": result["chapter"],
        "verse": result["verse"],
        "available_translations": result["available_translations"],
        "status": "displaying",
        "error": None,
    })
    push_event("verse", result)
    logger.info(f"✅ Displayed: {result['reference']} [{result['translation']}]")


# ── Whisper listener ───────────────────────────────────────────────────────────
def _whisper_listen_loop():
    """
    Continuous Whisper speech recognition loop.
    Records short audio clips and transcribes them using Whisper.
    Requires: whisper, sounddevice, scipy
    """
    try:
        import whisper
        import numpy as np
        import sounddevice as sd
        from scipy.io.wavfile import write as wav_write
        import tempfile

        logger.info("⚙️  Loading Whisper model (base)…")
        model = whisper.load_model("base")
        logger.info("✅ Whisper model loaded — listening for Bible references")

        SAMPLE_RATE = 16000
        CHUNK_SECONDS = 5  # listen in 5-second windows
        SILENCE_THRESHOLD = 0.01

        while is_listening:
            push_event("status", {"listening": True, "message": "Listening…"})

            # Record audio
            audio = sd.rec(
                int(CHUNK_SECONDS * SAMPLE_RATE),
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype="float32",
            )
            sd.wait()

            if not is_listening:
                break

            # Skip silent segments
            if np.max(np.abs(audio)) < SILENCE_THRESHOLD:
                continue

            # Transcribe
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                wav_write(f.name, SAMPLE_RATE, audio)
                tmp_path = f.name

            try:
                result = model.transcribe(tmp_path, language="en", fp16=False)
                text = result.get("text", "").strip()
                if text:
                    logger.info(f"🎙  Transcribed: {text}")
                    push_event("speech", {"text": text})
                    _process_speech(text)
            finally:
                os.unlink(tmp_path)

    except ImportError as e:
        msg = f"Missing dependency: {e}. Run: pip install openai-whisper sounddevice scipy"
        logger.error(msg)
        push_event("error", {"message": msg})
    except Exception as e:
        logger.error(f"Whisper listener error: {e}")
        push_event("error", {"message": str(e)})
    finally:
        global is_listening
        is_listening = False
        push_event("status", {"listening": False, "message": "Listening stopped"})


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not DB_PATH.exists():
        logger.warning("⚠️  Database not found — run: python database/seed.py")
    else:
        logger.info(f"✅ Database found: {DB_PATH}")

    logger.info("🚀 Starting Church Bible Verse Presentation System")
    logger.info("   Control Panel : http://localhost:5000")
    logger.info("   Display Screen : http://localhost:5000/display")

    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
