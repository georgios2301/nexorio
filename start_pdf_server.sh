#!/bin/bash
cd "$(dirname "$0")/Lieferschein/Programm"
export PORT=4000
echo "Starting PDF server on port 4000..."
python pdf_server.py