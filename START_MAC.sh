#!/bin/bash
clear

echo ""
echo "====================================================="
echo "     CHURCH BIBLE VERSE PRESENTATION SYSTEM"
echo "====================================================="
echo ""

# Check Python
echo "[1/5] Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo ""
    echo "ERROR: Python 3 is not installed!"
    echo "Download from: https://www.python.org/downloads/"
    echo ""
    open https://www.python.org/downloads/
    exit 1
fi
python3 --version
echo "Python found!"

# Install dependencies
echo ""
echo "[2/5] Installing packages (first time takes a few minutes)..."
pip3 install flask flask-cors openai-whisper sounddevice scipy numpy --quiet
echo "Packages ready!"

# macOS: install portaudio for microphone support
if command -v brew &> /dev/null; then
    brew install portaudio --quiet 2>/dev/null || true
fi

# Initialize database
echo ""
echo "[3/5] Setting up Bible database..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"
if [ ! -f "database/bible.db" ]; then
    python3 database/seed.py
else
    echo "Database already exists - skipping"
fi

# Find local IP
echo ""
echo "[4/5] Finding your network address..."
MYIP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "unknown")
echo "Your local IP: $MYIP"

# Launch
echo ""
echo "====================================================="
echo " SYSTEM IS RUNNING - DO NOT CLOSE THIS WINDOW"
echo "====================================================="
echo ""
echo " YOUR COMPUTER:"
echo " Control Panel  -- http://localhost:5000"
echo " Display Screen -- http://localhost:5000/display"
echo ""
echo " FROM PROJECTOR PC / ANOTHER DEVICE:"
echo " http://$MYIP:5000/display"
echo ""
echo "====================================================="
echo ""

sleep 3
open http://localhost:5000
open http://localhost:5000/display

python3 backend/app.py
